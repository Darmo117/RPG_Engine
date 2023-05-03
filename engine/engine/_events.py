import abc


class Event(abc.ABC):
    @abc.abstractmethod
    def execute(self, game_engine):
        """Execute this event.

        :param game_engine: The game engine.
        :type game_engine: engine.engine.GameEngine
        """
        pass


class QuitGameEvent(Event):
    def execute(self, game_engine):
        game_engine.stop()


class LoadSceneEvent(Event):
    def __init__(self, scene):
        """Create an event to load the given scene.

        :param scene: The screen.
        :type scene: engine.engine._scene.Scene
        """
        self._scene = scene

    def execute(self, game_engine):
        game_engine.set_active_scene(self._scene)


__all__ = [
    'Event',
    'QuitGameEvent',
    'LoadSceneEvent',
]
