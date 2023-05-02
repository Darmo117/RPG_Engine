"""This module defines common type hints aliases used throughout the engine."""
Color3 = tuple[int, int, int]
Color4 = tuple[int, int, int, int]
Color = Color3 | Color4

Position = tuple[int, int]
Dimension = tuple[int, int]
