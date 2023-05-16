from __future__ import annotations

import configparser as _cp
import typing as _typ

import pygame

from . import constants, i18n, maths


def load_config() -> Config:
    game_config_parser = _cp.ConfigParser()
    with constants.GAME_INIT_FILE.open(mode='r', encoding='UTF-8') as f:
        game_config_parser.read_file(f)
    settings_parser = _cp.ConfigParser()
    with constants.SETTINGS_FILE.open(mode='r', encoding='UTF-8') as f:
        settings_parser.read_file(f)
    font = pygame.font.Font(
        constants.FONTS_DIR / (game_config_parser.get('Game', 'font') + '.ttf'),
        game_config_parser.getint('Game', 'font_size', fallback=12)
    )
    config = Config(
        game_title=game_config_parser.get('Game', 'title', fallback='Game'),
        font=font,
        languages=list(map(i18n.Language, constants.LANGS_DIR.glob('*.json'))),
        bgm_volume=settings_parser.getint('Sound', 'bgm_volume', fallback=100),
        bgs_volume=settings_parser.getint('Sound', 'bgs_volume', fallback=100),
        sfx_volume=settings_parser.getint('Sound', 'sfx_volume', fallback=100),
        master_volume=settings_parser.getint('Sound', 'master_volume', fallback=100),
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
            sfx_volume: int,
            master_volume: int,
            always_run: bool,
            debug: bool = False
    ):
        self._game_title = game_title
        self._font = font
        self._languages = {lang.code: lang for lang in languages}
        self._bgm_volume = maths.clamp(bgm_volume, 0, 100)
        self._bgs_volume = maths.clamp(bgs_volume, 0, 100)
        self._sfx_volume = maths.clamp(sfx_volume, 0, 100)
        self._master_volume = maths.clamp(master_volume, 0, 100)
        self.always_run = always_run
        self._debug = debug
        self._active_language = next(iter(languages))

    @property
    def bg_music_volume(self) -> int:
        return self._bgm_volume

    @bg_music_volume.setter
    def bg_music_volume(self, value: int):
        self._bgm_volume = maths.clamp(value, 0, 100)

    @property
    def bg_sounds_volume(self) -> int:
        return self._bgs_volume

    @bg_sounds_volume.setter
    def bg_sounds_volume(self, value: int):
        self._bgs_volume = maths.clamp(value, 0, 100)

    @property
    def sound_effects_volume(self) -> int:
        return self._sfx_volume

    @sound_effects_volume.setter
    def sound_effects_volume(self, value: int):
        self._sfx_volume = maths.clamp(value, 0, 100)

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
        cp.add_section('Sound')
        cp['Volume']['bgm_volume'] = str(self.bg_music_volume)
        cp['Volume']['bgs_volume'] = str(self.bg_sounds_volume)
        cp['Volume']['sfx_volume'] = str(self.sound_effects_volume)
        cp['Volume']['master_volume'] = str(self.master_volume)
        cp.add_section('Gameplay')
        cp['Gameplay']['always_run'] = str(self.always_run).lower()
        with constants.SETTINGS_FILE.open(mode='w', encoding='UTF-8') as f:
            cp.write(f)

    def __repr__(self):
        return (f'Config[game_title={self.game_title},font={self.font},active_language={self.active_language},'
                f'bgm_volume={self.bg_music_volume},bgs_volume={self.bg_sounds_volume},'
                f'sfx_volume={self.sound_effects_volume},master_volume={self.master_volume},'
                f'always_run={self.always_run},languages=[{",".join(map(str, self._languages.values()))}]')
