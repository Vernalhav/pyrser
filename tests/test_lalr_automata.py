from compilers.grammar.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production
from compilers.grammar.terminals import Terminal
from compilers.parser.lalr_automata import (
    LALRAutomata,
    LookaheadRelationships,
    determine_lookahead_relationships,
    get_end_of_chain,
)
from compilers.parser.lr_automata import LRAutomata
from compilers.parser.lr_items import items_from_production
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

    sp_prod = Production(Sp, [S])
    s_prod = Production(S, [(L, eq, R), R])
    l_prod = Production(L, [(times, R), id])
    r_prod = Production(R, [L])

    (start_item,) = items_from_production(sp_prod)
    s_to_l, s_to_r = items_from_production(s_prod)
    l_to_r, l_to_id = items_from_production(l_prod)
    (r_to_l,) = items_from_production(r_prod)

    g = Grammar((sp_prod, s_prod, l_prod, r_prod), Sp)
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

    sp_prod = Production(Sp, [S])
    s_prod = Production(S, [(L, eq, R), R])
    l_prod = Production(L, [(times, R), id])
    r_prod = Production(R, [L])

    g = Grammar((sp_prod, s_prod, l_prod, r_prod), Sp)
    end_of_chain = get_end_of_chain(g)

    (start_item,) = items_from_production(sp_prod, end_of_chain)
    s_to_l, s_to_r = items_from_production(s_prod, end_of_chain)
    l_to_r, l_to_id = items_from_production(l_prod, end_of_chain)
    (r_to_l,) = items_from_production(r_prod, end_of_chain)
    r_to_l_eq = r_to_l.to_lr1(eq)
    l_to_r_eq = l_to_r.to_lr1(eq)
    l_to_id_eq = l_to_id.to_lr1(eq)

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

    automata = LALRAutomata(g)

    # Assumes transitions are OK since they should be copied from LR0 automata
    assert automata.transition_count == LRAutomata(g).transition_count
    assert automata.states == set(states)
