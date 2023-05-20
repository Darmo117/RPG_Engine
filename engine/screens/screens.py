from __future__ import annotations

import abc
import json
import math
import pathlib
import typing as _typ

import pygame

from . import components
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
        if component not in self._components:
            self._components.append(component)
        return component

    def _is_submenu_visible(self):
        return any(isinstance(comp, components.Menu) and comp.parent and comp.is_visible for comp in self._components)

    def on_input_event(self, event: pygame.event.Event):
        if not super().on_input_event(event):
            if (self.parent and not self._is_submenu_visible() and event.type == pygame.KEYDOWN
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
            self._config.music_effects_volume, self._on_master_volume))
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
        self._config.music_effects_volume = self._cycle_sound(self._config.music_effects_volume)
        self._config.save()
        button.data = self._config.music_effects_volume

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
            with (constants.DATA_DIR / f'credits-{lang.code}.txt').open(mode='r', encoding='UTF-8') as f:
                text = f.read()
            text = text.replace('${game_title}', self._game_engine.config.game_title)
        except FileNotFoundError:
            self._logger.warning(f'Missing credits file for language "{lang.code}"!')
            text = '§c#ff0000§b' + lang.translate('screen.credits.missing_file')
        text_area = self._add_component(components.TextArea(self._game_engine, text))
        w, h = self._game_engine.window_size
        text_area.w = math.floor(w * 0.8)
        text_area.h = math.floor(h * 0.8)
        text_area.set_center()


class KeyboardSettingsScreen(Screen):
    def __init__(self, game_engine, parent: Screen = None):
        """Create a screen to change keyboard settings.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The screen that lead to this one.
        """
        self._init = True
        super().__init__(game_engine, parent, constants.BACKGROUNDS_DIR / 'keyboard_settings_screen.png')
        translate = game_engine.config.active_language.translate
        actions = config.InputConfig.ACTION_DEFAULTS.keys()
        # Make local copy of keybinds and modify that until user confirms
        self._keybinds = game_engine.config.inputs.copy()

        self._menu = self._add_component(components.Menu(game_engine, 2 * len(actions) + 1,
                                                         config.InputConfig.MAX_KEYS, gap=0))
        for action_name in actions:
            self._menu.add_item(components.Label(game_engine, '§b' + translate(f'input.{action_name}')))
            for _ in range(self._menu.grid_width - 1):
                self._menu.add_item(components.Spacer(game_engine))
            inputs = self._keybinds.get_keys(action_name)
            for i in range(self._menu.grid_width):
                self._menu.add_item(components.Button(
                    game_engine,
                    translate('screen.keyboard_settings.menu.key_name_format', id=i + 1),
                    str(i),
                    data_label_format=lambda d: '§u' + io.get_key_name(d[1]) if d[1] is not None else '',
                    data=(action_name, inputs[i] if inputs[i] >= 0 else None),
                    action=self._on_button,
                ))
        self._menu.add_item(components.Button(
            game_engine, '§c#00e000' + translate('screen.keyboard_settings.menu.confirm'), 'confirm',
            action=self._on_confirm))
        self._menu.add_item(components.Button(
            game_engine, '§c#e00000' + translate('screen.keyboard_settings.menu.reset'), 'reset',
            action=self._on_reset))
        for _ in range(self._menu.grid_width - 2):
            self._menu.add_item(components.Spacer(game_engine))
        for c in range(self._menu.grid_width):
            self._menu.set_column_width(c, 200)
        self._menu.set_center()

        self._action_choice_menu = self._add_component(components.Menu(game_engine, 2, 3, parent=self._menu))
        self._action_choice_menu.add_item(components.Label(
            game_engine, translate('screen.keyboard_settings.menu.action_choice_menu.label')))
        self._action_choice_menu.add_item(components.Spacer(game_engine))
        self._action_choice_menu.add_item(components.Spacer(game_engine))
        self._action_choice_menu.add_item(components.Button(
            game_engine, translate('screen.keyboard_settings.menu.action_choice_menu.change_keybind'),
            'change_keybind', action=self._on_change_keybind))
        self._action_choice_menu.add_item(components.Button(
            game_engine, translate('screen.keyboard_settings.menu.action_choice_menu.remove_keybind'),
            'remove_keybind', action=self._on_remove_keybind))
        self._action_choice_menu.add_item(components.Button(
            game_engine, translate('screen.keyboard_settings.menu.action_choice_menu.cancel'),
            'cancel', action=lambda _: self._action_choice_menu.hide()))
        self._action_choice_menu.set_center()
        self._action_choice_menu.hide()

        self._set_key_menu = self._add_component(_KeyMenu(game_engine, self._menu, self._on_key_typed))
        self._set_key_menu.set_center()
        self._set_key_menu.hide()
        self._init = False

    def _on_confirm(self, _=None, go_back: bool = True):
        self._game_engine.config.inputs.update(self._keybinds)
        self._game_engine.config.save()
        if go_back:
            self._fire_screen_event(self.parent)

    def _on_reset(self, _=None):
        self._keybinds.reset()
        for r, action_name in enumerate(config.InputConfig.ACTION_DEFAULTS):
            inputs = self._keybinds.get_keys(action_name)
            for c in range(self._menu.grid_width):
                self._menu.get_button(2 * r + 1, c).data = (action_name, inputs[c] if c < len(inputs) else None)
        self._on_confirm(go_back=False)

    def _on_button(self, _):
        if self._menu.get_selected_button().data[1] is not None:
            self._action_choice_menu.show()
        else:
            self._set_key_menu.show()

    def _on_change_keybind(self, _):
        self._action_choice_menu.hide()
        self._set_key_menu.show()

    def _on_remove_keybind(self, _):
        self._action_choice_menu.hide()
        button = self._menu.get_selected_button()
        if self._keybinds.remove_key(button.data[0], int(button.name)):
            button.data = (button.data[0], None)

    def _on_key_typed(self, menu: _KeyMenu):
        if self._init:
            return
        button = self._menu.get_selected_button()
        self._keybinds.remove_key(button.data[0], int(button.name))
        button.data = (button.data[0], menu.typed_key)
        self._keybinds.set_key(button.data[0], int(button.name), button.data[1])

    def on_input_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == pygame.BUTTON_MIDDLE:
            self._on_reset()
            return True
        return super().on_input_event(event)


class _KeyMenu(components.Menu):
    def __init__(self, game_engine, parent, on_hide: _typ.Callable[[_KeyMenu], None]):
        """Create a menu that captures a keystroke.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: The menu opened this one.
        :param on_hide: A function to call when this menu is hidden.
        """
        # noinspection PyTypeChecker
        super().__init__(game_engine, 1, 1, parent=parent, on_hide=on_hide)
        self._label = self.add_item(components.Label(
            game_engine,
            game_engine.config.active_language.translate('screen.keyboard_settings.menu.key_menu.label'))
        )
        self._typed_key = None

    @property
    def typed_key(self) -> int | None:
        return self._typed_key

    def show(self):
        super().show()
        self._typed_key = None

    def on_event(self, event: pygame.event.Event):
        if not self.is_visible or not self.has_focus:
            return False
        if self._typed_key is None and event.type == pygame.KEYDOWN:
            self._typed_key = event.key
            self.hide()
            return True
        return super().on_event(event)


__all__ = [
    'Screen',
    'LanguageSelectScreen',
    'TitleScreen',
    'LoadGameScreen',
    'SettingsScreen',
    'CreditsScreen',
    'KeyboardSettingsScreen',
]
