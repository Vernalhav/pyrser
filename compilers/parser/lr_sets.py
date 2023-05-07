from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import AbstractSet, Generic, Iterable, Iterator, TypeVar, overload

from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import ProductionLine
from compilers.grammar.symbols import Symbol, is_nonterminal
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
        return self.kernel == other

    def __hash__(self) -> int:
        """Custom hashing method that excludes nonkernel items."""
        return hash(self.kernel)

    def __iter__(self) -> Iterator[LRItemType]:
        for item in self.kernel:
            yield item
        for item in self.nonkernel:
            yield item


def compute_lr_sets(g: Grammar) -> set[LRSet[LRItem]]:
    if is_augmented(g) is False:
        raise ValueError("Given grammar is not augmented with start production")

    sets: set[LRSet[LRItem]] = set()
    work: deque[LRSet[LRItem]] = deque()

    start_item = get_initial_lr_item(g)
    work.append(LRSet[LRItem](frozenset((start_item,))))

    while len(work) > 0:
        current_set = work.popleft()
        sets.add(current_set)

        transition_sets = compute_transition_sets(closure(current_set, g))
        for transition_set in transition_sets:
            if transition_set not in sets:
                work.append(transition_set)

    return sets


def compute_transition_sets(lr_set: LRSet[LRItem]) -> Iterable[LRSet[LRItem]]:
    """Assumes `lr_set` has already been closed"""
    return (goto(lr_set, symbol) for symbol, _ in get_transition_symbols(lr_set))


def goto(lr_set: LRSet[LRItem], symbol: Symbol) -> LRSet[LRItem]:
    """Assumes `lr_set` has already been closed"""
    kernel = frozenset(
        item.next()
        for item in lr_set
        if not item.complete and item.next_symbol == symbol
    )
    return LRSet(kernel)


def get_transition_symbols(
    lr_set: LRSet[LRItem],
) -> Iterable[tuple[Symbol, Iterable[LRItem]]]:
    """Assumes `lr_set` has already been closed"""
    transition_symbols = defaultdict(list)

    for item in lr_set:
        if not item.complete:
            transition_symbols[item.next_symbol].append(item)

    return transition_symbols.items()


def closure(lr_set: LRSet[LRItem], g: Grammar) -> LRSet[LRItem]:
    previous_set: LRSet[LRItem] | None = None
    current_set = lr_set

    while previous_set is None or previous_set.nonkernel != current_set.nonkernel:
        nonkernel_items = set(current_set.nonkernel)

        for item in current_set:
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


def is_augmented(g: Grammar) -> bool:
    if len(g.get_production(g.start_symbol).derivations) > 1:
        return False

    for _, handle in g.derivations:
        if g.start_symbol in handle:
            return False

    return True
