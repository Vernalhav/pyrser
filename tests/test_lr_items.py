import pytest

from compilers.grammar import Nonterminal, Terminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.parser.lr_items import LR1Item, LRItem, items_from_production


def test_lr_items_value_semantics() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")

    production = Production(A, [(a, b)])
    production_line, *_ = production.derivations
    item_a = LRItem(production_line)
    item_b = LRItem(production_line)

    assert len({item_a, item_b}) == 1


def test_cannot_advance_finished_item() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")

    production = Production(A, [(a, b)])
    production_line, *_ = production.derivations
    item = LRItem(production_line)

    for _ in production_line.derivation:
        item = item.next()

    with pytest.raises(ValueError):
        item.next()


def test_cannot_create_invalid_lr_item() -> None:
    A = Nonterminal("A")
    production = Production(A, [()])
    production_line, *_ = production.derivations

    with pytest.raises(ValueError):
        LRItem(production_line, stack_position=1)


def test_cannot_advance_null_production() -> None:
    A = Nonterminal("A")
    production = Production(A, [()])
    production_line, *_ = production.derivations

    item = LRItem(production_line)

    with pytest.raises(ValueError):
        item.next()


def test_items_from_production_multiple_lines() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")

    production = Production(A, [a, (b, a)])
    expected = (
        LRItem(ProductionLine(A, (a,))),
        LRItem(ProductionLine(A, (b, a))),
    )

    assert expected == items_from_production(production)


def test_items_from_null_production() -> None:
    A = Nonterminal("A")

    production = Production(A, [()])
    expected = (LRItem(ProductionLine(A, ())),)

    assert expected == items_from_production(production)


def test_lr1_items_from_production() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")
    end_of_chain = Terminal("#")

    production = Production(A, [a, (b, a), ()])
    expected = (
        LR1Item(ProductionLine(A, (a,)), end_of_chain),
        LR1Item(ProductionLine(A, (b, a)), end_of_chain),
        LR1Item(ProductionLine(A, ()), end_of_chain),
    )

    assert expected == items_from_production(production, end_of_chain)


def test_lr0_to_lr1_preserves_stack_position() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")
    end_of_chain = Terminal("#")

    line = ProductionLine(A, (b, a))
    item = LRItem(line).next()

    expected = (
        item.to_lr1(b),
        item.to_lr1(end_of_chain),
    )

    assert expected == item.to_lr1([b, end_of_chain])


def test_lr1_items_value_semantics() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")

    production = Production(A, [(a, b)])
    production_line, *_ = production.derivations
    item_a = LR1Item(production_line, b)
    item_b = LR1Item(production_line, b)

    assert len({item_a, item_b}) == 1


def test_advance_lr1_preserves_lookahead() -> None:
    A = Nonterminal("A")
    a = Terminal("a")
    b = Terminal("b")

    production = Production(A, [(a, b)])
    production_line, *_ = production.derivations
    item = LR1Item(production_line, b)

    item = item.next()
    assert item.lookahead == b
