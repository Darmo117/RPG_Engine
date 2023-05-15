from __future__ import annotations

import dataclasses
import gzip
import time
import typing as _typ

import pygame

from . import interactions as inter
from .. import constants, entities, events, io, render, scene
from ..render import util as _rutil
from ..screens import components as _comp, texts, screens


class LevelLoader:
    def __init__(self, engine):
        """Create a level loader.

        :param engine: The game engine.
        :type engine: engine.game_engine.GameEngine
        """
        self._engine = engine

    def load_level(self, name: str) -> Level:
        with gzip.open(constants.MAPS_DIR / f'{name}.map', mode='rb') as f:
            buffer = io.ByteBuffer(f.read())
        version = buffer.read_int(signed=False)  # Future-proofing
        if version != 1:
            raise ValueError(f'unrecognized level file version {version}')
        width = buffer.read_short(signed=False)
        height = buffer.read_short(signed=False)
        bg_color = pygame.Color(
            buffer.read_byte(signed=False),
            buffer.read_byte(signed=False),
            buffer.read_byte(signed=False)
        )
        entity_layer = buffer.read_byte(signed=False)
        tiles = self._load_tiles(buffer, width, height)
        interactions = self._load_interactions(buffer, width, height)
        return Level(
            self._engine,
            name,
            width,
            height,
            tiles,
            interactions,
            entity_layer,
            bg_color
        )

    @staticmethod
    def _load_tiles(buffer: io.ByteBuffer, width: int, height: int) -> list[list[list[Tile]]]:
        layers_nb = buffer.read_byte(signed=False)
        layers = []
        for layer in range(layers_nb):
            layers.append([])
            for y in range(height):
                layers[layer].append([None] * width)
                for x in range(width):
                    tileset_id = buffer.read_short(signed=False)
                    tile_id = buffer.read_short(signed=False)
                    if tileset_id > 0:
                        layers[layer][y][x] = Tile(tileset_id, tile_id)
        return layers

    def _load_interactions(self, buffer: io.ByteBuffer, width: int, height: int) \
            -> list[list[inter.TileInteraction]]:
        interactions = []
        for y in range(height):
            interactions.append([])
            for x in range(width):
                interactions[y].append(self._read_interaction(buffer))
        return interactions

    @staticmethod
    def _read_interaction(buffer: io.ByteBuffer):
        match buffer.read_byte(signed=False):
            case 1:
                return inter.WALL_INTERACTION
            case 2:
                return inter.ChangeLevelInteraction(
                    buffer.read_string(),
                    buffer.read_vector(as_ints=True),
                    buffer.read_byte(signed=False),
                    buffer.read_bool()
                )
            case 3:
                return inter.HurtEntityInteraction(buffer.read_double())
            case _:
                return inter.NO_INTERACTION


class Level(scene.Scene):
    def __init__(self,
                 game_engine,
                 name: str,
                 width: int,
                 height: int,
                 tiles: list[list[list[Tile]]],
                 interactions: list[list[inter.TileInteraction]],
                 entity_layer: int,
                 bg_color: pygame.Color
                 ):
        """Create a level.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param name: Level’s internal name.
        :param width: Level’s horizontal size.
        :param height: Level’s vertical size.
        :param tiles: List of tile layers.
        :param interactions: 2D grid of interactions for each tile position.
        :param entity_layer: Index of the layer on which to render entities.
        :param bg_color: The background color.
        """
        super().__init__()
        self._game_engine = game_engine
        self._width = width
        self._height = height
        self._tiles = tiles
        self._interactions = interactions
        self._entity_layer = entity_layer
        self._background_color = bg_color
        self._camera_pos = pygame.Vector2()
        self._controls_enabled = True

        self._player = None
        self._entities: set[entities.Entity] = set()

        self._title_label = _LevelNameLabel(
            game_engine.texture_manager,
            game_engine.config.active_language.translate(f'level.{name}.name')
        )
        self._title_label.x = 6
        self._title_label.y = 12

    @property
    def game_engine(self):
        """The game engine.

        :rtype: engine.game_engine.GameEngine"""
        return self._game_engine

    def spawn_player(self, at: pygame.Vector2):
        if self._player:
            raise RuntimeError('player entity already exists')
        self._player = entities.PlayerEntity('Character', self)
        self._player.position = at
        self._entities.add(self._player)

    def spawn_entity(self, supplier: _typ.Callable[[Level], entities.Entity], at: pygame.Vector2):
        entity = supplier(self)
        entity.position = at
        self._entities.add(entity)

    def on_input_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # TODO display menu
            self._game_engine.fire_event(events.GoToScreenEvent(screens.TitleScreen(self._game_engine)))
        else:
            super().on_input_event(event)

    def update(self):
        super().update()
        self._poll_events()
        for entity in self._entities:
            entity.update()
        self._title_label.update()

    def _poll_events(self):
        up, down, left, right = io.are_keys_pressed(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
        if up:
            self._player.go_up()
        elif down:
            self._player.go_down()
        if left:
            self._player.go_left()
        elif right:
            self._player.go_right()

    def _update_camera_position(self):
        w = self._width * constants.SCREEN_TILE_SIZE
        h = self._height * constants.SCREEN_TILE_SIZE
        ww, wh = self._game_engine.window_size
        player_pos = self._player.position
        if w <= ww:
            self._camera_pos.x = (w - ww) / 2
        else:
            self._camera_pos.x = (player_pos.x + 0.5) * constants.SCREEN_TILE_SIZE - ww / 2
        if h <= wh:
            self._camera_pos.y = (h - wh) / 2
        else:
            self._camera_pos.y = (player_pos.y + 0.5) * constants.SCREEN_TILE_SIZE - wh / 2

    def draw(self, screen: pygame.Surface):
        self._update_camera_position()
        screen.fill(self._background_color)
        # Render layers and entities
        for layer in range(len(self._tiles)):
            for y in range(self._height):
                for x in range(self._width):
                    tile = self.get_tile(layer, x, y)
                    pos = pygame.Vector2(x, y)
                    # Culling
                    size = pygame.Vector2(constants.SCREEN_TILE_SIZE, constants.SCREEN_TILE_SIZE)
                    if tile and self.is_rect_visible(screen, self._screen_pos(pos), size):
                        self._draw_tile(tile, pos, screen)
            if layer == self._entity_layer:
                for entity in self._entities:
                    # Culling
                    if self.is_rect_visible(screen, self._screen_pos(entity.position), entity.size * constants.SCALE):
                        self._draw_entity(entity, screen)
        # Render level name label
        if self._title_label.visible:
            self._title_label.draw(screen)

    def is_rect_visible(self, screen: pygame.Surface, pos: pygame.Vector2, size: pygame.Vector2) -> bool:
        w, h = screen.get_size()
        return -size[0] <= pos.x <= w and -size[1] <= pos.y <= h

    def _draw_tile(self, tile: Tile, pos: pygame.Vector2, screen: pygame.Surface):
        texture = self._game_engine.texture_manager.get_tile(tile.tile_id, tile.tileset_id)
        screen.blit(texture, self._screen_pos(pos))

    def _draw_entity(self, entity: entities.Entity, screen: pygame.Surface):
        screen.blit(entity.get_texture(), self._screen_pos(entity.position))

    def get_tile(self, layer: int, x: int, y: int):
        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            raise IndexError(f'({x}, {y})')
        return self._tiles[layer][y][x]

    def get_tile_interaction(self, x: int, y: int):
        if x < 0 or y < 0 or x >= self._width or y >= self._height:
            return inter.WALL_INTERACTION
        return self._interactions[y][x]

    def _screen_pos(self, pos: pygame.Vector2) -> pygame.Vector2:
        return pos * constants.SCREEN_TILE_SIZE - self._camera_pos


class _LevelNameLabel(_comp.Component):
    def __init__(self, texture_manager: render.TexturesManager, title: str):
        super().__init__(texture_manager)
        self._label = texts.parse_line(title)
        self._gradient_width = 30
        self._title_timer = None
        self._visible = False
        self.w, self.h = self._label.get_size(texture_manager)
        self._update_image()

    @property
    def visible(self) -> bool:
        return self._visible

    def update(self):
        if self._title_timer is None:
            self._title_timer = time.time()
        else:
            self._visible = 0.5 <= time.time() - self._title_timer <= 3

    def _draw(self) -> pygame.Surface:
        return self._image

    def _update_image(self):
        size = self._label.get_size(self._tm)
        alpha = 128
        image = pygame.Surface(size, pygame.SRCALPHA, 32)
        image.fill((0, 0, 0, alpha))
        self._label.draw(self._tm, image, (0, 0))

        w, h = size
        self._image = pygame.Surface((w + 2 * self._gradient_width, h), pygame.SRCALPHA, 32)
        _rutil.alpha_gradient(self._image, pygame.Color(0, 0, 0), 0, alpha,
                              rect=pygame.Rect(0, 0, self._gradient_width, h))
        _rutil.alpha_gradient(self._image, pygame.Color(0, 0, 0), alpha, 0,
                              rect=pygame.Rect(w + self._gradient_width, 0, self._gradient_width, h))
        self._image.blit(image, (self._gradient_width, 0))


@dataclasses.dataclass(frozen=True)
class Tile:
    tileset_id: int
    tile_id: int


__all__ = [
    'Level',
    'LevelLoader',
]
