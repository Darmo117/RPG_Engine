import datetime
import logging
import sys
import time
import traceback

import pygame

from . import config, constants, errors, events, level, maths, render, scene as scene_
from .screens import screens


class GameEngine:
    def __init__(self):
        self._logger = logging.getLogger('GameEngine')
        pygame.init()
        self._screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
        self._config = config.load_config()
        pygame.display.set_caption(self._config.game_title)
        logging_level = logging.INFO
        if self._config.debug:
            logging_level = logging.DEBUG
        logging.basicConfig(stream=sys.stdout, level=logging_level,
                            format='%(asctime)s (%(name)s) [%(levelname)s] %(message)s')
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

    @property
    def window_size(self) -> tuple[int, int]:
        return pygame.display.get_window_size()

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
            name = type(e).__name__
            tb = ''.join(traceback.format_tb(e.__traceback__))
            message = f'{name}: {e}\n{tb}'
            self._logger.error(message)
            date = datetime.datetime.now().replace(microsecond=0)
            crash_date = str(date).replace(' ', '_').replace(':', '-')
            if not constants.LOGS_DIR.exists():
                constants.LOGS_DIR.mkdir(parents=True)
            with (constants.LOGS_DIR / f'crash_report_{crash_date}.log').open(mode='w', encoding='UTF-8') as f:
                f.write(message)
            return 1
        finally:
            pygame.quit()

    def _loop(self):
        self._active_scene = screens.LanguageSelectScreen(self)
        pygame.key.set_repeat(300, 150)
        clock = pygame.time.Clock()
        self._running = True
        while self._running:
            if not self._active_scene:
                raise errors.NoSceneError()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    break
                if self._update_scene:
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

            clock.tick(60)
            pygame.display.flip()

    def _handle_event(self, event: events.Event):
        in_level = isinstance(self._active_scene, level.Level)
        match event:
            case events.ToggleSceneUpdateEvent(should_update=update):
                self._update_scene = update
            case events.ChangeLevelEvent(level_name=level_name, spawn_location=spawn_location):
                self.load_level(level_name, spawn_location)
            case events.GoToScreenEvent(screen=screen):
                self.load_screen(screen)
            case events.SpawnEntityEvent(at=at) as e if in_level:
                self._active_scene.spawn_entity(e.get_entity(self._active_scene), at)
            case events.DisplayDialogEvent(text_key=text_key) as e if in_level:
                text = self._config.active_language.translate(text_key, **e.kwargs)
                print(text)  # TODO properly display dialog
            case events.WaitEvent(milliseconds=ms):
                self._event_wait_delay = ms
                self._event_wait_start_time = _time_millis()
            case events.QuitGameEvent():
                self.stop()
            case e:
                self._logger.warning(f'Unexpected event: {e}')

    def load_level(self, name: str, player_spawn_location: pygame.Vector2):
        lvl = self._level_loader.load_level(name)
        lvl.spawn_player(player_spawn_location)
        self._transition_to_scene(lvl)

    def load_screen(self, screen: screens.Screen):
        self._transition_to_scene(screen, fade_out_duration=0)

    def _transition_to_scene(self, scene: scene_.Scene, fade_out_duration: int = 250):
        if not self._active_scene or fade_out_duration == 0:
            self._active_scene = scene
        else:
            self._scene_transition = _SceneTransition(self, fade_out_duration, scene)

    def stop(self):
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


__all__ = [
    'GameEngine',
]
