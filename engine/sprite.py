import typing as typ

import pygame

from engine import global_values as gv


class Sprite(pygame.sprite.Sprite):
    """Base class for all sprites."""

    def __init__(self, x: int, y: int, image: pygame.Surface):
        super().__init__()
        self._image = image
        self._rect = pygame.Rect(x, y, image.get_rect().width, image.get_rect().height)

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect.copy()

    @property
    def position(self) -> typ.Tuple[int, int]:
        return self._rect.x, self._rect.y

    def translate(self, tx, ty):
        self._rect.x += tx
        self._rect.y += ty
        self._image.get_rect().x += tx
        self._image.get_rect().y += ty


class TileSprite(Sprite):
    """Base class for tile-based sprites."""

    def __init__(self, tile_x: int, tile_y: int, image: pygame.Surface):
        super().__init__(tile_x * gv.SCREEN_TILE_SIZE, tile_y * gv.SCREEN_TILE_SIZE, image)
        self._tile_x = tile_x
        self._tile_y = tile_y

    @property
    def tile_position(self):
        return self._tile_x, self._tile_y
