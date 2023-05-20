from __future__ import annotations

import configparser as _cp
import json
import logging
import typing as _typ

import pygame

from . import constants, i18n, maths

_SECTION_UI = 'UI'
_SECTION_SOUND = 'Sound'
_SECTION_GAMEPLAY = 'Gameplay'

_OPTION_LANGUAGE = 'language'
_OPTION_BGM_VOLUME = 'bgm_volume'
_OPTION_BGS_VOLUME = 'bgs_volume'
_OPTION_MFX_VOLUME = 'mfx_volume'
_OPTION_SFX_VOLUME = 'sfx_volume'
_OPTION_ALWAYS_RUN = 'always_run'


def load_config(debug: bool = False) -> Config:
    with (constants.DATA_DIR / constants.GAME_SETUP_FILE_NAME).open(mode='r', encoding='UTF-8') as f:
        json_data = json.load(f)
    font_settings = json_data['font']
    font = pygame.font.Font(
        constants.FONTS_DIR / (str(font_settings['name']) + '.ttf'),
        int(font_settings['size'])
    )
    w, h = json_data['screen_size']
    languages = [i18n.Language(constants.LANGS_DIR / f'{lang}.json') for lang in json_data['available_languages']]

    settings_parser = _get_settings_parser()
    with constants.SETTINGS_FILE.open(mode='r', encoding='UTF-8') as f:
        settings_parser.read_file(f)

    def parse_keys(action: str) -> _typ.Sequence[int]:
        if not settings_parser.has_option(_SECTION_GAMEPLAY, action):
            return InputConfig.ACTION_DEFAULTS[action]
        return tuple(map(int, settings_parser.get(_SECTION_GAMEPLAY, action).split(',')))

    input_config = InputConfig(
        ok_interact_keys=parse_keys(InputConfig.ACTION_OK_INTERACT),
        up_keys=parse_keys(InputConfig.ACTION_UP),
        down_keys=parse_keys(InputConfig.ACTION_DOWN),
        left_keys=parse_keys(InputConfig.ACTION_LEFT),
        right_keys=parse_keys(InputConfig.ACTION_RIGHT),
        dash_keys=parse_keys(InputConfig.ACTION_DASH),
        cancel_menu_keys=parse_keys(InputConfig.ACTION_CANCEL_MENU),
        page_up_keys=parse_keys(InputConfig.ACTION_PAGE_UP),
        page_down_keys=parse_keys(InputConfig.ACTION_PAGE_DOWN),
    )

    return Config(
        game_title=str(json_data['game_title']),
        base_screen_size=(int(w), int(h)),
        font=font,
        languages=languages,
        bgm_volume=settings_parser.getint(_SECTION_SOUND, _OPTION_BGM_VOLUME, fallback=100),
        bgs_volume=settings_parser.getint(_SECTION_SOUND, _OPTION_BGS_VOLUME, fallback=100),
        mfx_volume=settings_parser.getint(_SECTION_SOUND, _OPTION_MFX_VOLUME, fallback=100),
        sfx_volume=settings_parser.getint(_SECTION_SOUND, _OPTION_SFX_VOLUME, fallback=100),
        always_run=settings_parser.getboolean(_SECTION_GAMEPLAY, _OPTION_ALWAYS_RUN, fallback=False),
        input_config=input_config,
        selected_language=settings_parser.get(
            _SECTION_UI, _OPTION_LANGUAGE, fallback=None if len(languages) > 1 else languages[0]),
        debug=debug,
    )


def _get_settings_parser():
    settings_parser = _cp.ConfigParser()
    settings_parser.add_section(_SECTION_UI)
    settings_parser.add_section(_SECTION_SOUND)
    settings_parser.add_section(_SECTION_GAMEPLAY)
    return settings_parser


class InputConfig:
    MAX_KEYS = 4

    ACTION_OK_INTERACT = 'ok/interact'
    ACTION_UP = 'up'
    ACTION_DOWN = 'down'
    ACTION_LEFT = 'left'
    ACTION_RIGHT = 'right'
    ACTION_DASH = 'dash'
    ACTION_CANCEL_MENU = 'cancel/menu'
    ACTION_PAGE_UP = 'page_up'
    ACTION_PAGE_DOWN = 'page_down'

    ACTION_DEFAULTS: dict[str, tuple[int, ...]] = {
        ACTION_OK_INTERACT: (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE,),
        ACTION_UP: (pygame.K_UP,),
        ACTION_DOWN: (pygame.K_DOWN,),
        ACTION_LEFT: (pygame.K_LEFT,),
        ACTION_RIGHT: (pygame.K_RIGHT,),
        ACTION_DASH: (pygame.K_LSHIFT, pygame.K_RSHIFT,),
        ACTION_CANCEL_MENU: (pygame.K_ESCAPE,),
        ACTION_PAGE_UP: (pygame.K_PAGEUP,),
        ACTION_PAGE_DOWN: (pygame.K_PAGEDOWN,),
    }

    def __init__(
            self,
            ok_interact_keys: _typ.Sequence[int],
            up_keys: _typ.Sequence[int],
            down_keys: _typ.Sequence[int],
            left_keys: _typ.Sequence[int],
            right_keys: _typ.Sequence[int],
            dash_keys: _typ.Sequence[int],
            cancel_menu_keys: _typ.Sequence[int],
            page_up_keys: _typ.Sequence[int],
            page_down_keys: _typ.Sequence[int],
    ):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._keys: dict[str, list[int]] = {action: [-1] * self.MAX_KEYS for action in self.ACTION_DEFAULTS}
        self._set_keys(self.ACTION_OK_INTERACT, ok_interact_keys)
        self._set_keys(self.ACTION_UP, up_keys)
        self._set_keys(self.ACTION_DOWN, down_keys)
        self._set_keys(self.ACTION_LEFT, left_keys)
        self._set_keys(self.ACTION_RIGHT, right_keys)
        self._set_keys(self.ACTION_DASH, dash_keys)
        self._set_keys(self.ACTION_CANCEL_MENU, cancel_menu_keys)
        self._set_keys(self.ACTION_PAGE_UP, page_up_keys)
        self._set_keys(self.ACTION_PAGE_DOWN, page_down_keys)

    def _set_keys(self, action: str, keys: _typ.Sequence[int]):
        self._keys[action] = [-1] * self.MAX_KEYS
        if not keys or all(key < 0 for key in keys):
            self._set_keys(action, self.ACTION_DEFAULTS[action])
            return
        for i in range(self.MAX_KEYS):
            self.set_key(action, i, keys[i] if i < len(keys) else -1)

    def get_keys(self, action: str) -> tuple[int]:
        return tuple(self._keys[action])

    def set_key(self, action: str, index: int, key: int):
        self._keys[action][index] = key

    def remove_key(self, action: str, index: int):
        self._keys[action][index] = -1

    def get_action(self, key: int) -> str | None:
        for action, keys in self._keys.items():
            if key in keys:
                return action
        return None

    def reset(self):
        for action, keys in self.ACTION_DEFAULTS.items():
            self._set_keys(action, keys)

    def update(self, config: InputConfig):
        for action in self.ACTION_DEFAULTS:
            self._set_keys(action, config.get_keys(action))

    def copy(self) -> InputConfig:
        return InputConfig(
            self._keys[self.ACTION_OK_INTERACT],
            self._keys[self.ACTION_UP],
            self._keys[self.ACTION_DOWN],
            self._keys[self.ACTION_LEFT],
            self._keys[self.ACTION_RIGHT],
            self._keys[self.ACTION_DASH],
            self._keys[self.ACTION_CANCEL_MENU],
            self._keys[self.ACTION_PAGE_UP],
            self._keys[self.ACTION_PAGE_DOWN],
        )

    def __repr__(self):
        return f'InputConfig[{self._keys}]'


class Config:
    MAX_VOLUME = 100

    def __init__(
            self,
            game_title: str,
            base_screen_size: tuple[int, int],
            font: pygame.font.Font,
            languages: _typ.Iterable[i18n.Language],
            bgm_volume: int,
            bgs_volume: int,
            mfx_volume: int,
            sfx_volume: int,
            always_run: bool,
            input_config: InputConfig,
            selected_language: str = None,
            debug: bool = False
    ):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._game_title = game_title
        self._screen_size = (max(base_screen_size[0], 1280), max(base_screen_size[1], 720))
        self._font = font
        self._languages = {lang.code: lang for lang in languages}

        # Define sound-related fields
        self._bgm_volume = 0
        self._bgs_volume = 0
        self._mfx_volume = 0
        self._sfx_volume = 0
        # Assign to them through property setter
        self.bg_music_volume = bgm_volume
        self.bg_sounds_volume = bgs_volume
        self.music_effects_volume = mfx_volume
        self.sound_effects_volume = sfx_volume

        self.always_run = always_run
        self._input_config = input_config
        self._debug = debug
        self._active_language: i18n.Language | None = self._languages.get(selected_language)

    @property
    def inputs(self) -> InputConfig:
        return self._input_config

    @property
    def base_screen_size(self) -> tuple[int, int]:
        return self._screen_size

    @property
    def screen_ratio(self) -> float:
        return self._screen_size[0] / self._screen_size[1]

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
    def music_effects_volume(self) -> int:
        return self._mfx_volume

    @music_effects_volume.setter
    def music_effects_volume(self, value: int):
        self._mfx_volume = maths.clamp(value, 0, 100)

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
            cp[_SECTION_UI][_OPTION_LANGUAGE] = self._active_language.code
        cp[_SECTION_SOUND][_OPTION_BGM_VOLUME] = str(self.bg_music_volume)
        cp[_SECTION_SOUND][_OPTION_BGS_VOLUME] = str(self.bg_sounds_volume)
        cp[_SECTION_SOUND][_OPTION_MFX_VOLUME] = str(self.music_effects_volume)
        cp[_SECTION_SOUND][_OPTION_SFX_VOLUME] = str(self.sound_effects_volume)
        cp[_SECTION_GAMEPLAY][_OPTION_ALWAYS_RUN] = str(self.always_run).lower()
        for action in InputConfig.ACTION_DEFAULTS:
            cp[_SECTION_GAMEPLAY][action] = ','.join(str(key) for key in self._input_config.get_keys(action))
        with constants.SETTINGS_FILE.open(mode='w', encoding='UTF-8') as f:
            cp.write(f)
        self._logger.info('Done.')

    def __repr__(self):
        return (f'Config[game_title={self.game_title},font={self.font},active_language={self.active_language},'
                f'bgm_volume={self.bg_music_volume},bgs_volume={self.bg_sounds_volume},'
                f'mfx_volume={self.music_effects_volume},sfx_volume={self.sound_effects_volume},'
                f'always_run={self.always_run},inputs={self._input_config},'
                f'languages=[{",".join(map(str, self._languages.values()))}]')


__all__ = [
    'load_config',
    'InputConfig',
    'Config',
]
