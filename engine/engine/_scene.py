from __future__ import annotations

import abc

import pygame

from . import _events


class Scene(abc.ABC):
    """A scene is a visual component that poll input events and may return actions to perform.

    Controls can be enabled/disabled.
    """

    def __init__(self, parent: Scene = None):
        """Create a scene with controls enabled."""
        self._parent = parent
        self._controls_enabled = True

    @property
    def parent(self) -> Scene:
        return self._parent

    @property
    def controls_enabled(self) -> bool:
        """Whether this scene has controls enabled."""
        return self._controls_enabled

    @controls_enabled.setter
    def controls_enabled(self, enable: bool):
        """Set whether this scene should be able to poll input events.

        :param enable: True to enable inputs, false to disable them.
        """
        self._controls_enabled = enable

    def on_event(self, event: pygame.event.Event):
        """Called when an input event occurs.

        :param event: The event.
        """
        pass

    def update(self) -> _events.Event | None:
        """Update this component and return an event if any.

        :return: The emitted event or None.
        """
        pass

    def draw(self, screen: pygame.Surface):
        """Draw this scene of the given screen.

        :param screen: The screen to draw on.
        """
        pass
