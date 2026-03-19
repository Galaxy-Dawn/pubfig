"""Color palettes and utilities."""

from .palettes import (
    DEFAULT,
    JAMA,
    LANCET,
    NATURE,
    ORANGE_RED_4,
    SCIENCE,
    get_palette,
    register_palette,
)
from .utils import color_to_rgba, darken_color, show_palette

__all__ = [
    "NATURE",
    "SCIENCE",
    "LANCET",
    "JAMA",
    "DEFAULT",
    "ORANGE_RED_4",
    "get_palette",
    "register_palette",
    "color_to_rgba",
    "darken_color",
    "show_palette",
]
