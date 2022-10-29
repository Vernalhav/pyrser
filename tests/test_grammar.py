from compilers.grammar import Grammar, Nonterminal, Production, Terminal


def test_production_length_discards_nullable() -> None:
    expr = Nonterminal("<expr>")
    plus = Terminal("+")
    minus = Terminal("-")

    production = Production(expr, [(expr, plus, expr), (expr, minus, expr), ()])
    assert len(production.derivations) == 2


def test_production_is_nullable() -> None:
    expr = Nonterminal("<expr>")
    plus = Terminal("+")
    minus = Terminal("-")

    production = Production(expr, [(expr, plus, expr), (expr, minus, expr), ()])
    assert production.nullable is True


def test_production_isnt_nullable() -> None:
    expr = Nonterminal("<expr>")
    plus = Terminal("+")
    minus = Terminal("-")

    production = Production(expr, [(expr, plus, expr), (expr, minus, expr)])
    assert production.nullable is False


def test_single_symbol_production_gets_added() -> None:
    zero = Terminal("0")
    one = Terminal("1")
    bit = Nonterminal("<bit>")

    bit_production = Production(bit, [zero, one])
    assert len(bit_production.derivations) == 2


def test_grammar_gets_production() -> None:
    expr = Nonterminal("<expr>")
    factor = Nonterminal("<factor>")
    term = Nonterminal("<term>")

    plus = Terminal("+")
    mult = Terminal("*")
    zero = Terminal("0")
    one = Terminal("1")

    expr_production = Production(expr, [(factor, plus, factor), factor, ()])
    factor_production = Production(factor, [(term, mult, term), term])
    term_production = Production(term, [zero, one])

    g = Grammar([expr_production, factor_production, term_production])
    assert g.get_production(expr) == expr_production


def test_first_of_terminal_derivation() -> None:
    minus = Terminal("-")
    number = Nonterminal("<number>")
    negative = Nonterminal("<negative>")

    negative_production = Production(negative, [(minus, number)])
    g = Grammar([negative_production])

    assert g.get_first(negative) == {minus}


def test_first_of_multiple_terminal_derivation() -> None:
    zero = Terminal("0")
    one = Terminal("1")
    bit = Nonterminal("<bit>")

    bit_production = Production(bit, [zero, one])
    g = Grammar([bit_production])

    assert g.get_first(bit) == {zero, one}


def test_first_of_nonterminal_derivation() -> None:
    minus = Terminal("-")
    one = Terminal("1")
    two = Terminal("2")
    digit = Nonterminal("<digit>")
    number = Nonterminal("<number>")

    digit_production = Production(digit, [one, two])
    number_production = Production(number, [(minus, digit), digit])
    g = Grammar([number_production, digit_production])

    assert g.get_first(number) == {minus, one, two}


def test_first_multiple_nonterminal_derivations() -> None:
    a = Terminal("a")
    b = Terminal("b")
    A = Nonterminal("<A>")
    B = Nonterminal("<B>")
    C = Nonterminal("<C>")

    A_produciion = Production(A, [a])
    B_produciion = Production(B, [b])
    C_production = Production(C, [A, B])
    g = Grammar([A_produciion, B_produciion, C_production])

    assert g.get_first(C) == {a, b}


def test_first_of_recursive_derivation() -> None:
    one = Terminal("1")
    two = Terminal("2")
    digit = Nonterminal("<digit>")
    number = Nonterminal("<number>")

    digit_production = Production(digit, [one, two])
    number_production = Production(number, [digit, (number, digit)])
    g = Grammar([number_production, digit_production])

    assert g.get_first(number) == {one, two}


def test_first_of_cyclic_derivations() -> None:
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")
    A = Nonterminal("<A>")
    B = Nonterminal("<B>")
    C = Nonterminal("<C>")

    A_produciion = Production(A, [C, a])
    B_produciion = Production(B, [A, b])
    C_production = Production(C, [B, c])
    g = Grammar([A_produciion, B_produciion, C_production])

    assert g.get_first(C) == {a, b, c}


def test_first_of_nullable_derivation() -> None:
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")
    A = Nonterminal("<A>")
    B = Nonterminal("<B>")

    A_produciion = Production(A, [(), a])
    B_produciion = Production(B, [(A, c), b])
    g = Grammar([A_produciion, B_produciion])

    assert g.get_first(B) == {a, b, c}


def test_nullable_nonterminal_is_nullable() -> None:
    a = Terminal("a")
    A = Nonterminal("<A>")

    A_produciion = Production(A, [(), a])
    g = Grammar([A_produciion])

    assert g.get_first(A).nullable

