from typing import Iterable

from .nonterminals import Nonterminal
from .symbols import Symbol

Derivation = tuple[Symbol, ...]


class Production:
    nonterminal: Nonterminal
    derivations: set[Derivation]
    nullable: bool

    def __init__(
        self,
        nonterminal: Nonterminal,
        derivations: Iterable[Derivation | Symbol],
    ) -> None:
        self.nonterminal = nonterminal
        self.derivations = set(
            derivation if isinstance(derivation, tuple) else (derivation,)
            for derivation in derivations
        )
        self.nullable = any(len(derivation) == 0 for derivation in self.derivations)

    def __repr__(self) -> str:
        def format_derivation(derivation: Derivation) -> str:
            if len(derivation) == 0:
                return "#"
            return "".join(repr(symbol) for symbol in derivation)

        derivations = " | ".join(
            format_derivation(derivation) for derivation in self.derivations
        )
        output = f"{self.nonterminal} -> {derivations}"
        return output
