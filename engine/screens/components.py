from __future__ import annotations

import abc
import itertools as _it
import typing as _typ

import pygame

from .. import render
from . import texts


class Component(abc.ABC):
    """Base class for graphical components."""

    def __init__(self, texture_manager: render.TexturesManager, padding: int = 0):
        self._tm = texture_manager
        self.x = 0
        self.y = 0
        self._w = 0
        self._h = 0
        self._padding = padding
        self._enabled = True

    @property
    def w(self) -> int:
        return self._w

    @w.setter
    def w(self, w: int):
        self._w = w
        self._on_size_changed()

    @property
    def h(self) -> int:
        return self._h

    @h.setter
    def h(self, h: int):
        self._h = h
        self._on_size_changed()

    def _on_size_changed(self):
        pass

    @property
    def size(self):
        return self.w + 2 * self._padding, self.h + 2 * self._padding

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool):
        self._enabled = value
        self._on_enable_changed()

    def _on_enable_changed(self):
        pass

    def on_event(self, event: pygame.event.Event) -> bool:
        return False

    def update(self):
        """Update this component."""
        pass

    def draw(self, screen: pygame.Surface):
        """Draw this component on a screen at the given position.
        Should not be overriden by subclasses.

        :param screen: The screen to draw on.
        """
        screen.blit(self._draw(), (self.x, self.y))

    @abc.abstractmethod
    def _draw(self) -> pygame.Surface:
        pass

    def _render_bg(self, image: pygame.Surface):
        w, h = self.w, self.h
        pad = self._padding
        size = (pad, pad)
        top_left = self._tm.get_menu_texture((0, 0), size)
        top_right = self._tm.get_menu_texture((2 * pad, 0), size)
        bottom_left = self._tm.get_menu_texture((0, 2 * pad), size)
        bottom_right = self._tm.get_menu_texture((2 * pad, 2 * pad), size)
        image.blit(top_left, (0, 0))
        image.blit(top_right, (pad + w, 0))
        image.blit(bottom_left, (0, pad + h))
        image.blit(bottom_right, (pad + w, pad + h))
        # Sides
        horizontal_nb = w // pad
        horizontal_diff = w - pad * horizontal_nb
        vertical_nb = h // pad
        vertical_diff = h - pad * vertical_nb
        # Full vertical sides
        for i in range(vertical_nb):
            left_side = self._tm.get_menu_texture((0, pad), size)
            image.blit(left_side, (0, pad * (i + 1)))
            right_side = self._tm.get_menu_texture((2 * pad, pad), size)
            image.blit(right_side, (pad + w, pad * (i + 1)))
            # Full background
            for j in range(horizontal_nb):
                bg = self._tm.get_menu_texture((pad, pad), size)
                image.blit(bg, (pad * (j + 1), pad * (i + 1)))
            # Partial vertical background
            bg = self._tm.get_menu_texture((pad, pad), (horizontal_diff, pad))
            image.blit(bg, (pad * (horizontal_nb + 1), pad * (i + 1)))
        # Partial vertical sides
        left_side = self._tm.get_menu_texture((0, pad), (pad, vertical_diff))
        image.blit(left_side, (0, pad * (vertical_nb + 1)))
        right_side = self._tm.get_menu_texture((2 * pad, pad), (pad, vertical_diff))
        image.blit(right_side, (pad + w, pad * (vertical_nb + 1)))
        # Full horizontal sides
        for i in range(horizontal_nb):
            top_side = self._tm.get_menu_texture((pad, 0), size)
            image.blit(top_side, (pad * (i + 1), 0))
            bottom_side = self._tm.get_menu_texture((pad, 2 * pad), size)
            image.blit(bottom_side, (pad * (i + 1), pad + h))
            # Partial horizontal background
            bg = self._tm.get_menu_texture((pad, pad), (pad, vertical_diff))
            image.blit(bg, (pad * (i + 1), pad * (vertical_nb + 1)))
        # Partial horizontal sides
        top_side = self._tm.get_menu_texture((pad, 0), (horizontal_diff, pad))
        image.blit(top_side, (pad * (horizontal_nb + 1), 0))
        bottom_side = self._tm.get_menu_texture((pad, 2 * pad), (horizontal_diff, pad))
        image.blit(bottom_side, (pad * (horizontal_nb + 1), pad + h))
        # Partial background bottom-right corner
        bg = self._tm.get_menu_texture((pad, pad), (horizontal_diff, vertical_diff))
        image.blit(bg, (pad * (horizontal_nb + 1), pad * (vertical_nb + 1)))


class Button(Component):
    def __init__(self, texture_manager: render.TexturesManager, label: str, name: str,
                 data_label_format: str | _typ.Callable[[_typ.Any], str] = None, data=None,
                 action: _typ.Callable[[Button], None] = None, enabled: bool = True):
        super().__init__(texture_manager, padding=5)
        self._raw_label = label
        self._name = name
        self._data_label_format = data_label_format
        self._data = data
        self._action = action
        self._enabled = enabled
        self._selected = False
        text_size = texts.parse_line(label).get_size(texture_manager)
        if self._data_label_format:
            data_text_size = texts.parse_line(self._get_data_label()).get_size(texture_manager)
            self.w, self.h = text_size[0] + data_text_size[0] + 2 * self._padding, max(text_size[1], data_text_size[1])
        else:
            self.w, self.h = text_size
        self._update_image()

    def _get_data_label(self) -> str:
        if isinstance(self._data_label_format, str):
            return self._data_label_format.format(self._data)
        return self._data_label_format(self._data)

    @property
    def label(self) -> str:
        return self._raw_label

    @label.setter
    def label(self, label: str):
        self._raw_label = label
        self._update_image()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value
        self._update_image()

    @property
    def name(self) -> str:
        return self._name

    def _on_size_changed(self):
        self._update_image()

    def _on_enable_changed(self):
        self._update_image()

    @property
    def selected(self) -> bool:
        return self._selected

    @selected.setter
    def selected(self, value: bool):
        self._selected = value
        self._update_image()

    def on_action(self):
        if self._enabled:
            self._action(self)

    def _draw(self) -> pygame.Surface:
        return self._image

    def _update_image(self):
        def disable(text: texts.Text):
            t = text
            while t:
                t.color = render.TexturesManager.DISABLED_FONT_COLOR
                t = t.next

        tm = self._tm
        w, h = self.w, self.h
        gaps = 2 * self._padding
        self._image = pygame.Surface((w + gaps, h + gaps), pygame.SRCALPHA, 32)

        label = texts.parse_line(self._raw_label)
        if not self._enabled:
            disable(label)
        label.draw(tm, self._image, (self._padding, self._padding))
        if self._data_label_format:
            data_label = texts.parse_line(self._get_data_label())
            if not self._enabled:
                disable(data_label)
            data_label.draw(tm, self._image, (self._padding + w - data_label.get_size(tm)[0], self._padding))

        if self._selected:
            # Corners
            size = (5, 5)
            top_left = tm.get_menu_texture((30, 0), size)
            top_right = tm.get_menu_texture((35, 0), size)
            bottom_left = tm.get_menu_texture((30, 5), size)
            bottom_right = tm.get_menu_texture((35, 5), size)
            self._image.blit(top_left, (0, 0))
            self._image.blit(top_right, (self._padding + w, 0))
            self._image.blit(bottom_left, (0, self._padding + h))
            self._image.blit(bottom_right, (self._padding + w, self._padding + h))


class Menu(Component):
    HORIZONTAL = 0
    VERTICAL = 1

    def __init__(self, texture_manager: render.TexturesManager,
                 rows: int, columns: int, layout: int = HORIZONTAL, gap: int = 5):
        super().__init__(texture_manager, padding=10)
        self._grid_width = columns
        self._grid_height = rows
        self._row_heights = [0] * self._grid_height
        self._column_widths = [0] * self._grid_width
        self._layout = layout
        self._grid: list[list[Button | None]] = [[None] * columns for _ in range(rows)]
        self._buttons_nb = 0
        self._selection = None
        self._gap = gap

    def _on_enable_changed(self):
        for r, c in _it.product(range(self._grid_height), range(self._grid_width)):
            if button := self._get_button(r, c):
                button.enabled = self._enabled

    def add_item(self, button: Button):
        if self._layout == self.HORIZONTAL:
            row = self._buttons_nb // self._grid_width
            col = self._buttons_nb % self._grid_width
        else:
            row = self._buttons_nb % self._grid_width
            col = self._buttons_nb // self._grid_width
        self._grid[row][col] = button
        if not self._selection:
            self._select_button(row, col)
        self._update_size(row, col, button)
        self._buttons_nb += 1

    def _update_size(self, row: int, col: int, new_button: Button):
        bw, bh = new_button.size

        if bw > self._column_widths[col]:
            self._column_widths[col] = bw
            for r in range(self._grid_height):
                if (button := self._get_button(r, col)) and button != new_button:
                    button.w = new_button.w
        else:
            new_button.w = self._get_button(0, 0).w

        if bh > self._row_heights[row]:
            self._row_heights[row] = bh
            for c in range(self._grid_width):
                if (button := self._get_button(row, c)) and button != new_button:
                    button.h = new_button.h
        else:
            new_button.h = self._get_button(0, 0).h

        self.w = sum(self._column_widths) + self._gap * (self._grid_width - 1)
        self.h = sum(self._row_heights) + self._gap * (self._grid_height - 1)

        # Update positions
        y = self._padding
        for r in range(self._grid_height):
            x = self._padding
            for c in range(self._grid_width):
                if button := self._get_button(r, c):
                    button.x = x
                    button.y = y
                x += self._column_widths[c] + self._gap
            y += self._row_heights[r] + self._gap

    def on_event(self, event: pygame.event.Event):
        if super().on_event(event):
            return True

        if self._selection and event.type == pygame.KEYDOWN:
            key = event.key
            if key in (pygame.K_RIGHT, pygame.K_LEFT, pygame.K_DOWN, pygame.K_UP):
                if self._buttons_nb > 0:
                    r, c = self._selection
                    while not self._select_button(r, c):
                        if key == pygame.K_RIGHT:
                            if self._selection[1] == self._grid_width - 1:
                                r = (r + 1) % self._grid_height
                                c = 0
                            else:
                                c += 1
                        elif key == pygame.K_LEFT:
                            if self._selection[1] == 0:
                                r = (r - 1) % self._grid_height
                                c = self._grid_width - 1
                            else:
                                c -= 1
                        elif key == pygame.K_DOWN:
                            if self._selection[0] == self._grid_height - 1:
                                r = 0
                                c = (c + 1) % self._grid_width
                            else:
                                r += 1
                        elif key == pygame.K_UP:
                            if self._selection[0] == 0:
                                r = self._grid_height - 1
                                c = (c - 1) % self._grid_width
                            else:
                                r -= 1
                    return True

            elif key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._get_button(*self._selection).on_action()
                return True

        return False

    def _select_button(self, row: int, col: int) -> bool:
        position = row, col
        if (previous := self._selection) != position and (b := self._get_button(*position)):
            if previous:
                self._get_button(*previous).selected = False
            self._selection = position
            b.selected = True
            return True
        return False

    def _get_button(self, row: int, col: int) -> Button | None:
        return self._grid[row][col]

    def _draw(self) -> pygame.Surface:
        image = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self._render_bg(image)
        for r in range(self._grid_height):
            for c in range(self._grid_width):
                if button := self._get_button(r, c):
                    button.draw(image)
        return image


class TextArea(Component):
    def __init__(self, texture_manager: render.TexturesManager, text: str):
        super().__init__(texture_manager, padding=10)
        self._raw_text = text
        self._text = texts.parse_lines(text)

    @property
    def text(self) -> str:
        return self._raw_text

    @text.setter
    def text(self, text: str):
        self._raw_text = text
        self._text = texts.parse_lines(text)

    def _draw(self) -> pygame.Surface:
        w, h = self.w, self.h
        gaps = 2 * self._padding
        image = pygame.Surface((w + gaps, h + gaps), pygame.SRCALPHA, 32)
        self._render_bg(image)
        font_h = self._tm.font.size('a')[1]
        offset = 0
        for line in self._text:
            line.draw(self._tm, image, (self._padding, self._padding + offset))
            offset += font_h
        return image


__all__ = [
    'Component',
    'Button',
    'Menu',
    'TextArea',
]
