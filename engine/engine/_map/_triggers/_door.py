from . import _base


class Door(_base.Trigger):
    OPEN = 0
    LOCKED = 1
    HIDDEN = 2

    def __init__(self, ident: int, x: int, y: int, state: int, destination_map: str = None,
                 destination_door_id: int = None):
        self._id = ident
        self._position = x, y
        self._dest_map = destination_map
        self._dest_door_id = destination_door_id
        self._state = state

    @property
    def id(self):
        return self._id

    @property
    def position(self):
        return self._position

    @property
    def destination_map(self):
        return self._dest_map

    @property
    def destination_door_id(self):
        return self._dest_door_id

    @property
    def open(self):
        return self._state == self.OPEN

    @property
    def locked(self):
        return self._state == self.LOCKED

    @property
    def hidden(self):
        return self._state == self.HIDDEN

    def execute(self, map_):
        pass  # TODO


__all__ = [
    'Door',
]
