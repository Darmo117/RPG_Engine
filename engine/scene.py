from __future__ import annotations

import abc

import pygame


class Scene(abc.ABC):
    """Scenes are the basic component of the game engine, i.e. levels or menu screens."""

    def __init__(self, game_engine, parent: Scene = None):
        """Create a scene.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        :param parent: This scene’s parent.
        """
        self._game_engine = game_engine
        self._parent = parent

    @property
    def game_engine(self):
        """The game engine.

        :rtype game_engine: engine.game_engine.GameEngine
        """
        return self._game_engine

    @property
    def parent(self) -> Scene:
        return self._parent

    def _get_keys(self, action: str) -> tuple[int, ...]:
        return self._game_engine.config.inputs.get_keys(action)

    def on_input_event(self, event: pygame.event.Event) -> bool:
        """Called when an input event occurs.

        :param event: The event.
        :return: True if the event has been processed and should be further ignored, false otherwise.
        """
        return False

    def update(self):
        """Update this scene."""
        pass

    @abc.abstractmethod
    def draw(self, screen: pygame.Surface):
        """Draw this scene on the given screen.

        :param screen: The screen to draw on.
        """
        pass
