from dataclasses import dataclass

from compilers.grammar.terminals import Terminal


@dataclass
class Token:
    terminal: Terminal
    value: str | None = None
