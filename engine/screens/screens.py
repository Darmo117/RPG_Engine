from __future__ import annotations

import abc
import json
import math
import pathlib
import typing as _typ

import pygame

from . import components
from .. import config, constants, events, game_state, i18n, scene

_C = _typ.TypeVar('_C', bound=components.Component)


class Screen(scene.Scene, abc.ABC):
    def __init__(self, game_engine, parent: Screen = None, background_image: str | pathlib.Path = None):
        """Create a screen.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        :param background_image: Path to the screen’s background image.
        """
        super().__init__(parent)
        self._game_engine = game_engine
        self._bg_image = None
        if background_image:
            try:
                self._bg_image = pygame.Surface(
                    self._game_engine.window_size,
                    pygame.SRCALPHA
                ).convert()
                self._bg_image.blit(pygame.image.load(background_image), (0, 0))
            except FileNotFoundError as e:
                self._game_engine.logger.error(e)
                self._bg_image = None
        self._components: list[components.Component] = []

    def _add_component(self, component: _C) -> _C:
        if component in self._components:
            self._components.remove(component)
        self._components.append(component)
        return component

    def on_input_event(self, event: pygame.event.Event):
        if not super().on_input_event(event):
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and self.parent:
                self._fire_screen_event(self.parent)
                return True
            for c in self._components:
                if c.on_event(event):
                    return True
        return False

    def update(self):
        super().update()
        for c in self._components:
            c.update()

    def draw(self, screen: pygame.Surface):
        if self._bg_image:
            screen.blit(self._bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))
        for c in self._components:
            c.draw(screen)

    def _fire_screen_event(self, screen: Screen):
        self._game_engine.fire_event(events.GoToScreenEvent(screen))


class LanguageSelectScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a language selection screen.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'title_screen.png')
        languages = self._game_engine.config.languages
        menu = self._add_component(components.Menu(self._game_engine.texture_manager, len(languages), 1))
        for i, language in enumerate(sorted(languages, key=lambda l: l.name)):
            button = components.Button(
                self._game_engine.texture_manager,
                language.name,
                language.code,
                action=self._on_language_selected
            )
            menu.add_item(button)
        w, h = self._game_engine.window_size
        menu.x = (w - menu.size[0]) / 2
        menu.y = 2 * (h - menu.size[1]) / 3

    def _on_language_selected(self, button: components.Button):
        self._game_engine.select_language(button.name)
        self._fire_screen_event(TitleScreen(self._game_engine))


class TitleScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a title screen.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'title_screen.png')
        tm = self._game_engine.texture_manager
        menu = self._add_component(components.Menu(tm, 5, 1))
        lang = self._game_engine.config.active_language
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.new_game'), 'new_game', action=self._on_new_game))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.load_game'), 'load_game', action=self._on_load_game,
            enabled=len(game_state.list_saves()) != 0))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.settings'), 'settings', action=self._on_settings))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.credits'), 'credits', action=self._on_credits))
        menu.add_item(components.Button(
            tm, lang.translate('screen.title.menu.quit_game'), 'quit_game', action=self._on_quit_game))
        w, h = self._game_engine.window_size
        menu.x = (w - menu.size[0]) / 2
        menu.y = 2 * (h - menu.size[1]) / 3
        # TODO load game events globally in engine
        with (constants.DATA_DIR / 'events.json').open(mode='r', encoding='UTF-8') as f:
            json_data = json.load(f)
        new_game_data = json_data['game_start']
        self._new_game_level_name = new_game_data['level_name']
        self._new_game_player_spawn = pygame.Vector2(*new_game_data['player_spawn'])

    def _on_new_game(self, _):
        self._game_engine.fire_event(events.ChangeLevelEvent(self._new_game_level_name, self._new_game_player_spawn))

    def _on_load_game(self, _):
        self._fire_screen_event(LoadGameScreen(self._game_engine, self))

    def _on_settings(self, _):
        self._fire_screen_event(SettingsScreen(self._game_engine, self))

    def _on_credits(self, _):
        self._fire_screen_event(CreditsScreen(self._game_engine, self))

    def _on_quit_game(self, _):
        self._game_engine.fire_event(events.QuitGameEvent())


class LoadGameScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen to load a save.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'load_game_screen.png')
        # TODO menu


class SettingsScreen(Screen):
    VOLUME_STEP = 20

    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen change game’s settings.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'settings_screen.png')
        self._config = self._game_engine.config
        tm = self._game_engine.texture_manager
        menu = self._add_component(components.Menu(tm, 7, 1))
        lang = self._config.active_language
        percent_format = lang.translate('menu.label.percent_format')
        menu.add_item(components.Button(
            tm, lang.translate('screen.settings.menu.keyboard_config'), 'keyboard_config',
            action=self._on_keyboard_config, enabled=False))
        menu.add_item(components.Button(
            tm, lang.translate('screen.settings.menu.language'), 'language', lambda l: l.name,
            self._config.active_language, self._on_language, enabled=len(self._config.languages) > 1))
        menu.add_item(components.Button(
            tm, lang.translate('screen.settings.menu.always_run'), 'always_run', '{}',
            self._on_off_label(self._config.always_run), self._on_always_run))
        menu.add_item(components.Button(
            tm, lang.translate(f'screen.settings.menu.bgm_volume'), 'bgm_volume', percent_format,
            self._config.bg_music_volume, self._on_bgm_volume))
        menu.add_item(components.Button(
            tm, lang.translate(f'screen.settings.menu.bgs_volume'), 'bgs_volume', percent_format,
            self._config.bg_sounds_volume, self._on_bgs_volume))
        menu.add_item(components.Button(
            tm, lang.translate(f'screen.settings.menu.sfx_volume'), 'sfx_volume', percent_format,
            self._config.sound_effects_volume, self._on_menu_volume))
        menu.add_item(components.Button(
            tm, lang.translate(f'screen.settings.menu.master_volume'), 'master_volume', percent_format,
            self._config.master_volume, self._on_master_volume))
        w, h = self._game_engine.window_size
        menu.x = (w - menu.size[0]) / 2
        menu.y = 2 * (h - menu.size[1]) / 3

    def _on_language(self, button: components.Button):
        current_lang: i18n.Language = button.data
        langs = sorted(self._config.languages, key=lambda l: l.name)
        lang = langs[(langs.index(current_lang) + 1) % len(langs)]
        self._game_engine.select_language(lang.code)
        button.data = lang

    def _on_off_label(self, on: bool) -> str:
        return self._config.active_language.translate('menu.label.' + ('on' if on else 'off'))

    def _on_always_run(self, button: components.Button):
        self._config.always_run = not self._config.always_run
        self._config.save()
        button.data = self._on_off_label(self._config.always_run)

    def _on_keyboard_config(self, _):
        self._fire_screen_event(KeyboardConfigScreen(self._game_engine, self))

    def _on_bgm_volume(self, button: components.Button):
        self._config.bg_music_volume = self._cycle_sound(self._config.bg_music_volume)
        self._config.save()
        button.data = self._config.bg_music_volume

    def _on_bgs_volume(self, button: components.Button):
        self._config.bg_sounds_volume = self._cycle_sound(self._config.bg_sounds_volume)
        self._config.save()
        button.data = self._config.bg_sounds_volume

    def _on_menu_volume(self, button: components.Button):
        self._config.sound_effects_volume = self._cycle_sound(self._config.sound_effects_volume)
        self._config.save()
        button.data = self._config.sound_effects_volume

    def _on_master_volume(self, button: components.Button):
        self._config.master_volume = self._cycle_sound(self._config.master_volume)
        self._config.save()
        button.data = self._config.master_volume

    def _cycle_sound(self, volume: int) -> int:
        return (volume + self.VOLUME_STEP) % (config.Config.MAX_VOLUME + self.VOLUME_STEP)


class CreditsScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen change game’s settings.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'credits_screen.png')
        lang = self._game_engine.config.active_language
        try:
            with (constants.LANGS_DIR / f'credits-{lang.code}.txt').open(mode='r', encoding='UTF-8') as f:
                text = f.read()
            text = text.replace('${game_title}', self._game_engine.config.game_title)
        except FileNotFoundError:
            text = 'Missing credits file!'
        text_area = self._add_component(components.TextArea(self._game_engine.texture_manager, text))
        w, h = self._game_engine.window_size
        text_area.w = math.floor(w * 0.8)
        text_area.h = math.floor(h * 0.8)
        text_area.x = (w - text_area.size[0]) / 2
        text_area.y = (h - text_area.size[1]) / 2


__all__ = [
    'Screen',
    'LanguageSelectScreen',
    'TitleScreen',
    'LoadGameScreen',
    'SettingsScreen',
    'CreditsScreen',
]
