import logging
import os
import pickle
import time
import typing as typ

import pygame
import pygame.sprite as psp

from engine import tiles, global_values as gv, entities, menus, actions


class Map:
    _LOGGER = logging.getLogger(__name__ + ".Map")

    def __init__(self, name: str, start_door_id: int = None):
        self._LOGGER.debug(f"Loading map '{name}...'")
        self._player = entities.Player("Character", self)
        self._player.map = self

        with open(os.path.join(gv.MAPS_DIR, name + ".map"), "rb") as f:
            raw_data = pickle.load(f)
        width, height = map(int, raw_data["size"])
        self._background_color = raw_data["background_color"]
        if start_door_id is None:
            self._player.set_position(*raw_data["start"])
        self._rect = pygame.Rect(0, 0, width * gv.SCREEN_TILE_SIZE, height * gv.SCREEN_TILE_SIZE)

        def load_layer(group, layer_name):
            layers = raw_data["layers"]
            if layer_name in layers:
                for y in range(height):
                    for x in range(width):
                        if layers[layer_name][y][x] is not None:
                            tile_index, tileset = layers[layer_name][y][x]
                            tile = tiles.Tile(x, y, int(tile_index), int(tileset))
                            if tile is not None:
                                group.add(tile)

        self._background_tiles_list = psp.Group()
        load_layer(self._background_tiles_list, "bg")
        self._background2_tiles_list = psp.Group()
        load_layer(self._background2_tiles_list, "bg2")
        self._main_tiles_list = psp.Group()
        load_layer(self._main_tiles_list, "main")
        self._foreground_tiles_list = psp.Group()
        load_layer(self._foreground_tiles_list, "fg")

        self._walls = raw_data["walls"]
        self._doors = {}
        for door in raw_data["doors"]:
            ident = door["id"]
            pos = door["position"]
            dest = door["destination"]
            if dest is not None:
                self._doors[pos] = tiles.Door(ident, pos[0], pos[1], door["state"], destination_map=dest["map"],
                                              destination_door_id=dest["door"])
            else:
                self._doors[pos] = tiles.Door(ident, pos[0], pos[1], door["state"])
            if start_door_id == ident:
                self._player.set_position(*self._doors[pos].position)

        self._entities_list = psp.Group()
        self._player_list = psp.Group()
        self._player_list.add(self._player)

        if self._rect.width < gv.SCREEN_WIDTH:
            self.translate((gv.SCREEN_WIDTH - self._rect.width) // 2, 0, player=True)
        if self._rect.height < gv.SCREEN_HEIGHT:
            self.translate(0, (gv.SCREEN_HEIGHT - self._rect.height) // 2, player=True)

        self._title_label = _MapTitleLabel(gv.I18N.map(name))
        self._controls_enabled = True
        self._LOGGER.debug(f"Loaded map '{name}.'")

    @property
    def shift_x(self) -> int:
        return self._rect.x

    @property
    def shift_y(self) -> int:
        return self._rect.y

    @property
    def player(self) -> entities.Player:
        return self._player

    @property
    def controls_enabled(self) -> bool:
        return self._controls_enabled

    @controls_enabled.setter
    def controls_enabled(self, value: bool):
        self._controls_enabled = value

    # TODO Retourner une action
    def update(self) -> typ.Optional[actions.AbstractAction]:
        """Updates this Map. May return a Map to load."""
        self._entities_list.update()
        previous_player_pos = self._player.tile_position
        self._player_list.update()
        self._title_label.update()

        if self._controls_enabled:
            self._events()
        self._translate_screen()

        player_pos = self._player.tile_position
        if previous_player_pos != player_pos and player_pos in self._doors:
            door = self._doors[player_pos]
            if self._controls_enabled and door.open:
                return actions.LoadMapAction(door.destination_map, door_id=door.id)
        return None

    def _events(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self._player.go_up()
        elif keys[pygame.K_DOWN]:
            self._player.go_down()
        if keys[pygame.K_LEFT]:
            self._player.go_left()
        elif keys[pygame.K_RIGHT]:
            self._player.go_right()

    def _translate_screen(self):
        if self._rect.top < 0:
            top_limit = (gv.SCREEN_HEIGHT - gv.SCREEN_TILE_SIZE) // 2
            if self._player.top < top_limit:
                diff = top_limit - self._player.top
                self._player.top = top_limit
                self.translate(0, diff)

        if self._rect.bottom > gv.SCREEN_HEIGHT:
            bottom_limit = (gv.SCREEN_HEIGHT + gv.SCREEN_TILE_SIZE) // 2
            if self._player.bottom > bottom_limit:
                diff = self._player.bottom - bottom_limit
                self._player.bottom = bottom_limit
                self.translate(0, -diff)

        if self._rect.left < 0:
            left_limit = (gv.SCREEN_WIDTH - gv.SCREEN_TILE_SIZE) // 2
            if self._player.left < left_limit:
                diff = left_limit - self._player.left
                self._player.left = left_limit
                self.translate(diff, 0)

        if self._rect.right > gv.SCREEN_WIDTH:
            right_limit = (gv.SCREEN_WIDTH + gv.SCREEN_TILE_SIZE) // 2
            if self._player.right > right_limit:
                diff = self._player.right - right_limit
                self._player.right = right_limit
                self.translate(-diff, 0)

    def draw(self, screen):
        screen.fill(self._background_color)
        self._background_tiles_list.draw(screen)
        self._background2_tiles_list.draw(screen)
        self._main_tiles_list.draw(screen)
        self._entities_list.draw(screen)
        self._player_list.draw(screen)
        self._foreground_tiles_list.draw(screen)

        if self._title_label.visible:
            self._title_label.draw(screen, (6, 12))

    def translate(self, tx: int, ty: int, player: bool = False):
        self._rect.x += tx
        self._rect.y += ty

        def translate_sprites(group):
            for element in group:
                element.translate(tx, ty)

        translate_sprites(self._background_tiles_list)
        translate_sprites(self._background2_tiles_list)
        translate_sprites(self._main_tiles_list)
        translate_sprites(self._foreground_tiles_list)
        translate_sprites(self._entities_list)

        if player:
            translate_sprites(self._player_list)

    def can_go(self, x: int, y: int) -> bool:
        """Checks if it is possible to go to a specific tile."""
        try:
            return 0 <= x < self._rect.width // gv.SCREEN_TILE_SIZE \
                   and 0 <= y < self._rect.height // gv.SCREEN_TILE_SIZE \
                   and self._walls[y][x] == 0
        except IndexError:
            return False


class _MapTitleLabel(menus.Component):
    def __init__(self, title: str):
        super().__init__(padding=0)
        self._label = gv.TEXTURE_MANAGER.render_text(title)
        self._gradient_width = 30
        self._title_timer = None
        self._visible = False
        self._update_image()

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def size(self) -> typ.Tuple[int, int]:
        return 2 * self._gradient_width + self._label.get_rect().width, self._label.get_rect().height

    def update(self):
        if self._title_timer is None:
            self._title_timer = time.time()
        else:
            self._visible = 0.5 <= time.time() - self._title_timer <= 3

    def _get_image(self) -> pygame.Surface:
        return self._image

    def _update_image(self):
        alpha = 128
        text = pygame.Surface(self._label.get_rect().size, pygame.SRCALPHA, 32)
        text.fill((0, 0, 0, alpha))
        text.blit(self._label, (0, 0))

        w, h = self._label.get_rect().size
        self._image = pygame.Surface((w + 2 * self._gradient_width, h), pygame.SRCALPHA, 32)
        gv.TEXTURE_MANAGER.alpha_gradient(self._image, (0, 0, 0), 0, alpha,
                                          rect=pygame.Rect(0, 0, self._gradient_width, h))
        gv.TEXTURE_MANAGER.alpha_gradient(self._image, (0, 0, 0), alpha, 0,
                                          rect=pygame.Rect(w + self._gradient_width, 0, self._gradient_width, h))
        self._image.blit(text, (self._gradient_width, 0))
