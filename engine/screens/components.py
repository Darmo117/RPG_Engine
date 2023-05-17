from __future__ import annotations

import abc
import itertools as _it
import typing as _typ

import pygame

from . import texts
from .. import config, render


class Component(abc.ABC):
    """Base class for graphical components."""

    def __init__(self, game_engine, padding: int = 0):
        """Create a component.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param padding: The space around the component’s contents.
        """
        self._game_engine = game_engine
        self._tm: render.TexturesManager = game_engine.texture_manager
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

    def _get_keys(self, action: str) -> tuple[int, ...]:
        return self._game_engine.config.inputs.get_keys(action)

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


class MenuComponent(Component, abc.ABC):
    """This class marks a component as being acceptable by Menu components as an item."""
    pass


class Spacer(MenuComponent):
    def __init__(self, game_engine, padding: int = 0):
        """Create a spacer. A spacer is an empty component meant to fill empty cells in a menu grid.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param padding: Inner padding.
        """
        super().__init__(game_engine, padding)

    def _draw(self) -> pygame.Surface:
        return pygame.Surface((0, 0))


class Label(MenuComponent):
    def __init__(self, game_engine, text: str, padding: int = 5):
        """Create a label. Labels are simple components that display some text.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param text: Label’s text.
        :param padding: Inner padding.
        """
        super().__init__(game_engine, padding=padding)
        self._text = text
        self.w, self.h = texts.parse_line(text).get_size(self._tm)
        self._image = None
        self._update_image()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self._update_image()

    def _draw(self) -> pygame.Surface:
        return self._image

    def _update_image(self):
        self._image = pygame.Surface(self.size, pygame.SRCALPHA)
        text = texts.parse_line(self._text)
        text.draw(self._tm, self._image, (self._padding, self._padding))


class Button(MenuComponent):
    def __init__(self, game_engine, label: str, name: str,
                 data_label_format: str | _typ.Callable[[_typ.Any], str] = None, data=None,
                 action: _typ.Callable[[Button], None] = None, enabled: bool = True):
        """Create a button. Buttons are labelled components that may trigger an action when activated.
        Buttons may hold some data that will be displayed to the right of the label if a data_label_format is provided.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param label: Button’s label.
        :param name: Button’s internal name.
        :param data_label_format: Optional format string/function to render the button’s data.
        :param data: Optional button data.
        :param action: Action to execute when this button is activated.
        :param enabled: Whether this button should respond to inputs.
        """
        super().__init__(game_engine, padding=5)
        self._raw_label = label
        self._name = name
        self._data_label_format = data_label_format
        self._data = data
        self._action = action
        self._enabled = enabled
        self._selected = False
        text_size = texts.parse_line(label).get_size(self._tm)
        if self._data_label_format:
            data_text_size = texts.parse_line(self._get_data_label()).get_size(self._tm)
            self.w = text_size[0] + data_text_size[0] + 2 * self._padding
            self.h = max(text_size[1], data_text_size[1])
        else:
            self.w, self.h = text_size
        self._image = None
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
        if self._enabled and self._action:
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
        self._image = pygame.Surface(self.size, pygame.SRCALPHA)

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

    def __init__(self, game_engine, rows: int, columns: int, layout: int = HORIZONTAL, gap: int = 5):
        """Create an empty menu.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param rows: Number of rows in the menu’s grid.
        :param columns: Number of columns in the menu’s grid.
        :param layout: How the components will be added to the menu.
        :param gap: Spacing between each component in the grid.
        """
        super().__init__(game_engine, padding=10)
        self._grid_width = columns
        self._grid_height = rows
        self._row_heights = [0] * self._grid_height
        self._column_widths = [0] * self._grid_width
        self._layout = layout
        self._grid: list[list[MenuComponent | None]] = [[None] * columns for _ in range(rows)]
        self._buttons_nb = 0
        self._selection = None
        self._gap = gap

    @property
    def grid_width(self) -> int:
        return self._grid_width

    @property
    def grid_height(self) -> int:
        return self._grid_height

    def _on_enable_changed(self):
        for r, c in _it.product(range(self._grid_height), range(self._grid_width)):
            if button := self._get_button(r, c):
                button.enabled = self._enabled

    def add_item(self, c: MenuComponent) -> MenuComponent:
        if not isinstance(c, MenuComponent):
            raise TypeError(f'expected MenuComponent, got {type(c)}')

        if self._layout == self.HORIZONTAL:
            row = self._buttons_nb // self._grid_width
            col = self._buttons_nb % self._grid_width
        else:
            row = self._buttons_nb % self._grid_width
            col = self._buttons_nb // self._grid_width
        self._grid[row][col] = c
        if not self._selection:
            self._select_button(row, col)
        self._update_size(row, col, c)
        self._buttons_nb += 1
        return c

    def _update_size(self, row: int, col: int, new_component: MenuComponent):
        cw, ch = new_component.size

        if cw > self._column_widths[col]:
            self._column_widths[col] = cw
            for r in range(self._grid_height):
                if (comp := self._grid[r][col]) and comp is not new_component:
                    comp.w = new_component.w
        else:
            new_component.w = self._grid[0][col].w

        if ch > self._row_heights[row]:
            self._row_heights[row] = ch
            for c in range(self._grid_width):
                if (comp := self._grid[row][c]) and comp is not new_component:
                    comp.h = new_component.h
        else:
            new_component.h = self._grid[row][0].h

        self.w = sum(self._column_widths) + self._gap * (self._grid_width - 1)
        self.h = sum(self._row_heights) + self._gap * (self._grid_height - 1)

        # Update positions
        y = self._padding
        for r in range(self._grid_height):
            x = self._padding
            for c in range(self._grid_width):
                if comp := self._grid[r][c]:
                    comp.x = x
                    comp.y = y
                x += self._column_widths[c] + self._gap
            y += self._row_heights[r] + self._gap

    def on_event(self, event: pygame.event.Event):
        if super().on_event(event):
            return True

        if self._selection and event.type == pygame.KEYDOWN and self._buttons_nb > 0:
            key = event.key

            if key in self._get_keys(config.InputConfig.ACTION_OK_INTERACT):
                self._get_button(*self._selection).on_action()
                return True

            right = key in self._get_keys(config.InputConfig.ACTION_RIGHT)
            left = key in self._get_keys(config.InputConfig.ACTION_LEFT)
            down = key in self._get_keys(config.InputConfig.ACTION_DOWN)
            up = key in self._get_keys(config.InputConfig.ACTION_UP)
            if right or left or down or up:
                r, c = self._selection
                start_pos = r, c
                while not self._select_button(r, c):
                    if right:
                        c = (c + 1) % self._grid_width
                    elif left:
                        c = (c - 1) % self._grid_width
                    elif down:
                        r = (r + 1) % self._grid_height
                    elif up:
                        r = (r - 1) % self._grid_height
                    if (r, c) == start_pos:  # We came back to the start, stop here to avoid infinite loop
                        break
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
        c = self._grid[row][col]
        return c if isinstance(c, Button) else None

    def _draw(self) -> pygame.Surface:
        image = pygame.Surface(self.size, pygame.SRCALPHA)
        self._render_bg(image)
        for r in range(self._grid_height):
            for c in range(self._grid_width):
                if comp := self._grid[r][c]:
                    comp.draw(image)
        return image


class TextArea(Component):
    def __init__(self, game_engine, text: str):
        """Create a text area. Text areas behave similarly to labels but cannot be used as menu items.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param text: Text to display.
        """
        super().__init__(game_engine, padding=10)
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
        image = pygame.Surface((w + gaps, h + gaps), pygame.SRCALPHA)
        self._render_bg(image)
        font_h = self._tm.font.size('a')[1]
        offset = 0
        for line in self._text:
            line.draw(self._tm, image, (self._padding, self._padding + offset))
            offset += font_h
        return image


__all__ = [
    'Component',
    'Spacer',
    'Label',
    'Button',
    'Menu',
    'TextArea',
]
