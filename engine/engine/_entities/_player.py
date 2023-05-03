from . import _entity


class PlayerEntity(_entity.Entity):
    """This class represents the player entity. The player is created each time a map is loaded."""

    def __init__(self, sprite_sheet: str, current_map):
        """Create a player entity.

        :param sprite_sheet: Player’s sprite sheet.
        :param current_map: Map containing this entity.
        :type current_map: engine.engine._map._map.Map
        """
        super().__init__(sprite_sheet, current_map, 2, 2)


__all__ = [
    'PlayerEntity',
]
