import json
import os
import pathlib


class Language:
    def __init__(self, lang_file: pathlib.Path):
        self._code = os.path.splitext(lang_file.name)[0]
        self._mappings: dict[str, str] = {}
        with lang_file.open(encoding='UTF-8') as f:
            json_object = json.load(f)
        self._name = json_object['name']
        self._mappings = self._load_mappings(json_object['translations'])

    @property
    def code(self) -> str:
        return self._code

    @property
    def name(self) -> str:
        return self._name

    def translate(self, key: str, **kwargs) -> str:
        return self._mappings.get(key, key).format(**kwargs)

    def _load_mappings(self, json_object: dict, key_prexif: str = None) -> dict[str, str]:
        translations = {}
        for k, v in json_object.items():
            if key_prexif:
                k = f'{key_prexif}.{k}'
            if isinstance(v, dict):
                translations.update(self._load_mappings(v, k))
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    translations.update(self._load_mappings(item, f'{k}.{i}'))
            elif v is None:
                translations[k] = None
            else:
                translations[k] = str(v)
        return translations
