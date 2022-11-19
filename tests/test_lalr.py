from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.productions import ProductionLine
from compilers.parser.lalr import LALRParser
from compilers.parser.lr_items import END_OF_CHAIN, LR1Item


def test_initial_item_closure() -> None:
    A = Nonterminal("A")
    a = Terminal("a")

    A_production = Production(A, [a])
    g = Grammar([A_production], A)

    parser = LALRParser(g)

    production_line = ProductionLine(A, (a,))
    item = LR1Item(production=production_line, lookahead=END_OF_CHAIN)

    assert parser.item_closure(item) == set()
