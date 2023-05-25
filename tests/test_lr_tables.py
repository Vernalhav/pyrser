import pytest

from compilers.grammar.productions import ProductionLine
from compilers.parser import actions
from compilers.parser.lr_items import LR1Item, LRItem
from compilers.parser.lr_sets import LR0Set, LR1Set
from compilers.parser.tables import LRParsingTable
from tests.utils import get_nonterminals, get_terminals


def test_lr_table_records_valid_action() -> None:
    (A,) = get_nonterminals("A")
    a, end_of_chain = get_terminals("a", "$")

    start_item = LR1Item(ProductionLine(A, (a,)), end_of_chain)
    state = LR1Set({start_item})
    target = LR1Set({start_item.next()})

    table = LRParsingTable[LR1Set]()
    action = actions.Shift(target)
    table[state, a] = action

    assert table[state, a] == action


def test_lr_table_records_valid_goto_entry() -> None:
    A, B = get_nonterminals("A", "B")
    a, end_of_chain = get_terminals("a", "$")

    start_item = LR1Item(ProductionLine(A, (B, a)), end_of_chain)
    b_item = LR1Item(ProductionLine(B, (a,)), end_of_chain)
    reduction_state = LR1Set({b_item.next()})
    reduction_target = LR1Set({start_item.next()})

    table = LRParsingTable[LR1Set]()
    action = actions.Goto(reduction_target)
    table[reduction_state, A] = action

    assert table[reduction_state, A] == action


def test_lr_table_returns_error_on_invalid_entry() -> None:
    (A,) = get_nonterminals("A")
    (a,) = get_terminals("a")

    start_item = LRItem(ProductionLine(A, ()))
    state = LR0Set({start_item})

    table = LRParsingTable[LR0Set]()

    assert isinstance(table[state, a], actions.Error)


def test_lr_table_throws_on_invalid_goto() -> None:
    (A,) = get_nonterminals("A")

    start_item = LRItem(ProductionLine(A, ()))
    state = LR0Set({start_item})

    table = LRParsingTable[LR0Set]()

    with pytest.raises(KeyError):
        table[state, A]
