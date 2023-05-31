from collections import deque
from typing import Iterable, Iterator

from compilers.grammar.grammar import Grammar
from compilers.grammar.productions import ProductionLine
from compilers.lexer.tokens import Token
from compilers.parser.actions import Accept, Error, Reduce, Shift
from compilers.parser.ast import ASTNode, NonterminalNode, TerminalNode
from compilers.parser.lalr_automata import LALRAutomata
from compilers.parser.lr_sets import LR1Set


class ParsingError(Exception):
    pass


class UnexpectedTokenError(ParsingError):
    def __init__(self, token: Token, index: int) -> None:
        self.token = token
        self.index = index

        message = f"Parsing error on token {token} at position {index}"
        super().__init__(message)


class NoEndOfInputTokenError(ParsingError):
    def __init__(self) -> None:
        super().__init__("Token chain does not end with end_of_chain token")


class LALRParser:
    grammar: Grammar

    def __init__(self, g: Grammar) -> None:
        self.grammar = g
        automata = LALRAutomata(g)
        self._start_state = automata.start_state
        self._parsing_table = automata.compute_parsing_table()
        self._parsing_stack = list[LR1Set]()
        self._ast_stack = list[ASTNode]()

    def parse(self, chain: Iterable[Token]) -> ASTNode:
        self._parsing_stack.clear()
        self._ast_stack.clear()

        chain_iterator = iter(chain)
        self._parsing_stack.append(self._start_state)

        token = consume_token(chain_iterator)
        while True:
            current_state = self._parsing_stack[-1]
            action = self._parsing_table[current_state, token.terminal]
            match action:
                case Shift(target=target_state):
                    self._shift(target_state, token)
                    token = consume_token(chain_iterator)

                case Reduce(production=production):
                    self._reduce(production, token)

                case Accept():
                    return self._ast_stack[-1]

                case Error():
                    raise UnexpectedTokenError(token, -1)

        raise NoEndOfInputTokenError()

    def _push_to_stacks(self, state: LR1Set, node: ASTNode) -> None:
        self._parsing_stack.append(state)
        self._ast_stack.append(node)

    def _shift(self, target_state: LR1Set, token: Token) -> None:
        self._push_to_stacks(target_state, TerminalNode(token.terminal, token.value))

    def _reduce(self, production: ProductionLine, token: Token) -> None:
        children: deque[ASTNode] = deque()
        for _, _ in enumerate(production.derivation):
            child = self._ast_stack.pop()
            self._parsing_stack.pop()
            children.appendleft(child)

        new_node = NonterminalNode(production.nonterminal, children)
        top_state = self._parsing_stack[-1]
        new_state = self._parsing_table[top_state, production.nonterminal].target

        self._push_to_stacks(new_state, new_node)


def consume_token(chain: Iterator[Token]) -> Token:
    return next(chain)
