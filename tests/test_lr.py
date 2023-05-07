from compilers.grammar import Grammar
from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import Production, ProductionLine
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import (
    LRSet,
    closure,
    compute_lr_sets,
    get_transition_symbols,
    goto,
)


def test_lr_sets_compare_kernel_only() -> None:
    S_prime = Nonterminal("S'")
    S = Nonterminal("S")
    a = Terminal("a")
    b = Terminal("b")

    start_item = LRItem(ProductionLine(S_prime, (S,)))
    s_to_a_item = LRItem(ProductionLine(S, (a,)))
    s_to_b_item = LRItem(ProductionLine(S, (b,)))

    kernel_only = LRSet({start_item})
    different_kernel = LRSet({start_item, s_to_a_item})
    with_nonkernel = LRSet({start_item}, {s_to_a_item, s_to_b_item})

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

    lr_set = LRSet({start_item, a_to_a_item.next()})

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

    lr_set = LRSet({start_item})

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

    lr_set = LRSet({start_item})

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

    lr_set = LRSet({s_to_a_item}, {a_to_b_item, b_to_aa_item, b_to_b_item})

    expected = {A: {s_to_a_item, b_to_aa_item}, B: {a_to_b_item}, b: {b_to_b_item}}
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

    s_to_a_item = LRItem(ProductionLine(S, (A,)))
    s_to_ba_item = LRItem(ProductionLine(S, (B, A)))
    b_to_a_item = LRItem(ProductionLine(B, (A,)))
    b_to_aab_item = LRItem(ProductionLine(B, (a, A, b))).next()

    lr_set = LRSet({b_to_aab_item}, {s_to_ba_item, b_to_a_item, s_to_a_item})
    assert goto(lr_set, A) == LRSet(
        {s_to_a_item.next(), b_to_aab_item.next(), b_to_a_item.next()}
    )


def test_lr_sets_creation_small_grammar() -> None:
    # S' -> S
    # S -> a | b

    Sp = Nonterminal("S'")
    S = Nonterminal("S")
    a = Terminal("a")
    b = Terminal("b")

    start_production = Production(Sp, (S,))
    s_production = Production(S, (a, b))

    start_item = LRItem(ProductionLine(Sp, (S,)))
    s_to_a_item = LRItem(ProductionLine(S, (a,)))
    s_to_b_item = LRItem(ProductionLine(S, (b,)))

    g = Grammar((start_production, s_production), Sp)
    lr_sets = compute_lr_sets(g)

    assert lr_sets == {
        LRSet({start_item}),  # Only including kernel items for brevity
        LRSet({start_item.next()}),
        LRSet({s_to_a_item.next()}),
        LRSet({s_to_b_item.next()}),
    }


def test_lr_sets_creation_recursive_grammar() -> None:
    # S -> L
    # L -> LP | P
    # P -> (L) | ()

    S = Nonterminal("S")
    P = Nonterminal("P")
    L = Nonterminal("L")
    open = Terminal("(")
    close = Terminal(")")

    start_production = Production(S, [L])
    p_production = Production(P, [(open, L, close), (open, close)])
    l_production = Production(L, [(L, P), P])

    start_item = LRItem(ProductionLine(S, (L,)))
    p_to_l = LRItem(ProductionLine(P, (open, L, close)))
    p_to_paren = LRItem(ProductionLine(P, (open, close)))
    l_to_lp = LRItem(ProductionLine(L, (L, P)))
    l_to_p = LRItem(ProductionLine(L, (P,)))

    g = Grammar((start_production, p_production, l_production), S)
    lr_sets = compute_lr_sets(g)

    assert lr_sets == {
        LRSet({start_item}),
        LRSet({p_to_l.next(), p_to_paren.next()}),
        LRSet({start_item.next(), l_to_lp.next()}),
        LRSet({l_to_p.next()}),
        LRSet({l_to_lp.next().next()}),
        LRSet({p_to_paren.next().next()}),
        LRSet({p_to_l.next().next(), l_to_lp.next()}),
        LRSet({p_to_l.next().next().next()}),
    }
