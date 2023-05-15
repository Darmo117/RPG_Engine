import collections
import json
import logging
import os

import pygame

from .. import constants


class TexturesManager:
    DEFAULT_FONT_COLOR = pygame.Color(255, 255, 255)
    DISABLED_FONT_COLOR = pygame.Color(128, 128, 128)

    NORMAL = 0
    ITALICS = 1
    BOLD = 2
    UNDERLINED = 4
    STRIKETHROUGH = 8

    def __init__(self, font: pygame.font.Font):
        """Create a texture manager.

        :param font: The font to use for all texts.
        """
        size = constants.TILE_SIZE
        self._missing_texture = pygame.Surface((size, size))
        magenta = (255, 0, 255)
        black = (0, 0, 0)
        self._missing_texture.fill(magenta, (0, 0, size // 2, size // 2))
        self._missing_texture.fill(magenta, (size // 2, size // 2, size // 2, size // 2))
        self._missing_texture.fill(black, (size // 2, 0, size // 2, size // 2))
        self._missing_texture.fill(black, (size // 2, 0, size // 2, size // 2))

        self._font = font
        self._tilesets: dict[int, tuple[pygame.Surface, int]] = collections.defaultdict(
            lambda: (self._missing_texture, size))
        self._sprite_sheets: dict[str, tuple[pygame.Surface, tuple[int, int], int]] = collections.defaultdict(
            lambda: (self._missing_texture, (size, size), 1))
        self._logger = logging.getLogger('Textures Manager')
        self._logger.debug('Loading textures…')
        self._load_tilesets()
        self._load_sprite_sheets()
        self._menu_box_texture = pygame.image.load(constants.MENUS_TEX_DIR / 'menu_box.png').convert_alpha()
        self._logger.debug('Done.')

    def _load_tilesets(self):
        self._logger.debug('Loading tilesets…')
        with (constants.TILESETS_DIR / constants.TILESETS_INDEX_FILE_NAME).open(encoding='UTF-8') as f:
            tilesets = json.load(f)

        for i, tileset in enumerate(tilesets):
            textures = pygame.image.load(constants.TILESETS_DIR / tileset).convert_alpha()
            with (constants.TILESETS_DIR / (tileset + '.json')).open(mode='r') as f:
                resolution = int(json.load(f)['resolution'])
            self._tilesets[i + 1] = (textures, resolution)
        self._logger.debug('Loaded tilesets.')

    def _load_sprite_sheets(self):
        self._logger.debug('Loading sprite sheets…')
        for sprite_sheet in constants.SPRITES_DIR.glob('*.png'):
            if sprite_sheet.is_file():
                name = os.path.splitext(sprite_sheet.name)[0]
                textures = pygame.image.load(sprite_sheet).convert_alpha()
                with (sprite_sheet.parent / (sprite_sheet.name + '.json')).open(mode='r') as f:
                    json_data = json.load(f)
                res = json_data['resolution']
                resolution = (int(res[0]), int(res[1]))
                frames = textures.get_width() // resolution[0] - 1  # First column is idle frame
                self._sprite_sheets[name] = (textures, resolution, frames)
        self._logger.debug('Loaded sprite sheets.')

    @property
    def font(self) -> pygame.font.Font:
        return self._font

    def render_text(self, text: str, color: pygame.Color = DEFAULT_FONT_COLOR, style: int = NORMAL) -> pygame.Surface:
        self._font.set_italic((style & self.ITALICS) != 0)
        self._font.set_bold((style & self.BOLD) != 0)
        self._font.set_underline((style & self.UNDERLINED) != 0)
        self._font.set_strikethrough((style & self.STRIKETHROUGH) != 0)
        text = self._font.render(text, True, color)
        self._font.set_italic(False)
        self._font.set_bold(False)
        self._font.set_underline(False)
        self._font.set_strikethrough(False)
        return text

    def get_tile(self, index: int, tileset: int) -> pygame.Surface:
        size = self._tilesets[tileset][1]
        return self._get_texture(index, self._tilesets[tileset][0], (size, size))

    def get_sprite(self, index: int, sprite_sheet: str) -> pygame.Surface:
        sheet_data = self._sprite_sheets[sprite_sheet]
        return self._get_texture(index, sheet_data[0], sheet_data[1])

    def get_sprite_size(self, sprite_sheet: str) -> tuple[int, int]:
        return self._sprite_sheets[sprite_sheet][1]

    def get_sprite_frames(self, sprite_sheet: str) -> int:
        return self._sprite_sheets[sprite_sheet][2]

    def get_menu_texture(self, position: tuple[int, int], size: tuple[int, int]) -> pygame.Surface:
        image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        image.blit(self._menu_box_texture, (0, 0), (*position, *size))
        scale = constants.SCALE
        return pygame.transform.scale(image, (size[0] * scale, size[1] * scale))

    def _get_texture(self, index: int, sheet: pygame.Surface, size: tuple[int, int]) -> pygame.Surface:
        image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        w, h = size
        sw = sheet.get_size()[0] // w
        sh = sheet.get_size()[1] // h
        x = index % sw
        y = (index // sw) % sh
        image.blit(sheet, (0, 0), (x * w, y * h, *size))
        scale = constants.SCALE
        return pygame.transform.scale(image, (w * scale, h * scale))


__all__ = [
    'TexturesManager',
]
