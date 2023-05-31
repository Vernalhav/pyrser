from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import Production
from compilers.lexer.tokens import Token
from compilers.parser.ast import NonterminalNode, TerminalNode
from compilers.parser.lalr_automata import get_end_of_chain
from compilers.parser.parser import LALRParser
from tests.utils import get_nonterminals, get_terminals


def test_parser_parses_single_terminal() -> None:
    (S,) = get_nonterminals("S")
    (a,) = get_terminals("a")

    start_prod = Production(S, [a])
    g = Grammar([start_prod], S)
    end_of_chain = get_end_of_chain(g)

    input = [Token(a, "a"), Token(end_of_chain)]

    parser = LALRParser(g)
    ast_root = parser.parse(input)

    expected = TerminalNode(
        symbol=a,
        value="a",
    )

    assert ast_root == expected


def test_parser_parses_empty_string() -> None:
    (S, A) = get_nonterminals("S", "A")
    (a,) = get_terminals("a")

    start_prod = Production(S, [A])
    a_prod = Production(A, [a, ()])
    g = Grammar([start_prod, a_prod], S)
    end_of_chain = get_end_of_chain(g)

    input = [Token(end_of_chain)]

    parser = LALRParser(g)
    ast_root = parser.parse(input)

    expected = NonterminalNode(symbol=A, children=())
    assert ast_root == expected


def test_parser_reduces_nonterminal_in_correct_order() -> None:
    # S -> A
    # A -> ab

    S, A = get_nonterminals("S", "A")
    a, b = get_terminals("a", "b")

    s_prod = Production(S, [A])
    a_prod = Production(A, [(a, b)])

    g = Grammar([s_prod, a_prod], S)
    end_of_chain = get_end_of_chain(g)

    input = [Token(a), Token(b), Token(end_of_chain)]

    parser = LALRParser(g)
    ast_root = parser.parse(input)

    # TODO: Fix default values being implementation-dependent
    assert ast_root == NonterminalNode(A, (TerminalNode(a, ""), TerminalNode(b, "")))


def test_parser_parses_expression_grammar() -> None:
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

    # (num + num) * num
    input = [
        Token(open),
        Token(num),
        Token(plus),
        Token(num),
        Token(close),
        Token(mult),
        Token(num),
        Token(end_of_chain),
    ]

    parser = LALRParser(g)
    ast_root = parser.parse(input)

    expected = NonterminalNode(
        E,
        [
            NonterminalNode(
                T,
                [
                    NonterminalNode(
                        T,
                        [
                            NonterminalNode(
                                F,
                                [
                                    TerminalNode(open, ""),
                                    NonterminalNode(
                                        E,
                                        [
                                            NonterminalNode(
                                                E,
                                                [
                                                    NonterminalNode(
                                                        T,
                                                        [
                                                            NonterminalNode(
                                                                F,
                                                                [TerminalNode(num, "")],
                                                            )
                                                        ],
                                                    )
                                                ],
                                            ),
                                            TerminalNode(plus, ""),
                                            NonterminalNode(
                                                T,
                                                [
                                                    NonterminalNode(
                                                        F, [TerminalNode(num, "")]
                                                    )
                                                ],
                                            ),
                                        ],
                                    ),
                                    TerminalNode(close, ""),
                                ],
                            )
                        ],
                    ),
                    TerminalNode(mult, ""),
                    NonterminalNode(F, [TerminalNode(num, "")]),
                ],
            )
        ],
    )
    assert ast_root == expected
