from __future__ import annotations

import abc

import pygame


class Scene(abc.ABC):
    """Scenes are the basic component of the game engine, i.e. levels or menu screens."""

    def __init__(self, parent: Scene = None):
        """Create a scene.

        :param parent: This scene’s parent.
        """
        self._parent = parent

    @property
    def parent(self) -> Scene:
        return self._parent

    def on_input_event(self, event: pygame.event.Event):
        """Called when an input event occurs.

        :param event: The event.
        """
        pass

    def update(self):
        """Update this scene."""
        pass

    @abc.abstractmethod
    def draw(self, screen: pygame.Surface):
        """Draw this scene on the given screen.

        :param screen: The screen to draw on.
        """
        pass
