import configparser as _cp
import datetime
import logging
import sys
import traceback

import pygame

from . import _config, _constants, _errors, _events, _i18n, _scene, _textures
from ._screens import screens as _sc


class GameEngine:
    def __init__(self):
        self._logger = logging.getLogger('GameEngine')
        pygame.init()
        self._screen = pygame.display.set_mode((_constants.SCREEN_WIDTH, _constants.SCREEN_HEIGHT))
        self._config = self._load_config()
        pygame.display.set_caption(self._config.game_title)
        logging_level = logging.INFO
        if self._config.debug:
            logging_level = logging.DEBUG
        logging.basicConfig(stream=sys.stdout, level=logging_level,
                            format='%(asctime)s (%(name)s) [%(levelname)s] %(message)s')
        self._logger.debug(f'Config: {self._config}')
        self._texture_manager = _textures.TexturesManager(self._config.font)
        self._active_scene: _scene.Scene | None = None
        self._running = False

    def _load_config(self) -> _config.Config:
        self._logger.info('Loading configuration…')
        parser = _cp.ConfigParser()
        with _constants.GAME_INIT_FILE.open(encoding='UTF-8') as f:
            parser.read_file(f)
        font = pygame.font.SysFont(
            parser.get('Game', 'font', fallback='Tahoma'),
            parser.getint('Game', 'font_size', fallback=15)
        )
        config = _config.Config(
            game_title=parser.get('Game', 'title', fallback='Game'),
            font=font,
            languages=list(map(_i18n.Language, _constants.LANGS_DIR.glob('*.json'))),
            debug=parser.getboolean('Game', 'debug', fallback=False)
        )
        self._logger.info('Done.')
        return config

    @property
    def config(self) -> _config.Config:
        return self._config

    @property
    def texture_manager(self) -> _textures.TexturesManager:
        return self._texture_manager

    @property
    def active_scene(self) -> _scene.Scene:
        return self._active_scene

    def set_active_scene(self, scene: _scene.Scene):
        # TODO trigger fade-out/fade-in transition in game loop
        self._active_scene = scene

    def select_language(self, code: str):
        self._config.set_active_language(code)

    @property
    def window_size(self) -> tuple[int, int]:
        return pygame.display.get_window_size()

    @property
    def logger(self) -> logging.Logger:
        return self._logger

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
            if not _constants.LOGS_DIR.exists():
                _constants.LOGS_DIR.mkdir(parents=True)
            with (_constants.LOGS_DIR / f'crash_report_{crash_date}.log').open(mode='w', encoding='UTF-8') as f:
                f.write(message)
            return 1
        finally:
            pygame.quit()

    def _loop(self):
        self._active_scene = _sc.LanguageSelectScreen(self)
        pygame.key.set_repeat(300, 150)
        clock = pygame.time.Clock()
        self._running = True
        while self._running:
            if not self._active_scene:
                raise _errors.NoSceneError()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    break
                self._active_scene.on_event(event)

            event = self._active_scene.update()
            self._active_scene.draw(self._screen)
            if event:
                event.execute(self)

            clock.tick(60)
            pygame.display.flip()

    def stop(self):
        self._running = False


__all__ = [
    'GameEngine',
]
