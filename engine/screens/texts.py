from __future__ import annotations

import re

import pygame

from .. import render

FORMAT_TOKEN = '§'
ITALICS_TOKEN = 'i'
BOLD_TOKEN = 'b'
UNDERLINE_TOKEN = 'u'
STRIKETHROUGH_TOKEN = 's'
COLOR_TOKEN = 'c'
COLOR_PATTERN = re.compile(r'#([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})')
COLOR_TOKEN_LENGTH = len('#000000')


def parse_lines(text: str) -> list[Text]:
    """Parse the given text, spliting it along LF characters.

    :param text: The text to parse.
    :return: The resulting text object.
    """
    lines = []
    for line in text.split('\n'):
        lines.append(parse_line(line))
    return lines


def parse_line(text: str) -> Text:
    """Parse the given text, LFs are ignored.

    :param text: The text to parse.
    :return: The resulting text object.
    """
    line = None
    italics = bold = underlined = strikethrough = False
    color = render.TexturesManager.DEFAULT_FONT_COLOR
    ignore_next = format_mode = color_mode = False
    buffer = color_buffer = ''

    def get_style() -> int:
        return (Text.NORMAL
                | Text.ITALICS * italics
                | Text.BOLD * bold
                | Text.UNDERLINED * underlined
                | Text.STRIKETHROUGH * strikethrough)

    def append_buffer_to_line(style_: int):
        nonlocal line
        t = Text(buffer, color, style_)
        if line is None:
            line = t
        else:
            line += t

    i = 0
    while i < len(text):
        c = text[i]
        if not format_mode and not color_mode and c == FORMAT_TOKEN:
            if ignore_next:
                ignore_next = False
                buffer += c
            else:
                format_mode = True
        elif format_mode:
            format_mode = False
            if c == FORMAT_TOKEN:  # §§ is treated as the literal character §
                buffer += c
                i += 1
                continue
            style = get_style()  # Generate style before eventual update
            if c == ITALICS_TOKEN:
                italics = not italics
            elif c == BOLD_TOKEN:
                bold = not bold
            elif c == UNDERLINE_TOKEN:
                underlined = not underlined
            elif c == STRIKETHROUGH_TOKEN:
                strikethrough = not strikethrough
            elif c == COLOR_TOKEN:
                color_mode = True
                color_buffer = ''
            else:
                buffer += c
                i += 1
                continue
            if buffer:
                append_buffer_to_line(style)
                buffer = ''
        elif color_mode:
            if len(color_buffer) < COLOR_TOKEN_LENGTH:
                color_buffer += c
            else:
                color_mode = False
                if m := COLOR_PATTERN.fullmatch(color_buffer):
                    color = pygame.Color(int(m.group(1), 16), int(m.group(2), 16), int(m.group(3), 16))
                else:
                    color = render.TexturesManager.DEFAULT_FONT_COLOR
                    i -= len(color_buffer)
                i -= 1
        else:
            buffer += c
        i += 1

    if buffer:
        append_buffer_to_line(get_style())

    return line or Text('')


class Text:
    """Represents some text with attached style."""

    NORMAL = render.TexturesManager.NORMAL
    ITALICS = render.TexturesManager.ITALICS
    BOLD = render.TexturesManager.BOLD
    UNDERLINED = render.TexturesManager.UNDERLINED
    STRIKETHROUGH = render.TexturesManager.STRIKETHROUGH

    def __init__(self, text: str, color: pygame.Color = render.TexturesManager.DEFAULT_FONT_COLOR, style: int = NORMAL):
        """Create styled text.

        :param text: The text.
        :param color: Text’s color.
        :param style: Text’s style.
        """
        self._text = text
        self._color = color
        self._style = style
        self._next: Text | None = None

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text

    @property
    def color(self) -> pygame.Color:
        return self._color

    @color.setter
    def color(self, color: pygame.Color):
        self._color = color

    @property
    def style(self) -> int:
        return self._style

    @style.setter
    def style(self, style: int):
        self._style = style

    @property
    def next(self) -> Text:
        return self._next

    @next.setter
    def next(self, next_: Text):
        self._next = next_

    def get_size(self, texture_manager: render.TexturesManager) -> tuple[int, int]:
        """Compute the size of this text based on the given texture manager.

        :param texture_manager: The texture manager to use.
        :return: The size as a (width, height) tuple.
        """
        # Dummy render to get size
        text = texture_manager.render_text(self._text, color=self._color, style=self._style)
        size = text.get_size()
        if self._next:
            next_size = self._next.get_size(texture_manager)
            size = (size[0] + next_size[0], max(size[1], next_size[1]))
        return size

    def draw(self, texture_manager: render.TexturesManager, screen: pygame.Surface, xy: tuple[int, int]):
        """Draw this text on the given surface.

        :param texture_manager: The texture manager to use.
        :param screen: Surface to draw on.
        :param xy: Coordinates where to draw at on the surface.
        """
        text = texture_manager.render_text(self._text, color=self._color, style=self._style)
        screen.blit(text, xy)
        if self._next:
            self._next.draw(texture_manager, screen, (xy[0] + text.get_size()[0], xy[1]))

    def __iadd__(self, text: Text):
        if not self._next:
            self._next = text
        else:
            self._next += text
        return self

    def __str__(self):
        return self._text + (str(self._next) if self._next else '')
