from compilers.grammar import Nonterminal, Production, Terminal


def test_production_length_counts_nullable() -> None:
    expr = Nonterminal("<expr>")
    plus = Terminal("+")
    minus = Terminal("-")

    production = Production(expr, [(expr, plus, expr), (expr, minus, expr), ()])
    assert len(production.derivations) == 3


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
