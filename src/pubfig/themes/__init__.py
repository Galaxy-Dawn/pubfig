"""Theme registry for Matplotlib figures."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional

import matplotlib as mpl

from .base import AxisStyle, Theme
from .cell import CELL_THEME
from .default import DEFAULT_THEME
from .nature import NATURE_THEME
from .science import SCIENCE_THEME

_THEME_REGISTRY: dict[str, Theme] = {
    "default": DEFAULT_THEME,
    "nature": NATURE_THEME,
    "science": SCIENCE_THEME,
    "cell": CELL_THEME,
}

_current_theme: Theme = NATURE_THEME


def set_default_theme(name_or_theme: str | Theme) -> None:
    """Set the global default theme."""
    global _current_theme
    if isinstance(name_or_theme, Theme):
        _current_theme = name_or_theme
    else:
        _current_theme = get_theme(name_or_theme)


def get_default_theme() -> Theme:
    """Get the current global default theme."""
    return _current_theme


def get_theme(name: str) -> Theme:
    """Get a named theme."""
    key = name.strip().lower()
    if key not in _THEME_REGISTRY:
        raise KeyError(f"Unknown theme '{name}'. Available: {list(_THEME_REGISTRY)}")
    return _THEME_REGISTRY[key]


def register_theme(name: str, theme: Theme) -> None:
    """Register a custom theme."""
    _THEME_REGISTRY[name.strip().lower()] = theme


@contextmanager
def theme_context(theme: Optional[Theme] = None) -> Iterator[Theme]:
    """Temporarily apply rcParams for a theme."""
    t = theme if theme is not None else _current_theme
    with mpl.rc_context(t.rc_params()):
        yield t


def _apply_theme(target, theme: Optional[Theme] = None):  # type: ignore[valid-type]
    """Apply theme to a Figure or Axes. Uses global default if none specified."""
    t = theme if theme is not None else _current_theme
    t.apply(target)
    return target


__all__ = [
    "AxisStyle",
    "Theme",
    "DEFAULT_THEME",
    "NATURE_THEME",
    "SCIENCE_THEME",
    "CELL_THEME",
    "set_default_theme",
    "get_default_theme",
    "get_theme",
    "register_theme",
    "theme_context",
]
