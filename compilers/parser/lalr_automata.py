from collections import defaultdict
from typing import NamedTuple

from compilers.grammar.grammar import Grammar
from compilers.grammar.symbols import Symbol
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LR1Item, LRItem
from compilers.parser.lr_sets import LR0Set, LR1Set


class LookaheadRelationships(NamedTuple):
    generated: dict[Symbol, dict[Symbol, set[LRItem]]]
    propagated: dict[Symbol, dict[LRItem, set[LRItem]]]


def determine_lookahead_relationships(
    state: LR0Set, g: Grammar
) -> LookaheadRelationships:
    dummy = Terminal("#")  # TODO: Dynamically change value to not conflict with grammar
    relationships = LookaheadRelationships(
        propagated=defaultdict(lambda: defaultdict(set)),
        generated=defaultdict(lambda: defaultdict(set)),
    )

    for kernel_item in state.kernel:
        closed_set = LR1Set({LR1Item(kernel_item.production, dummy)}).closure(g)
        for item in closed_set:
            if item.complete:
                continue

            next_symbol = item.next_symbol
            next_item = item.next().to_lr0()
            if item.lookahead == dummy:
                relationships.propagated[next_symbol][kernel_item].add(next_item)
            else:
                relationships.generated[next_symbol][item.lookahead].add(next_item)

    return relationships
