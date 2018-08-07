import os
import pickle
import typing as typ

import pygame

from engine import tiles, constants, entities


class Map:
    def __init__(self, file: str, player_data: entities.PlayerData):
        self._player = entities.Player("Character", self)
        self._player.map = self
        self._player_data = player_data

        with open(os.path.join(constants.MAPS_DIR, file), "rb") as f:
            raw_data = pickle.load(f)
        width = int(raw_data["width"])
        height = int(raw_data["height"])
        self._background_color = raw_data["background_color"]
        self._player.set_position(int(raw_data["start_x"]), int(raw_data["start_y"]))
        self._rect = pygame.Rect(0, 0, width * constants.SCREEN_TILE_SIZE, height * constants.SCREEN_TILE_SIZE)

        self._walls = raw_data["walls"]
        self._background_tiles_list = pygame.sprite.Group()
        self._floor_tiles_list = pygame.sprite.Group()
        self._tiles_list = pygame.sprite.Group()
        for y in range(height):
            for x in range(width):
                tile_index, tileset = raw_data["main_layer"][y][x]
                tile = tiles.Tile(x, y, tile_index, tileset)
                if tile is not None:
                    self._tiles_list.add(tile)
        self._foreground_tiles_list = pygame.sprite.Group()

        self._entities_list = pygame.sprite.Group()
        self._player_list = pygame.sprite.Group()
        self._player_list.add(self._player)

        if self._rect.width < constants.SCREEN_WIDTH:
            self.translate((constants.SCREEN_WIDTH - self._rect.width) // 2, 0, player=True)
        if self._rect.height < constants.SCREEN_HEIGHT:
            self.translate(0, (constants.SCREEN_HEIGHT - self._rect.height) // 2, player=True)

    @property
    def shift_x(self):
        return self._rect.x

    @property
    def shift_y(self):
        return self._rect.y

    @property
    def player(self):
        return self._player

    def update(self) -> typ.Optional[str]:
        """Updates this Map. May return a Map to load."""
        self._tiles_list.update()
        self._entities_list.update()
        self._player_list.update()

        if self._rect.top < 0:
            top_limit = (constants.SCREEN_HEIGHT - constants.SCREEN_TILE_SIZE) // 2
            if self._player.top < top_limit:
                diff = top_limit - self._player.top
                self._player.top = top_limit
                self.translate(0, diff)

        if self._rect.bottom > constants.SCREEN_HEIGHT:
            bottom_limit = (constants.SCREEN_HEIGHT + constants.SCREEN_TILE_SIZE) // 2
            if self._player.bottom > bottom_limit:
                diff = self._player.bottom - bottom_limit
                self._player.bottom = bottom_limit
                self.translate(0, -diff)

        if self._rect.left < 0:
            left_limit = (constants.SCREEN_WIDTH - constants.SCREEN_TILE_SIZE) // 2
            if self._player.left < left_limit:
                diff = left_limit - self._player.left
                self._player.left = left_limit
                self.translate(diff, 0)

        if self._rect.right > constants.SCREEN_WIDTH:
            right_limit = (constants.SCREEN_WIDTH + constants.SCREEN_TILE_SIZE) // 2
            if self._player.right > right_limit:
                diff = self._player.right - right_limit
                self._player.right = right_limit
                self.translate(-diff, 0)

        return None

    def draw(self, screen):
        screen.fill(self._background_color)
        self._tiles_list.draw(screen)
        self._entities_list.draw(screen)
        self._player_list.draw(screen)

    def translate(self, tx, ty, player=False):
        self._rect.x += tx
        self._rect.y += ty

        for block in self._tiles_list:
            block.translate(tx, ty)

        for entity in self._entities_list:
            entity.translate(tx, ty)

        if player:
            for player in self._player_list:
                player.translate(tx, ty)

    def can_go(self, x: int, y: int) -> bool:
        """Checks if it is possible to go to a specific tile."""
        try:
            return 0 <= x < self._rect.width // constants.SCREEN_TILE_SIZE \
                   and 0 <= y < self._rect.height // constants.SCREEN_TILE_SIZE \
                   and self._walls[y][x] == 0
        except IndexError:
            return False
