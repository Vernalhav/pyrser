from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
Predicate = Callable[[T], bool]


def find_first(items: Iterable[T], predicate: Predicate[T]) -> T | None:
    return next((item for item in items if predicate(item)), None)
