from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.productions import ProductionLine
from compilers.parser.lalr import (
    END_OF_CHAIN,
    LALRParser,
    can_merge,
    get_transition_symbols,
)
from compilers.parser.lr_items import LR1Item, LRItem


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
    item = LR1Item(production_line, lookahead=END_OF_CHAIN)

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
    item = LR1Item(s_line, lookahead=END_OF_CHAIN)

    a_line = ProductionLine(A, (a,))
    assert parser.get_implied_items(item) == {
        LR1Item(a_line, lookahead=END_OF_CHAIN),
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
    item = LR1Item(ProductionLine(goal, (ParenList,)), lookahead=END_OF_CHAIN)

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
    item = LR1Item(s_line, lookahead=END_OF_CHAIN)

    assert parser.get_state_for_transition({item}, A) == {
        LR1Item(s_line, 1, lookahead=END_OF_CHAIN),
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
    item = LR1Item(s_line, lookahead=END_OF_CHAIN)

    a_line = ProductionLine(A, (a,))
    assert parser.get_state_for_transition({item}, A) == {
        LR1Item(s_line, 1, lookahead=END_OF_CHAIN),
        LR1Item(a_line, lookahead=END_OF_CHAIN),
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
    item = LR1Item(ProductionLine(goal, (ParenList,)), lookahead=END_OF_CHAIN)

    core = parser.get_closure({item})
    assert len(parser.get_state_for_transition(core, open_paren)) == 6


def test_get_transition_symbols() -> None:
    ParenList = Nonterminal("ParenList")
    Pair = Nonterminal("Pair")
    open_paren = Terminal("(")
    close_paren = Terminal(")")

    paren_list_production_1 = ProductionLine(ParenList, (ParenList, Pair))
    paren_list_production_2 = ProductionLine(ParenList, (Pair,))

    pair_production_1 = ProductionLine(Pair, (open_paren, Pair, close_paren))

    lr_state = frozenset(
        {
            LRItem(paren_list_production_1, 2),
            LRItem(paren_list_production_2, 0),
            LRItem(pair_production_1, 2),
        }
    )

    assert get_transition_symbols(lr_state) == {Pair, close_paren}


def test_can_merge_lr1_states() -> None:
    ParenList = Nonterminal("ParenList")
    Pair = Nonterminal("Pair")
    open_paren = Terminal("(")
    close_paren = Terminal(")")

    paren_list_production_1 = ProductionLine(ParenList, (ParenList, Pair))
    paren_list_production_2 = ProductionLine(ParenList, (Pair,))

    pair_production_1 = ProductionLine(Pair, (open_paren, Pair, close_paren))

    lalr_state1 = frozenset(
        {
            LR1Item(paren_list_production_1, 2, lookahead=END_OF_CHAIN),
            LR1Item(paren_list_production_1, 2, lookahead=open_paren),
            LR1Item(paren_list_production_2, 0, lookahead=close_paren),
            LR1Item(pair_production_1, 2, lookahead=open_paren),
        }
    )

    lalr_state2 = frozenset(
        {
            LR1Item(paren_list_production_1, 2, lookahead=open_paren),
            LR1Item(paren_list_production_2, 0, lookahead=close_paren),
            LR1Item(pair_production_1, 2, lookahead=END_OF_CHAIN),
        }
    )

    assert can_merge(lalr_state1, lalr_state2)


def test_cannot_merge_lr1_states() -> None:
    ParenList = Nonterminal("ParenList")
    Pair = Nonterminal("Pair")
    open_paren = Terminal("(")
    close_paren = Terminal(")")

    paren_list_production_1 = ProductionLine(ParenList, (ParenList, Pair))
    paren_list_production_2 = ProductionLine(ParenList, (Pair,))

    pair_production_1 = ProductionLine(Pair, (open_paren, Pair, close_paren))

    lalr_state1 = frozenset(
        {
            LR1Item(paren_list_production_1, 2, lookahead=END_OF_CHAIN),
            LR1Item(paren_list_production_2, 0, lookahead=close_paren),
            LR1Item(pair_production_1, 2, lookahead=open_paren),
        }
    )

    lalr_state2 = frozenset(
        {
            LR1Item(paren_list_production_2, 0, lookahead=close_paren),
            LR1Item(pair_production_1, 2, lookahead=END_OF_CHAIN),
        }
    )

    assert can_merge(lalr_state1, lalr_state2) is False


def test_lalr_table_creation() -> None:
    e = Nonterminal("e")
    t = Nonterminal("t")
    f = Nonterminal("f")
    num = Terminal("NUM")
    plus = Terminal("+")
    mult = Terminal("*")
    open_paren = Terminal("(")
    close_paren = Terminal(")")

    expr_production = Production(e, [(e, plus, t), t])
    term_production = Production(t, [(t, mult, f), f])
    factor_production = Production(f, [(open_paren, e, close_paren), num])

    g = Grammar([expr_production, term_production, factor_production], e)
    parser = LALRParser(g)

    cc, transitions = parser.compute_parse_table()
    assert len(cc) == 12
    assert len(transitions.transitions) == 22
