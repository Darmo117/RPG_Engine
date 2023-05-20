import dataclasses


@dataclasses.dataclass(frozen=True)
class Item:
    """Represents an item. Each item has a unique ID and a type."""

    TYPE_NORMAL = 'normal'
    TYPE_EQUIP = 'equipment'
    TYPE_QUEST = 'quest'
    TYPES = [TYPE_NORMAL, TYPE_EQUIP, TYPE_QUEST, ]

    id: int
    type: str

    def __eq__(self, other):
        return isinstance(other, Item) and self.id == other.id

    def __hash__(self):
        return 31 ^ hash(self.id)


class ItemStack:
    """An itemstack holds an item and a count.
    The count may be updated but cannot be negative nor over the set limit.
    """

    MAX_COUNT = 9999

    def __init__(self, item: Item, count: int):
        self._item = item
        self._count = 0
        self.update_count(count)

    @property
    def item(self) -> Item:
        return self._item

    @property
    def count(self) -> int:
        return self._count

    @property
    def is_empty(self) -> bool:
        """Indicate whether the count is 0."""
        return self._count == 0

    def update_count(self, v: int) -> int:
        """Add the given value to the count of this item stack.

        :param v: The value to add. May be negative.
        :return: The actual value added to the count. May differ from the argument
            if the resulting stack size is negative or greater than the maximum.
        """
        c = self._count
        if c + v > self.MAX_COUNT:
            self._count = self.MAX_COUNT
            return self.MAX_COUNT - c
        elif c + v < 0:
            self._count = 0
            return -c
        else:
            self._count += v
            return v

    def copy(self):
        return ItemStack(self._item, self._count)

    def __eq__(self, other):
        return isinstance(other, ItemStack) and self.item == other.item and self.count == other.count

    def __hash__(self):
        return 31 ^ hash(self._item) ^ hash(self._count)


class PlayerInventory:
    """Holds the items of the player character."""

    def __init__(self):
        self._items: dict[str, set[ItemStack]] = {t: set() for t in Item.TYPES}

    def add_item(self, item_stack: ItemStack):
        if item_stack.is_empty:
            return
        stack_item = item_stack.item
        stacks = self._items[stack_item.type]
        for stack in stacks:
            if stack.item == stack_item:
                diff = stack.update_count(item_stack.count)
                item_stack.update_count(diff)
                break
        else:
            stacks.add(item_stack.copy())

    def remove_item(self, item_stack: ItemStack):
        if item_stack.is_empty:
            return
        stack_item = item_stack.item
        stacks = self._items[stack_item.type]
        for stack in stacks:
            if stack.item == stack_item:
                diff = stack.update_count(-item_stack.count)
                item_stack.update_count(diff)
                if stack.is_empty:
                    stacks.remove(stack)
                break
