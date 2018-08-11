import configparser as cp
import logging
import os
import typing as typ

import pygame

from engine import global_values as gv, types as tp


class TexturesManager:
    _LOGGER = logging.getLogger(__name__ + ".TexturesManager")

    FONT_COLOR = (255, 255, 255, 255)

    def __init__(self, font):
        self._font = font
        self._tilesets = {}
        self._sprite_sheets = {}
        self._dialog_box = None
        self._LOGGER.debug("Loading textures...")
        self._load_tilesets()
        self._load_sprite_sheets()
        self._dialog_box = pygame.image.load(os.path.join(gv.MENUS_DIR, "menu_box.png")).convert_alpha()
        self._LOGGER.debug("Loaded textures.")

    def _load_tilesets(self):
        self._LOGGER.debug("Loading tilesets...")
        with open(os.path.join(gv.TILESETS_DIR, gv.TILESETS_INDEX_FILE)) as f:
            # Add dummy section for parser
            content = "[Tilesets]\n" + f.read()
        parser = cp.ConfigParser()
        parser.read_string(content)

        for ident, tileset in parser["Tilesets"].items():
            if not tileset.endswith(".png"):
                raise ValueError("Tileset file is not PNG image!")
            ident = int(ident)
            if ident in self._tilesets:
                raise ValueError(f"Duplicate ID {ident}!")
            self._tilesets[ident] = pygame.image.load(os.path.join(gv.TILESETS_DIR, tileset)).convert_alpha()
        self._LOGGER.debug("Loaded tilesets.")

    def _load_sprite_sheets(self):
        self._LOGGER.debug("Loading sprite sheets...")
        path = gv.SPRITES_DIR
        for sprite_sheet in os.listdir(path):
            if sprite_sheet.endswith(".png"):
                self._sprite_sheets[os.path.splitext(sprite_sheet)[0]] = pygame.image.load(
                    os.path.join(path, sprite_sheet)).convert_alpha()
        self._LOGGER.debug("Loaded sprite sheets.")

    @property
    def font(self):
        return self._font

    def render_text(self, text: str, color: tp.Color = FONT_COLOR) -> pygame.Surface:
        return self._font.render(text, True, color)

    def get_tile(self, index: int, tileset: int):
        return self._get_texture(index, (gv.TILE_SIZE, gv.TILE_SIZE), self._tilesets, tileset)

    def get_sprite(self, index: int, size: tp.Dimension, sprite_sheet: str):
        return self._get_texture(index, size, self._sprite_sheets, sprite_sheet)

    def get_menu_texture(self, position: tp.Position, size: tp.Dimension):
        # noinspection PyArgumentList
        image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        image.blit(self._dialog_box, (0, 0), (*position, *size))
        return pygame.transform.scale(image, (size[0] * gv.SCALE, size[1] * gv.SCALE))

    @staticmethod
    def _get_texture(index: int, size: tp.Dimension, textures: typ.Dict[typ.Union[str, int], pygame.Surface],
                     sheet_name: typ.Union[str, int]):
        # noinspection PyArgumentList
        image = pygame.Surface(size, pygame.SRCALPHA).convert_alpha()
        sheet = textures[sheet_name]
        pixel_index = index * size[0]
        x = pixel_index % sheet.get_rect().width
        y = size[1] * (pixel_index // sheet.get_rect().width)
        image.blit(sheet, (0, 0), (x, y, *size))
        return pygame.transform.scale(image, (size[0] * gv.SCALE, size[1] * gv.SCALE))

    @staticmethod
    def fill_gradient(surface: pygame.Surface, start_color: tp.Color, end_color: tp.Color, rect: pygame.Rect = None,
                      horizontal=True, alpha=False):
        """
        Fills a surface with a gradient pattern.

        :param surface: Surface to fill.
        :param start_color: Starting color.
        :param end_color: Final color.
        :param rect: Area to fill; default is surface's rect.
        :param horizontal: True for horizontal; False for vertical.
        :param alpha: If True result will have same alpha as gradient argument; else result will be opaque.

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
            float(end_color[0] - start_color[0]) / h,
            float(end_color[1] - start_color[1]) / h,
            float(end_color[2] - start_color[2]) / h,
            end_color[3] if alpha else 0
        )
        draw_line = pygame.draw.line
        if horizontal:
            for col in range(x1, x2):
                start_color = (
                    min(max(start_color[0] + (rate[0] * (col - x1)), 0), 255),
                    min(max(start_color[1] + (rate[1] * (col - x1)), 0), 255),
                    min(max(start_color[2] + (rate[2] * (col - x1)), 0), 255),
                    end_color[3] if alpha else 255
                )
                draw_line(surface, start_color, (col, y1), (col, y2))
        else:
            for line in range(y1, y2):
                start_color = (
                    min(max(start_color[0] + (rate[0] * (line - y1)), 0), 255),
                    min(max(start_color[1] + (rate[1] * (line - y1)), 0), 255),
                    min(max(start_color[2] + (rate[2] * (line - y1)), 0), 255),
                    end_color[3] if alpha else 255
                )
                draw_line(surface, start_color, (x1, line), (x2, line))

    @staticmethod
    def alpha_gradient(surface: pygame.Surface, color: tp.Color, start_alpha: int, end_alpha: int,
                       rect: pygame.Rect = None, horizontal=True):
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
        rate = float(end_alpha - start_alpha) / h
        if horizontal:
            for col in range(x1, x2):
                c = (*color[:3], min(max(start_alpha + (rate * (col - x1)), 0), 255))
                pygame.draw.line(surface, c, (col, y1), (col, y2))
        else:
            for line in range(y1, y2):
                c = (*color[:3], min(max(start_alpha + (rate * (line - y1)), 0), 255))
                pygame.draw.line(surface, c, (x1, line), (x2, line))
