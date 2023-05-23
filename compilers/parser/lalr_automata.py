from typing import NamedTuple

from compilers.grammar.grammar import Grammar
from compilers.grammar.symbols import Symbol
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LRItem
from compilers.utils import GroupedDefaultDict, GroupedDict

GeneratedLookaheads = GroupedDict[Symbol, LRItem, set[Symbol]]
PropagatedLookaheads = GroupedDict[Symbol, LRItem, set[LRItem]]



class LookaheadRelationships(NamedTuple):
    generated: GeneratedLookaheads
    propagated: PropagatedLookaheads

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LookaheadRelationships):
            return False

        is_equal = True
        is_equal &= value.generated.flat_len() == self.generated.flat_len()
        for symbol, lookahead, symbols in self.generated.flatten():
            is_equal &= symbols == value.generated[symbol][lookahead]

        is_equal &= value.propagated.flat_len() == self.propagated.flat_len()
        for symbol, item, items in self.propagated.flatten():
            is_equal &= items == value.propagated[symbol][item]

        return is_equal


def determine_lookahead_relationships(
    state: LR0Set, g: Grammar
) -> LookaheadRelationships:
    dummy = Terminal("#")  # TODO: Dynamically change value to not conflict with grammar
    relationships = LookaheadRelationships(
        propagated=GroupedDefaultDict(set),
        generated=GroupedDefaultDict(set),
    )

    for kernel_item in state.kernel:
        closed_set = LR1Set({kernel_item.to_lr1(dummy)}).closure(g)
        for item in closed_set:
            if item.complete:
                continue

            next_symbol = item.next_symbol
            next_item = item.next().to_lr0()
            if item.lookahead == dummy:
                relationships.propagated[next_symbol][kernel_item].add(next_item)
            else:
                relationships.generated[next_symbol][next_item].add(item.lookahead)

    return relationships
