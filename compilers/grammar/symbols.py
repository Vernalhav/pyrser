from typing import TypeGuard

from .nonterminals import Nonterminal
from .terminals import Terminal

Symbol = Nonterminal | Terminal


def is_nonterminal(symbol: Symbol) -> TypeGuard[Nonterminal]:
    return isinstance(symbol, Nonterminal)


def is_terminal(symbol: Symbol) -> TypeGuard[Terminal]:
    return isinstance(symbol, Terminal)
