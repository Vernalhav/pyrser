from typing import Iterable, Mapping

from .nonterminals import Nonterminal
from .productions import Production
from .symbols import is_nonterminal, is_terminal
from .terminals import Terminal

FirstSet = set[Terminal]


class Grammar:
    productions: Mapping[Nonterminal, Production]

    def __init__(self, productions: Iterable[Production]) -> None:
        self.productions = {
            production.nonterminal: production for production in productions
        }
        # TODO: validate production invariants
        # TODO: make productions frozendict

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self.productions[nonterminal]

    @property
    def nonterminals(self) -> Iterable[Nonterminal]:
        # If productions is frozen, this can be a regular attribute
        return self.productions.keys()

    def get_first(self, nonterminal: Nonterminal) -> FirstSet:

        first_sets: dict[Nonterminal, FirstSet] = {
            nonterminal: set() for nonterminal in self.nonterminals
        }

        changed = True
        while changed:
            changed = False
            for current_nonterminal in self.nonterminals:
                new_symbols = self._get_new_first_pass(current_nonterminal, first_sets)
                first_sets[current_nonterminal].update(new_symbols)

                if len(new_symbols) > 0:
                    changed = True

        return first_sets[nonterminal]

    def _get_new_first_pass(
        self,
        nonterminal: Nonterminal,
        current_first_sets: Mapping[Nonterminal, FirstSet],
    ) -> FirstSet:

        first: FirstSet = set()

        for derivation in self.get_production(nonterminal).derivations:
            head, *_ = derivation
            if is_terminal(head):
                first.add(head)
            elif is_nonterminal(head):
                first.update(current_first_sets[head])

        return first - current_first_sets[nonterminal]
