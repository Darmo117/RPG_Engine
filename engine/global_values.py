from engine import texture_manager as tm, config, i18n, entities

SCALE = 1
TILE_SIZE = 32
SCREEN_TILE_SIZE = TILE_SIZE * SCALE

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 608

BACKGROUNDS_DIR = "data/backgrounds"
MAPS_DIR = "data/maps"
MENUS_DIR = "data/menus"
SPRITES_DIR = "data/sprites"
TILESETS_DIR = "data/tilesets"
TILESETS_INDEX_FILE = "tilesets.cfg"

GAME_INIT_FILE = "data/game.ini"
LANG_FILE = "data/langs.cfg"

LOG_DIR = "logs"

CONFIG: config.Config = None
TEXTURE_MANAGER: tm.TexturesManager = None
I18N: i18n.I18n = None

PLAYER_DATA: entities.PlayerData = None
