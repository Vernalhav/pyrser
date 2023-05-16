from typing import FrozenSet, Iterable, Iterator

from .first_set import FirstSet
from .follow_set import FollowSet
from .nonterminals import Nonterminal
from .productions import Chain, Production
from .symbols import Symbol, is_nonterminal, is_terminal
from .terminals import Terminal


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
        self._first_sets = {symbol: FirstSet() for symbol in self.nonterminals}
        self._follow_sets = {
            nonterminal: FollowSet() for nonterminal in self.nonterminals
        }

        self._validate_grammar()
        self._calculate_first_sets()
        self._calculate_follow_sets()

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self._productions[nonterminal]

    def get_first(self, derivation: Symbol | Chain) -> FirstSet:
        if isinstance(derivation, Iterable):
            return self._get_first_from_chain(derivation)
        return self._get_first_from_symbol(derivation)

    def get_follow(self, nonterminal: Nonterminal) -> FollowSet:
        return self._follow_sets[nonterminal]

    @property
    def productions(self) -> Iterable[Production]:
        return self._productions.values()

    @property
    def derivations(self) -> Iterable[tuple[Nonterminal, Chain]]:
        for production in self._productions.values():
            for nonterminal, derivation in production.derivations:
                yield nonterminal, derivation

    def _calculate_follow_sets(self) -> None:
        changed = True
        while changed:
            changed = False
            for nonterminal in self.nonterminals:
                changed |= self._update_follow(nonterminal)

    def _update_follow(self, nonterminal: Nonterminal) -> bool:
        previous_follow_set = self._follow_sets[nonterminal]
        updated_follow_set = self._get_follow_pass(nonterminal)
        self._follow_sets[nonterminal] = updated_follow_set
        return updated_follow_set != previous_follow_set

    def _get_follow_pass(self, nonterminal: Nonterminal) -> FollowSet:
        follow = FollowSet()

        if nonterminal == self.start_symbol:
            follow.ends_chain = True

        for production_nonterminal, derivation in self.derivations:
            self._process_follow_derivation(
                nonterminal, follow, production_nonterminal, derivation
            )

        return follow

    def _process_follow_derivation(
        self,
        nonterminal: Nonterminal,
        follow: FollowSet,
        production_nonterminal: Nonterminal,
        derivation: Chain,
    ) -> None:
        if nonterminal not in derivation:
            return

        for derivation_suffix in next_symbols(nonterminal, derivation):
            derivation_suffix_first = self._get_first_from_chain(derivation_suffix)
            follow.update(derivation_suffix_first)
            if derivation_suffix_first.nullable:
                follow.update(self._follow_sets[production_nonterminal])

    def _calculate_first_sets(self) -> None:
        changed = True
        while changed:
            changed = False
            for nonterminal in self.nonterminals:
                changed |= self._update_first(nonterminal)

    def _update_first(self, nonterminal: Nonterminal) -> bool:
        """
        Updates `nonterminal`'s first set with a single pass.
        Returns whether new symbols were added.
        """
        previous_first_set = self._first_sets[nonterminal]
        updated_first_set = self._get_first_pass(nonterminal)
        self._first_sets[nonterminal] = updated_first_set
        return updated_first_set != previous_first_set

    def _get_first_pass(self, nonterminal: Nonterminal) -> FirstSet:
        """
        Performs a single scan over `nonterminal`'s derivations,
        returning its current First set.
        """
        first = FirstSet()
        for _, derivation in self.get_production(nonterminal).derivations:
            derivation_first = self._get_first_from_chain(derivation)
            first.update(derivation_first)
        return first

    def _is_nullable(self, symbol: Symbol) -> bool:
        if is_nonterminal(symbol):
            return self._first_sets[symbol].nullable or (
                self.get_production(symbol).nullable
            )
        # TODO: Check if Symbol is the empty string?
        return False

    def _get_first_from_symbol(self, symbol: Symbol) -> FirstSet:
        if is_nonterminal(symbol):
            return self._first_sets[symbol]
        if is_terminal(symbol):
            return FirstSet({symbol})
        raise TypeError(f"{symbol} is not a symbol or chain")

    def _get_first_from_chain(self, chain: Chain) -> FirstSet:
        first = FirstSet()
        for symbol in chain:
            # Only update with the terminal symbols, don't propagate nullable
            first.update(self._get_first_from_symbol(symbol).terminals)
            if not self._is_nullable(symbol):
                break
        else:  # If for-loop exits without breaking
            first.nullable = True

        return first

    def _validate_grammar(self) -> None:
        # TODO: Check no reserved symbols used
        # TODO: Disallow same nonterminal in multiple productions
        for _, derivation in self.derivations:
            for symbol in derivation:
                if is_nonterminal(symbol) and symbol not in self.nonterminals:
                    raise ValueError(f"Nonterminal {symbol} has no derivation.")


def get_symbols(
    productions: Iterable[Production],
) -> tuple[FrozenSet[Terminal], FrozenSet[Nonterminal]]:
    terminals = frozenset(
        symbol
        for production in productions
        for _, derivation in production.derivations
        for symbol in derivation
        if is_terminal(symbol)
    )
    nonterminals = frozenset(production.nonterminal for production in productions)
    return terminals, nonterminals


def next_symbols(symbol: Symbol, derivation: Chain) -> Iterator[Chain]:
    for i, _ in enumerate(derivation):
        if symbol == derivation[i]:
            # If symbol appears last in the derivation, return empty tuple
            yield derivation[i + 1 :]
