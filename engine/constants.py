import pathlib

SCALE = 1.5
TILE_SIZE = 32
SCREEN_TILE_SIZE = TILE_SIZE * SCALE

USER_DATA_ROOT_DIR: pathlib.Path
LOGS_DIR: pathlib.Path
LANGS_DIR: pathlib.Path

DATA_DIR: pathlib.Path
MAPS_DIR: pathlib.Path
SAVES_DIR: pathlib.Path
FONTS_DIR: pathlib.Path

TEXTURES_DIR: pathlib.Path
BACKGROUNDS_DIR: pathlib.Path
MENUS_TEX_DIR: pathlib.Path
SPRITES_DIR: pathlib.Path
TILESETS_DIR: pathlib.Path
TILESETS_INDEX_FILE_NAME = 'tilesets.json'

GAME_SETUP_FILE_NAME = 'setup.json'
SETTINGS_FILE: pathlib.Path


def init(root: pathlib.Path = None):
    global USER_DATA_ROOT_DIR, TEXTURES_DIR, LANGS_DIR, DATA_DIR, MAPS_DIR, SAVES_DIR, FONTS_DIR, BACKGROUNDS_DIR, \
        MENUS_TEX_DIR, SPRITES_DIR, TILESETS_DIR, SETTINGS_FILE, LOGS_DIR

    SETTINGS_FILE = pathlib.Path('settings.ini')
    USER_DATA_ROOT_DIR = pathlib.Path('user-generated')
    LOGS_DIR = pathlib.Path('logs')
    LANGS_DIR = pathlib.Path('langs')
    if root:
        SETTINGS_FILE = root / SETTINGS_FILE
        USER_DATA_ROOT_DIR = root / USER_DATA_ROOT_DIR
        LOGS_DIR = root / LOGS_DIR
        LANGS_DIR = root / LANGS_DIR

    DATA_DIR = USER_DATA_ROOT_DIR / 'data'
    MAPS_DIR = USER_DATA_ROOT_DIR / 'maps'
    SAVES_DIR = USER_DATA_ROOT_DIR / 'saves'
    FONTS_DIR = USER_DATA_ROOT_DIR / 'fonts'

    TEXTURES_DIR = USER_DATA_ROOT_DIR / 'textures'
    BACKGROUNDS_DIR = TEXTURES_DIR / 'backgrounds'
    MENUS_TEX_DIR = TEXTURES_DIR / 'menus'
    SPRITES_DIR = TEXTURES_DIR / 'spritesheets'
    TILESETS_DIR = TEXTURES_DIR / 'tilesets'
