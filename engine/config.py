from __future__ import annotations

import configparser as _cp
import json
import logging
import typing as _typ

import pygame

from . import constants, i18n, maths


def load_config(debug: bool = False) -> Config:
    with (constants.DATA_DIR / constants.GAME_SETUP_FILE_NAME).open(mode='r', encoding='UTF-8') as f:
        json_data = json.load(f)
    font = pygame.font.Font(
        constants.FONTS_DIR / (str(json_data['font']['name']) + '.ttf'),
        int(json_data['font']['size'])
    )
    w, h = json_data['screen_size']
    languages = list(map(i18n.Language, constants.LANGS_DIR.glob('*.json')))
    settings_parser = _get_settings_parser()
    with constants.SETTINGS_FILE.open(mode='r', encoding='UTF-8') as f:
        settings_parser.read_file(f)
    return Config(
        game_title=str(json_data['game_title']),
        window_size=(int(w), int(h)),
        font=font,
        languages=languages,
        bgm_volume=settings_parser.getint('Sound', 'bgm_volume', fallback=100),
        bgs_volume=settings_parser.getint('Sound', 'bgs_volume', fallback=100),
        sfx_volume=settings_parser.getint('Sound', 'sfx_volume', fallback=100),
        master_volume=settings_parser.getint('Sound', 'master_volume', fallback=100),
        always_run=settings_parser.getboolean('Gameplay', 'always_run', fallback=False),
        selected_language=settings_parser.get('UI', 'language', fallback=None) if len(languages) > 1 else languages[0],
        debug=debug,
    )


def _get_settings_parser():
    settings_parser = _cp.ConfigParser()
    settings_parser.add_section('UI')
    settings_parser.add_section('Sound')
    settings_parser.add_section('Gameplay')
    return settings_parser


class Config:
    MAX_VOLUME = 100

    def __init__(
            self,
            game_title: str,
            window_size: tuple[int, int],
            font: pygame.font.Font,
            languages: _typ.Iterable[i18n.Language],
            bgm_volume: int,
            bgs_volume: int,
            sfx_volume: int,
            master_volume: int,
            always_run: bool,
            selected_language: str = None,
            debug: bool = False
    ):
        self._logger = logging.getLogger('Config')
        self._game_title = game_title
        self._window_size = (min(window_size[0], 800), min(window_size[1], 600))
        self._font = font
        self._languages = {lang.code: lang for lang in languages}
        self._bgm_volume = maths.clamp(bgm_volume, 0, 100)
        self._bgs_volume = maths.clamp(bgs_volume, 0, 100)
        self._sfx_volume = maths.clamp(sfx_volume, 0, 100)
        self._master_volume = maths.clamp(master_volume, 0, 100)
        self.always_run = always_run
        self._debug = debug
        self._active_language: i18n.Language | None = self._languages.get(selected_language)

    @property
    def window_size(self) -> tuple[int, int]:
        return self._window_size

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
    def active_language(self) -> i18n.Language | None:
        return self._active_language

    def set_active_language(self, code: str):
        if code not in self._languages:
            raise KeyError(f'undefined language code "{code}"')
        self._active_language = self._languages[code]

    @property
    def debug(self) -> bool:
        return self._debug

    def save(self):
        self._logger.info('Saving config…')
        cp = _get_settings_parser()
        if self._active_language:
            cp['UI']['language'] = self._active_language.code
        cp['Sound']['bgm_volume'] = str(self.bg_music_volume)
        cp['Sound']['bgs_volume'] = str(self.bg_sounds_volume)
        cp['Sound']['sfx_volume'] = str(self.sound_effects_volume)
        cp['Sound']['master_volume'] = str(self.master_volume)
        cp['Gameplay']['always_run'] = str(self.always_run).lower()
        with constants.SETTINGS_FILE.open(mode='w', encoding='UTF-8') as f:
            cp.write(f)
        self._logger.info('Done.')

    def __repr__(self):
        return (f'Config[game_title={self.game_title},font={self.font},active_language={self.active_language},'
                f'bgm_volume={self.bg_music_volume},bgs_volume={self.bg_sounds_volume},'
                f'sfx_volume={self.sound_effects_volume},master_volume={self.master_volume},'
                f'always_run={self.always_run},languages=[{",".join(map(str, self._languages.values()))}]')
