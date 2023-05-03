import pickle
import time

import pygame
import pygame.sprite as _psp

from . import _triggers
from .. import _constants, _entities, _events, _scene, _textures, _utils
from .._screens import components as _comp


class Map(_scene.Scene):
    def __init__(self, game_engine, name: str, start_door_id: int = None):
        """Create a map.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        :param name: Map’s internal name.
        :param start_door_id: ID of the door where to spawn the player at.
        """
        super().__init__()
        self._game_engine = game_engine
        self._player = _entities.PlayerEntity('Character', self)
        self._player.map = self

        with (_constants.MAPS_DIR / (name + '.map')).open(mode='rb') as f:
            raw_data = pickle.load(f)
        width, height = map(int, raw_data['size'])
        self._background_color = raw_data['background_color']
        if start_door_id is None:
            self._player.set_position(*raw_data['start'])
        self._rect = pygame.Rect(0, 0, width * _constants.SCREEN_TILE_SIZE, height * _constants.SCREEN_TILE_SIZE)

        def load_layer(group, layer_name):
            layers = raw_data['layers']
            if layer_name in layers:
                for y in range(height):
                    for x in range(width):
                        if layers[layer_name][y][x] is not None:
                            tile_index, tileset = layers[layer_name][y][x]
                            texture = self._game_engine.texture_manager.get_tile(int(tile_index), int(tileset))
                            tile = _textures.TileSprite(x, y, texture)
                            if tile is not None:
                                group.add(tile)

        self._background_tiles_list = _psp.Group()
        load_layer(self._background_tiles_list, 'bg')
        self._background2_tiles_list = _psp.Group()
        load_layer(self._background2_tiles_list, 'bg2')
        self._main_tiles_list = _psp.Group()
        load_layer(self._main_tiles_list, 'main')
        self._foreground_tiles_list = _psp.Group()
        load_layer(self._foreground_tiles_list, 'fg')

        self._walls = raw_data['walls']
        self._doors = {}
        for door in raw_data['doors']:
            ident = door['id']
            pos = door['position']
            dest = door['destination']
            if dest:
                self._doors[pos] = _triggers.Door(ident, pos[0], pos[1], door['state'], destination_map=dest['map'],
                                                  destination_door_id=dest['door'])
            else:
                self._doors[pos] = _triggers.Door(ident, pos[0], pos[1], door['state'])
            if start_door_id == ident:
                self._player.set_position(*self._doors[pos].position)

        self._entities_list = _psp.Group()
        # noinspection PyTypeChecker
        self._entities_list.add(self._player)

        w, h = game_engine.window_size
        if self._rect.width < w:
            self.translate((w - self._rect.width) // 2, 0, player=True)
        if self._rect.height < h:
            self.translate(0, (h - self._rect.height) // 2, player=True)

        self._title_label = _MapTitleLabel(
            game_engine.texture_manager,
            game_engine.config.active_language.translate(name)
        )
        self._title_label.x = 6
        self._title_label.y = 12

    @property
    def shift_x(self) -> int:
        return self._rect.x

    @property
    def shift_y(self) -> int:
        return self._rect.y

    @property
    def player(self) -> _entities.PlayerEntity:
        return self._player

    @property
    def game_engine(self):
        """
        :rtype: engine.engine.GameEngine
        """
        return self._game_engine

    def on_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # TODO display menu
            self._game_engine.stop()  # TODO temp
        else:
            super().on_event(event)

    def update(self) -> _events.Event | None:
        super().update()
        previous_player_pos = self._player.tile_position
        self._entities_list.update()
        self._title_label.update()

        if self._controls_enabled:
            self._events()
        self._translate_screen()

        player_pos = self._player.tile_position
        if previous_player_pos != player_pos and player_pos in self._doors:
            door = self._doors[player_pos]
            if self._controls_enabled and door.open:
                next_map = Map(self._game_engine, door.destination_map, start_door_id=door.id)
                return _events.LoadSceneEvent(next_map)
        return None

    def _events(self):
        up, down, left, right = _utils.are_keys_pressed(pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT)
        if up:
            self._player.go_up()
        elif down:
            self._player.go_down()
        if left:
            self._player.go_left()
        elif right:
            self._player.go_right()

    def _translate_screen(self):
        w, h = self._game_engine.window_size

        if self._rect.top < 0:
            top_limit = (h - _constants.SCREEN_TILE_SIZE) // 2
            if self._player.top < top_limit:
                diff = top_limit - self._player.top
                self._player.top = top_limit
                self.translate(0, diff)

        if self._rect.bottom > h:
            bottom_limit = (h + _constants.SCREEN_TILE_SIZE) // 2
            if self._player.bottom > bottom_limit:
                diff = self._player.bottom - bottom_limit
                self._player.bottom = bottom_limit
                self.translate(0, -diff)

        if self._rect.left < 0:
            left_limit = (w - _constants.SCREEN_TILE_SIZE) // 2
            if self._player.left < left_limit:
                diff = left_limit - self._player.left
                self._player.left = left_limit
                self.translate(diff, 0)

        if self._rect.right > w:
            right_limit = (w + _constants.SCREEN_TILE_SIZE) // 2
            if self._player.right > right_limit:
                diff = self._player.right - right_limit
                self._player.right = right_limit
                self.translate(-diff, 0)

    def draw(self, screen: pygame.Surface):
        screen.fill(self._background_color)
        self._background_tiles_list.draw(screen)
        self._background2_tiles_list.draw(screen)
        self._main_tiles_list.draw(screen)
        self._entities_list.draw(screen)
        self._foreground_tiles_list.draw(screen)

        if self._title_label.visible:
            self._title_label.draw(screen)

    def translate(self, tx: int, ty: int, player: bool = False):
        self._rect.x += tx
        self._rect.y += ty

        def translate_sprites(group):
            for element in group:
                if player or not isinstance(element, _entities.PlayerEntity):
                    element.translate(tx, ty)

        translate_sprites(self._background_tiles_list)
        translate_sprites(self._background2_tiles_list)
        translate_sprites(self._main_tiles_list)
        translate_sprites(self._foreground_tiles_list)
        translate_sprites(self._entities_list)

    def can_go(self, x: int, y: int) -> bool:
        """Checks if it is possible to go to a specific tile."""
        try:
            return (0 <= x < self._rect.width // _constants.SCREEN_TILE_SIZE
                    and 0 <= y < self._rect.height // _constants.SCREEN_TILE_SIZE
                    and self._walls[y][x] == 0)
        except IndexError:
            return False


class _MapTitleLabel(_comp.Component):
    def __init__(self, texture_manager: _textures.TexturesManager, title: str):
        super().__init__(texture_manager)
        self._label = texture_manager.render_text(title)
        self._gradient_width = 30
        self._title_timer = None
        self._visible = False
        self.w = self._label.get_rect().width
        self.h = self._label.get_rect().height
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
        alpha = 128
        text = pygame.Surface(self._label.get_rect().size, pygame.SRCALPHA, 32)
        text.fill((0, 0, 0, alpha))
        text.blit(self._label, (0, 0))

        w, h = self._label.get_rect().size
        self._image = pygame.Surface((w + 2 * self._gradient_width, h), pygame.SRCALPHA, 32)
        self._tm.alpha_gradient(self._image, pygame.Color(0, 0, 0), 0, alpha,
                                rect=pygame.Rect(0, 0, self._gradient_width, h))
        self._tm.alpha_gradient(self._image, pygame.Color(0, 0, 0), alpha, 0,
                                rect=pygame.Rect(w + self._gradient_width, 0, self._gradient_width, h))
        self._image.blit(text, (self._gradient_width, 0))


__all__ = [
    'Map',
]
