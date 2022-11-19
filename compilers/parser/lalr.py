from compilers.grammar import Grammar, Nonterminal, Production
from compilers.parser.lr_items import LR1Item


class LALRParser:
    grammar: Grammar

    def __init__(self, grammar: Grammar) -> None:
        self.grammar = augment_grammar(grammar)

    def item_closure(self, item: LR1Item) -> frozenset[LR1Item]:
        return frozenset()


def augment_grammar(grammar: Grammar) -> Grammar:
    augmented_start_symbol = Nonterminal(f"__{grammar.start_symbol.value}")
    augmented_production = Production(augmented_start_symbol, [grammar.start_symbol])

    productions = tuple(grammar.productions) + (augmented_production,)
    return Grammar(productions, augmented_start_symbol)
