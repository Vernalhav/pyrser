from typing import Generic, overload

from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.symbols import Symbol, is_terminal
from compilers.grammar.terminals import Terminal
from compilers.parser.actions import Action, Error, Goto
from compilers.parser.lr_sets import StateType
from compilers.utils import GroupedDict


class LRParsingTable(Generic[StateType]):
    def __init__(self) -> None:
        self._table = GroupedDict[StateType, Symbol, Action | Goto[StateType]]()

    @overload
    def __getitem__(self, key: tuple[StateType, Terminal]) -> Action:
        pass

    @overload
    def __getitem__(self, key: tuple[StateType, Nonterminal]) -> Goto[StateType]:
        pass

    def __getitem__(self, key: tuple[StateType, Symbol]) -> Action | Goto[StateType]:
        state, symbol = key
        try:
            return self._table[state, symbol]
        except KeyError as e:
            if is_terminal(symbol):
                return Error()
            raise e

    @overload
    def __setitem__(
        self, key: tuple[StateType, Nonterminal], action: Goto[StateType]
    ) -> None:
        pass

    @overload
    def __setitem__(self, key: tuple[StateType, Terminal], action: Action) -> None:
        pass

    def __setitem__(
        self, key: tuple[StateType, Symbol], action: Action | Goto[StateType]
    ) -> None:
        state, symbol = key
        self._table[state, symbol] = action
