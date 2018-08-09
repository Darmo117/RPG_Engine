import logging
import typing as typ


class Config:
    _LOGGER = logging.getLogger(__name__ + ".Config")

    def __init__(self, title="Game", start=None, languages=(), debug=False):
        self._title = title
        self._start_map = start
        self._languages = tuple(languages)
        self._debug = debug
        self._language_index = None

    @property
    def title(self) -> str:
        return self._title

    @property
    def start_map(self) -> str:
        return self._start_map

    @property
    def languages(self) -> typ.Tuple[str]:
        return self._languages

    @property
    def language_index(self) -> typ.Optional[int]:
        """Returns the index of the selected language if any."""
        return self._language_index

    @language_index.setter
    def language_index(self, index: int):
        """Sets the index of the selected language."""
        if index < 0 or index >= len(self._languages):
            raise IndexError(f"Language index {index} is not in range [0, {len(self._languages) - 1}]!")
        self._LOGGER.debug(f"Changed language index from {self._language_index} to {index}.")
        self._language_index = index

    @property
    def debug(self):
        return self._debug

    def __repr__(self):
        s = []
        for prop, value in vars(self).items():
            s.append(f"{prop[1:]}={value}")
        return "{" + ", ".join(s) + "}"
