import configparser as cp
import datetime
import functools as ft
import logging
import os
import sys
import traceback

import pygame

from engine import global_values as gv, game_map, entities, texture_manager as tl, config, i18n, menus


class GameEngine:
    _LOGGER = logging.getLogger(__name__ + ".GameEngine")

    TITLE = 0
    LEVEL = 1
    INVENTORY = 2

    def __init__(self):
        parser = cp.ConfigParser()
        with open(gv.GAME_INIT_FILE, encoding="UTF-8") as f:
            parser.read_file(f)
        cfg = dict(parser["Game"])
        if "languages" in cfg:
            cfg["languages"] = cfg["languages"].split("|")
        if "debug" in cfg:
            if cfg["debug"] == "true":
                v = True
            elif cfg["debug"] == "false":
                v = False
            else:
                raise ValueError(f"'{cfg['debug']}' cannot be converted to boolean!")
            cfg["debug"] = v
        gv.CONFIG = config.Config(**cfg)

        self._state = self.TITLE
        self._current_map = None

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, value: int):
        if value not in [self.TITLE, self.LEVEL, self.INVENTORY]:
            raise ValueError(f"Illegal state '{value}!'")
        self._state = value

    @property
    def current_map(self):
        return self._current_map

    @current_map.setter
    def current_map(self, value: game_map.Map):
        self._current_map = value

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

    def _loop(self, screen):
        def on_language_selected(engine, index):
            gv.CONFIG.language_index = index
            gv.I18N = i18n.I18n(gv.CONFIG.language_index)
            engine.state = self.LEVEL
            engine.current_map = game_map.Map(gv.CONFIG.start_map)

        # noinspection PyTypeChecker
        title_screen = menus.TitleScreen(on_language_selected=ft.partial(on_language_selected, self))

        clock = pygame.time.Clock()
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                    break
                if self._state == self.TITLE:
                    title_screen.on_event(event)

            if self._state == self.TITLE:
                title_screen.update()
                title_screen.draw(screen)
            elif self._state == self.LEVEL:
                door = self._current_map.update()
                self._current_map.draw(screen)
                if door is not None:
                    self._current_map = game_map.Map(door.destination_map, start_door_id=door.id)
            elif self._state == self.INVENTORY:
                pass  # TODO

            clock.tick(60)
            pygame.display.flip()


if __name__ == "__main__":
    sys.exit(GameEngine().run())
