from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Nonterminal:
    value: str

    def __str__(self) -> str:
        return self.value
