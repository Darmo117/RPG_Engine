import abc

import pygame

from . import texts
from .. import level


class HUD(abc.ABC):
    """A HUD is an overlay that is drawn over a scene (screen or level)."""

    def __init__(self, game_engine):
        """Create a heads-up display.

        :param game_engine: The game engine.
        :type game_engine: engine.game_engine.GameEngine
        """
        self._game_engine = game_engine

    @abc.abstractmethod
    def draw(self, screen: pygame.Surface):
        pass

    def update(self):
        pass


class DebugHUD(HUD):
    """HUD that displays useful debug information."""

    def draw(self, screen: pygame.Surface):
        config = self._game_engine.config
        scene = self._game_engine.active_scene
        fps = round(self._game_engine.fps)
        if fps <= 30:
            color = 'ff0000'
        elif fps <= 40:
            color = 'da7422'
        else:
            color = 'ffffff'
        s = f"""
§bDebug info (F3 to toggle)
§c#{color}FPS: {fps}
Language: {config.active_language}
Always run: {config.always_run}
BGM: {config.bg_music_volume}
BGS: {config.bg_sounds_volume}
MFX: {config.music_effects_volume}
SFX: {config.sound_effects_volume}
Scene type: {type(scene).__qualname__}
""".strip()
        if isinstance(scene, level.Level):
            s += f"""
Level name: {scene.name}
Entities: {len(scene.entity_set)}
""".rstrip()
        lines = texts.parse_lines(s)
        tm = self._game_engine.texture_manager
        y = 5
        x = 5
        for line in lines:
            line.draw(tm, screen, (x, y))
            y += line.get_size(tm)[1]


__all__ = [
    'HUD',
    'DebugHUD',
]
