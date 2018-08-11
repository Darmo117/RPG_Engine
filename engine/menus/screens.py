import abc
import os
import typing as typ

import pygame

from engine import menus, global_values as gv


class AbstractScreen(abc.ABC):
    def __init__(self, background_image: str = None):
        if background_image is not None:
            # noinspection PyArgumentList
            self._background_image = pygame.Surface((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT), pygame.SRCALPHA).convert()
            self._background_image.blit(pygame.image.load(background_image), (0, 0))
        else:
            self._background_image = None

    def on_event(self, event):
        """Called when an input event occurs."""
        pass

    def update(self):
        pass

    def draw(self, screen: pygame.Surface):
        if self._background_image is not None:
            screen.blit(self._background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))


class TitleScreen(AbstractScreen):
    def __init__(self, on_language_selected: typ.Callable[[int], None] = None):
        super().__init__(background_image=os.path.join(gv.BACKGROUNDS_DIR, "title_screen.png"))
        self._menu = menus.Menu(len(gv.CONFIG.languages), 1)
        for i, language in enumerate(gv.CONFIG.languages):
            self._menu.set_item((i, 0), menus.Button(language, name=str(i),
                                                     action=lambda index: on_language_selected(int(index))))

    def on_event(self, event):
        super().on_event(event)
        self._menu.on_event(event)

    def update(self):
        super().update()
        self._menu.update()

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self._menu.draw(screen, (gv.SCREEN_WIDTH - self._menu.size[0] - 50, gv.SCREEN_HEIGHT - self._menu.size[1] - 50))
