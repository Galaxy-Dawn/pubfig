"""Matplotlib theme system (publication-oriented defaults)."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Iterator, Mapping

import matplotlib as mpl


@dataclass(frozen=True)
class AxisStyle:
    """Axis styling configuration for Matplotlib Axes."""

    label_font_size: int = 11
    tick_font_size: int = 9
    line_width: float = 1.5
    line_color: str = "black"
    tick_color: str = "black"
    tick_direction: str = "out"
    tick_length: float = 4.0
    tick_width: float = 1.5
    show_left_spine: bool = True
    show_bottom_spine: bool = True
    show_top_spine: bool = False
    show_right_spine: bool = False
    show_grid: bool = False
    grid_color: str = "0.9"
    grid_line_width: float = 0.5


@dataclass(frozen=True)
class Theme:
    """Publication theme configuration for Matplotlib."""

    name: str = "default"
    font_family: str | list[str] = "Arial"
    font_size: int = 10
    font_color: str = "black"
    title_font_size: int = 12
    legend_font_size: int = 9
    background_color: str = "#FFFFFF"
    axis: AxisStyle = field(default_factory=AxisStyle)
    rc_overrides: Mapping[str, Any] = field(default_factory=dict)

    def rc_params(self) -> dict[str, Any]:
        """Build rcParams for this theme."""
        a = self.axis
        rc: dict[str, Any] = {
            # Typography
            "font.family": self.font_family,
            "font.size": self.font_size,
            "text.color": self.font_color,
            "axes.titlesize": self.title_font_size,
            "axes.labelsize": a.label_font_size,
            "xtick.labelsize": a.tick_font_size,
            "ytick.labelsize": a.tick_font_size,
            "legend.fontsize": self.legend_font_size,
            # Spacing and legend (publication-style defaults).
            "axes.labelpad": 2.5,
            "axes.titlepad": 2.0,
            "xtick.major.pad": 2.0,
            "ytick.major.pad": 2.0,
            "legend.frameon": False,
            "legend.fancybox": False,
            "legend.borderaxespad": 0.3,
            "legend.handlelength": 1.5,
            "legend.handletextpad": 0.4,
            "legend.columnspacing": 0.8,
            # Default artist sizes (many plot functions override explicitly).
            "lines.linewidth": 1.2,
            "lines.markersize": 3.5,
            "lines.markeredgewidth": 0.6,
            "patch.linewidth": 0.6,
            # Axes
            "axes.edgecolor": a.line_color,
            "axes.linewidth": a.line_width,
            "axes.labelcolor": self.font_color,
            "axes.spines.left": a.show_left_spine,
            "axes.spines.bottom": a.show_bottom_spine,
            "axes.spines.top": a.show_top_spine,
            "axes.spines.right": a.show_right_spine,
            "axes.axisbelow": True,
            "axes.grid": a.show_grid,
            "grid.color": a.grid_color,
            "grid.linewidth": a.grid_line_width,
            # Ticks
            "xtick.direction": a.tick_direction,
            "ytick.direction": a.tick_direction,
            "xtick.color": a.tick_color,
            "ytick.color": a.tick_color,
            "xtick.major.size": a.tick_length,
            "ytick.major.size": a.tick_length,
            "xtick.major.width": a.tick_width,
            "ytick.major.width": a.tick_width,
            # Backgrounds
            "figure.facecolor": self.background_color,
            "figure.edgecolor": self.background_color,
            "axes.facecolor": self.background_color,
            "savefig.facecolor": self.background_color,
            "savefig.edgecolor": self.background_color,
            # Keep text as text in vector outputs.
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "none",
        }
        rc.update(dict(self.rc_overrides))
        return rc

    @contextmanager
    def context(self) -> Iterator["Theme"]:
        """Temporarily apply rcParams for this theme."""
        with mpl.rc_context(self.rc_params()):
            yield self

    def apply_axes(self, ax) -> None:  # type: ignore[valid-type]
        """Apply axis styling to an Axes instance."""
        a = self.axis
        font_family = self.font_family

        # Common 2D axes spines/ticks.
        if hasattr(ax, "spines"):
            spine_visible = {
                "left": bool(a.show_left_spine),
                "bottom": bool(a.show_bottom_spine),
                "top": bool(a.show_top_spine),
                "right": bool(a.show_right_spine),
            }
            for name, spine in ax.spines.items():
                visible = spine_visible.get(str(name), True)
                spine.set_visible(bool(visible))
                spine.set_linewidth(a.line_width)
                spine.set_color(a.line_color)

        if hasattr(ax, "tick_params"):
            ax.tick_params(
                direction=a.tick_direction,
                length=a.tick_length,
                width=a.tick_width,
                colors=a.tick_color,
                labelsize=a.tick_font_size,
            )

        # Explicit font-family application for existing axis/title/tick artists.
        if hasattr(ax, "title"):
            try:
                ax.title.set_fontfamily(font_family)
            except Exception:
                pass

        for axis_name in ("xaxis", "yaxis", "zaxis"):
            axis_obj = getattr(ax, axis_name, None)
            if axis_obj is None:
                continue
            try:
                axis_obj.label.set_fontfamily(font_family)
            except Exception:
                pass
            try:
                for tick_label in axis_obj.get_ticklabels():
                    tick_label.set_fontfamily(font_family)
            except Exception:
                pass

        # Grid.
        if hasattr(ax, "grid"):
            if a.show_grid:
                ax.grid(True, color=a.grid_color, linewidth=a.grid_line_width)
            else:
                ax.grid(False)

        # Facecolor.
        if hasattr(ax, "set_facecolor"):
            ax.set_facecolor(self.background_color)

    def apply(self, target) -> None:  # type: ignore[valid-type]
        """Apply theme to a Figure or Axes."""
        from matplotlib.axes import Axes
        from matplotlib.figure import Figure

        if isinstance(target, Axes):
            self.apply_axes(target)
            target.figure.set_facecolor(self.background_color)
            return
        if isinstance(target, Figure):
            target.set_facecolor(self.background_color)
            for ax in target.axes:
                self.apply_axes(ax)
            return
        raise TypeError("Theme.apply expects a matplotlib Axes or Figure")
