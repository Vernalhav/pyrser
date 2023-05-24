from compilers.grammar.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.grammar.terminals import Terminal
from compilers.parser.lalr_automata import (
    LALRAutomata,
    LookaheadRelationships,
    determine_lookahead_relationships,
    get_end_of_chain,
)
from compilers.parser.lr_items import LR1Item, LRItem
from compilers.parser.lr_sets import LR0Set, LR1Set
from compilers.utils import GroupedDict


def test_lookahead_relationships() -> None:
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
    r_to_l = LRItem(ProductionLine(R, (L,)))

    g = Grammar((sp_production, s_production, l_production, r_production), Sp)
    state = LR0Set({start_item, s_to_l.next()})

    expected = LookaheadRelationships(
        generated=GroupedDict(
            {
                id: {l_to_id.next(): {eq}},
                times: {l_to_r.next(): {eq}},
            }
        ),
        propagated=GroupedDict(
            {
                S: {start_item: {start_item.next()}},
                L: {start_item: {s_to_l.next(), r_to_l.next()}},
                R: {start_item: {s_to_r.next()}},
                times: {start_item: {l_to_r.next()}},
                id: {start_item: {l_to_id.next()}},
                eq: {s_to_l.next(): {s_to_l.next().next()}},
            }
        ),
    )

    relationships = determine_lookahead_relationships(state, g)
    assert relationships == expected


def test_lalr_automata_creation_pointer_grammar() -> None:
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

    g = Grammar((sp_production, s_production, l_production, r_production), Sp)
    end_of_chain = get_end_of_chain(g)

    start_item = LR1Item(ProductionLine(Sp, (S,)), end_of_chain)
    s_to_l = LR1Item(ProductionLine(S, (L, eq, R)), end_of_chain)
    s_to_r = LR1Item(ProductionLine(S, (R,)), end_of_chain)
    l_to_r = LR1Item(ProductionLine(L, (times, R)), end_of_chain)
    l_to_r = LR1Item(ProductionLine(L, (times, R)), end_of_chain)
    l_to_id = LR1Item(ProductionLine(L, (id,)), end_of_chain)
    r_to_l = LR1Item(ProductionLine(R, (L,)), end_of_chain)
    r_to_l_eq = LR1Item(ProductionLine(R, (L,)), eq)
    l_to_r_eq = LR1Item(ProductionLine(L, (times, R)), eq)
    l_to_id_eq = LR1Item(ProductionLine(L, (id,)), eq)

    states = (
        LR1Set({start_item}),
        LR1Set({start_item.next()}),
        LR1Set({s_to_l.next(), r_to_l.next()}),
        LR1Set({s_to_r.next()}),
        LR1Set({l_to_r.next(), l_to_r_eq.next()}),
        LR1Set({l_to_id.next(), l_to_id_eq.next()}),
        LR1Set({s_to_l.next().next()}),
        LR1Set({l_to_r.next().next(), l_to_r_eq.next().next()}),
        LR1Set({r_to_l.next(), r_to_l_eq.next()}),
        LR1Set({s_to_l.next().next().next()}),
    )

    g = Grammar((sp_production, s_production, l_production, r_production), Sp)
    automata = LALRAutomata(g)
    assert automata.states == set(states)
