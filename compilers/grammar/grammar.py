from typing import Iterable, Mapping

from .nonterminals import Nonterminal
from .productions import Production
from .symbols import is_terminal
from .terminals import Terminal


class Grammar:
    productions: Mapping[Nonterminal, Production]

    def __init__(self, productions: Iterable[Production]) -> None:
        self.productions = {
            production.nonterminal: production for production in productions
        }

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self.productions[nonterminal]

    def get_first(self, nonterminal: Nonterminal) -> set[Terminal]:
        first: set[Terminal] = set()
        for derivation in self.get_production(nonterminal).derivations:
            if is_terminal(derivation[0]):
                first.add(derivation[0])
        return first
