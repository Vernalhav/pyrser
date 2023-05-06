from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import AbstractSet, Generic, Iterable, TypeVar

from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import ProductionLine
from compilers.grammar.symbols import is_nonterminal
from compilers.parser.lr_items import LRItem

LRItemType = TypeVar("LRItemType", bound=LRItem)


@dataclass(frozen=True)
class LRSet(Generic[LRItemType]):
    kernel: frozenset[LRItemType]
    nonkernel: frozenset[LRItemType] = field(default_factory=frozenset)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LRSet):
            return self.kernel == other.kernel
        if not isinstance(other, AbstractSet):
            return False
        return self.kernel == other

    def __hash__(self) -> int:
        """Custom hashing method that excludes nonkernel items."""
        return hash(self.kernel)

    @staticmethod
    def from_items(
        kernel: Iterable[LRItemType], nonkernel: Iterable[LRItemType] | None = None
    ) -> LRSet[LRItemType]:
        """Convenience method to pass any iterable to the constructor
        and avoid having to explicitly convert the iterables to frozensets.
        """
        if nonkernel is not None:
            return LRSet(frozenset(kernel), frozenset(nonkernel))
        return LRSet(frozenset(kernel))


def get_transition_symbols(
    lr_set: LRSet[LRItem],
) -> Iterable[tuple[Symbol, Iterable[LRItem]]]:
    transition_symbols = defaultdict(list)

    for item in lr_set.kernel | lr_set.nonkernel:
        if not item.complete:
            transition_symbols[item.next_symbol].append(item)

    return transition_symbols.items()


def closure(lr_set: LRSet[LRItem], g: Grammar) -> LRSet[LRItem]:
    previous_set: LRSet[LRItem] | None = None
    current_set = lr_set

    while previous_set is None or previous_set.nonkernel != current_set.nonkernel:
        nonkernel_items = set(current_set.nonkernel)

        for item in current_set.kernel | current_set.nonkernel:
            if not item.complete and is_nonterminal(nonterminal := item.next_symbol):
                production = g.get_production(nonterminal)
                for line in production.derivations:
                    nonkernel_items.add(LRItem(line))
                if production.nullable:
                    nonkernel_items.add(LRItem(ProductionLine(nonterminal, ())))

        previous_set = current_set
        current_set = LRSet(lr_set.kernel, frozenset(nonkernel_items))

    return current_set


def get_initial_lr_item(g: Grammar) -> LRItem:
    """Assumes `g` is an augmented grammar."""
    initial_line, *_ = g.get_production(g.start_symbol).derivations
    return LRItem(initial_line)

