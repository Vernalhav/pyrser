from collections import defaultdict
from typing import NamedTuple

from compilers.grammar.grammar import Grammar
from compilers.grammar.symbols import Symbol, is_nonterminal, is_terminal
from compilers.grammar.terminals import Terminal
from compilers.parser import actions
from compilers.parser.lr_automata import LRAutomata
from compilers.parser.lr_items import LRItem
from compilers.parser.lr_sets import LR0Set, LR1Set
from compilers.parser.tables import LRParsingTable
from compilers.utils import GroupedDefaultDict, GroupedDict, flatten

StateLookaheads = GroupedDict[LR0Set, LRItem, set[Terminal]]
PropagationTable = GroupedDict[LR0Set, LRItem, dict[LR0Set, set[LRItem]]]
GeneratedLookaheads = GroupedDict[Symbol, LRItem, set[Terminal]]
PropagatedLookaheads = GroupedDict[Symbol, LRItem, set[LRItem]]


class LALRAutomata:
    grammar: Grammar
    states: set[LR1Set]
    start_state: LR1Set
    _transitions: GroupedDict[LR1Set, Symbol, LR1Set]

    def __init__(self, g: Grammar) -> None:
        self.grammar = g
        self._compute_states_and_transitions()

    @property
    def transition_count(self) -> int:
        return self._transitions.flat_len()

    def get_transition(self, state: LR1Set, symbol: Symbol) -> LR1Set:
        return self._transitions[state, symbol]

    def compute_parsing_table(self) -> LRParsingTable[LR1Set]:
        table = LRParsingTable[LR1Set]()
        start_item, *_ = self.start_state.kernel
        accept_item = start_item.next()

        for state in self.states:
            for item in state:
                if item == accept_item:
                    table[state, item.lookahead] = actions.Accept()
                elif item.complete:
                    table[state, item.lookahead] = actions.Reduce(item.production)

            if state not in self._transitions:
                continue

            for symbol, target_state in self._transitions[state].items():
                if is_nonterminal(symbol):
                    table[state, symbol] = actions.Goto(target_state)
                elif is_terminal(symbol):
                    table[state, symbol] = actions.Shift(target_state)

        return table

    def _compute_states_and_transitions(self) -> None:
        lr0_automata = LRAutomata(self.grammar)
        lookaheads = self._propagate_lookaheads(lr0_automata)

        lr0_to_lr1_states: dict[LR0Set, LR1Set] = {}

        self.states = set()
        for lr0_state in lr0_automata.states:
            kernel_items = (
                lr0_item.to_lr1(lookahead)
                for lr0_item in lr0_state.kernel
                for lookahead in lookaheads[lr0_state, lr0_item]
            )
            lr1_state = LR1Set(kernel_items).closure(self.grammar)
            self.states.add(lr1_state)
            lr0_to_lr1_states[lr0_state] = lr1_state

        self.start_state = lr0_to_lr1_states[lr0_automata.start_state]

        self._transitions = GroupedDict()
        for lr0_start, symbol, lr0_end in lr0_automata.transitions:
            start, end = lr0_to_lr1_states[lr0_start], lr0_to_lr1_states[lr0_end]
            self._transitions[start, symbol] = end

    def _propagate_lookaheads(self, automata: LRAutomata) -> StateLookaheads:
        lookaheads, table = self._compute_initial_lookaheads_and_propagations(automata)

        changed = True
        while changed:
            changed = False

            for start_state, start_item, propagations in table.flatten():
                propagated_lookaheads = lookaheads[start_state, start_item]
                for target_state, target_item in flatten(propagations):
                    set_to_update = lookaheads[target_state, target_item]
                    changed |= not (propagated_lookaheads <= set_to_update)
                    set_to_update |= propagated_lookaheads

        return lookaheads

    def _compute_initial_lookaheads_and_propagations(
        self, automata: LRAutomata
    ) -> tuple[StateLookaheads, PropagationTable]:
        lookaheads: StateLookaheads = GroupedDefaultDict(set)
        propagations: PropagationTable = GroupedDefaultDict(lambda: defaultdict(set))

        start_state = automata.start_state
        start_item, *_ = start_state.kernel
        end_of_chain = get_end_of_chain(self.grammar)
        lookaheads[start_state, start_item].add(end_of_chain)

        for state in automata.states:
            generated, propagated = determine_lookahead_relationships(
                state, self.grammar
            )
            self._add_generated(state, generated, lookaheads, automata)
            self._add_propagated(state, propagated, propagations, automata)

        return lookaheads, propagations

    def _add_generated(
        self,
        state: LR0Set,
        generated: GeneratedLookaheads,
        lookaheads: StateLookaheads,
        automata: LRAutomata,
    ) -> None:
        for symbol, item, generated_lookaheads in generated.flatten():
            target_state = automata.get_transition(state, symbol)
            lookaheads[target_state, item] |= generated_lookaheads

    def _add_propagated(
        self,
        state: LR0Set,
        propagated: PropagatedLookaheads,
        propagation_table: PropagationTable,
        automata: LRAutomata,
    ) -> None:
        for symbol, item, propagated_items in propagated.flatten():
            target_state = automata.get_transition(state, symbol)
            propagation_table[state, item][target_state] |= propagated_items


class LookaheadRelationships(NamedTuple):
    generated: GeneratedLookaheads
    propagated: PropagatedLookaheads

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, LookaheadRelationships):
            return False

        is_equal = True
        is_equal &= value.generated.flat_len() == self.generated.flat_len()
        for symbol, lookahead, symbols in self.generated.flatten():
            is_equal &= symbols == value.generated[symbol][lookahead]

        is_equal &= value.propagated.flat_len() == self.propagated.flat_len()
        for symbol, item, items in self.propagated.flatten():
            is_equal &= items == value.propagated[symbol][item]

        return is_equal


def get_dummy(g: Grammar) -> Terminal:
    return Terminal("#")  # TODO: Dynamically change value to not conflict with grammar


def get_end_of_chain(g: Grammar) -> Terminal:
    return Terminal("$")  # TODO: Dynamically change value to not conflict with grammar


def determine_lookahead_relationships(
    state: LR0Set, g: Grammar
) -> LookaheadRelationships:
    dummy = get_dummy(g)
    relationships = LookaheadRelationships(
        propagated=GroupedDefaultDict(set),
        generated=GroupedDefaultDict(set),
    )

    for kernel_item in state.kernel:
        closed_set = LR1Set({kernel_item.to_lr1(dummy)}).closure(g)
        for item in closed_set:
            if item.complete:
                continue

            next_symbol = item.next_symbol
            next_item = item.next().to_lr0()
            if item.lookahead == dummy:
                relationships.propagated[next_symbol, kernel_item].add(next_item)
            else:
                relationships.generated[next_symbol, next_item].add(item.lookahead)

    return relationships
