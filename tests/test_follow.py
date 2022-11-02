from compilers.grammar import Grammar, Nonterminal, Production, Terminal
from compilers.grammar.first_set import FirstSet
from compilers.grammar.follow_set import FollowSet


def test_follow_single_production() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(A, b)])

    g = Grammar([A_production, E_production], E)
    assert g.get_follow(A) == {b}


def test_follow_start_production() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(A, a, A, b), b])

    g = Grammar([A_production, E_production], E)
    assert g.get_follow(A) == {a, b}


def test_follow_of_last_nonterminal_adds_follow() -> None:
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")
    E = Nonterminal("E")
    A = Nonterminal("A")
    B = Nonterminal("B")

    A_production = Production(A, [a, B])
    B_production = Production(B, [c])
    E_production = Production(E, [(A, a, A, b), b])

    g = Grammar([A_production, B_production, E_production], E)
    assert g.get_follow(B) == {a, b}


def test_follow_start_symbol_end_of_chain() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(A, b)])

    g = Grammar([A_production, E_production], E)
    assert g.get_follow(E).ends_chain


def test_follow_not_start_symbol_end_of_chain() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(b, A)])

    g = Grammar([A_production, E_production], E)
    assert g.get_follow(A).ends_chain


def test_follow_indirect_end_of_chain() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")
    B = Nonterminal("B")

    A_production = Production(A, [a])
    B_production = Production(B, [(), b])
    E_production = Production(E, [(b, A, B)])

    g = Grammar([A_production, B_production, E_production], E)
    assert g.get_follow(A).ends_chain


def test_larger_grammar() -> None:
    E = Nonterminal("E")
    Ep = Nonterminal("E'")
    T = Nonterminal("T")
    Tp = Nonterminal("T'")
    F = Nonterminal("F")
    id = Terminal("id")
    open_paren = Terminal("(")
    close_paren = Terminal(")")
    plus = Terminal("+")
    mult = Terminal("*")

    E_production = Production(E, [(T, Ep)])
    Ep_production = Production(Ep, [(plus, T, Ep), ()])
    T_production = Production(T, [(F, Tp)])
    Tp_production = Production(Tp, [(mult, F, Tp), ()])
    F_production = Production(F, [(open_paren, E, close_paren), id])

    g = Grammar(
        [E_production, Ep_production, T_production, Tp_production, F_production], E
    )

    assert g.get_first(E) == FirstSet({open_paren, id}, nullable=False)
    assert g.get_first(T) == FirstSet({open_paren, id}, nullable=False)
    assert g.get_first(F) == FirstSet({open_paren, id}, nullable=False)
    assert g.get_first(Ep) == FirstSet({plus}, nullable=True)
    assert g.get_first(Tp) == FirstSet({mult}, nullable=True)

    assert g.get_follow(E) == FollowSet({close_paren}, ends_chain=True)
    assert g.get_follow(Ep) == FollowSet({close_paren}, ends_chain=True)
    assert g.get_follow(T) == FollowSet({plus, close_paren}, ends_chain=True)
    assert g.get_follow(Tp) == FollowSet({plus, close_paren}, ends_chain=True)
    assert g.get_follow(F) == FollowSet({plus, mult, close_paren}, ends_chain=True)
