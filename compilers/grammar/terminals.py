from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Terminal:
    value: str
