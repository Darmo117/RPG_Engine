from __future__ import annotations


def load_save(id_: int) -> SaveState | None:
    """Load the save file with the given ID.

    :param id_: Save’s ID.
    :return: A SaveState object for the given save or None if no file was found.
    """
    pass  # TODO


def list_saves() -> list[int]:
    """List all available save files.

    :return: A list of all available save IDs.
    """
    return []  # TODO


class SaveState:  # TODO
    """Represents the state of a save."""

    def __init__(self, id_: int):
        self._id = id_

    @property
    def id(self) -> int:
        return self._id

    @id.setter
    def id(self, id_: int):
        self._id = id_

    def save(self):
        pass  # TODO
