import abc

from engine import game_map


class AbstractAction(abc.ABC):
    @abc.abstractmethod
    def execute(self, game_engine):
        """
        Executes this action.

        :param game_engine: Instance of the running game engine.
        """
        pass


class LoadMapAction(AbstractAction):
    def __init__(self, map_name: str, door_id: int = None):
        """
        Creates an action to load a map.

        :param map_name: Name of the map to load.
        :param door_id: ID of the door to spawn at. If left empty, player will be spawned at the default start position.
        """
        self._map_name = map_name
        self._door_id = door_id

    def execute(self, game_engine):
        game_engine.current_map = game_map.Map(self._map_name, start_door_id=self._door_id)
        game_engine.current_screen = None
