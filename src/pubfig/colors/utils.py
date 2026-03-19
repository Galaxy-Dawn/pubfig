"""Color utility functions (Matplotlib)."""

from __future__ import annotations

import re
from typing import Sequence

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi


_RGB_RE = re.compile(r"rgba?\(([^)]+)\)")


def _parse_color_rgb(color: str) -> tuple[float, float, float]:
    """Parse a color string into RGB floats in [0,1]."""
    import matplotlib.colors as mcolors

    c = color.strip()
    if c.startswith("#") or c.lower() in mcolors.get_named_colors_mapping():
        return tuple(float(x) for x in mcolors.to_rgb(c))  # type: ignore[return-value]

    m = _RGB_RE.match(c.lower())
    if m is None:
        # Fall back to Matplotlib's parser for other formats.
        return tuple(float(x) for x in mcolors.to_rgb(c))  # type: ignore[return-value]

    parts = [p.strip() for p in m.group(1).split(",")]
    if len(parts) < 3:
        raise ValueError(f"Unsupported color format: {color}")

    rgb = [float(parts[0]), float(parts[1]), float(parts[2])]
    # Accept 0-255 or 0-1.
    if any(v > 1 for v in rgb):
        rgb = [v / 255.0 for v in rgb]

    return (float(rgb[0]), float(rgb[1]), float(rgb[2]))


def color_to_rgba(color: str, alpha: float = 0.6) -> tuple[float, float, float, float]:
    """Convert a color string to an RGBA tuple usable by Matplotlib."""
    r, g, b = _parse_color_rgb(color)
    return (r, g, b, float(alpha))


def darken_color(color: str, factor: float = 0.9) -> str:
    """Darken a color by a factor and return a hex string."""
    import matplotlib.colors as mcolors

    if not (0 < factor <= 1):
        raise ValueError("factor must be in (0, 1]")
    r, g, b = _parse_color_rgb(color)
    r2, g2, b2 = (max(0.0, min(1.0, r * factor)), max(0.0, min(1.0, g * factor)), max(0.0, min(1.0, b * factor)))
    return mcolors.to_hex((r2, g2, b2))


def show_palette(
    colors: Sequence[str],
    *,
    width: int = 600,
    height: int = 400,
):
    """Display a color palette as a bar chart (Matplotlib Figure)."""
    import matplotlib.pyplot as plt

    dpi = resolve_design_dpi("nature")
    fig, ax = get_fig_ax(width_px=width, height_px=height, design_dpi=dpi)

    n = len(colors)
    x = np.arange(n)
    ax.bar(x, np.ones(n), color=list(colors), edgecolor="black", linewidth=0.8)
    ax.set_ylim(0, 1.2)
    ax.set_xticks(x, labels=[str(i + 1) for i in range(n)])
    ax.set_yticks([])
    ax.set_xlabel("Color Index")
    ax.set_title("Palette", fontfamily=plt.rcParams.get("font.family"))
    for spine in ax.spines.values():
        spine.set_visible(False)
    plt.tight_layout()
    return fig
