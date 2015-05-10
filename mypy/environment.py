from abc import abstractmethod
from mypy.errors import Errors
from typing import Set, List
from mypy.nodes import SymbolTableNode, SymbolTable, UNBOUND_TVAR, BOUND_TVAR


class Environment:
    """ Provides access to all symbols visible in a scope
    """

    symbol_table = None  # type: SymbolTable

    block_depth = 0

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


class FunctionEnvironment(NonGlobalEnvironment):

    nonlocal_decls = None  # type: Set[str]
    global_decls = None  # type: Set[str]

    def add_symbol(self, symbol) -> None:
        pass


class ClassEnvironment(NonGlobalEnvironment):

    def add_symbol(self, symbol) -> None:
        pass