from . import _base
from ... import entities, io


class HurtEntityInteraction(_base.TileInteraction):
    def __init__(self, damage_amount: float):
        super().__init__(3)
        self._damage_amount = damage_amount

    @property
    def damage_amount(self) -> float:
        return self._damage_amount

    def can_entity_go_through(self, level, entity: entities.Entity) -> bool:
        return True

    def on_entity_enter(self, level, entity: entities.Entity):
        pass  # TODO

    def write_to_buffer(self, buffer: io.ByteBuffer):
        super().write_to_buffer(buffer)
        buffer.write_double(self._damage_amount)


__all__ = [
    'HurtEntityInteraction',
]
