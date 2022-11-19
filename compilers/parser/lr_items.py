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
    def next_symbol(self) -> Symbol | None:
        next_symbols = self.tail
        return next_symbols[0] if len(next_symbols) > 0 else None

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
