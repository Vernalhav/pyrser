from __future__ import annotations

from dataclasses import dataclass

from compilers.grammar.productions import ProductionLine


@dataclass(frozen=True)
class LRItem:
    production: ProductionLine
    _stack_position: int = 0

    @property
    def can_reduce(self) -> bool:
        return self._stack_position == len(self.production.derivation)

    def next(self) -> LRItem:
        if self.can_reduce:
            raise ValueError(
                "Cannot advance an LR Item that is at the end of the production"
            )
        return LRItem(self.production, self._stack_position + 1)
