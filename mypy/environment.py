from abc import abstractmethod
from mypy.errors import Errors
from typing import Undefined, Set, List, cast, Optional
from mypy.nodes import SymbolTableNode, SymbolTable, UNBOUND_TVAR, BOUND_TVAR, TypeInfo, Context, MypyFile


# Map from obsolete name to the current spelling.
obsolete_name_mapping = {
    'typing.Function': 'typing.Callable',
    'typing.typevar': 'typing.TypeVar',
}


class Environment:
    """ Provides access to all symbols visible in a scope
    """

    symbol_table = Undefined(SymbolTable)

    _block_depth = 0

    errors = Undefined(Errors)

    def __init__(self, errors: Errors):
        self.symbol_table = SymbolTable()
        self.errors = errors

    @abstractmethod
    def lookup_forward_reference(self, name: str) -> SymbolTableNode:
        pass

    @abstractmethod
    def add_symbol(self, name: str, symbol: SymbolTableNode, context: Context) -> None:
        pass

    @abstractmethod
    def global_scope(self):
        pass

    @abstractmethod
    def lookup(self, name: str, ctx: Context) -> SymbolTableNode:
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

    def name_not_defined(self, name: str, ctx: Context) -> None:
        message = "Name '{}' is not defined".format(name)
        extra = self.undefined_name_extra_info(name)
        if extra:
            message += ' {}'.format(extra)
        self.fail(message, ctx)

    def undefined_name_extra_info(self, fullname: str) -> Optional[str]:
        if fullname in obsolete_name_mapping:
            return "(it's now called '{}')".format(obsolete_name_mapping[fullname])
        else:
            return None

    def check_for_obsolete_short_name(self, name: str, ctx: Context) -> None:
        matches = [obsolete_name
                   for obsolete_name in obsolete_name_mapping
                   if obsolete_name.rsplit('.', 1)[-1] == name]
        if len(matches) == 1:
            self.fail("(Did you mean '{}'?)".format(obsolete_name_mapping[matches[0]]), ctx)

    def name_already_defined(self, name: str, ctx: Context) -> None:
        self.fail("Name '{}' already defined".format(name), ctx)

    def lookup_local(self, name: str, context: Context) -> SymbolTableNode:
        self.name_not_defined(name, context)


class GlobalEnvironment(Environment):

    def lookup(self, name: str, ctx: Context) -> SymbolTableNode:
        if name in self.symbol_table:
            return self.symbol_table[name]

        # Builtins
        b = self.symbol_table.get('__builtins__', None)
        if b:
            table = cast(MypyFile, b.node).names
            if name in table:
                if name[0] == "_" and name[1] != "_":
                    self.name_not_defined(name, ctx)
                    return None
                node = table[name]
                # Only succeed if we are not using a type alias such List -- these must be
                # be accessed via the typing module.
                if node.node.name() == name:
                    return node

        # Give up.
        self.name_not_defined(name, ctx)
        self.check_for_obsolete_short_name(name, ctx)
        return None

    def lookup_forward_reference(self, name: str):
        pass

    def add_symbol(self, name: str, symbol: SymbolTableNode, context: Context) -> None:
        if name in self.symbol_table and (not isinstance(symbol.node, MypyFile) or
                                          self.symbol_table[name].node != symbol.node):
            # Modules can be imported multiple times to support import
            # of multiple submodules of a package (e.g. a.x and a.y).
            self.name_already_defined(name, context)
        self.symbol_table[name] = symbol

    def replace_symbol(self, name: str, symbol: SymbolTableNode, context: Context) -> None:
        self.symbol_table[name] = symbol

    def global_scope(self):
        return self


class NonGlobalEnvironment(Environment):

    parent_scope = None  # type: Environment

    bound_tvars = Undefined(List[SymbolTableNode])

    def __init__(self, parent_scope: Environment):
        self.parent_scope = parent_scope
        self.errors = parent_scope.errors
        self.bound_tvars = []
        self.symbol_table = SymbolTable()

    def lookup(self, name: str, context: Context) -> SymbolTableNode:
        if self.parent_scope:
            return self.parent_scope.lookup(name, context)
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

    nonlocal_decls = Undefined(Set[str])
    global_decls = Undefined(Set[str])

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

    def lookup(self, name: str, context: Context) -> SymbolTableNode:
        # 1a. Name declared using 'global x'
        if name in self.global_decls:
            if name in self.global_scope().symbol_table:
                return self.global_scope().symbol_table[name]
            else:
                self.name_not_defined(name, context)
                return None

        # TODO call parent

    def lookup_local(self, name: str, context: Context) -> SymbolTableNode:
        if name in self.symbol_table:
            return self.symbol_table[name]
        else:
            self.parent_scope.lookup_local(name, context)


class ClassEnvironment(NonGlobalEnvironment):

    _type = Undefined(TypeInfo)
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
