from typing import Iterable, Mapping, MutableMapping

from .first_set import FirstSet
from .nonterminals import Nonterminal
from .productions import Derivation, Production
from .symbols import is_nonterminal, is_terminal


class Grammar:
    _productions: Mapping[Nonterminal, Production]
    _first_sets: MutableMapping[Nonterminal, FirstSet]

    @property
    def nonterminals(self) -> Iterable[Nonterminal]:
        return self._productions.keys()

    def __init__(self, productions: Iterable[Production]) -> None:
        self._productions = {
            production.nonterminal: production for production in productions
        }
        self._first_sets = {
            nonterminal: FirstSet() for nonterminal in self.nonterminals
        }

        self._validate_grammar()
        self._calculate_first_sets()

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self._productions[nonterminal]

    def get_first(self, nonterminal: Nonterminal) -> FirstSet:
        return self._first_sets[nonterminal]

    def _calculate_first_sets(self) -> None:
        changed = True
        while changed:
            changed = any(
                self._update_first(current_nonterminal)
                for current_nonterminal in self.nonterminals
            )

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
        Performs a single scan over `nonterminal`'s derivations,
        returning its current First set.
        """
        first = FirstSet()

        for derivation in self.get_production(nonterminal).derivations:
            is_nullable = self._process_derivation(first, derivation)
            first.nullable |= is_nullable  # If any derivation is nullable, `first` is.

        return first

    def _process_derivation(self, first: FirstSet, derivation: Derivation) -> bool:
        """
        Performs a pass of adding first symbols coming from
        the given derivation to the set.
        Returns whether or not the `derivation` is nullable.
        """
        for symbol in derivation:
            if is_terminal(symbol):
                first.add(symbol)
                return False

            elif is_nonterminal(symbol):
                first.update(self._first_sets[symbol])
                if not self.get_production(symbol).nullable:
                    return False
        return True

    def _validate_grammar(self) -> None:
        for production in self._productions.values():
            for derivation in production.derivations:
                for symbol in derivation:
                    if is_nonterminal(symbol) and symbol not in self.nonterminals:
                        raise ValueError(f"Nonterminal {symbol} has no derivation.")
