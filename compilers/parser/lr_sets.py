from __future__ import annotations

from dataclasses import dataclass
from typing import AbstractSet, Generic, Iterable, Iterator, TypeVar, overload

from compilers.parser.lr_items import LRItem

LRItemType = TypeVar("LRItemType", bound=LRItem)


@dataclass(frozen=True)
class LRSet(Generic[LRItemType]):
    _KERNEL_FIELD_NAME = "_kernel"
    _NONKERNEL_FIELD_NAME = "_nonkernel"

    @property
    def kernel(self) -> frozenset[LRItemType]:
        return getattr(self, self._KERNEL_FIELD_NAME)

    @property
    def nonkernel(self) -> frozenset[LRItemType]:
        return getattr(self, self._NONKERNEL_FIELD_NAME)

    @overload
    def __init__(self, kernel: Iterable[LRItemType]) -> None:
        pass

    @overload
    def __init__(
        self, kernel: Iterable[LRItemType], nonkernel: Iterable[LRItemType]
    ) -> None:
        pass

    def __init__(
        self,
        kernel: Iterable[LRItemType],
        nonkernel: Iterable[LRItemType] | None = None,
    ) -> None:
        object.__setattr__(self, self._KERNEL_FIELD_NAME, frozenset(kernel))
        object.__setattr__(self, self._NONKERNEL_FIELD_NAME, frozenset(nonkernel or {}))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LRSet):
            return self.kernel == other.kernel
        if not isinstance(other, AbstractSet):
            return False
        # NOTE: this will fail equality check if the other set contains nonkernels
        return self.kernel == other

    def __hash__(self) -> int:
        """Custom hashing method that excludes nonkernel items."""
        return hash(self.kernel)

    def __iter__(self) -> Iterator[LRItemType]:
        for item in self.kernel:
            yield item
        for item in self.nonkernel:
            yield item

    def __repr__(self) -> str:
        kernel_lines = [str(item).strip() for item in self.kernel]
        return ", ".join(kernel_lines)
