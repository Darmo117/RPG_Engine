import typing as typ

import pygame


class Sprite(pygame.sprite.Sprite):
    """Base class for all sprites."""

    def __init__(self):
        self._image: pygame.Surface = None
        self._rect: pygame.Rect = None

    @property
    def image(self) -> pygame.Surface:
        return self._image

    @property
    def rect(self) -> pygame.Rect:
        return self._rect.copy()

    @property
    def position(self) -> typ.Tuple[int, int]:
        return self._rect.x, self._rect.y
