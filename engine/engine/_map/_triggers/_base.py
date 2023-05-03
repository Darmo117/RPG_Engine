import abc


class Trigger(abc.ABC):
    @abc.abstractmethod
    def execute(self, map_):
        """Execute this trigger.

        :param map_: The map that contains this trigger.
        :type map_: engine.engine._map._map.Map
        """
        pass
