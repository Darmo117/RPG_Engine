from __future__ import annotations

import datetime
import re

from . import inventory, io, constants


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
    data = []
    for file in constants.SAVES_DIR.glob('save_*.dat'):
        if file.is_file() and (m := re.fullmatch(r'save_(\d+)\.dat', file.name)):
            save_id = int(m.group(1))
            with file.open(mode='rb') as f:
                buffer = io.ByteBuffer(f.read(30))
            date = datetime.datetime.strptime(buffer.read_string(), '%Y-%m-%dT%H:%M:%S')
            data.append((save_id, date))
    return sorted(data, key=lambda e: e[0])


FlagValue = bool | int | float | str


class GameState:
    """Represents the state of the game."""

    def __init__(self, save_id: int = None):
        self._save_id = save_id
        self._flags: dict[str, FlagValue] = {}
        if save_id is not None:
            with (constants.SAVES_DIR / f'save_{save_id}.dat').open(mode='rb') as f:
                buffer = io.ByteBuffer(f.read())
            buffer.read_string()  # Skip date string
            # TODO load from file
            self._player_inventory = inventory.PlayerInventory(buffer)
        else:
            self._player_inventory = inventory.PlayerInventory()

    @property
    def save_id(self) -> int | None:
        return self._save_id

    @save_id.setter
    def save_id(self, save_id: int):
        if save_id is None:
            raise ValueError('expected int, got None')
        self._save_id = save_id

    @property
    def player_inventory(self) -> inventory.PlayerInventory:
        return self._player_inventory

    def is_flag_set(self, name: str) -> bool:
        return name in self._flags

    def get_flag(self, name: str) -> FlagValue:
        return self._flags[name]

    def set_flag(self, name: str, value: FlagValue):
        if not isinstance(value, FlagValue):
            t = str(FlagValue).replace(' | ', ', ')
            raise TypeError(f'expected {t}, got {type(value).__qualname__}')
        self._flags[name] = value

    def save(self, save_id: int = None):
        if save_id is None and self._save_id is None:
            raise ValueError('cannot save GameState object with no save ID')
        self._save_id = save_id
        buffer = io.ByteBuffer()
        buffer.write_string(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
        buffer.write_int(len(self._flags), signed=False)
        for flag_name, flag_value in self._flags.items():
            buffer.write_string(flag_name)
            match type(flag_value):
                case bool(b):
                    buffer.write_bool(b)
                case int(i):
                    buffer.write_int(i)
                case float(f):
                    buffer.write_double(f)
                case str(s):
                    buffer.write_string(s)
        self._player_inventory.save(buffer)
        with (constants.SAVES_DIR / f'save_{self._save_id}.dat').open(mode='wb') as f:
            f.write(buffer.bytes)
