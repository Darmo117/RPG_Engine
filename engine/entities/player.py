from .entity import Entity


class Player(Entity):
    """This class represents the player entity. The player is created each time a map is loaded."""

    def __init__(self, sprite_sheet: str, current_map):
        super().__init__(sprite_sheet, current_map, 2, 2)


class PlayerData:
    """
    This class holds all data about the player (inventory, HP, etc.).
    The same instance is used throughout a game session.
    """
    pass  # TODO
