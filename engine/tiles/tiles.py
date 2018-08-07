from engine import sprite, tileset as ts


class Tile(sprite.Sprite):
    def __init__(self, x, y, texture_index, tileset):
        super().__init__(x, y, ts.get_tile(texture_index, tileset))
