"""Shared style helpers for publication figures (Matplotlib).

These helpers keep plot functions consistent with the active Theme without
hard-coding lots of repeated magic numbers.
"""

from __future__ import annotations

import math
from typing import Literal, Optional, Sequence

import matplotlib as mpl

from .themes import Theme, get_default_theme


def title_above(
    ax,  # type: ignore[valid-type]
    title: str,
    *,
    y: float = 1.16,
    pad: float = 0.0,
    loc: str = "center",
    **kwargs,
):
    """Place a compact axes title above the plotting area without wasting vertical space."""
    kwargs.setdefault("fontweight", "semibold")
    kwargs.setdefault("fontfamily", mpl.rcParams.get("font.family"))
    txt = ax.set_title(str(title), loc=str(loc), y=float(y), pad=float(pad), **kwargs)
    try:
        txt.set_in_layout(True)
    except Exception:
        pass
    return txt


def coerce_linewidth(
    theme: Optional[Theme],
    *,
    kind: Literal["axis", "data", "errorbar", "ref"] = "data",
) -> float:
    """Return a reasonable linewidth (in points) for a given artist kind."""
    t = theme if theme is not None else get_default_theme()
    axis_lw = float(t.axis.line_width)
    if kind == "axis":
        return axis_lw
    if kind == "errorbar":
        return max(axis_lw, 0.8)
    if kind == "ref":
        return max(axis_lw, 0.8)
    # data
    return max(axis_lw * 1.5, 1.2)


def coerce_marker_size(
    theme: Optional[Theme],
    *,
    kind: Literal["line", "scatter", "paired", "bubble"] = "scatter",
) -> float:
    """Return a reasonable marker size (in points) for a given plot kind."""
    t = theme if theme is not None else get_default_theme()
    base = float(t.font_size)
    if kind == "line":
        return max(3.0, base * 0.5)
    if kind == "paired":
        return max(3.5, base * 0.6)
    if kind == "bubble":
        return max(12.0, base * 2.0)
    # scatter
    return max(4.0, base * 0.8)


def legend_above(
    ax,  # type: ignore[valid-type]
    *,
    ncol: Optional[int] = None,
    y: float = 1.25,
    x: float = 0.5,
    max_cols: int = 6,
    frameon: bool = False,
    **kwargs,
):
    """Place a legend above the axes (Nature-like), avoiding data occlusion.

    Returns:
        The created legend, or None if there is nothing to show.
    """
    handles, labels = ax.get_legend_handles_labels() if hasattr(ax, "get_legend_handles_labels") else ([], [])
    if not labels:
        return None

    if ncol is None:
        ncol = max(1, min(int(len(labels)), int(max_cols)))

    # Lift the legend higher when it wraps to multiple rows. Using a fixed small y offset
    # (e.g. 1.02) often causes the legend to overlap the top of the plotting area,
    # especially for bar/scatter where data can touch the top edge.
    nrows = int(math.ceil(len(labels) / float(ncol))) if ncol > 0 else 1
    # Extra lift to avoid overlap with titles when both are present.
    # Empirically, legend height scales roughly with number of rows; use a larger per-row
    # lift so multi-row legends do not collide with the axes title.
    y_final = float(y) + 0.18 * float(max(0, nrows - 1))

    kwargs.setdefault(
        "prop",
        {
            "family": mpl.rcParams.get("font.family"),
            "size": mpl.rcParams.get("legend.fontsize"),
        },
    )
    leg = ax.legend(
        handles=handles,
        labels=labels,
        frameon=bool(frameon),
        ncol=int(ncol),
        loc="upper center",
        bbox_to_anchor=(float(x), float(y_final)),
        **kwargs,
    )
    # Make sure layout engines reserve space for the legend.
    try:
        leg.set_in_layout(True)
    except Exception:
        pass
    try:
        leg.set_zorder(10)
    except Exception:
        pass
    return leg


def legend_below_title(
    ax,  # type: ignore[valid-type]
    *,
    ncol: Optional[int] = None,
    loc: str = "upper center",
    x: float = 0.5,
    y_if_no_title: float = 1.18,
    gap: float = 0.06,
    max_cols: int = 6,
    frameon: bool = False,
    **kwargs,
):
    """Place a legend below the title (and above the axes), avoiding data occlusion."""
    handles, labels = ax.get_legend_handles_labels() if hasattr(ax, "get_legend_handles_labels") else ([], [])
    if not labels:
        return None

    if ncol is None:
        ncol = max(1, min(int(len(labels)), int(max_cols)))

    title_text = ax.get_title() if hasattr(ax, "get_title") else ""
    if title_text:
        title_y = float(getattr(ax.title, "get_position")()[1])  # axes coords
        y_anchor = max(1.02, title_y - float(gap))
    else:
        y_anchor = float(y_if_no_title)

    kwargs.setdefault(
        "prop",
        {
            "family": mpl.rcParams.get("font.family"),
            "size": mpl.rcParams.get("legend.fontsize"),
        },
    )
    leg = ax.legend(
        handles=handles,
        labels=labels,
        frameon=bool(frameon),
        ncol=int(ncol),
        loc=str(loc),
        bbox_to_anchor=(float(x), float(y_anchor)),
        **kwargs,
    )
    try:
        leg.set_in_layout(True)
    except Exception:
        pass
    try:
        leg.set_zorder(10)
    except Exception:
        pass
    return leg


def note_below_title(
    ax,  # type: ignore[valid-type]
    text: str,
    *,
    x: float = 0.0,
    y_if_no_title: float = 1.18,
    gap: float = 0.06,
    ha: str = "left",
    va: str = "bottom",
    **kwargs,
):
    """Add a small note below the title (outside axes), useful for significance keys."""
    title_text = ax.get_title() if hasattr(ax, "get_title") else ""
    if title_text:
        title_y = float(getattr(ax.title, "get_position")()[1])
        y = max(1.02, title_y - float(gap))
    else:
        y = float(y_if_no_title)

    kwargs.setdefault("fontfamily", mpl.rcParams.get("font.family"))
    txt = ax.text(
        float(x),
        float(y),
        str(text),
        transform=ax.transAxes,
        ha=str(ha),
        va=str(va),
        clip_on=False,
        **kwargs,
    )
    try:
        txt.set_in_layout(True)
    except Exception:
        pass
    try:
        txt.set_zorder(10)
    except Exception:
        pass
    return txt


def normalize_palette(palette: Optional[Sequence[str]], *, fallback: Sequence[str]) -> list[str]:
    """Return a non-empty list of colors."""
    if palette is None:
        return list(fallback)
    colors = [str(c) for c in palette]
    return colors if colors else list(fallback)


def apply_cartesian_axis_controls(
    ax,  # type: ignore[valid-type]
    *,
    tick_direction: Literal["in", "out", "inout"] | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    grid_color: str = "0.85",
    grid_linestyle: str = "--",
    grid_line_width: float = 0.6,
) -> None:
    """Apply common Cartesian-axis controls after theme defaults.

    This helper is intended for standard 2D x/y axes. It should be called after
    ``Theme.apply_axes(...)`` so explicit function arguments override theme defaults.
    """
    if tick_direction is not None and hasattr(ax, "tick_params"):
        ax.tick_params(axis="both", direction=str(tick_direction))

    if show_full_box is not None and hasattr(ax, "spines"):
        for name in ("left", "bottom"):
            if name in ax.spines:
                ax.spines[name].set_visible(True)
        for name in ("top", "right"):
            if name in ax.spines:
                ax.spines[name].set_visible(bool(show_full_box))

    grid_kwargs = {
        "color": str(grid_color),
        "linestyle": str(grid_linestyle),
        "linewidth": float(grid_line_width),
    }
    if show_x_grid is not None and hasattr(ax, "xaxis"):
        if bool(show_x_grid):
            ax.xaxis.grid(True, which="major", **grid_kwargs)
        else:
            ax.xaxis.grid(False, which="major")
    if show_y_grid is not None and hasattr(ax, "yaxis"):
        if bool(show_y_grid):
            ax.yaxis.grid(True, which="major", **grid_kwargs)
        else:
            ax.yaxis.grid(False, which="major")
