import typing as typ

import pygame

from engine import sprite as sp, tileset, constants


class Player(sp.Sprite):
    """This class represents the player entity. The player is created each time a level is loaded."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    SPEED = 3

    def __init__(self):
        super().__init__()

        self._speed_x = 0
        self._speed_y = 0

        self._direction = self.DOWN

        self._current_level = None

        sprite_sheet = tileset.Tileset("data/tiles/player.png")

        self._walking_frames_r = []
        self._walking_frames_r.append(sprite_sheet.get_image(16, 32, 16, 16))
        self._walking_frames_r.append(sprite_sheet.get_image(32, 32, 16, 16))
        self._walking_frames_r.append(sprite_sheet.get_image(48, 32, 16, 16))

        self._walking_frames_l = []
        for frame in self._walking_frames_r:
            image = pygame.transform.flip(frame, True, False)
            self._walking_frames_l.append(image)

        self._animation_index = 0

        self._image = self._walking_frames_r[self._animation_index]
        self._rect = pygame.Rect(0, 0, constants.SCREEN_TILE_SIZE, constants.SCREEN_TILE_SIZE)

    @property
    def top(self) -> int:
        return self._rect.top

    @top.setter
    def top(self, value: int):
        self._rect.top = value

    @property
    def bottom(self) -> int:
        return self._rect.bottom

    @bottom.setter
    def bottom(self, value: int):
        self._rect.bottom = value

    @property
    def left(self) -> int:
        return self._rect.left

    @left.setter
    def left(self, value: int):
        self._rect.left = value

    @property
    def right(self) -> int:
        return self._rect.right

    @right.setter
    def right(self, value: int):
        self._rect.right = value

    @property
    def speed(self) -> typ.Tuple[float, float]:
        return self._speed_x, self._speed_y

    @property
    def speed_x(self) -> float:
        return self._speed_x

    @property
    def speed_y(self) -> float:
        return self._speed_y

    @property
    def current_level(self):
        return self._current_level

    @current_level.setter
    def current_level(self, value):
        self._current_level = value

    def set_position(self, x: int, y: int):
        self._rect.x = x
        self._rect.y = y

    def update(self):
        self._rect.x += self._speed_x

        for sprite in self._current_level.collides(self):
            if self._speed_x > 0:
                self._rect.right = sprite.rect.left
            elif self._speed_x < 0:
                self._rect.left = sprite.rect.right

        self._rect.y += self._speed_y

        for sprite in self._current_level.collides(self):
            if self._speed_y > 0:
                self._rect.bottom = sprite.rect.top
            elif self._speed_y < 0:
                self._rect.top = sprite.rect.bottom

        pos = self._rect.x + self._current_level.shift_x
        if self._direction == self.RIGHT:
            frame = (pos // 30) % len(self._walking_frames_r)
            self._image = self._walking_frames_r[frame]
        else:
            frame = (pos // 30) % len(self._walking_frames_l)
            self._image = self._walking_frames_l[frame]

    def go_up(self):
        self._speed_y = -self.SPEED
        self._direction = self.UP

    def go_down(self):
        self._speed_y = self.SPEED
        self._direction = self.DOWN

    def go_left(self):
        self._speed_x = -self.SPEED
        self._direction = self.LEFT

    def go_right(self):
        self._speed_x = self.SPEED
        self._direction = self.RIGHT

    def _move_to_next_tile(self):
        pass  # TODO


class PlayerData:
    """
    This class holds all data about the player (inventory, HP, etc.).
    The same instance is used throughout a game session.
    """
    pass  # TODO
