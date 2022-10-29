from __future__ import annotations

from typing import Any, Iterable, Mapping, ParamSpec

from .nonterminals import Nonterminal
from .productions import Production
from .symbols import is_nonterminal, is_terminal
from .terminals import Terminal

P = ParamSpec("P")


class FirstSet(set[Terminal]):
    nullable: bool

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.nullable = False

    def remove_terminals(self, terminals: set[Terminal]) -> FirstSet:
        return FirstSet(self - terminals)


class Grammar:
    _productions: Mapping[Nonterminal, Production]

    def __init__(self, productions: Iterable[Production]) -> None:
        self._productions = {
            production.nonterminal: production for production in productions
        }
        self._first_sets: dict[Nonterminal, FirstSet] = {
            nonterminal: FirstSet() for nonterminal in self.nonterminals
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
        updated_first_set = self._get_first_pass(nonterminal)
        changed = len(updated_first_set) != len(self._first_sets[nonterminal])

        self._first_sets[nonterminal] = updated_first_set
        return changed

    def _get_first_pass(self, nonterminal: Nonterminal) -> FirstSet:
        """
        Performs a single scan over `nonterminal`'s derivations.
        """
        first = FirstSet()

        first.nullable = self.get_production(nonterminal).nullable

        for derivation in self.get_production(nonterminal).derivations:
            for symbol in derivation:
                if is_terminal(symbol):
                    first.add(symbol)
                    break

                elif is_nonterminal(symbol):
                    first.update(self._first_sets[symbol])
                    if not self.get_production(symbol).nullable:
                        break

        return first
