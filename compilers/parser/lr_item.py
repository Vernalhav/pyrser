from __future__ import annotations

from dataclasses import dataclass

from compilers.grammar.productions import ProductionLine


@dataclass(frozen=True)
class LRItem:
    production: ProductionLine
    _stack_position: int = 0

    def next(self) -> LRItem:
        if self._stack_position == len(self.production.derivation):
            raise ValueError(
                "Cannot advance an LR Item that is at the end of the production"
            )
        return LRItem(self.production, self._stack_position + 1)
