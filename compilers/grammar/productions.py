from typing import Iterable

from .nonterminals import Nonterminal
from .symbols import Symbol


class Production:
    nonterminal: Nonterminal
    derivations: set[tuple[Symbol, ...]]
    nullable: bool

    def __init__(
        self, nonterminal: Nonterminal, derivations: Iterable[tuple[Symbol, ...]]
    ) -> None:
        self.nonterminal = nonterminal
        self.derivations = set(
            derivation for derivation in derivations if len(derivation) > 0
        )
        self.nullable = any(len(derivation) == 0 for derivation in derivations)
