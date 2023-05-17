from __future__ import annotations

import abc
import json
import math
import pathlib
import typing as _typ

import pygame

from . import components, texts
from .. import config, constants, events, game_state, i18n, io, scene

_C = _typ.TypeVar('_C', bound=components.Component)


class Screen(scene.Scene, abc.ABC):
    def __init__(self, game_engine, parent: Screen = None, background_image: str | pathlib.Path = None):
        """Create a screen.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        :param background_image: Path to the screen’s background image.
        """
        super().__init__(game_engine, parent)
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
            if (self.parent and event.type == pygame.KEYDOWN
                    and event.key in self._get_keys(config.InputConfig.ACTION_CANCEL_MENU)):
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
        menu = self._add_component(components.Menu(self._game_engine, len(languages), 1))
        for i, language in enumerate(sorted(languages, key=lambda l: l.name)):
            button = components.Button(
                self._game_engine,
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
        ge = self._game_engine
        menu = self._add_component(components.Menu(ge, 5, 1))
        lang = self._game_engine.config.active_language
        menu.add_item(components.Button(
            ge, lang.translate('screen.title.menu.new_game'), 'new_game', action=self._on_new_game))
        menu.add_item(components.Button(
            ge, lang.translate('screen.title.menu.load_game'), 'load_game', action=self._on_load_game,
            enabled=len(game_state.list_saves()) != 0))
        menu.add_item(components.Button(
            ge, lang.translate('screen.title.menu.settings'), 'settings', action=self._on_settings))
        menu.add_item(components.Button(
            ge, lang.translate('screen.title.menu.credits'), 'credits', action=self._on_credits))
        menu.add_item(components.Button(
            ge, lang.translate('screen.title.menu.quit_game'), 'quit_game', action=self._on_quit_game))
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
        self._language = self._config.active_language
        ge = self._game_engine
        menu = self._add_component(components.Menu(ge, 7, 1))
        lang = self._config.active_language
        percent_format = lang.translate('menu.label.percent_format')
        menu.add_item(components.Button(
            ge, lang.translate('screen.settings.menu.keyboard_settings'), 'keyboard_settings',
            action=self._on_keyboard_settings))
        menu.add_item(components.Button(
            ge, lang.translate('screen.settings.menu.language'), 'language', lambda l: l.name,
            self._config.active_language, self._on_language, enabled=len(self._config.languages) > 1))
        menu.add_item(components.Button(
            ge, lang.translate('screen.settings.menu.always_run'), 'always_run', '{}',
            self._on_off_label(self._config.always_run), self._on_always_run))
        menu.add_item(components.Button(
            ge, lang.translate(f'screen.settings.menu.bgm_volume'), 'bgm_volume', percent_format,
            self._config.bg_music_volume, self._on_bgm_volume))
        menu.add_item(components.Button(
            ge, lang.translate(f'screen.settings.menu.bgs_volume'), 'bgs_volume', percent_format,
            self._config.bg_sounds_volume, self._on_bgs_volume))
        menu.add_item(components.Button(
            ge, lang.translate(f'screen.settings.menu.sfx_volume'), 'sfx_volume', percent_format,
            self._config.sound_effects_volume, self._on_menu_volume))
        menu.add_item(components.Button(
            ge, lang.translate(f'screen.settings.menu.master_volume'), 'master_volume', percent_format,
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

    def _on_keyboard_settings(self, _):
        self._fire_screen_event(KeyboardSettingsScreen(self._game_engine, self))

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

    def on_input_event(self, event: pygame.event.Event):
        if (self._language is not self._config.active_language and event.type == pygame.KEYDOWN
                and event.key in self._get_keys(config.InputConfig.ACTION_CANCEL_MENU)):
            # Reset to title screen if language has changed
            self._fire_screen_event(TitleScreen(self._game_engine))
            return True
        return super().on_input_event(event)


class CreditsScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen to change game’s settings.

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
        text_area = self._add_component(components.TextArea(self._game_engine, text))
        w, h = self._game_engine.window_size
        text_area.w = math.floor(w * 0.8)
        text_area.h = math.floor(h * 0.8)
        text_area.x = (w - text_area.size[0]) / 2
        text_area.y = (h - text_area.size[1]) / 2


class KeyboardSettingsScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen to change keyboard settings.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'keyboard_settings_screen.png')
        actions = config.InputConfig.ACTION_DEFAULTS.keys()
        menu = self._add_component(components.Menu(game_engine, 2 * len(actions), 3, gap=0))
        for action_name in actions:
            translate = game_engine.config.active_language.translate
            menu.add_item(components.Label(game_engine, '§b' + translate(f'input.{action_name}')))
            for _ in range(menu.grid_width - 1):
                menu.add_item(components.Spacer(game_engine))
            inputs = game_engine.config.inputs.get_keys(action_name)
            for i in range(menu.grid_width):
                input_ = inputs[i] if i < len(inputs) else None
                menu.add_item(components.Button(
                    game_engine,
                    '§u' + translate('screen.keyboard_settings.menu.key_name_format', id=i + 1),
                    f'{actions}_{i + 1}',
                    data_label_format=lambda data: '§c#00ff00' + io.get_key_name(data) if data is not None else '',
                    data=input_
                ))
        menu.x = (game_engine.window_size[0] - menu.size[0]) / 2
        menu.y = (game_engine.window_size[1] - menu.size[1]) / 2

    class Keyboard(components.Menu):
        # FIXME key codes are not bound to physical keys
        def __init__(self, game_engine):
            """Create a keyboard.

            :param game_engine: The game engine.
            :type game_engine: engine.game_engine.GameEngine
            """
            super().__init__(game_engine, 5, 23, gap=0)
            size = (int((2 / 3 * game_engine.window_size[0]) / self._grid_width),
                    int((1 / 3 * game_engine.window_size[1]) / self._grid_height))
            self.w = self._grid_width * (size[0] + 10)
            self.h = self._grid_height * (size[1] + 10)

            # Row 1
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_ESCAPE, self._on_key_change, size))
            self._spacer(size)
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F1, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F2, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F3, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F4, self._on_key_change, size))
            self._spacer(size)
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F5, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F6, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F7, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F8, self._on_key_change, size))
            self._spacer(size)
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F9, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F10, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F11, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_F12, self._on_key_change, size))
            self._spacer(size)  # ScreenCap skipped
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_SCROLLLOCK, self._on_key_change, size))
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_PAUSE, self._on_key_change, size))
            self._spacer(size)
            self._spacer(size)
            self._spacer(size)
            self._spacer(size)

            # Row 2
            self.add_item(KeyboardSettingsScreen.Key(game_engine, pygame.K_DOLLAR, self._on_key_change,
                                                     (size[0] * 1.3, size[1])))

        def _spacer(self, size: tuple[int, int]):
            s = components.Spacer(self._game_engine, padding=5)
            s.w, s.h = size
            self.add_item(s)

        def _update_size(self, row: int, col: int, new_component: components.Button | components.Spacer):
            if col == 0:
                new_component.x = self._padding
            else:
                prev_key = self._grid[row][col - 1]
                new_component.x = prev_key.x + prev_key.size[0]
            if row == 0:
                new_component.y = self._padding
            else:
                above_key = self._grid[row - 1][col]
                new_component.y = above_key.y + above_key.size[1]

        def _on_key_change(self, button: components.Button):
            pass  # TODO

    class Key(components.Button):
        def __init__(self, game_engine, key: int, action: _typ.Callable[[components.Button], None],
                     size: tuple[float, float]):
            """Create a keyboard key.

            :param game_engine: The game engine.
            :type game_engine: engine.game_engine.GameEngine
            :param key: The keyboard key code this component corresponds to.
            :param action: Action to execute when this button is activated.
            :param size: Key’s size.
            """

            def format_(data):
                if not data:
                    return ''
                return game_engine.config.active_language.translate(f'input.{data}')

            super().__init__(
                game_engine,
                io.get_key_name(key),
                str(key),
                data_label_format=format_,
                data=game_engine.config.inputs.get_action(key),
                action=action
            )
            self.w, self.h = size

        def _update_image(self):
            tm = self._tm
            self._image = pygame.Surface(self.size, pygame.SRCALPHA)
            if self._selected:
                color = (50, 50, 50)
            else:
                color = (0, 0, 0)
            self._image.fill((*color, 200))
            label = texts.parse_line(self._raw_label)
            label.draw(tm, self._image, (self._padding, self._padding))
            if self._data_label_format:
                data_label = texts.parse_line(self._get_data_label())
                data_label.draw(tm, self._image, (self._padding, self._padding + self._padding + label.get_size(tm)[1]))


__all__ = [
    'Screen',
    'LanguageSelectScreen',
    'TitleScreen',
    'LoadGameScreen',
    'SettingsScreen',
    'CreditsScreen',
    'KeyboardSettingsScreen',
]
