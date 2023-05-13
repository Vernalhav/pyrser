from compilers.grammar.nonterminals import Nonterminal
from compilers.grammar.productions import ProductionLine
from compilers.grammar.terminals import Terminal
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import LRSet


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
