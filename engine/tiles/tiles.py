from .. import global_values as gv, sprite


class Tile(sprite.TileSprite):
    def __init__(self, tile_x, tile_y, texture_index, tileset):
        super().__init__(tile_x, tile_y, gv.TEXTURE_MANAGER.get_tile(texture_index, tileset))
