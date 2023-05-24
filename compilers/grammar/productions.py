from collections.abc import Iterable, Sequence
from typing import NamedTuple

from .nonterminals import Nonterminal
from .symbols import Symbol

Chain = tuple[Symbol, ...]


class ProductionLine(NamedTuple):
    nonterminal: Nonterminal
    derivation: Chain


# TODO: Make class frozen and add value semantics?
class Production:
    nonterminal: Nonterminal
    nullable: bool
    derivations: Sequence[ProductionLine]  # Same order as given in construction

    def __init__(
        self,
        nonterminal: Nonterminal,
        derivations: Iterable[Chain | Symbol],
    ) -> None:
        self.nonterminal = nonterminal
        tuple_derivations = (
            derivation if isinstance(derivation, tuple) else (derivation,)
            for derivation in derivations
        )
        self.derivations = tuple(
            ProductionLine(self.nonterminal, derivation)
            for derivation in tuple_derivations
        )

        if len(set(self.derivations)) != len(self.derivations):
            raise ValueError("Cannot create a production with duplicate derivations")

        if len(self.derivations) == 0:
            raise ValueError("Cannot create a production with no derivations")

        self.nullable = any(len(derivation) == 0 for _, derivation in self.derivations)

    def __getitem__(self, index: int) -> ProductionLine:
        return self.derivations[index]

    def __repr__(self) -> str:
        def format_derivation(derivation: Chain) -> str:
            if len(derivation) == 0:
                return "#"
            return "".join(repr(symbol) for symbol in derivation)

        derivations = " | ".join(
            format_derivation(derivation) for _, derivation in self.derivations
        )
        output = f"{self.nonterminal} -> {derivations}"
        return output
