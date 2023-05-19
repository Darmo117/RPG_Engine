import argparse
import dataclasses
import datetime
import logging
import pathlib
import sys
import time
import traceback

import pygame

from . import config, constants, errors, events, level, maths, render, scene as scene_
from .screens import screens, texts


def run(*argv: str) -> int:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', '--debug', action='store_true', help='run in debug mode')
    arg_parser.add_argument('-r', '--run-path', type=str, help='path to the directory containing the data directory')
    try:
        args = arg_parser.parse_args(argv)
    except SystemExit as e:
        # Prevent exit, return error code instead
        return e.code
    cli_args = _CLIArgs(
        debug=args.debug,
        run_dir=args.run_path,
    )
    try:
        return GameEngine(cli_args).run()
    except BaseException as e:  # Catch errors that may occur before game loop starts
        print(_generate_crash_report(e), file=sys.stderr)
        return 1


@dataclasses.dataclass(frozen=True)
class _CLIArgs:
    debug: bool
    run_dir: pathlib.Path = None


class GameEngine:
    NAME = 'RPG Engine'
    VERSION = '1.0'

    FPS = 60

    def __init__(self, args: _CLIArgs):
        self._logger = logging.getLogger(self.__class__.__qualname__)
        pygame.init()
        constants.init(root=args.run_dir)
        self._config = config.load_config(debug=args.debug)
        self._window = pygame.display.set_mode(self._config.base_screen_size, pygame.RESIZABLE)
        self._screen = pygame.Surface(self._config.base_screen_size)
        pygame.display.set_caption(self._config.game_title)

        if self._config.debug:
            logging_level = logging.DEBUG
        else:
            logging_level = logging.INFO
        logging.basicConfig(
            stream=sys.stdout,
            level=logging_level,
            format='%(asctime)s.%(msecs)03d (%(name)s) [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
        self._logger.debug(f'Config: {self._config}')
        self._texture_manager = render.TexturesManager(self._config.font)
        self._level_loader = level.LevelLoader(self)
        self._active_scene: scene_.Scene | None = None
        self._scene_transition: _SceneTransition | None = None
        self._events_queue = []
        self._event_wait_delay = 0
        self._event_wait_start_time = 0
        self._update_scene = True
        self._running = False
        self._clock = pygame.time.Clock()
        self._show_debug_info = self._config.debug

    @property
    def config(self) -> config.Config:
        return self._config

    @property
    def texture_manager(self) -> render.TexturesManager:
        return self._texture_manager

    @property
    def active_scene(self) -> scene_.Scene:
        return self._active_scene

    def _set_active_scene(self, scene: scene_.Scene):
        self._active_scene = scene

    def select_language(self, code: str):
        self._config.set_active_language(code)
        self._config.save()

    @property
    def window_size(self) -> tuple[int, int]:
        return self._screen.get_size()

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    def fire_event(self, event: events.Event):
        self._events_queue.append(event)

    def run(self) -> int:
        """Runs the game engine.

        :return: An error code; 0 if engine terminated normally.
        """
        try:
            self._loop()
            return 0
        except BaseException as e:
            self._logger.error(_generate_crash_report(e, scene=self.active_scene))
            return 1
        finally:
            pygame.quit()

    def _loop(self):
        if not self._config.active_language:
            self._active_scene = screens.LanguageSelectScreen(self)
        else:
            self._active_scene = screens.TitleScreen(self)

        pygame.key.set_repeat(300, 150)
        self._running = True
        while self._running:
            if not self._active_scene:
                raise errors.NoSceneError()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._stop()
                    break
                if self._config.debug and event.type == pygame.KEYDOWN and event.key == pygame.K_F3:
                    self._show_debug_info = not self._show_debug_info
                if self._update_scene and not self._scene_transition:
                    self._active_scene.on_input_event(event)

            if self._scene_transition:
                self._scene_transition.update()
                if self._scene_transition.is_done:
                    self._scene_transition = None
            else:
                if self._update_scene:
                    self._active_scene.update()

                delay_expired = (self._event_wait_delay == 0
                                 or _time_millis() - self._event_wait_start_time >= self._event_wait_delay)
                if delay_expired and self._events_queue:
                    if self._event_wait_delay != 0:
                        self._event_wait_delay = 0
                    event = self._events_queue.pop(0)
                    self._handle_event(event)
                    if next_event := event.next:
                        # Insert next event at start of queue
                        self._events_queue.insert(0, next_event)

            self._active_scene.draw(self._screen)
            if self._scene_transition:
                self._scene_transition.draw(self._screen)

            if self._show_debug_info:
                self._draw_debug_info()

            self._window.fill((0, 0, 0))
            image = self._scale_screen()
            x = (self._window.get_width() - image.get_width()) / 2
            y = (self._window.get_height() - image.get_height()) / 2
            self._window.blit(image, (x, y))
            self._clock.tick(self.FPS)
            pygame.display.flip()

    def _draw_debug_info(self):
        fps = round(self._clock.get_fps())
        if fps <= 30:
            color = 'ff0000'
        elif fps <= 40:
            color = 'da7422'
        else:
            color = 'ffffff'
        s = f"""
§bDebug info (F3 to toggle)
§c#{color}FPS: {fps}
Scene type: {type(self._active_scene).__qualname__}
""".strip()
        if isinstance(self._active_scene, level.Level):
            s += f"""
Level name: {self._active_scene.name}
Entities: {len(self._active_scene.entity_set)}
""".rstrip()
        lines = texts.parse_lines(s)
        tm = self._texture_manager
        y = 5
        x = 5
        for line in lines:
            line.draw(tm, self._screen, (x, y))
            y += line.get_size(tm)[1]

    def _scale_screen(self) -> pygame.Surface:
        r = self._config.screen_ratio
        ww, wh = self._window.get_size()
        w = ww
        h = w / r
        if h > wh:
            h = wh
            w = h * r
        return pygame.transform.smoothscale(self._screen, (w, h))

    def _handle_event(self, event: events.Event):
        in_level = isinstance(self._active_scene, level.Level)
        match event:
            case events.ToggleSceneUpdateEvent(should_update=update):
                self._update_scene = update
            case events.ChangeLevelEvent(level_name=level_name, spawn_location=spawn_location):
                self.load_level(level_name, spawn_location)
            case events.GoToScreenEvent(screen=screen):
                self.load_screen(screen)
            case events.SpawnEntityEvent(entity_supplier=entity_supplier, at=at) if in_level:
                # noinspection PyTypeChecker
                lvl: level.Level = self._active_scene
                lvl.spawn_entity(entity_supplier, at)
            case events.DisplayDialogEvent(text_key=text_key) as e if in_level:
                text = self._config.active_language.translate(text_key, **e.kwargs)
                print(text)  # TODO properly display dialog
            case events.WaitEvent(milliseconds=ms):
                self._event_wait_delay = ms
                self._event_wait_start_time = _time_millis()
            case events.QuitGameEvent():
                self._stop()
            case e:
                self._logger.warning(f'Unexpected event: {e}')

    def load_level(self, name: str, player_spawn_location: pygame.Vector2):
        lvl = self._level_loader.load_level(name)
        lvl.spawn_player(player_spawn_location)
        self._transition_to_scene(lvl, fade_out_duration=500)

    def load_screen(self, screen: screens.Screen):
        duration = 0 if isinstance(self._active_scene, screens.Screen) else 500
        self._transition_to_scene(screen, fade_out_duration=duration)

    def _transition_to_scene(self, scene: scene_.Scene, fade_out_duration: int = 250):
        if not self._active_scene or fade_out_duration == 0:
            self._active_scene = scene
        else:
            self._scene_transition = _SceneTransition(self, fade_out_duration, scene)

    def _stop(self):
        self._running = False


def _time_millis() -> int:
    return time.time_ns() // 1_000_000


class _SceneTransition:
    def __init__(self, engine: GameEngine, fade_out_duration: int, queued_scene: scene_.Scene):
        self._engine = engine
        self._fade_out_duration = fade_out_duration
        self._start_time = _time_millis()
        self._queued_scene = queued_scene
        self._fading_out = True
        self._done = False

    @property
    def is_done(self) -> bool:
        return self._done

    def update(self):
        if self._done:
            return
        diff = _time_millis() - self._start_time
        if self._fading_out and diff >= self._fade_out_duration:
            self._fading_out = False
            self._start_time = _time_millis()  # Reset start time for fade-in
            # noinspection PyProtectedMember
            self._engine._set_active_scene(self._queued_scene)
        elif not self._fading_out and diff >= self._fade_out_duration:
            self._done = True

    def draw(self, screen: pygame.Surface):
        diff = _time_millis() - self._start_time
        progress = diff / self._fade_out_duration
        if not self._fading_out:
            progress = 1 - progress
        surface = pygame.Surface(screen.get_size()).convert_alpha()
        alpha = maths.clamp(progress * 255, 0, 255)
        surface.fill((0, 0, 0, alpha))
        screen.blit(surface, (0, 0))


def _generate_crash_report(e: BaseException, scene: scene_.Scene = None) -> str:
    tb = ''.join(traceback.format_tb(e.__traceback__))
    date = datetime.datetime.now()
    message = f"""\
--- {GameEngine.NAME} (v{GameEngine.VERSION}) Crash Report ---

Time: {date.strftime("%Y-%m-%d %H:%M:%S")}
Description: {e} 

{e.__class__.__name__}: {e}
{tb}
"""
    if scene:
        message += f"""\
-- Affected Scene --
Type: {scene.__module__}.{scene.__class__.__qualname__}
"""
    if not constants.LOGS_DIR.exists():
        constants.LOGS_DIR.mkdir(parents=True)
    crash_date = date.strftime('%Y-%m-%d_%H.%M.%S')
    with (constants.LOGS_DIR / f'crash_report_{crash_date}.log').open(mode='w', encoding='UTF-8') as f:
        f.write(message)
    return message


__all__ = [
    'run',
    'GameEngine',
]
