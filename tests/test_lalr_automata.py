from itertools import chain

from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import Production
from compilers.grammar.symbols import Symbol
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
from tests.utils import get_nonterminals, get_terminals

Transitions = dict[tuple[LR1Set, Symbol], LR1Set]


def test_lookahead_relationships() -> None:
    # S' -> S
    # S -> L = R | R
    # L -> *R | id
    # R -> L

    Sp, S, L, R = get_nonterminals("S'", "S", "L", "R")
    times, eq, id = get_terminals("*", "=", "id")

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
                eq: {s_to_l.next(): {s_to_l.next(2)}},
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

    Sp, S, L, R = get_nonterminals("S'", "S", "L", "R")
    times, eq, id = get_terminals("*", "=", "id")

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
        LR1Set({s_to_l.next(2)}),
        LR1Set({l_to_r.next(2), l_to_r_eq.next(2)}),
        LR1Set({r_to_l.next(), r_to_l_eq.next()}),
        LR1Set({s_to_l.next(3)}),
    )

    automata = LALRAutomata(g)

    # Assumes transitions are OK since they should be copied from LR0 automata
    assert automata.transition_count == LRAutomata(g).transition_count
    assert automata.start_state == states[0]
    assert automata.states == set(states)


def test_lalr_automata_creation_expression_grammar() -> None:
    # S -> E
    # E -> E + T | T
    # T -> T * F | F
    # F -> (E) | num

    S, E, T, F = get_nonterminals("S", "E", "T", "F")
    plus, mult, open, close, num = get_terminals("+", "*", "(", ")", "num")

    s_prod = Production(S, [E])
    e_prod = Production(E, [(E, plus, T), T])
    t_prod = Production(T, [(T, mult, F), F])
    f_prod = Production(F, [(open, E, close), num])

    g = Grammar([s_prod, e_prod, t_prod, f_prod], S)
    end_of_chain = get_end_of_chain(g)

    (start_item,) = items_from_production(s_prod)
    e_to_e, e_to_t = items_from_production(e_prod)
    t_to_t, t_to_f = items_from_production(t_prod)
    f_to_e, f_to_num = items_from_production(f_prod)

    states = (
        LR1Set(start_item.to_lr1([end_of_chain])),
        LR1Set(
            chain(
                start_item.next().to_lr1([end_of_chain]),
                e_to_e.next().to_lr1([end_of_chain, plus]),
            )
        ),
        LR1Set(e_to_e.next(2).to_lr1([end_of_chain, plus, close])),
        LR1Set(t_to_f.next().to_lr1([end_of_chain, plus, close, mult])),
        LR1Set(
            chain(
                e_to_e.next(3).to_lr1([end_of_chain, plus, close]),
                t_to_t.next().to_lr1([end_of_chain, plus, close, mult]),
            )
        ),
        LR1Set(
            chain(
                e_to_t.next().to_lr1([end_of_chain, plus, close]),
                t_to_t.next().to_lr1([end_of_chain, plus, close, mult]),
            )
        ),
        LR1Set(
            t_to_t.next(2).to_lr1([end_of_chain, plus, close, mult]),
        ),
        LR1Set(
            f_to_e.next().to_lr1([end_of_chain, plus, close, mult]),
        ),
        LR1Set(
            t_to_t.next(3).to_lr1([end_of_chain, plus, close, mult]),
        ),
        LR1Set(
            chain(
                f_to_e.next(2).to_lr1([end_of_chain, plus, close, mult]),
                e_to_e.next().to_lr1([plus, close]),
            )
        ),
        LR1Set(
            f_to_num.next().to_lr1([end_of_chain, plus, close, mult]),
        ),
        LR1Set(
            f_to_e.next(3).to_lr1([end_of_chain, plus, close, mult]),
        ),
    )

    expected_transitions: Transitions = {
        (states[0], E): states[1],
        (states[0], F): states[3],
        (states[0], T): states[5],
        (states[0], open): states[7],
        (states[0], num): states[10],
        (states[1], plus): states[2],
        (states[2], F): states[3],
        (states[2], T): states[4],
        (states[2], open): states[7],
        (states[2], num): states[10],
        (states[4], mult): states[6],
        (states[5], mult): states[6],
        (states[6], open): states[7],
        (states[6], F): states[8],
        (states[6], num): states[10],
        (states[7], F): states[3],
        (states[7], T): states[5],
        (states[7], open): states[7],
        (states[7], E): states[9],
        (states[7], num): states[10],
        (states[9], plus): states[2],
        (states[9], close): states[11],
    }

    automata = LALRAutomata(g)

    assert set(automata._transitions.items()) == set(expected_transitions.items())

    assert automata.start_state == states[0]
    assert automata.states == set(states)
    assert automata.transition_count == len(expected_transitions)
    for (start, symbol), end in expected_transitions.items():
        assert automata.get_transition(start, symbol) == end
