import pygame

from engine import constants


class Tileset:
    """Class used to cut images out of a sprite sheet."""

    def __init__(self, file: str):
        self._tileset = pygame.image.load(file).convert()

    def get_image(self, x: int, y: int, width: int, height: int):
        """Grabs a single image out of the tileset."""
        # noinspection PyArgumentList
        image = pygame.Surface([width, height]).convert()
        image.blit(self._tileset, (0, 0), (x, y, width, height))
        return pygame.transform.scale(image, (constants.SCREEN_TILE_SIZE, constants.SCREEN_TILE_SIZE))
