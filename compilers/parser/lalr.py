from collections import deque
from dataclasses import dataclass, field
from typing import AbstractSet, Iterable

from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.productions import ProductionLine
from compilers.grammar.symbols import Symbol, is_nonterminal
from compilers.parser.lr_items import LR1Item
from compilers.parser.types import CanonicalCollection, LR1State, LRState
from compilers.utils import find_first

END_OF_CHAIN = Terminal("$")


@dataclass
class TransitionTable:
    transitions: dict[tuple[LR1State, Symbol], LR1State] = field(
        default_factory=dict, init=False
    )

    def record_transition(
        self, source: LR1State, dest: LR1State, symbol: Symbol
    ) -> None:
        if (source, symbol) in self.transitions:
            raise ValueError(
                f"Transition on {symbol} from {source} to {dest} already exists"
            )
        self.transitions[(source, symbol)] = dest

    def replace(self, old: LR1State, new: LR1State) -> None:
        transitions = dict()
        for (src, symbol), dest in self.transitions.items():
            src = new if src == old else src
            dest = new if dest == old else dest
            transitions[(src, symbol)] = dest

        self.transitions = transitions


class LALRParser:
    grammar: Grammar

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = augment_grammar(grammar)

    def compute_parse_table(self) -> tuple[CanonicalCollection, TransitionTable]:

        initial_state = self.get_closure(
            {LR1Item(self.goal_production, lookahead=END_OF_CHAIN)}
        )

        canonical_collection = CanonicalCollection({initial_state})
        transitions = TransitionTable()

        work_queue = deque((initial_state,))
        while len(work_queue) > 0:
            state = work_queue.popleft()
            for transition_symbol in get_transition_symbols(state):
                work = self.process_transition(
                    canonical_collection, transitions, state, transition_symbol
                )
                if work is not None:
                    work_queue.append(work)

        return canonical_collection, transitions

    def process_transition(
        self,
        canonical_collection: CanonicalCollection,
        transitions: TransitionTable,
        state: LR1State,
        transition_symbol: Symbol,
    ) -> LR1State | None:
        transition = self.get_state_for_transition(state, transition_symbol)
        to_merge = find_first(canonical_collection, lambda x: can_merge(x, transition))

        if to_merge is None:
            canonical_collection.add(transition)
            transitions.record_transition(state, transition, transition_symbol)
            return transition

        merged = transition | to_merge
        canonical_collection.replace(to_merge, merged)
        transitions.replace(to_merge, merged)
        transitions.record_transition(state, merged, transition_symbol)
        return None

    def get_closure(self, items: AbstractSet[LR1Item]) -> LR1State:
        previous_items: frozenset[LR1Item] = frozenset()

        while previous_items != items:
            previous_items = frozenset(items)
            for item in previous_items:
                items |= self.get_implied_items(item)

        return previous_items

    def get_state_for_transition(
        self, items: AbstractSet[LR1Item], symbol: Symbol
    ) -> LR1State:
        transition_state: set[LR1Item] = set()

        for item in items:
            if not item.complete and item.next_symbol == symbol:
                transition_state.add(item.next())

        return self.get_closure(transition_state)

    def get_implied_items(self, item: LR1Item) -> AbstractSet[LR1Item]:
        if item.complete:
            return set()

        implied_items: set[LR1Item] = set()

        next_symbol = item.next_symbol
        if is_nonterminal(next_symbol):
            for production_line in self.grammar.get_production(next_symbol).derivations:
                for lookahead in self._get_implied_lookaheads(item):
                    implied_items.add(
                        LR1Item(production=production_line, lookahead=lookahead)
                    )

        return implied_items

    def _get_implied_lookaheads(self, item: LR1Item) -> Iterable[Terminal]:
        lookaheads = self.grammar.get_first(item.next().tail)
        if lookaheads.nullable:
            lookaheads.add(item.lookahead)
        return lookaheads.terminals

    @property
    def goal_production(self) -> ProductionLine:
        return self.grammar.get_production(self.grammar.start_symbol).derivations[0]


def augment_grammar(grammar: Grammar) -> Grammar:
    augmented_start_symbol = Nonterminal(f"__{grammar.start_symbol.value}")
    augmented_production = Production(augmented_start_symbol, [grammar.start_symbol])

    productions = tuple(grammar.productions) + (augmented_production,)
    return Grammar(productions, augmented_start_symbol)


def get_transition_symbols(state: LRState) -> AbstractSet[Symbol]:
    return {item.next_symbol for item in state if not item.complete}


def can_merge(state_a: LR1State, state_b: LR1State) -> bool:
    return {item.to_lr() for item in state_a} == {item.to_lr() for item in state_b}
