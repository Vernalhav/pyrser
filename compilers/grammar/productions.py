from collections.abc import Iterable, Sequence
from typing import NamedTuple

from .nonterminals import Nonterminal
from .symbols import Symbol

Derivation = tuple[Symbol, ...]


class ProductionLine(NamedTuple):
    nonterminal: Nonterminal
    derivation: Derivation


# TODO: Make class frozen and add value semantics?
class Production:
    nonterminal: Nonterminal
    nullable: bool
    derivations: Sequence[ProductionLine]

    def __init__(
        self,
        nonterminal: Nonterminal,
        derivations: Iterable[Derivation | Symbol],
    ) -> None:
        self.nonterminal = nonterminal
        tuple_derivations = set(
            derivation if isinstance(derivation, tuple) else (derivation,)
            for derivation in derivations
        )
        self.derivations = tuple(
            ProductionLine(self.nonterminal, derivation)
            for derivation in tuple_derivations
        )
        self.nullable = any(len(derivation) == 0 for _, derivation in self.derivations)

    def __repr__(self) -> str:
        def format_derivation(derivation: Derivation) -> str:
            if len(derivation) == 0:
                return "#"
            return "".join(repr(symbol) for symbol in derivation)

        derivations = " | ".join(
            format_derivation(derivation) for _, derivation in self.derivations
        )
        output = f"{self.nonterminal} -> {derivations}"
        return output
