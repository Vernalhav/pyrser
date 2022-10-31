import pytest

from compilers.grammar import Grammar, Nonterminal, Production, Terminal


def test_invalid_grammar_rejected() -> None:
    A = Nonterminal("A")
    B = Nonterminal("B")
    A_production = Production(A, [B])

    with pytest.raises(ValueError):
        Grammar([A_production], A)


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

    g = Grammar([expr_production, factor_production, term_production], expr)
    assert g.get_production(expr) == expr_production
