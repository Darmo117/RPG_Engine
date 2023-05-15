from __future__ import annotations

import configparser as _cp
import typing as _typ

import pygame

from . import constants, i18n, maths


def load_config() -> Config:
    game_config_parser = _cp.ConfigParser()
    with constants.GAME_INIT_FILE.open(encoding='UTF-8') as f:
        game_config_parser.read_file(f)
    settings_parser = _cp.ConfigParser()
    with constants.SETTINGS_FILE.open(encoding='UTF-8') as f:
        settings_parser.read_file(f)
    font = pygame.font.Font(
        constants.FONTS_DIR / (game_config_parser.get('Game', 'font') + '.ttf'),
        game_config_parser.getint('Game', 'font_size', fallback=12)
    )
    config = Config(
        game_title=game_config_parser.get('Game', 'title', fallback='Game'),
        font=font,
        languages=list(map(i18n.Language, constants.LANGS_DIR.glob('*.json'))),
        bgm_volume=settings_parser.getint('Volume', 'bgm', fallback=100),
        bgs_volume=settings_parser.getint('Volume', 'bgs', fallback=100),
        menu_volume=settings_parser.getint('Volume', 'menu', fallback=100),
        master_volume=settings_parser.getint('Volume', 'master', fallback=100),
        always_run=settings_parser.getboolean('Gameplay', 'always_run', fallback=False),
        debug=game_config_parser.getboolean('Game', 'debug', fallback=False)
    )
    return config


class Config:
    MAX_VOLUME = 100

    def __init__(
            self,
            game_title: str,
            font: pygame.font.Font,
            languages: _typ.Iterable[i18n.Language],
            bgm_volume: int,
            bgs_volume: int,
            menu_volume: int,
            master_volume: int,
            always_run: bool,
            debug: bool = False
    ):
        self._game_title = game_title
        self._font = font
        self._languages = {lang.code: lang for lang in languages}
        self._bgm_volume = maths.clamp(bgm_volume, 0, 100)
        self._bgs_volume = maths.clamp(bgs_volume, 0, 100)
        self._menu_volume = maths.clamp(menu_volume, 0, 100)
        self._master_volume = maths.clamp(master_volume, 0, 100)
        self.always_run = always_run
        self._debug = debug
        self._active_language = next(iter(languages))

    @property
    def bgm_volume(self) -> int:
        return self._bgm_volume

    @bgm_volume.setter
    def bgm_volume(self, value: int):
        self._bgm_volume = maths.clamp(value, 0, 100)

    @property
    def bgs_volume(self) -> int:
        return self._bgs_volume

    @bgs_volume.setter
    def bgs_volume(self, value: int):
        self._bgs_volume = maths.clamp(value, 0, 100)

    @property
    def menu_volume(self) -> int:
        return self._menu_volume

    @menu_volume.setter
    def menu_volume(self, value: int):
        self._menu_volume = maths.clamp(value, 0, 100)

    @property
    def master_volume(self) -> int:
        return self._master_volume

    @master_volume.setter
    def master_volume(self, value: int):
        self._master_volume = maths.clamp(value, 0, 100)

    @property
    def game_title(self) -> str:
        return self._game_title

    @property
    def font(self) -> pygame.font.Font:
        return self._font

    @property
    def languages(self) -> set[i18n.Language]:
        return set(self._languages.values())

    @property
    def active_language(self) -> i18n.Language:
        return self._active_language

    def set_active_language(self, code: str):
        if code not in self._languages:
            raise KeyError(f'undefined language code "{code}"')
        self._active_language = self._languages[code]

    @property
    def debug(self) -> bool:
        return self._debug

    def save(self):
        cp = _cp.ConfigParser()
        cp.add_section('Volume')
        cp['Volume']['bgm'] = str(self.bgm_volume)
        cp['Volume']['bgs'] = str(self.bgs_volume)
        cp['Volume']['menu'] = str(self.menu_volume)
        cp['Volume']['master'] = str(self.master_volume)
        cp.add_section('Gameplay')
        cp['Gameplay']['always_run'] = str(self.always_run).lower()
        with constants.SETTINGS_FILE.open(mode='w', encoding='UTF-8') as f:
            cp.write(f)

    def __repr__(self):
        return (f'Config[game_title={self.game_title},font={self.font},active_language={self.active_language},'
                f'bgm_volume={self.bgm_volume},bgs_volume={self.bgs_volume},menu_volume={self.menu_volume},'
                f'master_volume={self.master_volume},always_run={self.always_run},'
                f'languages=[{",".join(map(str, self._languages.values()))}]')
