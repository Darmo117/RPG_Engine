"""This module defines various graphical components such as menus and buttons."""
import abc
import itertools as it
import typing as typ

import pygame

from .. import global_values as gv, types as tp


class Component(abc.ABC):
    """Base class for graphical components."""

    def __init__(self, padding: int = 0):
        self._padding = padding
        self._enabled = True

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        self._on_enable_changed()

    def _on_enable_changed(self):
        pass

    @property
    @abc.abstractmethod
    def size(self) -> tp.Dimension:
        pass

    def update(self):
        """Updates this component."""
        pass

    def draw(self, surface: pygame.Surface, position: tp.Position):
        """
        Draws this component on a surface at the given position.
        Should not be overriden by subclasses.

        :param surface: The surface to draw on.
        :param position: Where to draw the component.
        """
        surface.blit(self._get_image(), position)

    @abc.abstractmethod
    def _get_image(self) -> pygame.Surface:
        pass


class Button(Component):
    def __init__(self, label: str, name: str = None, action: typ.Callable[[str], None] = None, enabled=True):
        super().__init__(padding=5)
        self._label = label
        self._name = name if name is not None else label
        self._action = action
        self._enabled = enabled
        self._selected = False
        self._update_image()

    @property
    def label(self):
        return self._label

    @property
    def name(self):
        return self._name

    def _on_enable_changed(self):
        self._update_image()

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        self._selected = value
        self._update_image()

    @property
    def size(self) -> tp.Dimension:
        return self._image.get_rect().size

    def on_action(self):
        if self._enabled:
            self._action(self._name)

    def _get_image(self) -> pygame.Surface:
        return self._image

    def _update_image(self):
        color = gv.TEXTURE_MANAGER.FONT_COLOR if self._enabled else (128, 128, 128)
        text = gv.TEXTURE_MANAGER.render_text(self._label, color=color)
        w, h = text.get_rect().size
        gaps = 2 * self._padding
        self._image = pygame.Surface((w + gaps, h + gaps), pygame.SRCALPHA, 32)
        self._image.blit(text, (self._padding, self._padding))
        if self._selected:
            # Corners
            size = (5, 5)
            top_left = gv.TEXTURE_MANAGER.get_menu_texture((30, 0), size)
            top_right = gv.TEXTURE_MANAGER.get_menu_texture((35, 0), size)
            bottom_left = gv.TEXTURE_MANAGER.get_menu_texture((30, 5), size)
            bottom_right = gv.TEXTURE_MANAGER.get_menu_texture((35, 5), size)
            self._image.blit(top_left, (0, 0))
            self._image.blit(top_right, (self._padding + w, 0))
            self._image.blit(bottom_left, (0, self._padding + h))
            self._image.blit(bottom_right, (self._padding + w, self._padding + h))


class Menu(Component):
    def __init__(self, rows: int, columns: int, gap: int = 5):
        super().__init__(padding=10)
        self._grid_width = columns
        self._grid_height = rows
        self._grid: list[list[Button | None]] = [[None] * columns for _ in range(rows)]
        self._selection = None
        self._gap = gap
        self._update_size()

    @property
    def size(self) -> tp.Dimension:
        return self._size

    def _on_enable_changed(self):
        for r, c in it.product(range(self._grid_height), range(self._grid_width)):
            button = self._grid[r][c]
            if button is not None:
                button.enabled = self._enabled

    def set_item(self, position: tp.Position, button: Button):
        if not isinstance(button, Button):
            raise ValueError('Component is not a button!')
        self._grid[position[0]][position[1]] = button
        self._update_size()

    _KEYS = {
        pygame.K_LEFT: (0, -1),
        pygame.K_RIGHT: (0, 1),
        pygame.K_UP: (-1, 0),
        pygame.K_DOWN: (1, 0)
    }

    def on_event(self, event):
        if self._selection is not None and event.type == pygame.KEYDOWN:
            previous = self._selection
            key = event.key
            if key in self._KEYS:
                while "Button is None and not skipping empty cells":
                    self._selection = ((self._selection[0] + self._KEYS[key][0]) % self._grid_height,
                                       (self._selection[1] + self._KEYS[key][1]) % self._grid_width)
                    if self._selected_button() is not None:
                        break

            if previous != self._selection:
                if previous is not None:
                    self._grid[previous[0]][previous[1]].selected = False
                self._selected_button().selected = True
            if key == pygame.K_RETURN:
                self._selected_button().on_action()

    def _selected_button(self) -> Button:
        return self._grid[self._selection[0]][self._selection[1]]

    def _get_image(self) -> pygame.Surface:
        image = pygame.Surface(self._size, pygame.SRCALPHA, 32)

        w, h = self._size[0] - 2 * self._padding, self._size[1] - 2 * self._padding
        # Corners
        t_size = self._padding
        size = (t_size, t_size)
        top_left = gv.TEXTURE_MANAGER.get_menu_texture((0, 0), size)
        top_right = gv.TEXTURE_MANAGER.get_menu_texture((2 * t_size, 0), size)
        bottom_left = gv.TEXTURE_MANAGER.get_menu_texture((0, 2 * t_size), size)
        bottom_right = gv.TEXTURE_MANAGER.get_menu_texture((2 * t_size, 2 * t_size), size)
        image.blit(top_left, (0, 0))
        image.blit(top_right, (t_size + w, 0))
        image.blit(bottom_left, (0, t_size + h))
        image.blit(bottom_right, (t_size + w, t_size + h))
        # Sides
        horizontal_nb = w // t_size
        horizontal_diff = w - t_size * horizontal_nb
        vertical_nb = h // t_size
        vertical_diff = h - t_size * vertical_nb
        # Full vertical sides
        for i in range(vertical_nb):
            left_side = gv.TEXTURE_MANAGER.get_menu_texture((0, t_size), size)
            image.blit(left_side, (0, t_size * (i + 1)))
            right_side = gv.TEXTURE_MANAGER.get_menu_texture((2 * t_size, t_size), size)
            image.blit(right_side, (t_size + w, t_size * (i + 1)))
            # Full background
            for j in range(horizontal_nb):
                bg = gv.TEXTURE_MANAGER.get_menu_texture((t_size, t_size), size)
                image.blit(bg, (t_size * (j + 1), t_size * (i + 1)))
            # Partial vertical background
            bg = gv.TEXTURE_MANAGER.get_menu_texture((t_size, t_size), (horizontal_diff, t_size))
            image.blit(bg, (t_size * (horizontal_nb + 1), t_size * (i + 1)))
        # Partial vertical sides
        left_side = gv.TEXTURE_MANAGER.get_menu_texture((0, t_size), (t_size, vertical_diff))
        image.blit(left_side, (0, t_size * (vertical_nb + 1)))
        right_side = gv.TEXTURE_MANAGER.get_menu_texture((2 * t_size, t_size), (t_size, vertical_diff))
        image.blit(right_side, (t_size + w, t_size * (vertical_nb + 1)))
        # Full horizontal sides
        for i in range(horizontal_nb):
            top_side = gv.TEXTURE_MANAGER.get_menu_texture((t_size, 0), size)
            image.blit(top_side, (t_size * (i + 1), 0))
            bottom_side = gv.TEXTURE_MANAGER.get_menu_texture((t_size, 2 * t_size), size)
            image.blit(bottom_side, (t_size * (i + 1), t_size + h))
            # Partial horizontal background
            bg = gv.TEXTURE_MANAGER.get_menu_texture((t_size, t_size), (t_size, vertical_diff))
            image.blit(bg, (t_size * (i + 1), t_size * (vertical_nb + 1)))
        # Partial horizontal sides
        top_side = gv.TEXTURE_MANAGER.get_menu_texture((t_size, 0), (horizontal_diff, t_size))
        image.blit(top_side, (t_size * (horizontal_nb + 1), 0))
        bottom_side = gv.TEXTURE_MANAGER.get_menu_texture((t_size, 2 * t_size), (horizontal_diff, t_size))
        image.blit(bottom_side, (t_size * (horizontal_nb + 1), t_size + h))
        # Partial background bottom-right corner
        bg = gv.TEXTURE_MANAGER.get_menu_texture((t_size, t_size), (horizontal_diff, vertical_diff))
        image.blit(bg, (t_size * (horizontal_nb + 1), t_size * (vertical_nb + 1)))

        y = self._padding
        for r in range(self._grid_height):
            x = self._padding
            for c in range(self._grid_width):
                button = self._grid[r][c]
                if button is not None:
                    button.draw(image, (x, y))
                x += self._column_widths[c] + self._gap
            y += self._row_heights[r] + self._gap

        return image

    def _update_size(self):
        self._row_heights = [0] * self._grid_height
        self._column_widths = [0] * self._grid_width
        for r in range(self._grid_height):
            for c in range(self._grid_width):
                button = self._grid[r][c]
                if button is not None:
                    if self._selection is None:
                        self._selection = (r, c)
                        self._selected_button().selected = True
                    w, h = button.size
                    self._row_heights[r] = max(h, self._row_heights[r])
                    self._column_widths[c] = max(w, self._column_widths[c])
        w = 2 * self._padding + sum(self._column_widths) + self._gap * (self._grid_width - 1)
        h = 2 * self._padding + sum(self._row_heights) + self._gap * (self._grid_height - 1)
        self._size = (w, h)


class DialogBox(Component):
    def __init__(self, text: str):
        super().__init__(padding=10)
        self._text = text

    @property
    def size(self) -> tp.Dimension:
        return 800, 200

    def update(self):
        pass  # TODO

    def _get_image(self) -> pygame.Surface:
        pass  # TODO
