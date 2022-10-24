from dataclasses import FrozenInstanceError

import pytest

from compilers.grammar import Nonterminal, Terminal


def test_terminal_has_value_semantics() -> None:
    terminal_a = Terminal(";")
    terminal_b = Terminal(";")
    assert terminal_a == terminal_b


def test_terminal_is_immutable() -> None:
    terminal = Terminal("+")
    with pytest.raises(FrozenInstanceError):
        terminal.value = "-"  # type: ignore


def test_nonterminal_has_value_semantics() -> None:
    nonterminal_a = Nonterminal("<expr>")
    nonterminal_b = Nonterminal("<expr>")
    assert nonterminal_a == nonterminal_b


def test_nonterminal_is_immutable() -> None:
    terminal = Nonterminal("<expr>")
    with pytest.raises(FrozenInstanceError):
        terminal.value = "<number>"  # type: ignore
