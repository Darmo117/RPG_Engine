import pygame


def fill_gradient(surface: pygame.Surface, start_color: pygame.Color, end_color: pygame.Color,
                  rect: pygame.Rect = None, horizontal: bool = True, alpha: bool = False):
    """Fills a surface with a gradient pattern.

    :param surface: Surface to fill.
    :param start_color: Starting color.
    :param end_color: Final color.
    :param rect: Area to fill; default is surface's rect.
    :param horizontal: True for horizontal; False for vertical.
    :param alpha: If True result will have same alpha as end color; else result will be opaque.

    Source: http://www.pygame.org/wiki/GradientCode
    """
    if rect is None:
        rect = surface.get_rect()
    x1, x2 = rect.left, rect.right
    y1, y2 = rect.top, rect.bottom
    if horizontal:
        h = x2 - x1
    else:
        h = y2 - y1
    rate = (
        float(end_color.r - start_color.r) / h,
        float(end_color.g - start_color.g) / h,
        float(end_color.b - start_color.b) / h,
    )
    if horizontal:
        for col in range(x1, x2):
            start_color = (
                min(max(start_color.r + (rate[0] * (col - x1)), 0), 255),
                min(max(start_color.g + (rate[1] * (col - x1)), 0), 255),
                min(max(start_color.b + (rate[2] * (col - x1)), 0), 255),
                end_color.a if alpha else 255
            )
            pygame.draw.line(surface, start_color, (col, y1), (col, y2))
    else:
        for line in range(y1, y2):
            start_color = (
                min(max(start_color.r + (rate[0] * (line - y1)), 0), 255),
                min(max(start_color.g + (rate[1] * (line - y1)), 0), 255),
                min(max(start_color.b + (rate[2] * (line - y1)), 0), 255),
                end_color.a if alpha else 255
            )
            pygame.draw.line(surface, start_color, (x1, line), (x2, line))


def alpha_gradient(surface: pygame.Surface, color: pygame.Color, start_alpha: int, end_alpha: int,
                   rect: pygame.Rect = None, horizontal: bool = True):
    """Fills a surface with a gradient pattern.

    :param surface: Surface to fill.
    :param color: Base color.
    :param start_alpha: Start alpha value.
    :param end_alpha: Final alpha value.
    :param rect: Area to fill; default is surface's rect.
    :param horizontal: True for horizontal; False for vertical.
    """
    if rect is None:
        rect = surface.get_rect()
    x1, x2 = rect.left, rect.right
    y1, y2 = rect.top, rect.bottom
    if horizontal:
        h = x2 - x1
    else:
        h = y2 - y1
    rate = (end_alpha - start_alpha) / h
    if horizontal:
        for col in range(x1, x2):
            c = (color.r, color.g, color.b, min(max(start_alpha + (rate * (col - x1)), 0), 255))
            pygame.draw.line(surface, c, (col, y1), (col, y2))
    else:
        for line in range(y1, y2):
            c = (color.r, color.g, color.b, min(max(start_alpha + (rate * (line - y1)), 0), 255))
            pygame.draw.line(surface, c, (x1, line), (x2, line))
