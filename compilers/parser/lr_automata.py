from collections import defaultdict, deque
from typing import Iterable

from compilers.grammar.grammar import Grammar
from compilers.grammar.symbols import Symbol
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import LR0Set


class LRAutomata:
    grammar: Grammar
    states: set[LR0Set]
    start_state: LR0Set
    _transitions: dict[tuple[LR0Set, Symbol], LR0Set]

    def __init__(self, g: Grammar) -> None:
        self.grammar = g
        self._compute_states_and_transitions()

    @property
    def transition_count(self) -> int:
        return len(self._transitions)

    @property
    def transitions(self) -> Iterable[tuple[LR0Set, Symbol, LR0Set]]:
        for (start, symbol), end in self._transitions.items():
            yield start, symbol, end

    def get_transition(self, state: LR0Set, symbol: Symbol) -> LR0Set:
        return self._transitions[(state, symbol)]

    def _compute_states_and_transitions(self) -> None:
        if not is_augmented(self.grammar):
            raise ValueError("Given grammar is not augmented with start production")

        self.states = set()
        self._transitions = {}
        work: deque[LR0Set] = deque()

        start_item = get_initial_lr_item(self.grammar)
        self.start_state = LR0Set({start_item})
        work.append(self.start_state)

        while len(work) > 0:
            current_set = work.popleft()
            self.states.add(current_set)

            transition_sets = compute_transition_sets(current_set.closure(self.grammar))
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
    return LR0Set(kernel)


def get_transition_symbols(
    lr_set: LR0Set,
) -> Iterable[tuple[Symbol, Iterable[LRItem]]]:
    """Assumes `lr_set` has already been closed"""
    transition_symbols = defaultdict(list)

    for item in lr_set:
        if not item.complete:
            transition_symbols[item.next_symbol].append(item)

    return transition_symbols.items()


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
