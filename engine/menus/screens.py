import os

import pygame

from .. import actions, controllable, global_values as gv, i18n, menus


class AbstractScreen(controllable.Controllable):
    def __init__(self, background_image: str = None):
        super().__init__()
        if background_image is not None:
            # noinspection PyArgumentList
            self._background_image = pygame.Surface((gv.SCREEN_WIDTH, gv.SCREEN_HEIGHT), pygame.SRCALPHA).convert()
            self._background_image.blit(pygame.image.load(background_image), (0, 0))
        else:
            self._background_image = None

    def draw(self, screen: pygame.Surface):
        if self._background_image is not None:
            screen.blit(self._background_image, (0, 0))
        else:
            screen.fill((0, 0, 0))


class TitleScreen(AbstractScreen):
    def __init__(self):
        super().__init__(background_image=os.path.join(gv.BACKGROUNDS_DIR, "title_screen.png"))
        self._menu = menus.Menu(len(gv.CONFIG.languages), 1)
        for i, language in enumerate(gv.CONFIG.languages):
            self._menu.set_item((i, 0), menus.Button(language, name=str(i),
                                                     action=lambda index: self._on_language_selected(int(index))))
        self._action = None

    def _on_language_selected(self, index):
        gv.CONFIG.language_index = index
        gv.I18N = i18n.I18n(gv.CONFIG.language_index)
        self._action = actions.LoadMapAction(gv.CONFIG.start_map)

    def on_event(self, event):
        super().on_event(event)
        if self._controls_enabled:
            self._menu.on_event(event)

    def update(self) -> actions.AbstractAction | None:
        super().update()
        self._menu.update()
        return self._action if self._controls_enabled else None

    def draw(self, screen: pygame.Surface):
        super().draw(screen)
        self._menu.draw(screen, (gv.SCREEN_WIDTH - self._menu.size[0] - 50, gv.SCREEN_HEIGHT - self._menu.size[1] - 50))
