from compilers.grammar import Terminal
from compilers.parser.lr_items import LR1Item, LRItem

LR1State = frozenset[LR1Item]
LRState = frozenset[LRItem]


class CanonicalCollection(set[LR1State]):
    def replace(self, old: LR1State, new: LR1State) -> None:
        if old not in self:
            raise ValueError(f"State {old} does not exist in canonical collection")
        self.remove(old)
        self.add(new)

    def __repr__(self) -> str:
        def group_items_by_lookahead(
            collection: LR1State,
        ) -> dict[LRItem, list[Terminal]]:
            items: dict[LRItem, list[Terminal]] = dict()
            for item in collection:
                if item.to_lr() in items:
                    items[item.to_lr()].append(item.lookahead)
                else:
                    items[item.to_lr()] = [item.lookahead]
            return items

        ITEM_HEADER_LENGTH = 30
        ITEM_PAD_LENGTH = 15

        lines = []
        for collection in self:
            items = group_items_by_lookahead(collection)
            lines.append("-" * ITEM_HEADER_LENGTH)
            for item, lookaheads in items.items():
                lines.append(f"{repr(item).ljust(ITEM_PAD_LENGTH)} | {lookaheads}")
            lines.append("-" * ITEM_HEADER_LENGTH)
            lines.append("")

        return "\n".join(lines)
