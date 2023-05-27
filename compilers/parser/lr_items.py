from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Iterable, Sequence, overload

from typing_extensions import Self

from compilers.grammar import Terminal
from compilers.grammar.productions import Chain, Production, ProductionLine
from compilers.grammar.symbols import Symbol


@dataclass(frozen=True)
class LRItem:
    production: ProductionLine
    stack_position: int = field(kw_only=True, default=0)

    def __post_init__(self) -> None:
        if (
            self.stack_position > len(self.production.derivation)
            or self.stack_position < 0
        ):
            raise ValueError("LR Item with invalid stack position")

    @property
    def complete(self) -> bool:
        return self.stack_position == len(self.production.derivation)

    @property
    def next_symbol(self) -> Symbol:
        if self.complete:
            raise ValueError(f"Complete item {self} has no next symbol.")
        return self.tail[0]

    @property
    def tail(self) -> Chain:
        return self.production.derivation[self.stack_position :]

    def next(self, amount: int = 1) -> Self:
        if amount < 0:
            raise ValueError("Advance amount must be non-negative")
        if self.stack_position + amount > len(self.production.derivation):
            raise ValueError("Cannot advance an LR Item past the end of the production")
        return dataclasses.replace(self, stack_position=self.stack_position + amount)

    @overload
    def to_lr1(self, lookaheads: Terminal) -> LR1Item:
        """Returns an LR1 item with the given lookahead.
        If `self` is an LR1 item, return a new item with
        its lookahead replaced."""
        pass

    @overload
    def to_lr1(self, lookaheads: Iterable[Terminal]) -> Sequence[LR1Item]:
        """Returns an LR1 item for each given lookahead."""
        pass

    def to_lr1(
        self, lookaheads: Terminal | Iterable[Terminal]
    ) -> LR1Item | Sequence[LR1Item]:
        if isinstance(lookaheads, Iterable):
            return tuple(self.to_lr1(lookahead) for lookahead in lookaheads)
        return LR1Item(self.production, lookaheads, stack_position=self.stack_position)

    def __repr__(self) -> str:
        head = "".join(
            str(symbol) for symbol in self.production.derivation[: self.stack_position]
        )
        tail = "".join(str(symbol) for symbol in self.tail)

        s = f"{self.production.nonterminal} -> {head} ⋅"
        if len(tail) > 0:
            s += f" {tail}"
        return s


@dataclass(frozen=True)
class LR1Item(LRItem):
    lookahead: Terminal

    def to_lr0(self) -> LRItem:
        return LRItem(self.production, stack_position=self.stack_position)

    def __repr__(self) -> str:
        return f"{super().__repr__()} | {self.lookahead}"


@overload
def items_from_production(production: Production) -> Sequence[LRItem]:
    """Returns a Sequence of LR0 items with the dot at the
    start position in the same order of the production lines
    in `production`."""
    pass


@overload
def items_from_production(
    production: Production, lookahead: Terminal
) -> Sequence[LR1Item]:
    """Returns a Sequence of LR1 items with the dot at the
    start position in the same order of the production lines
    in `production`. All items will have `lookahead` as their
    lookahead"""
    pass


def items_from_production(
    production: Production, lookahead: Terminal | None = None
) -> Sequence[LRItem] | Sequence[LR1Item]:
    if lookahead is None:
        return tuple(LRItem(line) for line in production.derivations)
    return tuple(LR1Item(line, lookahead) for line in production.derivations)
