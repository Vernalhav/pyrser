import dataclasses
from dataclasses import dataclass, field

from typing_extensions import Self

from compilers.grammar import Terminal
from compilers.grammar.productions import Chain, ProductionLine
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

    def next(self) -> Self:
        if self.complete:
            raise ValueError(
                "Cannot advance an LR Item that is at the end of the production"
            )
        return dataclasses.replace(self, stack_position=self.stack_position + 1)

    def __repr__(self) -> str:
        head = "".join(
            str(symbol) for symbol in self.production.derivation[: self.stack_position]
        )
        tail = "".join(str(symbol) for symbol in self.tail)
        return f"{self.production.nonterminal} -> {head} ⋅ {tail}"


@dataclass(frozen=True)
class LR1Item(LRItem):
    lookahead: Terminal

    def to_lr0(self) -> LRItem:
        return LRItem(self.production, stack_position=self.stack_position)

    def __repr__(self) -> str:
        return f"{super().__repr__()} , {self.lookahead}"
