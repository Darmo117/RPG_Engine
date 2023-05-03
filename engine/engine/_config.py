import typing as _typ

from . import _i18n
import pygame


class Config:
    def __init__(
            self,
            game_title: str,
            font: pygame.font.Font,
            languages: _typ.Sequence[_i18n.Language] = (),
            debug: bool = False
    ):
        self._game_title = game_title
        self._font = font
        self._languages = {lang.code: lang for lang in languages}
        self._debug = debug
        self._active_language = next(iter(languages))

    @property
    def game_title(self) -> str:
        return self._game_title

    @property
    def font(self) -> pygame.font.Font:
        return self._font

    @property
    def languages(self) -> set[_i18n.Language]:
        return set(self._languages.values())

    @property
    def active_language(self) -> _i18n.Language:
        return self._active_language

    def set_active_language(self, code: str):
        if code not in self._languages:
            raise KeyError(f'undefined language code "{code}"')
        self._active_language = self._languages[code]

    @property
    def debug(self) -> bool:
        return self._debug

    def __repr__(self):
        s = []
        for prop, value in self.__dict__.items():
            s.append(f'{prop[1:]}={value}')
        return '{' + ', '.join(s) + '}'
