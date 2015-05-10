from abc import abstractmethod
from mypy.errors import Errors
from typing import Undefined, Set, List
from mypy.nodes import SymbolTableNode, SymbolTable, UNBOUND_TVAR, BOUND_TVAR, TypeInfo


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

    bound_tvars = Undefined(List[SymbolTableNode])

    def __init__(self, parent_scope: Environment):
        self.parent_scope = parent_scope

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

    nonlocal_decls = Undefined(Set[str])
    global_decls = Undefined(Set[str])

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


class ClassEnvironment(NonGlobalEnvironment):

    _type = Undefined(TypeInfo)

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
