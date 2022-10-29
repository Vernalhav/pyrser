from __future__ import annotations

from collections.abc import MutableSet
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from .terminals import Terminal


@dataclass
class FirstSet(MutableSet):
    nullable: bool = False
    terminals: set[Terminal] = field(default_factory=set, init=False)

    def __eq__(self, __o: object) -> bool:
        return self.terminals.__eq__(__o)

    def __contains__(self, x: object) -> bool:
        return self.terminals.__contains__(x)

    def __iter__(self) -> Iterator[Terminal]:
        return self.terminals.__iter__()

    def __len__(self) -> int:
        return self.terminals.__len__()

    def add(self, value: Terminal) -> None:
        return self.terminals.add(value)

    def discard(self, value: Terminal) -> None:
        return self.terminals.discard(value)

    def update(self, *s: Iterable[Terminal]) -> None:
        return self.terminals.update(*s)
