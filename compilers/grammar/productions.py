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
