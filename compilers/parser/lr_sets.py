from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from dataclasses import dataclass
from typing import AbstractSet, Generic, Iterable, Iterator, TypeVar, overload

from typing_extensions import Self

from compilers.grammar.grammar import Grammar
from compilers.grammar.symbols import is_nonterminal
from compilers.parser.lr_items import LR1Item, LRItem

LRItemType = TypeVar("LRItemType", bound=LRItem)


@dataclass(frozen=True)
class LRSet(Generic[LRItemType], ABC):
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
        kernel_lines = (str(item).strip() for item in self.kernel)
        return ", ".join(kernel_lines)

    @abstractmethod
    def closure(self, g: Grammar) -> Self:
        pass


class LR0Set(LRSet[LRItem]):
    def closure(self, g: Grammar) -> LR0Set:
        previous_set: LR0Set | None = None
        current_set = self

        while previous_set is None or previous_set.nonkernel != current_set.nonkernel:
            nonkernel_items = set(current_set.nonkernel)

            for item in current_set:
                if not item.complete and is_nonterminal(
                    nonterminal := item.next_symbol
                ):
                    production = g.get_production(nonterminal)
                    for line in production.derivations:
                        nonkernel_items.add(LRItem(line))

            previous_set = current_set
            current_set = LR0Set(self.kernel, frozenset(nonkernel_items))

        return current_set


class LR1Set(LRSet[LR1Item]):
    def closure(self, g: Grammar) -> LR1Set:
        previous_set: LR1Set | None = None
        current_set = self

        while previous_set is None or previous_set.nonkernel != current_set.nonkernel:
            nonkernel_items = set(current_set.nonkernel)

            for item in current_set:
                if not item.complete and is_nonterminal(
                    nonterminal := item.next_symbol
                ):
                    production = g.get_production(nonterminal)
                    for lookahead in g.get_first((*item.next().tail, item.lookahead)):
                        for line in production.derivations:
                            nonkernel_items.add(LR1Item(line, lookahead))

            previous_set = current_set
            current_set = LR1Set(self.kernel, frozenset(nonkernel_items))

        return current_set

    def __str__(self) -> str:
        lines = []
        header = "-" * 20

        items = defaultdict(list)
        for item in self.kernel:
            items[item.to_lr0()].append(item.lookahead)

        lines.append(header)
        for lr0_item, lookaheads in items.items():
            lines.append(f"{lr0_item} | {', '.join(str(x) for x in lookaheads)}")
        lines.append(header)

        return "\n".join(lines)
