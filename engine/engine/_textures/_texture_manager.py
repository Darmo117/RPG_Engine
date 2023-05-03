import configparser
import logging
import os

import pygame

from .. import _constants


class TexturesManager:
    DEFAULT_FONT_COLOR = pygame.Color(255, 255, 255)
    DISABLED_FONT_COLOR = pygame.Color(128, 128, 128)

    def __init__(self, font: pygame.font.Font):
        """Create a texture manager.

        :param font: The font to use for all texts.
        """
        self._font = font
        self._tilesets = {}
        self._sprite_sheets = {}
        self._logger = logging.getLogger('Textures Manager')
        self._logger.debug('Loading textures…')
        self._load_tilesets()
        self._load_sprite_sheets()
        self._menu_box_texture = pygame.image.load(_constants.MENUS_TEX_DIR / 'menu_box.png').convert_alpha()
        self._logger.debug('Done.')

    def _load_tilesets(self):
        self._logger.debug('Loading tilesets…')
        with (_constants.TILESETS_DIR / _constants.TILESETS_INDEX_FILE_NAME).open(encoding='UTF-8') as f:
            # Add dummy section for parser
            content = '[Tilesets]\n' + f.read()
        parser = configparser.ConfigParser()
        parser.read_string(content)

        for ident, tileset in parser['Tilesets'].items():
            if not tileset.endswith('.png'):
                raise ValueError('Tileset file is not PNG image!')
            ident = int(ident)
            if ident in self._tilesets:
                raise ValueError(f'Duplicate tileset ID: {ident}')
            self._tilesets[ident] = pygame.image.load(_constants.TILESETS_DIR / tileset).convert_alpha()
        self._logger.debug('Loaded tilesets.')

    def _load_sprite_sheets(self):
        self._logger.debug('Loading sprite sheets…')
        for sprite_sheet in _constants.SPRITES_DIR.glob('*'):
            if sprite_sheet.name.endswith('.png'):
                name = os.path.splitext(sprite_sheet.name)[0]
                self._sprite_sheets[name] = pygame.image.load(sprite_sheet).convert_alpha()
        self._logger.debug('Loaded sprite sheets.')

    @property
    def font(self) -> pygame.font.Font:
        return self._font

    def render_text(self, text: str, color: pygame.Color = DEFAULT_FONT_COLOR) -> pygame.Surface:
        return self._font.render(text, True, color)

    def get_tile(self, index: int, tileset: int):
        size = _constants.TILE_SIZE
        return self._get_texture(index, (size, size), self._tilesets, tileset)

    def get_sprite(self, index: int, size: tuple[int, int], sprite_sheet: str):
        return self._get_texture(index, size, self._sprite_sheets, sprite_sheet)

    def get_menu_texture(self, position: tuple[int, int], size: tuple[int, int]):
        image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        image.blit(self._menu_box_texture, (0, 0), (*position, *size))
        scale = _constants.SCALE
        return pygame.transform.scale(image, (size[0] * scale, size[1] * scale))

    @staticmethod
    def _get_texture(index: int, size: tuple[int, int], textures: dict[str | int, pygame.Surface],
                     sheet_name: str | int):
        image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        sheet = textures[sheet_name]
        pixel_index = index * size[0]
        x = pixel_index % sheet.get_rect().width
        y = size[1] * (pixel_index // sheet.get_rect().width)
        image.blit(sheet, (0, 0), (x, y, *size))
        scale = _constants.SCALE
        return pygame.transform.scale(image, (size[0] * scale, size[1] * scale))

    @staticmethod
    def fill_gradient(surface: pygame.Surface, start_color: pygame.Color, end_color: pygame.Color,
                      rect: pygame.Rect = None, horizontal: bool = True, alpha: bool = False):
        """
        Fills a surface with a gradient pattern.

        :param surface: Surface to fill.
        :param start_color: Starting color.
        :param end_color: Final color.
        :param rect: Area to fill; default is surface's rect.
        :param horizontal: True for horizontal; False for vertical.
        :param alpha: If True result will have same alpha as end color; else result will be opaque.

        Source: http://www.pygame.org/wiki/GradientCode
        """
        if rect is None:
            rect = surface.get_rect()
        x1, x2 = rect.left, rect.right
        y1, y2 = rect.top, rect.bottom
        if horizontal:
            h = x2 - x1
        else:
            h = y2 - y1
        rate = (
            float(end_color.r - start_color.r) / h,
            float(end_color.g - start_color.g) / h,
            float(end_color.b - start_color.b) / h,
        )
        if horizontal:
            for col in range(x1, x2):
                start_color = (
                    min(max(start_color.r + (rate[0] * (col - x1)), 0), 255),
                    min(max(start_color.g + (rate[1] * (col - x1)), 0), 255),
                    min(max(start_color.b + (rate[2] * (col - x1)), 0), 255),
                    end_color.a if alpha else 255
                )
                pygame.draw.line(surface, start_color, (col, y1), (col, y2))
        else:
            for line in range(y1, y2):
                start_color = (
                    min(max(start_color.r + (rate[0] * (line - y1)), 0), 255),
                    min(max(start_color.g + (rate[1] * (line - y1)), 0), 255),
                    min(max(start_color.b + (rate[2] * (line - y1)), 0), 255),
                    end_color.a if alpha else 255
                )
                pygame.draw.line(surface, start_color, (x1, line), (x2, line))

    @staticmethod
    def alpha_gradient(surface: pygame.Surface, color: pygame.Color, start_alpha: int, end_alpha: int,
                       rect: pygame.Rect = None, horizontal: bool = True):
        """
        Fills a surface with a gradient pattern.

        :param surface: Surface to fill.
        :param color: Base color.
        :param start_alpha: Start alpha value.
        :param end_alpha: Final alpha value.
        :param rect: Area to fill; default is surface's rect.
        :param horizontal: True for horizontal; False for vertical.
        """
        if rect is None:
            rect = surface.get_rect()
        x1, x2 = rect.left, rect.right
        y1, y2 = rect.top, rect.bottom
        if horizontal:
            h = x2 - x1
        else:
            h = y2 - y1
        rate = (end_alpha - start_alpha) / h
        if horizontal:
            for col in range(x1, x2):
                c = (color.r, color.g, color.b, min(max(start_alpha + (rate * (col - x1)), 0), 255))
                pygame.draw.line(surface, c, (col, y1), (col, y2))
        else:
            for line in range(y1, y2):
                c = (color.r, color.g, color.b, min(max(start_alpha + (rate * (line - y1)), 0), 255))
                pygame.draw.line(surface, c, (x1, line), (x2, line))


__all__ = [
    'TexturesManager',
]
