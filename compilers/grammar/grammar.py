from typing import FrozenSet, Iterable, Iterator

from .first_set import FirstSet
from .follow_set import FollowSet
from .nonterminals import Nonterminal
from .productions import Derivation, Production
from .symbols import Symbol, is_nonterminal, is_terminal
from .terminals import Terminal

END_OF_CHAIN = Terminal("$")


class Grammar:
    symbols: FrozenSet[Symbol]
    terminals: FrozenSet[Terminal]
    nonterminals: FrozenSet[Nonterminal]
    start_symbol: Nonterminal

    def __init__(
        self,
        productions: Iterable[Production],
        start_symbol: Nonterminal,
    ) -> None:

        self.terminals, self.nonterminals = get_symbols(productions)
        self.symbols = self.terminals.union(self.nonterminals)
        self.start_symbol = start_symbol

        self._productions = {
            production.nonterminal: production for production in productions
        }
        self._first_sets = {symbol: FirstSet() for symbol in self.symbols}
        self._follow_sets = {
            nonterminal: FollowSet() for nonterminal in self.nonterminals
        }

        self._validate_grammar()
        self._calculate_first_sets()
        self._calculate_follow_sets()

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self._productions[nonterminal]

    def get_first(self, nonterminal: Nonterminal) -> FirstSet:
        return self._first_sets[nonterminal]

    def get_follow(self, nonterminal: Nonterminal) -> FollowSet:
        return self._follow_sets[nonterminal]

    @property
    def _derivations(self) -> Iterable[tuple[Nonterminal, Derivation]]:
        for production in self._productions.values():
            for derivation in production.derivations:
                yield production.nonterminal, derivation

    def _calculate_follow_sets(self) -> None:
        changed = True
        while changed:
            changed = any(
                self._update_follow(nonterminal) for nonterminal in self.nonterminals
            )

    def _update_follow(self, nonterminal: Nonterminal) -> bool:
        previous_follow_set = self._follow_sets[nonterminal]
        updated_follow_set = self._get_follow_pass(nonterminal)
        self._follow_sets[nonterminal] = updated_follow_set
        return updated_follow_set != previous_follow_set

    def _get_follow_pass(self, nonterminal: Nonterminal) -> FollowSet:
        follow = FollowSet()

        if nonterminal == self.start_symbol:
            follow.end_chain_follows = True

        for production_nonterminal, derivation in self._derivations:
            for next_symbol in next_symbols(nonterminal, derivation):
                if next_symbol != END_OF_CHAIN:
                    follow.update(self._first_sets[next_symbol])
                else:
                    follow.update(self._follow_sets[production_nonterminal])

        return follow

    def _calculate_first_sets(self) -> None:
        changed = True
        while changed:
            changed = any(self._update_first(symbol) for symbol in self.symbols)

    def _update_first(self, symbol: Symbol) -> bool:
        """
        Updates `symbol`'s first set with a single pass.
        Returns whether new symbols were added.
        """
        previous_first_set = self._first_sets[symbol]
        updated_first_set = self._get_first_pass(symbol)
        self._first_sets[symbol] = updated_first_set
        return updated_first_set != previous_first_set

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
        # TODO: Check no reserved symbols used
        # TODO: Ensure only one start symbol
        # TODO: Disallow same nonterminal in multiple productions
        for _, derivation in self._derivations:
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


def next_symbols(symbol: Symbol, derivation: Derivation) -> Iterator[Symbol]:
    if len(derivation) == 0:
        return
    for i, current_symbol in enumerate(derivation[1:] + (END_OF_CHAIN,), 1):
        if symbol == derivation[i - 1]:
            yield current_symbol
