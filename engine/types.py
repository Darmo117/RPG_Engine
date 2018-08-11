"""This modules defines common type hints aliases used throughout the engine."""
import typing as typ

Color3 = typ.Tuple[int, int, int]
Color4 = typ.Tuple[int, int, int, int]
Color = typ.Union[Color3, Color4]

Position = typ.Tuple[int, int]
Dimension = typ.Tuple[int, int]
