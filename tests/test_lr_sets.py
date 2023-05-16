from compilers.grammar.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LR1Item, LRItem
from compilers.parser.lr_sets import LR0Set, LR1Set


def test_lr_sets_compare_kernel_only() -> None:
    S_prime = Nonterminal("S'")
    S = Nonterminal("S")
    a = Terminal("a")
    b = Terminal("b")

    start_item = LRItem(ProductionLine(S_prime, (S,)))
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

    S = Nonterminal("S")
    A = Nonterminal("A")
    B = Nonterminal("B")
    C = Nonterminal("C")
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

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

    S = Nonterminal("S")
    A = Nonterminal("A")
    B = Nonterminal("B")
    C = Nonterminal("C")
    a = Terminal("a")
    b = Terminal("b")
    c = Terminal("c")

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

    S = Nonterminal("S")
    A = Nonterminal("A")

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

    S = Nonterminal("S")
    A = Nonterminal("A")
    end_marker = Terminal("$")

    s_production = Production(S, [A])
    a_production = Production(A, [()])

    start_item = LR1Item(ProductionLine(S, (A,)), end_marker)
    empty_item = LR1Item(ProductionLine(A, ()), end_marker)

    g = Grammar((s_production, a_production), S)

    lr_set = LR1Set({start_item})

    assert lr_set.closure(g).nonkernel == {empty_item}


def test_lr1_set_closure_doesnt_propagate_terminal() -> None:
    # S -> b

    S = Nonterminal("S")
    end_marker = Terminal("$")
    b = Terminal("b")

    s_production = Production(S, [b])

    start_item = LR1Item(ProductionLine(S, (b,)), end_marker)

    g = Grammar((s_production,), S)

    lr_set = LR1Set({start_item})

    assert lr_set.closure(g).nonkernel == set()


def test_lr1_set_closure_generates_lookaheads() -> None:
    # S' -> S
    # S -> CC
    # C -> cC | d

    Sp = Nonterminal("S'")
    S = Nonterminal("S")
    C = Nonterminal("C")
    c = Terminal("c")
    d = Terminal("d")
    end_marker = Terminal("$")

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
