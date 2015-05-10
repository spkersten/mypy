from abc import abstractmethod
from mypy.errors import Errors
from typing import Set, List
from mypy.nodes import SymbolTableNode, SymbolTable, UNBOUND_TVAR, BOUND_TVAR, TypeInfo, Context


class Environment:
    """ Provides access to all symbols visible in a scope
    """

    symbol_table = None  # type: SymbolTable

    _block_depth = 0

    errors = None  # type: Errors

    def __init__(self, errors: Errors):
        self.symbol_table = SymbolTable()
        self.errors = errors

    @abstractmethod
    def lookup(self, name: str) -> SymbolTableNode:
        pass

    @abstractmethod
    def lookup_forward_reference(self, name: str) -> SymbolTableNode:
        pass

    @abstractmethod
    def add_symbol(self, symbol) -> None:
        pass

    @abstractmethod
    def global_scope(self):
        pass

    def increase_block_depth(self):
        self._block_depth += 1

    def decrease_block_depth(self):
        self._block_depth -= 1

    def block_depth(self) -> int:
        return self._block_depth

    def type_var_names(self) -> Set[str]:
        return set()

    def disable_typevars(self) -> None:
        pass

    def enable_typevars(self) -> None:
        pass

    def fail(self, msg: str, ctx: Context) -> None:
        self.errors.report(ctx.get_line(), msg)

    def add_global_decl(self, name: str, ctx: Context) -> None:
        pass  # global declarations are allowed in all scopes,
              # but only have an effect in function scopes.


class GlobalEnvironment(Environment):

    def lookup(self, name: str):
        pass

    def lookup_forward_reference(self, name: str):
        pass

    def add_symbol(self, symbol) -> None:
        pass

    def global_scope(self):
        return self


class NonGlobalEnvironment(Environment):

    parent_scope = None  # type: Environment

    bound_tvars = None  # type: List[SymbolTableNode]

    def __init__(self, parent_scope: Environment):
        self.parent_scope = parent_scope
        self.errors = parent_scope.errors
        self.bound_tvars = []

    def lookup(self, name: str) -> SymbolTableNode:
        if self.parent_scope:
            return self.parent_scope.lookup(name)
        else:
            pass
            # TODO FAIL

    def lookup_forward_reference(self, name: str) -> SymbolTableNode:
        if self.parent_scope:
            return self.parent_scope.lookup_forward_reference(name)
        else:
            pass
            # TODO FAIL

    def add_symbol(self, symbol):
        pass

    def global_scope(self):
        return self.parent_scope.global_scope()

    def disable_typevars(self) -> None:
        for node in self.bound_tvars:
            assert node.kind in (BOUND_TVAR, UNBOUND_TVAR)
            node.kind = UNBOUND_TVAR

    def enable_typevars(self) -> None:
        for node in self.bound_tvars:
            assert node.kind in (BOUND_TVAR, UNBOUND_TVAR)
            node.kind = BOUND_TVAR

    @abstractmethod
    def type(self):
        pass


class FunctionEnvironment(NonGlobalEnvironment):

    nonlocal_decls = None  # type: Set[str]
    global_decls = None  # type: Set[str]

    def __init__(self, parent_scope: Environment):
        super().__init__(parent_scope)
        self.nonlocal_decls = set()
        self.global_decls = set()

    def add_symbol(self, symbol) -> None:
        pass

    def increase_block_depth(self) -> None:
        self.parent_scope.increase_block_depth()

    def decrease_block_depth(self) -> None:
        self.parent_scope.decrease_block_depth()

    def block_depth(self) -> None:
        return self.parent_scope.block_depth()

    def type(self) -> TypeInfo:
        return self.parent_scope.type()

    def type_var_names(self) -> Set[str]:
        return self.parent_scope.type_var_names()

    def in_method(self) -> bool:
        return isinstance(self.parent_scope, ClassEnvironment)

    def add_nonlocal_decl(self, name: str, ctx: Context) -> None:
        if name in self.global_decls:
            self.fail("Name '{}' is nonlocal and global".format(name), ctx)
        self.nonlocal_decls.add(name)

    def add_global_decl(self, name: str, ctx: Context) -> None:
        if name in self.nonlocal_decls:
            self.fail("Name '{}' is nonlocal and global".format(name), ctx)
        self.global_decls.add(name)


class ClassEnvironment(NonGlobalEnvironment):

    _type = None  # type: TypeInfo
    sem = None  # TODO temporary until lookup has been move here

    def __init__(self, parent_scope: Environment):
        super().__init__(parent_scope)
        self._block_depth = -1  # The class body increments this to 0

    def add_symbol(self, symbol) -> None:
        pass

    def type(self) -> TypeInfo:
        return self._type

    def set_type(self, type: TypeInfo) -> None:
        self._type = type

    def type_var_names(self) -> Set[str]:
        return set(self._type.type_vars)

    def bind_type_vars(self) -> None:
        """ Unbind type variables of previously active class and bind
        the type variables for the active class.
        """
        self.parent_scope.disable_typevars()
        self.bound_tvars = self.bind_class_type_variables_in_symbol_table()

    def unbind_type_vars(self) -> None:
        """ Unbind the active class' type vars and rebind the
        type vars of the previously active class.
        """
        self.disable_typevars()
        self.parent_scope.enable_typevars()

    def bind_class_type_variables_in_symbol_table(self) -> List[SymbolTableNode]:
        vars = self._type.type_vars
        nodes = []  # type: List[SymbolTableNode]
        if vars:
            for i in range(len(vars)):
                node = self.bind_type_var(vars[i], i + 1, self._type)
                nodes.append(node)
        return nodes

    def bind_type_var(self, fullname: str, id: int, context: Context) -> SymbolTableNode:
        node = self.sem.lookup_qualified(fullname, context)
        node.kind = BOUND_TVAR
        node.tvar_id = id
        return node
