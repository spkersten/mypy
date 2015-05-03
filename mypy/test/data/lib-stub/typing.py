# Stub for typing module. Many of the definitions have special handling in
# the type checker, so they can just be initialized to anything.

from abc import abstractmethod

cast = object()
overload = object()
Any = object()
Union = object()
Optional = object()
TypeVar = object()
Generic = object()
Tuple = object()
Callable = object()
builtinclass = object()
_promote = object()
NamedTuple = object()
no_type_check = object()

# Type aliases.
List = object()
Dict = object()
Set = object()

T = TypeVar('T')
T_contra = TypeVar('T_contra')
V_co = TypeVar('V_co')

class Iterable(Generic[T]):
    @abstractmethod
    def __iter__(self) -> 'Iterator[T]': pass

class Iterator(Iterable[T], Generic[T]):
    @abstractmethod
    def __next__(self) -> T: pass

class Generator(Iterator[T], Generic[T, T_contra, V_co]): pass

class Sequence(Generic[T]):
    @abstractmethod
    def __getitem__(self, n: Any) -> T: pass
