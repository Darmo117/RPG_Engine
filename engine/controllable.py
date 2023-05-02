import abc

import pygame

from engine import actions


class Controllable(abc.ABC):
    """A controllable element can be updated and drawn onto the screen.
    Controls can also be enabled/disabled.
    """

    def __init__(self):
        self._controls_enabled = True

    @property
    def controls_enabled(self) -> bool:
        return self._controls_enabled

    @controls_enabled.setter
    def controls_enabled(self, value: bool):
        self._controls_enabled = value

    def on_event(self, event):
        """Called when an input event occurs."""
        pass

    def update(self) -> actions.AbstractAction | None:
        pass

    def draw(self, screen: pygame.Surface):
        pass
