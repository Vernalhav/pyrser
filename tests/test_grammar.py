from compilers.grammar import Production
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.terminals import Terminal


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
    assert production.nullable


def test_production_isnt_nullable() -> None:
    expr = Nonterminal("<expr>")
    plus = Terminal("+")
    minus = Terminal("-")

    production = Production(expr, [(expr, plus, expr), (expr, minus, expr)])
    assert production.nullable is False
