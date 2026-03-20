"""Curated academic color palettes."""

from typing import Sequence

from .plotly_palettes import PLOTLY_PALETTES

# Nature-style palette
NATURE: list[str] = [
    "#E64B35", "#4DBBD5", "#00A087", "#3C5488",
    "#F39B7F", "#8491B4", "#91D1C2", "#DC0000",
    "#7E6148", "#B09C85",
]

# Science-style palette
SCIENCE: list[str] = [
    "#3B4992", "#EE0000", "#008B45", "#631879",
    "#008280", "#BB0021", "#5F559B", "#A20056",
    "#808180", "#1B1919",
]

# Lancet palette
LANCET: list[str] = [
    "#00468B", "#ED0000", "#42B540", "#0099B4",
    "#925E9F", "#FDAF91", "#AD002A", "#ADB6B6",
    "#1B1919",
]

# JAMA palette
JAMA: list[str] = [
    "#374E55", "#DF8F44", "#00A1D5", "#B24745",
    "#79AF97", "#6A6599", "#80796B",
]

# Default palette (same as Nature)
DEFAULT: list[str] = NATURE

# Orange -> red gradient (4 colors), useful when groups represent increasing intensity.
ORANGE_RED_4: list[str] = [
    "#FEB24C",  # orange
    "#FD8D3C",  # orange-red
    "#FC4E2A",  # red-orange (lighter)
    "#F03B20",  # red-orange (previous 3rd color; less aggressive than deep red)
]

_PALETTE_REGISTRY: dict[str, list[str]] = {
    "nature": NATURE,
    "science": SCIENCE,
    "lancet": LANCET,
    "jama": JAMA,
    "orange_red": ORANGE_RED_4,
    "default": DEFAULT,
    **PLOTLY_PALETTES,
}


def get_palette(name: str) -> list[str]:
    """Get a named color palette."""
    key = name.lower()
    if key not in _PALETTE_REGISTRY:
        raise KeyError(f"Unknown palette '{name}'. Available: {list(_PALETTE_REGISTRY)}")
    return _PALETTE_REGISTRY[key]


def register_palette(name: str, colors: Sequence[str]) -> None:
    """Register a custom color palette."""
    _PALETTE_REGISTRY[name.lower()] = list(colors)
