from __future__ import annotations

from collections.abc import MutableSet
from dataclasses import dataclass, field
from typing import Iterable, Iterator

from .terminals import Terminal


@dataclass
class FollowSet(MutableSet):
    end_chain_follows: bool = False
    terminals: set[Terminal] = field(default_factory=set, init=False)

    def __repr__(self) -> str:
        return self.terminals.__repr__()

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, FollowSet):
            return (
                self.terminals == __o.terminals
                and self.end_chain_follows == __o.end_chain_follows
            )
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
        for iterable in s:
            if isinstance(iterable, FollowSet):
                self.end_chain_follows |= iterable.end_chain_follows
            self.terminals.update(iterable)
