from compilers.grammar import Grammar, Nonterminal, Production, Terminal


def test_follow_single_production() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(A, b)])

    g = Grammar([A_production, E_production])
    assert g.get_follow(A) == {b}


def test_follow_start_production() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(A, a, A, b), b])

    g = Grammar([A_production, E_production])
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

    g = Grammar([A_production, B_production, E_production])
    assert g.get_follow(B) == {a, b}


def test_follow_end_of_chain() -> None:
    a = Terminal("a")
    b = Terminal("b")
    E = Nonterminal("E")
    A = Nonterminal("A")

    A_production = Production(A, [a])
    E_production = Production(E, [(A, b)])

    g = Grammar([A_production, E_production])
    assert g.get_follow(E).end_chain_follows
