import dataclasses
from dataclasses import dataclass
from typing import TypeVar

from compilers.grammar.productions import ProductionLine
from compilers.grammar.terminals import Terminal

Self = TypeVar("Self", bound="LRItem")  # TODO: Remove once mypy supports Self
END_OF_CHAIN = Terminal("$")


@dataclass(frozen=True, kw_only=True)
class LRItem:
    production: ProductionLine
    _stack_position: int = 0

    @property
    def complete(self) -> bool:
        return self._stack_position == len(self.production.derivation)

    def next(self: Self) -> Self:
        if self.complete:
            raise ValueError(
                "Cannot advance an LR Item that is at the end of the production"
            )
        return dataclasses.replace(self, _stack_position=self._stack_position + 1)


@dataclass(frozen=True, kw_only=True)
class LR1Item(LRItem):
    lookahead: Terminal
