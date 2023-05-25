from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import Production, ProductionLine
from compilers.parser.lr_items import LR1Item, LRItem
from compilers.parser.lr_sets import LR0Set, LR1Set
from tests.utils import get_nonterminals, get_terminals


def test_lr_sets_compare_kernel_only() -> None:
    Sp, S = get_nonterminals("S'", "S")
    a, b = get_terminals("a", "b")

    start_item = LRItem(ProductionLine(Sp, (S,)))
    s_to_a_item = LRItem(ProductionLine(S, (a,)))
    s_to_b_item = LRItem(ProductionLine(S, (b,)))

    kernel_only = LR0Set({start_item})
    different_kernel = LR0Set({start_item, s_to_a_item})
    with_nonkernel = LR0Set({start_item}, {s_to_a_item, s_to_b_item})

    assert kernel_only == with_nonkernel
    assert len({kernel_only, with_nonkernel}) == 1
    assert len({kernel_only, different_kernel}) == 2


def test_lr0_set_closure_includes_all_kernel_items() -> None:
    # S -> A
    # A -> aC | B
    # B -> b
    # C -> c

    S, A, B, C = get_nonterminals("S", "A", "B", "C")
    a, b, c = get_terminals("a", "b", "c")

    s_production = Production(S, [A])
    a_production = Production(A, [(a, C), B])
    b_production = Production(B, [b])
    c_production = Production(C, [c])

    start_item = LRItem(ProductionLine(S, (A,)))
    a_to_a_item = LRItem(ProductionLine(A, (a, C)))
    a_to_b_item = LRItem(ProductionLine(A, (B,)))
    b_to_b_item = LRItem(ProductionLine(B, (b,)))
    c_to_c_item = LRItem(ProductionLine(C, (c,)))

    g = Grammar((s_production, a_production, b_production, c_production), S)

    lr_set = LR0Set({start_item, a_to_a_item.next()})

    assert lr_set.closure(g).nonkernel == {
        a_to_a_item,
        a_to_b_item,
        b_to_b_item,
        c_to_c_item,
    }


def test_lr0_set_closure_doesnt_propagate_terminal() -> None:
    # S -> A
    # A -> aC | B
    # B -> b
    # C -> c

    S, A, B, C = get_nonterminals("S", "A", "B", "C")
    a, b, c = get_terminals("a", "b", "c")

    s_production = Production(S, [A])
    a_production = Production(A, [(a, C), B])
    b_production = Production(B, [b])
    c_production = Production(C, [c])

    start_item = LRItem(ProductionLine(S, (A,)))
    a_to_a_item = LRItem(ProductionLine(A, (a, C)))
    a_to_b_item = LRItem(ProductionLine(A, (B,)))
    b_to_b_item = LRItem(ProductionLine(B, (b,)))

    g = Grammar((s_production, a_production, b_production, c_production), S)

    lr_set = LR0Set({start_item})

    assert lr_set.closure(g).nonkernel == {a_to_a_item, a_to_b_item, b_to_b_item}


def test_lr0_set_closure_creates_empty_item() -> None:
    # S -> A
    # A -> <empty string>

    S, A = get_nonterminals("S", "A")

    s_production = Production(S, [A])
    a_production = Production(A, [()])

    start_item = LRItem(ProductionLine(S, (A,)))
    empty_item = LRItem(ProductionLine(A, ()))

    g = Grammar((s_production, a_production), S)

    lr_set = LR0Set({start_item})

    assert lr_set.closure(g).nonkernel == {empty_item}


def test_lr1_set_closure_creates_empty_item() -> None:
    # S -> A
    # A -> <empty string>

    S, A = get_nonterminals("S", "A")
    (end_of_chain,) = get_terminals("$")

    s_production = Production(S, [A])
    a_production = Production(A, [()])

    start_item = LR1Item(ProductionLine(S, (A,)), end_of_chain)
    empty_item = LR1Item(ProductionLine(A, ()), end_of_chain)

    g = Grammar((s_production, a_production), S)

    lr_set = LR1Set({start_item})

    assert lr_set.closure(g).nonkernel == {empty_item}


def test_lr1_set_closure_doesnt_propagate_terminal() -> None:
    # S -> b

    (S,) = get_nonterminals("S")
    end_marker, b = get_terminals("$", "b")

    s_production = Production(S, [b])

    start_item = LR1Item(ProductionLine(S, (b,)), end_marker)

    g = Grammar((s_production,), S)

    lr_set = LR1Set({start_item})

    assert lr_set.closure(g).nonkernel == set()


def test_lr1_set_closure_generates_lookaheads() -> None:
    # S' -> S
    # S -> CC
    # C -> cC | d

    Sp, S, C = get_nonterminals("S'", "S", "C")
    c, d, end_marker = get_terminals("c", "d", "$")

    sp_production = Production(Sp, [S])
    s_production = Production(S, [(C, C)])
    c_production = Production(C, [(c, C), d])

    start_item = LR1Item(ProductionLine(Sp, (S,)), end_marker)
    s_to_cc_item = LR1Item(ProductionLine(S, (C, C)), end_marker)
    c_to_cc_item_c = LR1Item(ProductionLine(C, (c, C)), c)
    c_to_cc_item_d = LR1Item(ProductionLine(C, (c, C)), d)
    c_to_d_item_c = LR1Item(ProductionLine(C, (d,)), c)
    c_to_d_item_d = LR1Item(ProductionLine(C, (d,)), d)

    g = Grammar((sp_production, s_production, c_production), Sp)

    lr_set = LR1Set({start_item})

    assert lr_set.closure(g).nonkernel == {
        s_to_cc_item,
        c_to_cc_item_c,
        c_to_cc_item_d,
        c_to_d_item_c,
        c_to_d_item_d,
    }


def test_lr1_set_closure_pointer_grammar() -> None:
    # S' -> S
    # S -> L = R | R
    # L -> *R | id
    # R -> L

    Sp, S, L, R = get_nonterminals("S'", "S", "L", "R")
    times, eq, id, dummy = get_terminals("*", "=", "id", "#")

    sp_production = Production(Sp, [S])
    s_production = Production(S, [(L, eq, R), R])
    l_production = Production(L, [(times, R), id])
    r_production = Production(R, [L])

    start_item = LR1Item(ProductionLine(Sp, (S,)), dummy)
    s_to_l_dummy = LR1Item(ProductionLine(S, (L, eq, R)), dummy)
    s_to_r_dummy = LR1Item(ProductionLine(S, (R,)), dummy)
    l_to_r_dummy = LR1Item(ProductionLine(L, (times, R)), dummy)
    l_to_r_eq = LR1Item(ProductionLine(L, (times, R)), eq)
    l_to_id_dummy = LR1Item(ProductionLine(L, (id,)), dummy)
    l_to_id_eq = LR1Item(ProductionLine(L, (id,)), eq)
    r_to_l_dummy = LR1Item(ProductionLine(R, (L,)), dummy)

    g = Grammar((sp_production, s_production, l_production, r_production), Sp)

    lr_set = LR1Set({start_item})

    assert lr_set.closure(g).nonkernel == {
        s_to_l_dummy,
        s_to_r_dummy,
        l_to_r_dummy,
        l_to_r_eq,
        l_to_id_dummy,
        l_to_id_eq,
        r_to_l_dummy,
    }
