from typing import Sequence

from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.terminals import Terminal


def get_terminals(*values: str) -> Sequence[Terminal]:
    return tuple(Terminal(value) for value in values)


def get_nonterminals(*values: str) -> Sequence[Nonterminal]:
    return tuple(Nonterminal(value) for value in values)
