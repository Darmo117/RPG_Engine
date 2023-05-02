import configparser as cp
import logging
import typing as typ

from . import global_values as gv


class I18n:
    _LOGGER = logging.getLogger('I18n')

    def __init__(self, language_index: int):
        self._language_index = language_index
        self._LOGGER.debug('Loading language file...')
        with open(gv.LANG_FILE, encoding="UTF-8") as f:
            parser = cp.ConfigParser()
            parser.read_file(f)
            self._map_names = {}
            self._load(parser['Maps'], self._map_names, 'map names')
        self._LOGGER.debug('Loaded language file.')

    def map(self, ident: str) -> str:
        """Returns the localized name of a map."""
        return self._get_localized_value(ident, self._map_names)

    def _get_localized_value(self, ident: str, registry: dict) -> str:
        """Returns the localized value of an identifier in the given registry."""
        if ident not in registry:
            return ident
        return registry[ident][self._language_index]

    def _load(self, config: typ.Mapping, registry: dict, debug_msg: str):
        self._LOGGER.debug(f'Loading {debug_msg}…')
        for ident, names in config.items():
            values = tuple(names.split('|'))
            if len(values) < len(gv.CONFIG.languages):
                raise ValueError(f"Not enough values for identifier '{ident}'!")
            registry[ident] = values
        self._LOGGER.debug(f'Loaded {debug_msg}.')
