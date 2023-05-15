from __future__ import annotations

import pygame


class Event:
    """Base class for events."""

    def __init__(self):
        """Create an event with no next event."""
        self._next_event: Event | None = None

    @property
    def next(self) -> Event | None:
        """The event that immediately follows this one."""
        return self._next_event

    def then(self, event: Event | None) -> Event:
        """Queue an event right after this one.

        :param event: The event to queue.
        :return: This event.
        """
        self._next_event = event
        return self


class GoToScreenEvent(Event):
    def __init__(self, screen):
        """Create an event to load the given screen.

        :param screen: The screen to go to.
        :type screen: engine.screens.screens.Screen
        """
        super().__init__()
        self.screen = screen


class ChangeLevelEvent(Event):
    def __init__(self, level_name: str, spawn_location: pygame.Vector2):
        """Create an event to load the specified level.

        :param level_name: Name of the level to load.
        :param spawn_location: Location where to spawn the player at.
        """
        super().__init__()
        self.level_name = level_name
        self.spawn_location = spawn_location


class SpawnEntityEvent(Event):
    def __init__(self, entity_supplier, at: pygame.Vector2):
        """Create an event to spawn an entity in the current level.

        :param entity_supplier: A function that takes a level and returns an entity.
        :type entity_supplier: typing.Callable[[engine.level.Level], engine.entities.Entity]
        :param at: The tile position where to spawn the entity.
        """
        super().__init__()
        self.entity_supplier = entity_supplier
        self.at = at

    def get_entity(self, level):
        """Get the entity to spawn into the level.

        :param level: The level to spawn the entity into.
        :type level: engine.level.Level
        :return: The entity.
        :rtype: engine.entities.Entity
        """
        return self.entity_supplier(level)


class DisplayDialogEvent(Event):
    def __init__(self, text_key: str, **kwargs):
        """Create an event to show a dialog.

        :param text_key: Localization key for the text to display.
        :param kwargs: Optional arguments to use as format arguments in the localized text.
        """
        super().__init__()
        self.text_key = text_key
        self.kwargs = kwargs


class ToggleSceneUpdateEvent(Event):
    def __init__(self, should_update: bool):
        """Create an event that changes whether scenes should be updated.

        :param should_update: Whether to enable scene update.
        """
        super().__init__()
        self.should_update = should_update


class WaitEvent(Event):
    def __init__(self, milliseconds: int):
        """Create an event to force the engine to wait for a given amount of time before handling any other event.

        :param milliseconds: The wait time in milliseconds.
        """
        super().__init__()
        self.milliseconds = milliseconds


class QuitGameEvent(Event):
    """This event quits the game by stopping the game engine."""
    pass


__all__ = [
    'Event',
    'GoToScreenEvent',
    'ChangeLevelEvent',
    'SpawnEntityEvent',
    'DisplayDialogEvent',
    'ToggleSceneUpdateEvent',
    'WaitEvent',
    'QuitGameEvent',
]
