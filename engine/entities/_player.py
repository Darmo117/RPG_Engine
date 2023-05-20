from . import _entity


class PlayerEntity(_entity.Entity):
    """This class represents the player entity. The player is created each time a map is loaded."""

    def __init__(self, sprite_sheet: str, level, sprint_ratio: float):
        """Create a player entity.

        :param sprite_sheet: Player’s sprite sheet.
        :param level: Level containing this entity.
        :type level: engine.level.Level
        :param sprint_ratio: Coefficient to apply to base speed when running.
        """
        super().__init__(sprite_sheet, level, 0.1)
        if sprint_ratio < 1:
            raise ValueError(f'sprint ratio must be >= 1, got {sprint_ratio}')
        self.sprint_ratio = sprint_ratio
        self._base_speed = self.speed
        self._is_running = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    @is_running.setter
    def is_running(self, run: bool):
        self._is_running = run
        if self._is_running:
            self.speed = self.sprint_ratio * self._base_speed
        else:
            self.speed = self._base_speed


__all__ = [
    'PlayerEntity',
]
