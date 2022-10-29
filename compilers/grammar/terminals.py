from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Terminal:
    value: str

    def __str__(self) -> str:
        return self.value
