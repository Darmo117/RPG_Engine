# http://programarcadegames.com/python_examples/en/sprite_sheets/
import pygame

from engine import player as ply, constants, game_map as gmap


def main():
    pygame.init()

    screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
    pygame.display.set_caption("SMB")

    player = ply.Player()
    current_map = gmap.Map("data/maps/test.map", player)
    current_map.translate(0, -constants.SCREEN_TILE_SIZE // 2)

    clock = pygame.time.Clock()

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.go_up()
                elif event.key == pygame.K_DOWN:
                    player.go_down()
                elif event.key == pygame.K_LEFT:
                    player.go_left()
                elif event.key == pygame.K_RIGHT:
                    player.go_right()

        next_level = current_map.update()
        current_map.draw(screen)
        if next_level is not None:
            current_map = current_map.Level(next_level, player)
        clock.tick(60)
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
