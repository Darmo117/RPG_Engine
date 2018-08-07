# http://programarcadegames.com/python_examples/en/sprite_sheets/
import sys

import pygame

from engine import constants, game_map, entities, tileset


def main():
    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    pygame.display.set_caption("RPG Engine")

    try:
        tileset.load_textures()
    except ValueError as e:
        print(e)
        return 1

    player_data = entities.PlayerData()
    current_map = game_map.Map("test.map", player_data)

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

        next_map = current_map.update()
        current_map.draw(screen)
        if next_map is not None:
            current_map = game_map.Map(next_map, player_data)
        clock.tick(60)
        pygame.display.flip()

    return 0


if __name__ == "__main__":
    pygame.init()
    error = main()
    pygame.quit()
    sys.exit(error)
