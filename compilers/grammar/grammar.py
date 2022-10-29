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
            changed = any(
                self._update_first(current_nonterminal)
                for current_nonterminal in self.nonterminals
            )

        return self._first_sets[nonterminal]

    def _update_first(self, nonterminal: Nonterminal) -> bool:
        """
        Updates `nonterminal`'s first set with a single pass.
        Returns whether new symbols were added
        """
        new_symbols = self._get_new_first_pass(nonterminal)
        self._first_sets[nonterminal].update(new_symbols)
        return len(new_symbols) > 0

    def _get_new_first_pass(self, nonterminal: Nonterminal) -> FirstSet:
        """
        Performs a single scan over `nonterminal`'s derivations.
        Returning any new first symbols that aren't in the current set.
        """
        first: FirstSet = set()

        for derivation in self.get_production(nonterminal).derivations:
            head, *_ = derivation
            if is_terminal(head):
                first.add(head)
            elif is_nonterminal(head):
                first.update(self._first_sets[head])

        return first - self._first_sets[nonterminal]
