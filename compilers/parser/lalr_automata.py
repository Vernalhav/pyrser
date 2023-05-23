from collections import defaultdict
from typing import NamedTuple

from compilers.grammar.grammar import Grammar
from compilers.grammar.symbols import Symbol
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LRItem


class LookaheadRelationships(NamedTuple):
    generated: dict[Symbol, dict[LRItem, set[Symbol]]]
    propagated: dict[Symbol, dict[LRItem, set[LRItem]]]

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LookaheadRelationships):
            return False

        is_equal = True
        is_equal &= len(value.generated) == len(self.generated)
        for symbol, generated_lookaheads in self.generated.items():
            is_equal &= len(generated_lookaheads) == len(value.generated[symbol])
            for lookahead, symbols in generated_lookaheads.items():
                is_equal &= symbols == value.generated[symbol][lookahead]

        is_equal &= len(value.propagated) == len(self.propagated)
        for symbol, propagated_lookaheads in self.propagated.items():
            is_equal &= len(propagated_lookaheads) == len(value.propagated[symbol])
            for item, items in propagated_lookaheads.items():
                is_equal &= items == value.propagated[symbol][item]

        return is_equal


def determine_lookahead_relationships(
    state: LR0Set, g: Grammar
) -> LookaheadRelationships:
    dummy = Terminal("#")  # TODO: Dynamically change value to not conflict with grammar
    relationships = LookaheadRelationships(
        propagated=defaultdict(lambda: defaultdict(set)),
        generated=defaultdict(lambda: defaultdict(set)),
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
