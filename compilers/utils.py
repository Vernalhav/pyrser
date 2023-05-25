from collections import defaultdict
from collections.abc import Mapping
from typing import Any, Callable, Generic, Iterable, TypeVar, overload

T = TypeVar("T")
Predicate = Callable[[T], bool]


def find_first(items: Iterable[T], predicate: Predicate[T]) -> T | None:
    return next((item for item in items if predicate(item)), None)


K = TypeVar("K")
K1 = TypeVar("K1")
K2 = TypeVar("K2")
V = TypeVar("V")


class GroupedDict(Generic[K1, K2, V], dict[K1, dict[K2, V]]):
    def flatten(self) -> Iterable[tuple[K1, K2, V]]:
        for k1, subdict in self.items():
            for k2, v in subdict.items():
                yield k1, k2, v

    def flat_len(self) -> int:
        return len(tuple(self.flatten()))

    @overload
    def __getitem__(self, key: tuple[K1, K2]) -> V:
        pass

    @overload
    def __getitem__(self, key: K1) -> dict[K2, V]:
        pass

    def __getitem__(self, key: K1 | tuple[K1, K2]) -> V | dict[K2, V]:
        if isinstance(key, tuple):
            k1, k2 = key
            return super().__getitem__(k1)[k2]
        return super().__getitem__(key)

    @overload
    def __setitem__(self, key: tuple[K1, K2], value: V) -> None:
        pass

    @overload
    def __setitem__(self, key: K1, value: dict[K2, V]) -> None:
        pass

    def __setitem__(self, key: K1 | tuple[K1, K2], value: V | dict[K2, V]) -> None:
        if isinstance(key, tuple) and not isinstance(value, dict):
            k1, k2 = key
            if k1 not in self:
                self[k1] = {}
            return super().__getitem__(k1).__setitem__(k2, value)
        if not isinstance(key, tuple) and isinstance(value, dict):
            return super().__setitem__(key, value)
        raise TypeError("Inappropriate index or value type.")


class GroupedDefaultDict(Generic[K1, K2, V], GroupedDict[K1, K2, V]):
    def __init__(
        self, default_factory: Callable[[], V], *args: Any, **kwargs: Any
    ) -> None:
        self.default_factory = default_factory
        super().__init__(self, *args, **kwargs)

    @overload
    def __getitem__(self, key: tuple[K1, K2]) -> V:
        pass

    @overload
    def __getitem__(self, key: K1) -> dict[K2, V]:
        pass

    def __getitem__(self, key: K1 | tuple[K1, K2]) -> V | dict[K2, V]:
        if isinstance(key, tuple):
            k1, k2 = key
            if k1 not in self:
                super().__setitem__(k1, defaultdict(self.default_factory))
            # ignoring line below because of mypy bug
            return super().__getitem__(k1).__getitem__(k2)  # type: ignore

        if key not in self:
            super().__setitem__(key, defaultdict(self.default_factory))
        return super().__getitem__(key)


def flatten(d: Mapping[K, Iterable[V]], /) -> Iterable[tuple[K, V]]:
    for key, iterable in d.items():
        for x in iterable:
            yield key, x
