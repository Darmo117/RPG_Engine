import pickle
import typing as typ

import pygame

from engine import blocks, player as ply, constants


class Map:
    def __init__(self, file: str, player: ply.Player):
        self._player = player
        self._player.current_level = self

        with open(file, "rb") as f:
            raw_data = pickle.load(f)
        width = raw_data["width"]
        height = raw_data["height"]
        self._background_color = raw_data["background"]
        self._player.set_position(raw_data["player_x"] * constants.SCREEN_TILE_SIZE,
                                  raw_data["player_y"] * constants.SCREEN_TILE_SIZE)
        self._can_go_back = raw_data["go_back"]
        self._shift_x = 0
        self._shift_y = 0

        self._floor_blocks_list = pygame.sprite.Group()
        self._blocks_list = pygame.sprite.Group()
        for y in range(height):
            for x in range(width):
                block_id = raw_data["main_layer"][y][x]
                block = blocks.get_block(block_id, x, y)
                if block is not None:
                    self._blocks_list.add(block)

        self._enemy_list = pygame.sprite.Group()
        self._items_list = pygame.sprite.Group()
        self._player_list = pygame.sprite.Group()
        self._player_list.add(self._player)

    @property
    def shift_x(self):
        return self._shift_x

    @property
    def shift_y(self):
        return self._shift_y

    def update(self) -> typ.Optional[str]:
        """Updates this Map. May return a Map to load."""
        self._blocks_list.update()
        self._enemy_list.update()
        self._player_list.update()

        top_limit = (constants.SCREEN_HEIGHT - constants.SCREEN_TILE_SIZE) // 2
        if self._player.top < top_limit:
            diff = self._player.top - top_limit
            self._player.top = top_limit
            self.translate(0, diff)

        bottom_limit = (constants.SCREEN_HEIGHT + constants.SCREEN_TILE_SIZE) // 2
        if self._player.bottom > bottom_limit:
            diff = self._player.bottom - bottom_limit
            self._player.bottom = bottom_limit
            self.translate(0, -diff)

        left_limit = (constants.SCREEN_WIDTH - constants.SCREEN_TILE_SIZE) // 2
        if self._can_go_back and self._player.left < left_limit and self._shift_x < 0:
            diff = left_limit - self._player.left
            self._player.left = left_limit
            self.translate(diff, 0)

        right_limit = (constants.SCREEN_WIDTH + constants.SCREEN_TILE_SIZE) // 2
        if self._player.right > right_limit:
            diff = self._player.right - right_limit
            self._player.right = right_limit
            self.translate(-diff, 0)

        if self._player.left <= 0:
            self._player.left = 0

        return None

    def draw(self, screen):
        screen.fill(self._background_color)
        self._blocks_list.draw(screen)
        self._enemy_list.draw(screen)
        self._player_list.draw(screen)

    def translate(self, tx, ty):
        self._shift_x += tx
        self._shift_y += ty

        for block in self._blocks_list:
            block.translate(tx, ty)

        for enemy in self._enemy_list:
            enemy.translate(tx, ty)

        for item in self._items_list:
            item.translate(tx, ty)

    def collides(self, entity) -> list:
        """Returns the list of blocks the given entity collides."""
        return pygame.sprite.spritecollide(entity, self._blocks_list, False)
