import abc
import time

from engine import sprite as sp, global_values as gv


class Entity(sp.TileSprite, metaclass=abc.ABCMeta):
    """This class represents an entity. Entities are created each time a map is loaded."""

    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    def __init__(self, sprite_sheet: str, current_map, animation_length: int, speed: int):
        self._remaining_x = 0
        self._remaining_y = 0

        self._direction = self.DOWN
        self._speed = speed
        self._animation_length = animation_length

        self._map = current_map

        size = (gv.SCREEN_TILE_SIZE, gv.SCREEN_TILE_SIZE)
        self._frames = {}
        self._idle_frames = {}
        for i, side in enumerate([self.DOWN, self.LEFT, self.RIGHT, self.UP]):
            self._frames[side] = [
                gv.TEXTURE_MANAGER.get_sprite(offset + 3 * i, size, sprite_sheet)
                for offset in range(1, animation_length + 1)
            ]
            self._idle_frames[side] = gv.TEXTURE_MANAGER.get_sprite(3 * i, size, sprite_sheet)

        self._animation_index = 0
        self._animation_timer = time.time()

        image = self._frames[self._direction][self._animation_index]
        super().__init__(0, 0, image)

    @property
    def top(self) -> int:
        return self._rect.top

    @top.setter
    def top(self, value: int):
        self._rect.top = value
        self._update_image()

    @property
    def bottom(self) -> int:
        return self._rect.bottom

    @bottom.setter
    def bottom(self, value: int):
        self._rect.bottom = value
        self._update_image()

    @property
    def left(self) -> int:
        return self._rect.left

    @left.setter
    def left(self, value: int):
        self._rect.left = value
        self._update_image()

    @property
    def right(self) -> int:
        return self._rect.right

    @right.setter
    def right(self, value: int):
        self._rect.right = value
        self._update_image()

    @property
    def map(self):
        return self._map

    @map.setter
    def map(self, value):
        self._map = value

    @property
    def speed(self) -> int:
        return self._speed

    @speed.setter
    def speed(self, value: int):
        self._speed = max(min(value, 16), 1)

    def set_position(self, x: int, y: int):
        self._rect.x = x * gv.SCREEN_TILE_SIZE
        self._rect.y = y * gv.SCREEN_TILE_SIZE
        self._update_image()
        self._tile_x = x
        self._tile_y = y

    def update(self):
        if self._remaining_x > 0:
            self._rect.x += self._speed * self._direction[0]
            self._remaining_x -= self._speed
        else:
            self._remaining_x = 0

        if self._remaining_x == 0:
            actual_x = self._rect.x - self._map.shift_x
            if actual_x % gv.SCREEN_TILE_SIZE != 0:
                offset = actual_x % gv.SCREEN_TILE_SIZE
                adjust = offset - (gv.SCREEN_TILE_SIZE if self._direction[0] < 0 else 0)
                self._rect.x -= adjust
            self._tile_x = (self._rect.x - self._map.shift_x) // gv.SCREEN_TILE_SIZE

        if self._remaining_y > 0:
            self._rect.y += self._speed * self._direction[1]
            self._remaining_y -= self._speed
        else:
            self._remaining_y = 0

        if self._remaining_y == 0:
            actual_y = self._rect.y - self._map.shift_y
            if actual_y % gv.SCREEN_TILE_SIZE != 0:
                offset = actual_y % gv.SCREEN_TILE_SIZE
                adjust = offset - (gv.SCREEN_TILE_SIZE if self._direction[1] < 0 else 0)
                self._rect.y -= adjust
            self._tile_y = (self._rect.y - self._map.shift_y) // gv.SCREEN_TILE_SIZE

        if self.is_moving():
            current_time = time.time()
            diff = current_time - self._animation_timer
            if diff >= 1 / (3 * self._speed):
                self._animation_index = (self._animation_index + 1) % self._animation_length
                self._animation_timer = current_time

        self._update_image()

    def go_up(self):
        self._move_to_next_tile(*self.UP)

    def go_down(self):
        self._move_to_next_tile(*self.DOWN)

    def go_left(self):
        self._move_to_next_tile(*self.LEFT)

    def go_right(self):
        self._move_to_next_tile(*self.RIGHT)

    def is_moving(self):
        return self._remaining_x + self._remaining_y != 0

    def _move_to_next_tile(self, tx, ty):
        can_go = self._map.can_go(self._tile_x + tx, self._tile_y + ty)
        if self._remaining_x == 0 and self._remaining_y == 0:
            self._direction = tx, ty
            if can_go:
                self._remaining_x = abs(tx) * gv.SCREEN_TILE_SIZE
                self._remaining_y = abs(ty) * gv.SCREEN_TILE_SIZE
        self._update_image()

    def _update_image(self):
        if self.is_moving():
            self._image = self._frames[self._direction][self._animation_index]
        else:
            self._image = self._idle_frames[self._direction]
        self._image.get_rect().x = self._rect.x
        self._image.get_rect().y = self._rect.y
