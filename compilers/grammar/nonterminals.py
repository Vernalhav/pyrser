from dataclasses import dataclass

from compilers.grammar.symbols import Symbol


@dataclass(frozen=True, slots=True)
class Nonterminal(Symbol):
    value: str
