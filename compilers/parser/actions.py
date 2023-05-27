from dataclasses import dataclass
from typing import Generic

from compilers.grammar.productions import ProductionLine
from compilers.parser.lr_sets import StateType


@dataclass(frozen=True)
class Action:
    pass


@dataclass(frozen=True)
class Shift(Action, Generic[StateType]):
    target: StateType


@dataclass(frozen=True)
class Reduce(Action):
    item: ProductionLine


@dataclass(frozen=True)
class Goto(Generic[StateType]):
    target: StateType


@dataclass(frozen=True)
class Accept(Action):
    pass


@dataclass(frozen=True)
class Error(Action):
    pass
