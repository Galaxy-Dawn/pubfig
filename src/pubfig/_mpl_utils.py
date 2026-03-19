"""Small Matplotlib helpers used across plot functions."""

from __future__ import annotations

from typing import Optional

from .specs import get_figure_spec, px_to_inches


def resolve_design_dpi(theme_name: Optional[str]) -> int:
    """Resolve design DPI from a theme name via FigureSpec registry."""
    key = (theme_name or "nature").strip().lower()
    try:
        return int(get_figure_spec(key).design_dpi)
    except Exception:
        return int(get_figure_spec("nature").design_dpi)


def resolve_figsize_inches(
    *,
    width_px: Optional[int],
    height_px: Optional[int],
    design_dpi: int,
    default_aspect_ratio: float = 0.75,
) -> Optional[tuple[float, float]]:
    """Convert optional width/height in design pixels to a Matplotlib figsize in inches."""
    if width_px is None and height_px is None:
        return None

    if width_px is not None and height_px is not None:
        return (px_to_inches(width_px, dpi=design_dpi), px_to_inches(height_px, dpi=design_dpi))

    if width_px is not None:
        w = px_to_inches(width_px, dpi=design_dpi)
        return (w, w * float(default_aspect_ratio))

    h = px_to_inches(height_px, dpi=design_dpi)
    return (h / float(default_aspect_ratio), h)


def get_fig_ax(
    *,
    ax=None,  # type: ignore[valid-type]
    width_px: Optional[int] = None,
    height_px: Optional[int] = None,
    design_dpi: int = 96,
    projection: Optional[str] = None,
):
    """Return (fig, ax), creating them if needed."""
    if ax is not None:
        return ax.figure, ax

    import matplotlib.pyplot as plt

    figsize = resolve_figsize_inches(width_px=width_px, height_px=height_px, design_dpi=design_dpi)
    subplot_kw = {"projection": projection} if projection is not None else None
    fig, new_ax = plt.subplots(figsize=figsize, subplot_kw=subplot_kw)
    return fig, new_ax


def resolve_cmap(name: str) -> str:
    """Resolve a colormap name robustly (accepts common capitalization variants)."""
    import matplotlib as mpl

    if name in mpl.colormaps:
        return name
    lower = name.lower()
    if lower in mpl.colormaps:
        return lower
    return name
