from typing import Iterable, Mapping

from compilers.grammar.nonterminals import Nonterminal

from .productions import Production


class Grammar:
    productions: Mapping[Nonterminal, Production]

    def __init__(self, productions: Iterable[Production]) -> None:
        self.productions = {
            production.nonterminal: production for production in productions
        }

    def get_production(self, nonterminal: Nonterminal) -> Production:
        return self.productions[nonterminal]
