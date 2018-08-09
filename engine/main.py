import configparser as cp
import datetime
import logging
import os
import sys
import traceback

import pygame

from engine import global_values as gv, game_map, entities, texture_manager as tl, config, i18n

_LOGGER = logging.getLogger(__name__)


def _init_config():
    parser = cp.ConfigParser()
    # noinspection PyShadowingNames
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


def _run():
    _init_config()

    logging_level = logging.INFO
    if gv.CONFIG.debug:
        logging_level = logging.DEBUG
    logging.basicConfig(stream=sys.stdout, level=logging_level,
                        format="%(asctime)s (%(name)s) [%(levelname)s] %(message)s")
    _LOGGER.debug(f"Config: {gv.CONFIG}")
    screen = pygame.display.set_mode((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT))
    pygame.display.set_caption(gv.CONFIG.title)

    gv.TEXTURE_MANAGER = tl.TexturesManager(pygame.font.SysFont("Tahoma", 15))
    gv.CONFIG.language_index = 1  # TEMP
    gv.I18N = i18n.I18n(gv.CONFIG.language_index)
    gv.PLAYER_DATA = entities.PlayerData()

    _loop(screen)

    return 0


def _loop(screen):
    current_map = game_map.Map(gv.CONFIG.start_map)
    clock = pygame.time.Clock()
    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                break
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            current_map.player.go_up()
        elif keys[pygame.K_DOWN]:
            current_map.player.go_down()
        if keys[pygame.K_LEFT]:
            current_map.player.go_left()
        elif keys[pygame.K_RIGHT]:
            current_map.player.go_right()

        door = current_map.update()
        current_map.draw(screen)
        if door is not None:
            current_map = game_map.Map(door.destination_map, start_door_id=door.id)
        clock.tick(60)
        pygame.display.flip()


# noinspection PyShadowingNames
def run() -> int:
    """
    Runs the game engine.

    :return: An error code; 0 if engine terminated normally.
    """
    pygame.init()

    try:
        _run()
        error = 0
    except BaseException as e:
        name = type(e).__name__
        tb = "".join(traceback.format_tb(e.__traceback__))
        message = f"{name}: {e}\n{tb}"
        _LOGGER.error(message)
        date = datetime.datetime.now().replace(microsecond=0)
        crash_date = str(date).replace(" ", "_").replace(":", "-")
        with open(os.path.join(gv.LOG_DIR, f"crash_report_{crash_date}.log"), mode="w", encoding="UTF-8") as f:
            f.write(message)
        error = 1

    pygame.quit()

    return error


if __name__ == "__main__":
    error = run()
    sys.exit(error)
