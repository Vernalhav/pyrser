from compilers.grammar import Grammar, Nonterminal, Production, Terminal


def test_first_of_terminal_derivation() -> None:
    minus = Terminal("-")
    one = Terminal("1")
    number = Nonterminal("<number>")
    negative = Nonterminal("<negative>")

    number_production = Production(number, [one])
    negative_production = Production(negative, [(minus, number)])
    g = Grammar([negative_production, number_production], negative)

    assert g.get_first(negative) == {minus}


def test_first_of_multiple_terminal_derivation() -> None:
    zero = Terminal("0")
    one = Terminal("1")
    bit = Nonterminal("<bit>")

    bit_production = Production(bit, [zero, one])
    g = Grammar([bit_production], bit)

    assert g.get_first(bit) == {zero, one}


def test_first_of_nonterminal_derivation() -> None:
    minus = Terminal("-")
    one = Terminal("1")
    two = Terminal("2")
    digit = Nonterminal("<digit>")
    number = Nonterminal("<number>")

    digit_production = Production(digit, [one, two])
    number_production = Production(number, [(minus, digit), digit])
    g = Grammar([number_production, digit_production], number)

    assert g.get_first(number) == {minus, one, two}


def test_first_multiple_nonterminal_derivations() -> None:
    a = Terminal("a")
    b = Terminal("b")
    A = Nonterminal("A")
    B = Nonterminal("B")
    C = Nonterminal("C")

    A_production = Production(A, [a])
    B_production = Production(B, [b])
    C_production = Production(C, [A, B])
    g = Grammar([A_production, B_production, C_production], C)

    assert g.get_first(C) == {a, b}


def test_first_of_recursive_derivation() -> None:
    one = Terminal("1")
    two = Terminal("2")
    digit = Nonterminal("<digit>")
    number = Nonterminal("<number>")

    digit_production = Production(digit, [one, two])
    number_production = Production(number, [digit, (number, digit)])
    g = Grammar([number_production, digit_production], number)

    assert g.get_first(number) == {one, two}


def test_first_of_cyclic_derivations() -> None:
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")
    A = Nonterminal("A")
    B = Nonterminal("B")
    C = Nonterminal("C")

    A_produciion = Production(A, [C, a])
    B_produciion = Production(B, [A, b])
    C_production = Production(C, [B, c])
    g = Grammar([A_produciion, B_produciion, C_production], C)

    assert g.get_first(C) == {a, b, c}


def test_first_of_nullable_derivation() -> None:
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")
    A = Nonterminal("A")
    B = Nonterminal("B")

    A_produciion = Production(A, [(), a])
    B_produciion = Production(B, [(A, c), b])
    g = Grammar([A_produciion, B_produciion], B)

    assert g.get_first(B) == {a, b, c}


def test_direct_nullable_is_nullable() -> None:
    a = Terminal("a")
    A = Nonterminal("A")

    A_produciion = Production(A, [(), a])
    g = Grammar([A_produciion], A)

    assert g.get_first(A).nullable


def test_indirect_nullable_is_nullable() -> None:
    a = Terminal("a")
    b = Terminal("b")
    A = Nonterminal("A")
    B = Nonterminal("B")
    C = Nonterminal("C")

    A_produciion = Production(A, [(), a])
    B_produciion = Production(B, [(), b])
    C_produciion = Production(C, [(A, B)])
    g = Grammar([A_produciion, B_produciion, C_produciion], C)

    assert g.get_first(C).nullable


def test_productioon_with_nullable_is_not_nullable() -> None:
    a = Terminal("a")
    b = Terminal("b")
    A = Nonterminal("A")
    B = Nonterminal("B")
    C = Nonterminal("C")

    A_produciion = Production(A, [(), a])
    B_produciion = Production(B, [b])
    C_produciion = Production(C, [(A, B)])
    g = Grammar([A_produciion, B_produciion, C_produciion], C)

    assert not g.get_first(C).nullable
