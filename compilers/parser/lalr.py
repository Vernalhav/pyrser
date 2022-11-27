from typing import AbstractSet, Iterable

from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.symbols import Symbol, is_nonterminal
from compilers.parser.lr_items import LR1Item, LRItem

END_OF_CHAIN = Terminal("$")

LR1State = frozenset[LR1Item]
LRState = frozenset[LRItem]

class LALRParser:
    grammar: Grammar

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = augment_grammar(grammar)

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


def augment_grammar(grammar: Grammar) -> Grammar:
    augmented_start_symbol = Nonterminal(f"__{grammar.start_symbol.value}")
    augmented_production = Production(augmented_start_symbol, [grammar.start_symbol])

    productions = tuple(grammar.productions) + (augmented_production,)
    return Grammar(productions, augmented_start_symbol)


def get_transition_symbols(state: LRState) -> AbstractSet[Symbol]:
    return {item.next_symbol for item in state if not item.complete}
