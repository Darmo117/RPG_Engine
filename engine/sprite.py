import typing as typ

import pygame

from engine import constants


class Sprite(pygame.sprite.Sprite):
    """Base class for all sprites."""

    def __init__(self, tile_x: int, tile_y: int, image: pygame.Surface):
        super().__init__()
        self._image = image
        self._rect = pygame.Rect(tile_x * constants.SCREEN_TILE_SIZE, tile_y * constants.SCREEN_TILE_SIZE,
                                 image.get_rect().width, image.get_rect().height)
        self._tile_x = tile_x
        self._tile_y = tile_y

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect.copy()

    @property
    def position(self) -> typ.Tuple[int, int]:
        return self._rect.x, self._rect.y

    @property
    def tile_position(self):
        return self._tile_x, self._tile_y

    def translate(self, tx, ty):
        self._rect.x += tx
        self._rect.y += ty
        self._image.get_rect().x += tx
        self._image.get_rect().y += ty
