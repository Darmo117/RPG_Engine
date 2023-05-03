from __future__ import annotations

import abc
import json
import pathlib
import typing as _typ

import pygame

from . import components
from .. import _constants, _events, _map, _scene

_C = _typ.TypeVar('_C', bound=components.Component)


class Screen(_scene.Scene, abc.ABC):
    def __init__(self, game_engine, parent: Screen = None, background_image: str | pathlib.Path = None):
        """Create a screen.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        :param parent: The screen that lead to this one.
        :param background_image: Path to the screen’s background image.
        """
        super().__init__(parent)
        self._game_engine = game_engine
        self._background_image = None
        if background_image:
            try:
                self._background_image = pygame.Surface(
                    self._game_engine.window_size,
                    pygame.SRCALPHA
                ).convert()
                self._background_image.blit(pygame.image.load(background_image), (0, 0))
            except FileNotFoundError as e:
                self._game_engine.logger.error(e)
                self._background_image = None
        self._go_to_scene = None
        self._components: list[components.Component] = []

    def _add_component(self, component: _C) -> _C:
        if component in self._components:
            self._components.remove(component)
        self._components.append(component)
        return component

    def on_event(self, event: pygame.event.Event):
        super().on_event(event)
        self._reset()
        if self._controls_enabled:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.parent:
                self._go_to_scene = self.parent
            else:
                for c in self._components:
                    c.on_event(event)

    def update(self) -> _events.Event | None:
        super().update()
        for c in self._components:
            c.update()
        if self._go_to_scene:
            event = _events.LoadSceneEvent(self._go_to_scene)
            self._go_to_scene = None  # Reset as player may go back to this screen
            return event
        return None

    def draw(self, screen: pygame.Surface):
        if self._background_image:
            screen.blit(self._background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))
        for c in self._components:
            c.draw(screen)

    def _reset(self):
        self._go_to_scene = None


class LanguageSelectScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a language selection screen.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, _constants.BACKGROUNDS_DIR / 'title_screen.png')
        languages = self._game_engine.config.languages
        menu = self._add_component(components.Menu(self._game_engine.texture_manager, len(languages), 1))
        for i, language in enumerate(languages):
            button = components.Button(
                self._game_engine.texture_manager,
                language.name,
                name=language.code,
                action=self._on_language_selected
            )
            menu.add_item(button)
        w, h = self._game_engine.window_size
        menu.x = (w - menu.size[0]) / 2
        menu.y = (h - menu.size[1]) / 2

    def _on_language_selected(self, lang_code: str):
        self._game_engine.select_language(lang_code)
        self._go_to_scene = TitleScreen(self._game_engine)


class TitleScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a title screen.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, _constants.BACKGROUNDS_DIR / 'title_screen.png')
        tm = self._game_engine.texture_manager
        menu = self._add_component(components.Menu(tm, 4, 1))
        lang = self._game_engine.config.active_language
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.new_game'), 'new_game', self._on_new_game))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.load_game'), 'load_game', self._on_load_game))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.settings'), 'settings', self._on_settings))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.quit_game'), 'quit_game', self._on_quit_game))
        w, h = self._game_engine.window_size
        menu.x = (w - menu.size[0]) / 2
        menu.y = (h - menu.size[1]) / 2
        with (_constants.SCREENS_DIR / 'title.json').open(encoding='UTF-8') as f:
            name = json.load(f)['new_game_map']
        self._new_game_map = _map.Map(game_engine, name)
        self._exit_game = False

    def _on_new_game(self, _):
        self._go_to_scene = self._new_game_map

    def _on_load_game(self, _):
        self._go_to_scene = LoadGameScreen(self._game_engine, self)

    def _on_settings(self, _):
        self._go_to_scene = SettingsScreen(self._game_engine, self)

    def _on_quit_game(self, _):
        self._exit_game = True

    def update(self) -> _events.Event | None:
        if self._exit_game:
            return _events.QuitGameEvent()
        return super().update()

    def _reset(self):
        self._exit_game = False


class LoadGameScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen to load a save.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, _constants.BACKGROUNDS_DIR / 'load_game_screen.png')
        # TODO menu


class SettingsScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen change game’s settings.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, _constants.BACKGROUNDS_DIR / 'settings_screen.png')
        # TODO menu


__all__ = [
    'Screen',
    'LanguageSelectScreen',
    'TitleScreen',
]
