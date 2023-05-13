from collections import defaultdict, deque
from typing import Iterable

from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import ProductionLine
from compilers.grammar.symbols import Symbol, is_nonterminal
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import LR0Set, LRSet


class LRAutomata:
    grammar: Grammar
    states: set[LR0Set]
    _transitions: dict[tuple[LR0Set, Symbol], LR0Set]

    def __init__(self, g: Grammar) -> None:
        self.grammar = g
        self._compute_states_and_transitions()

    @property
    def transition_count(self) -> int:
        return len(self._transitions)

    def get_transition(self, state: LR0Set, symbol: Symbol) -> LR0Set:
        return self._transitions[(state, symbol)]

    def _compute_states_and_transitions(self) -> None:
        if is_augmented(self.grammar) is False:
            raise ValueError("Given grammar is not augmented with start production")

        self.states = set()
        self._transitions = {}
        work: deque[LR0Set] = deque()

        start_item = get_initial_lr_item(self.grammar)
        work.append(LR0Set(frozenset((start_item,))))

        while len(work) > 0:
            current_set = work.popleft()
            self.states.add(current_set)

            transition_sets = compute_transition_sets(
                closure(current_set, self.grammar)
            )
            for symbol, transition_set in transition_sets:
                self._transitions[(current_set, symbol)] = transition_set
                if transition_set not in self.states:
                    work.append(transition_set)


def compute_transition_sets(lr_set: LR0Set) -> Iterable[tuple[Symbol, LR0Set]]:
    """Assumes `lr_set` has already been closed"""
    return (
        (symbol, goto(lr_set, symbol)) for symbol, _ in get_transition_symbols(lr_set)
    )


def goto(lr_set: LR0Set, symbol: Symbol) -> LR0Set:
    """Assumes `lr_set` has already been closed"""
    kernel = frozenset(
        item.next()
        for item in lr_set
        if not item.complete and item.next_symbol == symbol
    )
    return LRSet(kernel)


def get_transition_symbols(
    lr_set: LR0Set,
) -> Iterable[tuple[Symbol, Iterable[LRItem]]]:
    """Assumes `lr_set` has already been closed"""
    transition_symbols = defaultdict(list)

    for item in lr_set:
        if not item.complete:
            transition_symbols[item.next_symbol].append(item)

    return transition_symbols.items()


def closure(lr_set: LR0Set, g: Grammar) -> LR0Set:
    previous_set: LR0Set | None = None
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
