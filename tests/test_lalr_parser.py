from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.productions import ProductionLine
from compilers.parser.lalr import END_OF_CHAIN, LALRParser
from compilers.parser.lr_items import LR1Item


def test_parser_augments_grammar() -> None:
    A = Nonterminal("A")
    a = Terminal("a")

    A_production = Production(A, [a])
    g = Grammar([A_production], A)

    parser = LALRParser(g)
    assert len(parser.grammar.nonterminals) == 2


def test_follow_terminal_implied_items() -> None:
    A = Nonterminal("A")
    a = Terminal("a")

    A_production = Production(A, [a])
    g = Grammar([A_production], A)

    parser = LALRParser(g)

    production_line = ProductionLine(A, (a,))
    item = LR1Item(production=production_line, lookahead=END_OF_CHAIN)

    assert parser.get_implied_items(item) == set()


def test_follow_nonterminal_implied_items() -> None:
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


def test_closure() -> None:
    ParenList = Nonterminal("ParenList")
    Pair = Nonterminal("Pair")
    open_paren = Terminal("(")
    close_paren = Terminal(")")

    paren_list_production = Production(ParenList, [(ParenList, Pair), Pair])
    pair_production = Production(
        Pair, [(open_paren, Pair, close_paren), (open_paren, close_paren)]
    )

    g = Grammar([paren_list_production, pair_production], ParenList)
    parser = LALRParser(g)

    goal = parser.grammar.start_symbol
    item = LR1Item(
        production=ProductionLine(goal, (ParenList,)), lookahead=END_OF_CHAIN
    )

    core = parser.get_closure({item})
    assert len(core) == 9


def test_goto_adds_advanced_item() -> None:
    S = Nonterminal("S")
    A = Nonterminal("A")
    a = Terminal("a")

    S_production = Production(S, [A])
    A_production = Production(A, [a])
    g = Grammar([A_production, S_production], S)

    parser = LALRParser(g)

    s_line = ProductionLine(S, (A,))
    item = LR1Item(production=s_line, lookahead=END_OF_CHAIN)

    assert parser.get_state_for_transition({item}, A) == {
        LR1Item(production=s_line, stack_position=1, lookahead=END_OF_CHAIN),
    }


def test_goto_adds_implied_items() -> None:
    S = Nonterminal("S")
    A = Nonterminal("A")
    a = Terminal("a")

    S_production = Production(S, [(A, A)])
    A_production = Production(A, [a])
    g = Grammar([A_production, S_production], S)

    parser = LALRParser(g)

    s_line = ProductionLine(S, (A, A))
    item = LR1Item(production=s_line, lookahead=END_OF_CHAIN)

    a_line = ProductionLine(A, (a,))
    assert parser.get_state_for_transition({item}, A) == {
        LR1Item(production=s_line, stack_position=1, lookahead=END_OF_CHAIN),
        LR1Item(production=a_line, lookahead=END_OF_CHAIN),
    }


def test_goto() -> None:
    ParenList = Nonterminal("ParenList")
    Pair = Nonterminal("Pair")
    open_paren = Terminal("(")
    close_paren = Terminal(")")

    paren_list_production = Production(ParenList, [(ParenList, Pair), Pair])
    pair_production = Production(
        Pair, [(open_paren, Pair, close_paren), (open_paren, close_paren)]
    )

    g = Grammar([paren_list_production, pair_production], ParenList)
    parser = LALRParser(g)

    goal = parser.grammar.start_symbol
    item = LR1Item(
        production=ProductionLine(goal, (ParenList,)), lookahead=END_OF_CHAIN
    )

    core = parser.get_closure({item})
    assert len(parser.get_state_for_transition(core, open_paren)) == 6
