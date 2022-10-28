from typing import Iterable

from .nonterminals import Nonterminal
from .symbols import Symbol


class Production:
    nonterminal: Nonterminal
    derivations: set[tuple[Symbol, ...]]
    nullable: bool

    def __init__(
        self,
        nonterminal: Nonterminal,
        derivations: Iterable[tuple[Symbol, ...] | Symbol],
    ) -> None:
        self.nonterminal = nonterminal
        self.derivations = set(
            derivation if isinstance(derivation, tuple) else (derivation,)
            for derivation in derivations
            if not isinstance(derivation, tuple) or len(derivation) > 0
        )
        self.nullable = any(
            len(derivation) == 0
            for derivation in derivations
            if isinstance(derivation, tuple)
        )
