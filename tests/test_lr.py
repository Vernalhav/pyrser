from compilers.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import LRSet, closure, get_transition_symbols


def test_lr_sets_compare_kernel_only() -> None:
    S_prime = Nonterminal("S'")
    S = Nonterminal("S")
    a = Terminal("a")
    b = Terminal("b")

    start_item = LRItem(ProductionLine(S_prime, (S,)))
    s_to_a_item = LRItem(ProductionLine(S, (a,)))
    s_to_b_item = LRItem(ProductionLine(S, (b,)))

    kernel_only = LRSet.from_items({start_item})
    different_kernel = LRSet.from_items({start_item, s_to_a_item})
    with_nonkernel = LRSet.from_items({start_item}, {s_to_a_item, s_to_b_item})

    assert kernel_only == with_nonkernel
    assert len({kernel_only, with_nonkernel}) == 1
    assert len({kernel_only, different_kernel}) == 2


def test_lr_set_closure_includes_all_kernel_items() -> None:
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

    s_production = Production(S, (A,))
    a_production = Production(A, ((a, C), B))
    b_production = Production(B, (b,))
    c_production = Production(C, (c,))

    start_item = LRItem(ProductionLine(S, (A,)))
    a_to_a_item = LRItem(ProductionLine(A, (a, C)))
    a_to_b_item = LRItem(ProductionLine(A, (B,)))
    b_to_b_item = LRItem(ProductionLine(B, (b,)))
    c_to_c_item = LRItem(ProductionLine(C, (c,)))

    g = Grammar((s_production, a_production, b_production, c_production), S)

    lr_set = LRSet.from_items({start_item, a_to_a_item.next()})

    assert closure(lr_set, g).nonkernel == {
        a_to_a_item,
        a_to_b_item,
        b_to_b_item,
        c_to_c_item,
    }


def test_lr_set_closure_doesnt_propagate_nonterminal() -> None:
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

    s_production = Production(S, (A,))
    a_production = Production(A, ((a, C), B))
    b_production = Production(B, (b,))
    c_production = Production(C, (c,))

    start_item = LRItem(ProductionLine(S, (A,)))
    a_to_a_item = LRItem(ProductionLine(A, (a, C)))
    a_to_b_item = LRItem(ProductionLine(A, (B,)))
    b_to_b_item = LRItem(ProductionLine(B, (b,)))

    g = Grammar((s_production, a_production, b_production, c_production), S)

    lr_set = LRSet.from_items({start_item})

    assert closure(lr_set, g).nonkernel == {a_to_a_item, a_to_b_item, b_to_b_item}


def test_lr_set_closure_creates_empty_item() -> None:
    # S -> A
    # A -> <empty string>

    S = Nonterminal("S")
    A = Nonterminal("A")

    s_production = Production(S, (A,))
    a_production = Production(A, ((),))

    start_item = LRItem(ProductionLine(S, (A,)))
    empty_item = LRItem(ProductionLine(A, ()))

    g = Grammar((s_production, a_production), S)

    lr_set = LRSet.from_items({start_item})

    assert closure(lr_set, g).nonkernel == {empty_item}


def test_symbol_grouping_includes_nonkernel() -> None:
    # S -> aA
    # A -> B
    # B -> b | Aa

    S = Nonterminal("S")
    A = Nonterminal("A")
    B = Nonterminal("B")
    a = Terminal("a")
    b = Terminal("b")

    s_to_a_item = LRItem(ProductionLine(S, (a, A))).next()
    a_to_b_item = LRItem(ProductionLine(A, (B,)))
    b_to_b_item = LRItem(ProductionLine(B, (b,)))
    b_to_aa_item = LRItem(ProductionLine(B, (A, a)))

    lr_set = LRSet.from_items({s_to_a_item}, {a_to_b_item, b_to_aa_item, b_to_b_item})

    expected = {A: {s_to_a_item, b_to_aa_item}, B: {a_to_b_item}, b: {b_to_b_item}}
    received = list(get_transition_symbols(lr_set))

    assert len(expected) == len(received)
    for nonterminal, items in received:
        assert nonterminal in expected
        assert set(items) == expected[nonterminal]


