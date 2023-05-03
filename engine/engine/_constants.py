import pathlib

SCALE = 1
TILE_SIZE = 32
SCREEN_TILE_SIZE = TILE_SIZE * SCALE

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

ROOT_DIR = pathlib.Path('data')
TEXTURES_DIR = ROOT_DIR / 'textures'

LANGS_DIR = ROOT_DIR / 'langs'
SCREENS_DIR = ROOT_DIR / 'screens'
MAPS_DIR = ROOT_DIR / 'maps'
SAVES_DIR = ROOT_DIR / 'saves'

BACKGROUNDS_DIR = TEXTURES_DIR / 'backgrounds'
MENUS_TEX_DIR = TEXTURES_DIR / 'menus'
SPRITES_DIR = TEXTURES_DIR / 'sprites'
TILESETS_DIR = TEXTURES_DIR / 'tilesets'
TILESETS_INDEX_FILE_NAME = 'tilesets.cfg'

GAME_INIT_FILE = ROOT_DIR / 'game.ini'

LOGS_DIR = pathlib.Path('logs')
