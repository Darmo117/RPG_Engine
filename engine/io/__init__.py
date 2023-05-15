import pygame.key

from ._byte_buffer import *


def are_keys_pressed(*keys: int) -> tuple[bool, ...]:
    states = pygame.key.get_pressed()
    return tuple(states[key] for key in keys)


def is_any_key_pressed(*keys: int) -> bool:
    return any(are_keys_pressed(*keys))
