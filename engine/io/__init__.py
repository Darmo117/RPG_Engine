import pygame.key

from ._byte_buffer import *


def are_keys_pressed(*keys: int) -> tuple[bool, ...]:
    states = pygame.key.get_pressed()
    return tuple(states[key] for key in keys)


def is_any_key_pressed(*keys: int) -> bool:
    return any(are_keys_pressed(*keys))


def get_key_name(key: int) -> str:
    """Return a readable name for the given keyboard key code.

    :param key: Key code as defined by PyGame.
    :return: The corresponding key name.
    """
    return pygame.key.name(key, use_compat=False)
