from typing import Iterable

from compilers.grammar import Grammar, Nonterminal, Production
from compilers.grammar.symbols import is_nonterminal
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LR1Item

END_OF_CHAIN = Terminal("$")


class LALRParser:
    grammar: Grammar

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = augment_grammar(grammar)

    def get_closure(self, items: frozenset[LR1Item]) -> frozenset[LR1Item]:
        previous_items: frozenset[LR1Item] = frozenset()

        while previous_items != items:
            previous_items = items.copy()
            for item in previous_items:
                items |= self.get_implied_items(item)

        return items

    def get_implied_items(self, item: LR1Item) -> frozenset[LR1Item]:
        implied_items: set[LR1Item] = set()

        next_symbol = item.next_symbol
        if next_symbol is not None and is_nonterminal(next_symbol):
            for production_line in self.grammar.get_production(next_symbol).derivations:
                for lookahead in self._get_implied_lookaheads(item):
                    implied_items.add(
                        LR1Item(production=production_line, lookahead=lookahead)
                    )

        return frozenset(implied_items)

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
