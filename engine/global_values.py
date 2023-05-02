import pathlib

from . import texture_manager as tm, config, i18n, entities

SCALE = 1
TILE_SIZE = 32
SCREEN_TILE_SIZE = TILE_SIZE * SCALE

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 608

BACKGROUNDS_DIR = pathlib.Path('data/backgrounds')
MAPS_DIR = pathlib.Path('data/maps')
MENUS_DIR = pathlib.Path('data/menus')
SPRITES_DIR = pathlib.Path('data/sprites')
TILESETS_DIR = pathlib.Path('data/tilesets')
TILESETS_INDEX_FILE = pathlib.Path('tilesets.cfg')

GAME_INIT_FILE = pathlib.Path('data/game.ini')
LANG_FILE = pathlib.Path('data/langs.cfg')

LOG_DIR = pathlib.Path('logs')

CONFIG: config.Config = None
TEXTURE_MANAGER: tm.TexturesManager = None
I18N: i18n.I18n = None

PLAYER_DATA: entities.PlayerData = None
