from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Nonterminal:
    value: str
