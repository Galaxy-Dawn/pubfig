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
from .plotly_palettes import (
    PLOTLY_CARTO_PALETTES,
    PLOTLY_CMOCEAN_PALETTES,
    PLOTLY_COLORBREWER_PALETTES,
    PLOTLY_PALETTES,
)
from .utils import color_to_rgba, darken_color, show_palette

__all__ = [
    "PLOTLY_CARTO_PALETTES",
    "PLOTLY_CMOCEAN_PALETTES",
    "PLOTLY_COLORBREWER_PALETTES",
    "PLOTLY_PALETTES",
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
