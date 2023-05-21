from compilers.grammar.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.grammar.terminals import Terminal
from compilers.parser.lalr_automata import (
    LookaheadRelationship,
    determine_lookahead_relationship,
)
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import LR0Set


def test_lookahead_relationship() -> None:
    # S' -> S
    # S -> L = R | R
    # L -> *R | id
    # R -> L

    Sp = Nonterminal("S'")
    S = Nonterminal("S")
    L = Nonterminal("L")
    R = Nonterminal("R")
    times = Terminal("*")
    eq = Terminal("=")
    id = Terminal("id")

    sp_production = Production(Sp, [S])
    s_production = Production(S, [(L, eq, R), R])
    l_production = Production(L, [(times, R), id])
    r_production = Production(R, [L])

    start_item = LRItem(ProductionLine(Sp, (S,)))
    s_to_l = LRItem(ProductionLine(S, (L, eq, R)))
    s_to_r = LRItem(ProductionLine(S, (R,)))
    l_to_r = LRItem(ProductionLine(L, (times, R)))
    l_to_r = LRItem(ProductionLine(L, (times, R)))
    l_to_id = LRItem(ProductionLine(L, (id,)))
    l_to_id = LRItem(ProductionLine(L, (id,)))
    r_to_l = LRItem(ProductionLine(R, (L,)))

    g = Grammar((sp_production, s_production, l_production, r_production), Sp)
    state = LR0Set({start_item})

    expected = LookaheadRelationship(
        generated={
            id: {eq: {l_to_id.next()}},
            times: {eq: {l_to_r.next()}},
        },
        propagated={
            S: {start_item: {start_item.next()}},
            L: {start_item: {s_to_l.next(), r_to_l.next()}},
            R: {start_item: {s_to_r.next()}},
            times: {start_item: {l_to_r.next()}},
            id: {start_item: {l_to_id.next()}},
        },
    )

    generated, propagated = determine_lookahead_relationship(state, g)

    assert len(expected.generated) == len(generated)
    for symbol, generated_lookaheads in generated.items():
        assert len(generated_lookaheads) == len(expected.generated[symbol])
        for lookahead, items in generated_lookaheads.items():
            assert items == expected.generated[symbol][lookahead]

    assert len(expected.propagated) == len(propagated)
    for symbol, propagated_lookaheads in propagated.items():
        assert len(propagated_lookaheads) == len(expected.propagated[symbol])
        for item, items in propagated_lookaheads.items():
            assert items == expected.propagated[symbol][item]
