import dataclasses
from dataclasses import dataclass
from typing import TypeVar

from compilers.grammar import Terminal
from compilers.grammar.productions import Chain, ProductionLine
from compilers.grammar.symbols import Symbol

Self = TypeVar("Self", bound="LRItem")  # TODO: Remove once mypy supports Self


@dataclass(frozen=True, kw_only=True)
class LRItem:
    production: ProductionLine
    _stack_position: int = 0

    @property
    def complete(self) -> bool:
        return self._stack_position == len(self.production.derivation)

    @property
    def next_symbol(self) -> Symbol:
        if self.complete:
            raise ValueError(f"Complete item {self} has no next symbol.")
        return self.tail[0]

    @property
    def tail(self) -> Chain:
        return self.production.derivation[self._stack_position :]

    def next(self: Self) -> Self:
        if self.complete:
            raise ValueError(
                "Cannot advance an LR Item that is at the end of the production"
            )
        return dataclasses.replace(self, _stack_position=self._stack_position + 1)


@dataclass(frozen=True, kw_only=True)
class LR1Item(LRItem):
    lookahead: Terminal

    def __repr__(self) -> str:
        head = "".join(
            str(symbol) for symbol in self.production.derivation[: self._stack_position]
        )
        tail = "".join(str(symbol) for symbol in self.tail)
        return f"[{self.production.nonterminal} -> {head} ⋅ {tail} , {self.lookahead}]"
