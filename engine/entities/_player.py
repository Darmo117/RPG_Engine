from . import _entity


class PlayerEntity(_entity.Entity):
    """This class represents the player entity. The player is created each time a map is loaded."""

    def __init__(self, sprite_sheet: str, level):
        """Create a player entity.

        :param sprite_sheet: Player’s sprite sheet.
        :param level: Level containing this entity.
        :type level: engine.level.Level
        """
        super().__init__(sprite_sheet, level, 0.065)


__all__ = [
    'PlayerEntity',
]
