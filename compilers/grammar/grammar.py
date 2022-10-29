from typing import Iterable, Mapping

from .nonterminals import Nonterminal
from .productions import Production
from .symbols import is_nonterminal, is_terminal
from .terminals import Terminal

FirstSet = set[Terminal]


class Grammar:
    _productions: Mapping[Nonterminal, Production]

    def __init__(self, productions: Iterable[Production]) -> None:
        self._productions = {
            production.nonterminal: production for production in productions
        }
        self._first_sets: dict[Nonterminal, FirstSet] = {
            nonterminal: set() for nonterminal in self.nonterminals
        }
        # TODO: validate production invariants
        # TODO: make productions frozendict

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self._productions[nonterminal]

    @property
    def nonterminals(self) -> Iterable[Nonterminal]:
        # If productions is frozen, this can be a regular attribute
        return self._productions.keys()

    def get_first(self, nonterminal: Nonterminal) -> FirstSet:

        changed = True
        while changed:
            changed = False
            for current_nonterminal in self.nonterminals:
                new_symbols = self._get_new_first_pass(current_nonterminal)
                self._first_sets[current_nonterminal].update(new_symbols)

                if len(new_symbols) > 0:
                    changed = True

        return self._first_sets[nonterminal]

    def _get_new_first_pass(self, nonterminal: Nonterminal) -> FirstSet:
        first: FirstSet = set()

        for derivation in self.get_production(nonterminal).derivations:
            head, *_ = derivation
            if is_terminal(head):
                first.add(head)
            elif is_nonterminal(head):
                first.update(self._first_sets[head])

        return first - self._first_sets[nonterminal]
