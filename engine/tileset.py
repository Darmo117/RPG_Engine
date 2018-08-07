import os
import typing as typ

import pygame

from engine import constants

_TILESETS = {}
_SPRITE_SHEETS = {}


def load_textures():
    _load_tilesets()
    _load_sprite_sheets()


def _load_tilesets():
    path = constants.TILESETS_DIR
    for tileset in os.listdir(path):
        if tileset.endswith(".png"):
            _TILESETS[os.path.splitext(tileset)[0]] = pygame.image.load(os.path.join(path, tileset)).convert_alpha()


def _load_sprite_sheets():
    path = constants.SPRITES_DIR
    for sprite_sheet in os.listdir(path):
        if sprite_sheet.endswith(".png"):
            _SPRITE_SHEETS[os.path.splitext(sprite_sheet)[0]] = pygame.image.load(
                os.path.join(path, sprite_sheet)).convert_alpha()


def get_tile(index: int, tileset: str):
    return _get_texture(index, constants.TILE_SIZE, constants.TILE_SIZE, _TILESETS, tileset)


def get_sprite(index: int, width: int, height: int, sprite_sheet: str):
    return _get_texture(index, width, height, _SPRITE_SHEETS, sprite_sheet)


def _get_texture(index: int, width: int, height: int, textures: typ.Dict[str, pygame.Surface], sheet_name: str):
    # noinspection PyArgumentList
    image = pygame.Surface([width, height], pygame.SRCALPHA).convert_alpha()
    sheet = textures[sheet_name]
    pixel_index = index * width
    x = pixel_index % sheet.get_rect().width
    y = height * (pixel_index // sheet.get_rect().width)
    image.blit(sheet, (0, 0), (x, y, width, height))
    return pygame.transform.scale(image, (width * constants.SCALE, height * constants.SCALE))
