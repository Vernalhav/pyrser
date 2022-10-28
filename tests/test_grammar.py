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


def test_first_of_terminal_production() -> None:
    minus = Terminal("-")
    number = Nonterminal("<number>")
    negative = Nonterminal("<negative>")

    negative_production = Production(negative, [(minus, number)])
    g = Grammar([negative_production])

    assert g.get_first(negative) == {minus}


def test_first_of_multiple_terminal_productions() -> None:
    zero = Terminal("0")
    one = Terminal("1")
    bit = Nonterminal("<bit>")

    bit_production = Production(bit, [zero, one])
    g = Grammar([bit_production])

    assert g.get_first(bit) == {zero, one}
