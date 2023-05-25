from compilers.grammar.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.grammar.symbols import Symbol
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_automata import LRAutomata, get_transition_symbols, goto
from compilers.parser.lr_items import LRItem, items_from_production
from compilers.parser.lr_sets import LR0Set

Transitions = dict[tuple[LR0Set, Symbol], LR0Set]


def test_symbol_grouping_includes_nonkernel() -> None:
    # S -> aA
    # A -> B
    # B -> b | Aa

    S = Nonterminal("S")
    A = Nonterminal("A")
    B = Nonterminal("B")
    a = Terminal("a")
    b = Terminal("b")

    s_to_a = LRItem(ProductionLine(S, (a, A))).next()
    a_to_b = LRItem(ProductionLine(A, (B,)))
    b_to_b = LRItem(ProductionLine(B, (b,)))
    b_to_aa = LRItem(ProductionLine(B, (A, a)))

    lr_set = LR0Set({s_to_a}, {a_to_b, b_to_aa, b_to_b})

    expected = {A: {s_to_a, b_to_aa}, B: {a_to_b}, b: {b_to_b}}
    received = list(get_transition_symbols(lr_set))

    assert len(expected) == len(received)
    for nonterminal, items in received:
        assert nonterminal in expected
        assert set(items) == expected[nonterminal]


def test_goto_state_creation() -> None:
    # S -> A | BA
    # B -> aAb | A

    S = Nonterminal("S")
    A = Nonterminal("A")
    B = Nonterminal("B")
    a = Terminal("a")
    b = Terminal("b")

    s_to_a = LRItem(ProductionLine(S, (A,)))
    s_to_ba = LRItem(ProductionLine(S, (B, A)))
    b_to_a = LRItem(ProductionLine(B, (A,)))
    b_to_aab = LRItem(ProductionLine(B, (a, A, b))).next()

    lr_set = LR0Set({b_to_aab}, {s_to_ba, b_to_a, s_to_a})
    assert goto(lr_set, A) == LR0Set({s_to_a.next(), b_to_aab.next(), b_to_a.next()})


def test_lr_sets_creation_small_grammar() -> None:
    # S' -> S
    # S -> a | b

    Sp = Nonterminal("S'")
    S = Nonterminal("S")
    a = Terminal("a")
    b = Terminal("b")

    sp_prod = Production(Sp, [S])
    s_prod = Production(S, [a, b])

    (start_item,) = items_from_production(sp_prod)
    s_to_a, s_to_b = items_from_production(s_prod)

    g = Grammar((sp_prod, s_prod), Sp)
    lr_automata = LRAutomata(g)

    states = (
        LR0Set({start_item}),
        LR0Set({s_to_a.next()}),
        LR0Set({s_to_b.next()}),
        LR0Set({start_item.next()}),
    )

    expected_transitions: Transitions = {
        (states[0], a): states[1],
        (states[0], b): states[2],
        (states[0], S): states[3],
    }

    assert lr_automata.states == set(states)
    assert lr_automata.start_state == states[0]
    assert len(expected_transitions) == lr_automata.transition_count
    for (start, symbol), end in expected_transitions.items():
        assert lr_automata.get_transition(start, symbol) == end


def test_lr_sets_creation_recursive_grammar() -> None:
    # S -> L
    # L -> LP | P
    # P -> (L) | ()

    S = Nonterminal("S")
    P = Nonterminal("P")
    L = Nonterminal("L")
    open = Terminal("(")
    close = Terminal(")")

    start_prod = Production(S, [L])
    p_prod = Production(P, [(open, L, close), (open, close)])
    l_prod = Production(L, [(L, P), P])

    (start_item,) = items_from_production(start_prod)
    p_to_l, p_to_paren = items_from_production(p_prod)
    l_to_lp, l_to_p = items_from_production(l_prod)

    g = Grammar((start_prod, p_prod, l_prod), S)
    lr_automata = LRAutomata(g)

    states = (
        LR0Set({start_item}),
        LR0Set({p_to_l.next(), p_to_paren.next()}),
        LR0Set({start_item.next(), l_to_lp.next()}),
        LR0Set({l_to_p.next()}),
        LR0Set({l_to_lp.next().next()}),
        LR0Set({p_to_paren.next().next()}),
        LR0Set({p_to_l.next().next(), l_to_lp.next()}),
        LR0Set({p_to_l.next().next().next()}),
    )

    expected_transitions: Transitions = {
        (states[0], P): states[3],
        (states[0], open): states[1],
        (states[0], L): states[2],
        (states[1], open): states[1],
        (states[1], close): states[5],
        (states[1], L): states[6],
        (states[1], P): states[3],
        (states[2], open): states[1],
        (states[2], P): states[4],
        (states[6], open): states[1],
        (states[6], close): states[7],
        (states[6], P): states[4],
    }

    assert lr_automata.states == set(states)
    assert lr_automata.start_state == states[0]
    assert len(expected_transitions) == lr_automata.transition_count
    for (start, symbol), end in expected_transitions.items():
        assert lr_automata.get_transition(start, symbol) == end
