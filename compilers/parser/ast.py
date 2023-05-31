from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Iterable, Sequence, TypeVar

from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.symbols import Symbol
from compilers.grammar.terminals import Terminal

_T = TypeVar("_T")


@dataclass(frozen=True)
class ASTNode:
    symbol: Symbol
    children: Sequence[ASTNode]


@dataclass(frozen=True)
class TerminalNode(ASTNode, Generic[_T]):
    _VALUE_FIELD_NAME = "_value"

    @property
    def value(self) -> _T:
        return getattr(self, self._VALUE_FIELD_NAME)

    def __init__(self, symbol: Terminal, value: _T) -> None:
        super().__init__(symbol, ())
        object.__setattr__(self, self._VALUE_FIELD_NAME, value)


@dataclass(frozen=True)
class NonterminalNode(ASTNode):
    def __init__(
        self,
        symbol: Nonterminal,
        children: Iterable[ASTNode],
    ) -> None:
        super().__init__(symbol, tuple(children))
