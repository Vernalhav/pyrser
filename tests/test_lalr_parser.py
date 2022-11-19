from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.productions import ProductionLine
from compilers.parser.lalr import END_OF_CHAIN, LALRParser
from compilers.parser.lr_items import LR1Item


def test_follow_terminal_item_closure() -> None:
    A = Nonterminal("A")
    a = Terminal("a")

    A_production = Production(A, [a])
    g = Grammar([A_production], A)

    parser = LALRParser(g)

    production_line = ProductionLine(A, (a,))
    item = LR1Item(production=production_line, lookahead=END_OF_CHAIN)

    assert parser.get_implied_items(item) == set()


def test_follow_nonterminal_item_closure() -> None:
    S = Nonterminal("S")
    A = Nonterminal("A")
    a = Terminal("a")

    S_production = Production(S, [A])
    A_production = Production(A, [a])
    g = Grammar([A_production, S_production], S)

    parser = LALRParser(g)

    s_line = ProductionLine(S, (A,))
    item = LR1Item(production=s_line, lookahead=END_OF_CHAIN)

    a_line = ProductionLine(A, (a,))
    assert parser.get_implied_items(item) == {
        LR1Item(production=a_line, lookahead=END_OF_CHAIN),
    }
