import configparser as cp
import datetime
import logging
import os
import sys
import time
import traceback

import pygame

from . import actions, config, controllable, entities, game_map, global_values as gv, menus, texture_manager as tl


class GameEngine:
    _LOGGER = logging.getLogger('GameEngine')

    def __init__(self):
        parser = cp.ConfigParser()
        with open(gv.GAME_INIT_FILE, encoding='UTF-8') as f:
            parser.read_file(f)
        cfg = dict(parser['Game'])
        if 'languages' in cfg:
            cfg['languages'] = cfg['languages'].split("|")
        if "debug" in cfg:
            if cfg['debug'] == 'true':
                v = True
            elif cfg['debug'] == 'false':
                v = False
            else:
                raise ValueError(f"'{cfg['debug']}' cannot be converted to boolean!")
            cfg['debug'] = v
        gv.CONFIG = config.Config(**cfg)

        self._current_map = None
        self._current_screen = None

    @property
    def current_map(self):
        return self._current_map

    @current_map.setter
    def current_map(self, value: game_map.Map):
        self._current_map = value

    @property
    def current_screen(self) -> menus.AbstractScreen:
        return self._current_screen

    @current_screen.setter
    def current_screen(self, value: menus.AbstractScreen):
        self._current_screen = value

    def run(self) -> int:
        """
        Runs the game engine.

        :return: An error code; 0 if engine terminated normally.
        """
        pygame.init()

        try:
            self._run()
            error = 0
        except BaseException as e:
            name = type(e).__name__
            tb = "".join(traceback.format_tb(e.__traceback__))
            message = f"{name}: {e}\n{tb}"
            self._LOGGER.error(message)
            date = datetime.datetime.now().replace(microsecond=0)
            crash_date = str(date).replace(" ", "_").replace(":", "-")
            with open(os.path.join(gv.LOG_DIR, f"crash_report_{crash_date}.log"), mode="w", encoding="UTF-8") as f:
                f.write(message)
            error = 1

        pygame.quit()

        return error

    def _run(self):
        logging_level = logging.INFO
        if gv.CONFIG.debug:
            logging_level = logging.DEBUG
        logging.basicConfig(stream=sys.stdout, level=logging_level,
                            format="%(asctime)s (%(name)s) [%(levelname)s] %(message)s")
        self._LOGGER.debug(f"Config: {gv.CONFIG}")
        screen = pygame.display.set_mode((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT))
        pygame.display.set_caption(gv.CONFIG.title)

        gv.TEXTURE_MANAGER = tl.TexturesManager(pygame.font.SysFont("Tahoma", 15))
        gv.PLAYER_DATA = entities.PlayerData()

        self._loop(screen)

        return 0

    def _loop(self, screen: pygame.Surface):
        transition = None

        def get_transition(c: controllable.Controllable, trans):
            """Updates and draws a controllable component. May return a transition."""
            if c is not None:
                c.controls_enabled = trans is None
                action = c.update()
                c.draw(screen)
                if action is not None:
                    return _Transition(action)
            return None

        self._current_screen = menus.TitleScreen()

        clock = pygame.time.Clock()
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    break
                if self._current_screen is not None:
                    self._current_screen.on_event(event)
                if self._current_map is not None:
                    self._current_map.on_event(event)

            t1 = get_transition(self._current_screen, transition)
            t2 = get_transition(self._current_map, transition)

            if t1 is not None:
                transition = t1
            if t2 is not None:
                transition = t2

            if transition is not None:
                transition.update(self)
                transition.draw(screen)
                if transition.finished:
                    transition = None

            clock.tick(60)
            pygame.display.flip()


class _Transition:
    """This class adds a fade out/fade in effect to transitions between actions."""

    FADE_IN = -1
    FADE_OUT = 1

    FADE_LENGTH = 0.2
    FRAMES_NUMBER = 20
    FRAMES_INTERVAL = FADE_LENGTH / FRAMES_NUMBER

    def __init__(self, action: actions.AbstractAction):
        """
        Creates a transition.

        :param action: Action to execute between fade out and fade in effects.
        """
        self._action = action
        self._fade_direction = self.FADE_OUT
        self._frame = 0
        self._timer = 0
        self._image = None
        self._faded_out = False
        self._finished = False

    @property
    def finished(self):
        return self._finished

    def update(self, engine: GameEngine):
        if self._finished:
            return

        if self._frame == self.FRAMES_NUMBER:
            if not self._faded_out:
                self._faded_out = True
                self._action.execute(engine)
                self._fade_direction = self.FADE_IN
                self._frame = 0
            else:
                self._finished = True

        if time.time() - self._timer >= self.FRAMES_INTERVAL:
            alpha = int((self._frame / self.FRAMES_NUMBER) * 255)
            if self._fade_direction == self.FADE_IN:
                alpha = 255 - alpha
            # noinspection PyArgumentList
            self._image = pygame.Surface((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT), pygame.SRCALPHA, 32).convert_alpha()
            self._image.fill((0, 0, 0, alpha))
            self._frame += 1
            self._timer = time.time()

    def draw(self, screen: pygame.Surface):
        if self._image is not None:
            screen.blit(self._image, (0, 0))


if __name__ == "__main__":
    sys.exit(GameEngine().run())
