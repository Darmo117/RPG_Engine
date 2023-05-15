import abc
import time

import pygame


class Entity(abc.ABC):
    """This class represents an entity. Entities are created each time a map is loaded."""

    EPS = 1e-5

    DIRECTIONS = (
        pygame.Vector2(0, 1),  # Down
        pygame.Vector2(-1, 0),  # Left
        pygame.Vector2(1, 0),  # Right
        pygame.Vector2(0, -1),  # Up
    )

    ANIMATION_COEF = 5

    def __init__(self, sprite_sheet: str, level, speed: float):
        """Create an entity.

        :param sprite_sheet: Entity’s sprite sheet name.
        :param level: Level that contains this entity.
        :type level: engine.level.Level
        :param speed: Movement speed.
        """
        tm = level.game_engine.texture_manager
        self._level = level
        self._pos = pygame.Vector2()
        self._size = tm.get_sprite_size(sprite_sheet)
        self._next_tile = None
        self._queued_direction = None  # Helps reduce character stutter
        self._remaining_distance = 0
        self._direction = 0
        self._speed = speed
        self._anim_frames = tm.get_sprite_frames(sprite_sheet)

        self._frames: list[list[pygame.Surface]] = []
        self._idle_frames = []
        for i in range(len(self.DIRECTIONS)):
            line_start_index = (self._anim_frames + 1) * i
            self._frames.append(
                [tm.get_sprite(line_start_index + 1 + frame_offset, sprite_sheet)
                 for frame_offset in range(self._anim_frames)]
            )
            self._idle_frames.append(tm.get_sprite(line_start_index, sprite_sheet))

        self._animation_index = 0
        self._animation_timer = time.time()

    @property
    def position(self) -> pygame.Vector2:
        return self._pos

    @position.setter
    def position(self, p: pygame.Vector2):
        self._pos = p.copy()

    @property
    def tile_position(self) -> pygame.Vector2:
        return pygame.Vector2(int(self._pos.x), int(self._pos.y))

    @property
    def size(self) -> pygame.Vector2:
        return pygame.Vector2(self._size)

    @property
    def direction(self) -> int:
        return self._direction

    @property
    def animation_index(self):
        return self._animation_index

    @property
    def speed(self) -> float:
        return self._speed

    @speed.setter
    def speed(self, value: float):
        self._speed = max(min(value, 16), 1)

    def update(self):
        self._move()
        if self.is_moving():
            current_time = time.time()
            diff = current_time - self._animation_timer
            if diff >= self.ANIMATION_COEF * self._speed:
                self._animation_index = (self._animation_index + 1) % self._anim_frames
                self._animation_timer = current_time

    def _move(self):
        if self._next_tile is None:
            return

        if self._remaining_distance < self.EPS:
            self._pos = self._next_tile
            interaction = self._level.get_tile_interaction(int(self.tile_position.x), int(self.tile_position.y))
            interaction.on_entity_inside(self._level, self)
            self._next_tile = None
            if self._queued_direction is not None:
                self._move_to_next_tile(self._queued_direction)
                self._queued_direction = None
            else:
                self._remaining_distance = 0

        if self.is_moving():
            speed = pygame.Vector2()
            if self._next_tile.x < self._pos.x:
                speed.x = -self._speed
            elif self._next_tile.x > self._pos.x:
                speed.x = self._speed
            if self._next_tile.y < self._pos.y:
                speed.y = -self._speed
            elif self._next_tile.y > self._pos.y:
                speed.y = self._speed
            self._remaining_distance -= speed.length()
            self._pos += speed

    def go_up(self):
        self._move_to_next_tile(3)

    def go_down(self):
        self._move_to_next_tile(0)

    def go_left(self):
        self._move_to_next_tile(1)

    def go_right(self):
        self._move_to_next_tile(2)

    def is_moving(self):
        return self._next_tile is not None

    def _move_to_next_tile(self, d: int):
        if self.is_moving():
            if self._remaining_distance < 0.25:
                self._queued_direction = d
            return
        self._direction = d
        direction = self.DIRECTIONS[d]
        pos = self.tile_position + direction
        interaction = self._level.get_tile_interaction(int(pos.x), int(pos.y))
        if interaction.can_entity_go_through(self._level, self):
            interaction.on_entity_enter(self._level, self)
            self._next_tile = pos
            self._remaining_distance = self._next_tile.distance_to(self.tile_position)

    def get_texture(self) -> pygame.Surface:
        if self.is_moving():
            return self._frames[self._direction][self._animation_index]
        return self._idle_frames[self._direction]


__all__ = [
    'Entity',
]
