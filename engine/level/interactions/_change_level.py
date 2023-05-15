import pygame

from . import _base
from ... import entities, io, events


class ChangeLevelInteraction(_base.TileInteraction):
    OPEN = 0
    CLOSED = 1
    LOCKED = 2

    def __init__(self, destination_map: str, player_spawn_location: pygame.Vector2, state: int, hidden: bool):
        super().__init__(2)
        self._dest_map = destination_map
        self._position = player_spawn_location.copy()
        self._state = state
        self._hidden = hidden

    @property
    def player_spawn_location(self) -> pygame.Vector2:
        return self._position.copy()

    @property
    def destination_map(self) -> str:
        return self._dest_map

    @property
    def is_open(self) -> bool:
        return self._state != self.CLOSED and not self.is_locked

    @property
    def is_locked(self) -> bool:
        return self._state == self.LOCKED

    @property
    def is_hidden(self) -> bool:
        return self._hidden

    def can_entity_go_through(self, level, entity: entities.Entity) -> bool:
        return self.is_open and isinstance(entity, entities.PlayerEntity)

    def on_entity_inside(self, level, entity: entities.Entity):
        level.game_engine.fire_event(events.ChangeLevelEvent(self._dest_map, self._position))

    def write_to_buffer(self, buffer: io.ByteBuffer):
        super().write_to_buffer(buffer)
        buffer.write_string(self._dest_map)
        buffer.write_vector(self._position, as_ints=True)
        buffer.write_byte(self._state, signed=False)
        buffer.write_bool(self._hidden)


__all__ = [
    'ChangeLevelInteraction',
]
