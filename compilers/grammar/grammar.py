from typing import FrozenSet, Iterable

from .first_set import FirstSet
from .nonterminals import Nonterminal
from .productions import Derivation, Production
from .symbols import Symbol, is_nonterminal, is_terminal
from .terminals import Terminal


class Grammar:
    symbols: FrozenSet[Symbol]
    terminals: FrozenSet[Terminal]
    nonterminals: FrozenSet[Nonterminal]

    def __init__(self, productions: Iterable[Production]) -> None:

        self.terminals, self.nonterminals = get_symbols(productions)
        self.symbols = self.terminals.union(self.nonterminals)

        self._productions = {
            production.nonterminal: production for production in productions
        }
        self._first_sets = {symbol: FirstSet() for symbol in self.symbols}
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


    def _update_first(self, nonterminal: Symbol) -> bool:
        """
        Updates `nonterminal`'s first set with a single pass.
        Returns whether new symbols were added.
        """
        updated_first_set = self._get_first_pass(nonterminal)
        changed = len(updated_first_set) != len(self._first_sets[nonterminal])

        self._first_sets[nonterminal] = updated_first_set
        return changed

    def _get_first_pass(self, symbol: Symbol) -> FirstSet:
        """
        Performs a single scan over `symbol`'s derivations,
        returning its current First set.
        """
        first = FirstSet()

        if is_terminal(symbol):
            first.add(symbol)

        if is_nonterminal(symbol):
            for derivation in self.get_production(symbol).derivations:
                is_nullable = self._process_derivation(first, derivation)
                # If any derivation is nullable, `first` is
                first.nullable |= is_nullable

        return first

    def _process_derivation(self, first: FirstSet, derivation: Derivation) -> bool:
        """
        Performs a pass of adding first symbols coming from
        the given derivation to the set.
        Returns whether or not the `derivation` is nullable.
        """
        for symbol in derivation:
            first.update(self._first_sets[symbol])
            if not self._is_nullable(symbol):
                return False
        return True

    def _validate_grammar(self) -> None:
        # TODO: "Find" start symbol
        # TODO: Ensure only one start symbol
        # TODO: Disallow same nonterminal in multiple productions
        for production in self._productions.values():
            for derivation in production.derivations:
                for symbol in derivation:
                    if is_nonterminal(symbol) and symbol not in self.nonterminals:
                        raise ValueError(f"Nonterminal {symbol} has no derivation.")

    def _is_nullable(self, symbol: Symbol) -> bool:
        return is_nonterminal(symbol) and self.get_production(symbol).nullable


def get_symbols(
    productions: Iterable[Production],
) -> tuple[FrozenSet[Terminal], FrozenSet[Nonterminal]]:
    terminals = frozenset(
        symbol
        for production in productions
        for derivation in production.derivations
        for symbol in derivation
        if is_terminal(symbol)
    )
    nonterminals = frozenset(production.nonterminal for production in productions)
    return terminals, nonterminals
