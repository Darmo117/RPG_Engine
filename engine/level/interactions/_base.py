import abc

from ... import entities, io


class TileInteraction(abc.ABC):
    def __init__(self, id_: int):
        self._id = id_

    @property
    def id(self) -> int:
        return self._id

    @abc.abstractmethod
    def can_entity_go_through(self, level, entity: entities.Entity) -> bool:
        """Indicate whether the given entity can go through the tile associated to this interaction.

        :param level: The level that contains this interaction.
        :type level: engine.level.Level
        :param entity: An entity.
        :return: True if the entity can pass through the tile, false otherwise.
        """
        pass

    def on_entity_enter(self, level, entity: entities.Entity):
        """Called whenever an entity just entered this interaction.

        :param level: The level that contains this interaction.
        :type level: engine.level.Level
        :param entity: The entity.
        """
        pass

    def on_entity_inside(self, level, entity: entities.Entity):
        """Called whenever an entity is inside this interaction.

        :param level: The level that contains this interaction.
        :type level: engine.level.Level
        :param entity: The entity.
        """
        pass

    def write_to_buffer(self, buffer: io.ByteBuffer):
        """Serialize this interaction into the given byte buffer. """
        buffer.write_byte(self.id, signed=False)


class _NoInteraction(TileInteraction):
    def __init__(self):
        super().__init__(0)

    def can_entity_go_through(self, level, entity: entities.Entity) -> bool:
        return True


class _WallInteraction(TileInteraction):
    def __init__(self):
        super().__init__(1)

    def can_entity_go_through(self, level, entity: entities.Entity) -> bool:
        return False


NO_INTERACTION = _NoInteraction()
WALL_INTERACTION = _WallInteraction()

__all__ = [
    'TileInteraction',
    'NO_INTERACTION',
    'WALL_INTERACTION',
]
