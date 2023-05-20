from __future__ import annotations

import datetime

from . import inventory


def load_save(save_id: int) -> GameState | None:
    """Load the save file with the given ID.

    :param save_id: Save’s ID.
    :return: A SaveState object for the given save or None if no file was found.
    """
    pass  # TODO


def list_saves() -> list[tuple[int, datetime.datetime]]:
    """List all available saves.

    :return: A list of all available save IDs and their date.
    """
    return []  # TODO


class GameState:  # TODO
    """Represents the state of the game."""

    def __init__(self, save_id: int):
        self._save_id = save_id
        self._flags = {}
        self._player_inventory = inventory.PlayerInventory()

    @property
    def save_id(self) -> int:
        return self._save_id

    @save_id.setter
    def save_id(self, save_id: int):
        self._save_id = save_id

    @property
    def player_inventory(self) -> inventory.PlayerInventory:
        return self._player_inventory

    def save(self):
        pass  # TODO
