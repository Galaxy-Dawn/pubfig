"""Stacked bar charts (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import apply_cartesian_axis_controls, normalize_palette
from ..colors.palettes import DEFAULT
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def stacked_bar(
    data: np.ndarray,
    *,
    group_names: Optional[list[str]] = None,
    category_spacing: Optional[float] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    normalize: bool = True,
    bar_thickness: float = 0.25,
    bar_height_ratio: float = 0.9,
    group_gap: Optional[float] = None,
    xlim_normalized: tuple[float, float] = (0.0, 1.0),
    height_min_px: int = 300,
    height_row_px: int = 15,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 6,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = 800,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a horizontal stacked bar chart.

    Args:
        data: 3D array `(groups, rows, segments)`.
        group_names: Labels for the outer groups shown on the y-axis.
        category_spacing: Preferred extra spacing between adjacent outer groups (data units).
            If provided, overrides `group_gap`. Use smaller values for a denser layout.
        x_label: X-axis label.
        y_label: Y-axis label.
        title: Optional plot title.
        color_palette: Optional palette used for stacked segments.
        normalize: If True, normalize each `(group, row)` to sum to 1.0 so rows have
            consistent total length (composition view). Set False for absolute totals.
        bar_thickness: Height of each row (data units).
        bar_height_ratio: Actual bar height as a fraction of `bar_thickness`.
        group_gap: Extra whitespace between outer groups (data units).
        xlim_normalized: X limits to use when `normalize=True`.
        height_min_px: Minimum figure height in pixels when `height` is None.
        height_row_px: Per-row height scaling (pixels) when `height` is None.
        legend_show: Whether to show the legend.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns.
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    if not isinstance(data, np.ndarray) or data.ndim != 3:
        raise ValueError("Data must be a 3D numpy array: (groups, rows, segments)")

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    n_groups, n_rows, n_segments = data.shape
    if group_names is None:
        group_names = [f"Group {i + 1}" for i in range(n_groups)]
    resolved_group_gap = (
        float(category_spacing)
        if category_spacing is not None
        else (0.35 if group_gap is None else float(group_gap))
    )

    if bar_thickness <= 0:
        raise ValueError("bar_thickness must be > 0")
    if resolved_group_gap < 0:
        raise ValueError("group_gap must be >= 0")
    group_step = float(n_rows) * float(bar_thickness) + float(resolved_group_gap)

    all_y: list[float] = []
    all_x: list[np.ndarray] = []
    for group_idx in range(n_groups):
        y_base = float(group_idx) * group_step
        for row_idx in range(n_rows):
            all_y.append(y_base + float(row_idx) * float(bar_thickness))
            all_x.append(data[group_idx, row_idx, :])

    y = np.asarray(all_y, dtype=float)
    x = np.asarray(all_x, dtype=float)  # shape: (n_groups*n_rows, n_segments)

    if normalize:
        if np.any(x < 0):
            raise ValueError("normalize=True requires non-negative values (stacked composition).")
        row_sums = np.sum(x, axis=1, dtype=float)
        nonzero = row_sums > 0
        if np.any(nonzero):
            x[nonzero, :] = x[nonzero, :] / row_sums[nonzero, None]

    if height is None:
        height = max(int(height_min_px), n_groups * (n_rows + 1) * int(height_row_px))

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        left = np.zeros(len(y), dtype=float)
        for segment_idx in range(n_segments):
            ax.barh(
                y,
                x[:, segment_idx],
                left=left,
                height=float(bar_thickness) * float(bar_height_ratio),
                color=colors[segment_idx % len(colors)],
                edgecolor="none",
                label=f"Segment {segment_idx + 1}",
            )
            left = left + x[:, segment_idx]

        if normalize:
            ax.set_xlim(float(xlim_normalized[0]), float(xlim_normalized[1]))

        group_positions = [
            float(i) * group_step + (n_rows - 1) * float(bar_thickness) / 2 for i in range(n_groups)
        ]
        ax.set_yticks(group_positions, labels=group_names)
        ax.set_ylabel(y_label or "Group")
        ax.set_xlabel(x_label or ("Proportion" if normalize else ""))
        if title:
            sup = fig.suptitle(
                str(title),
                y=0.968,
                fontsize=float(t.title_font_size),
                color=str(t.font_color),
                fontfamily=t.font_family,
                fontweight="semibold",
            )
            try:
                sup.set_in_layout(True)
            except Exception:
                pass

        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else min(int(legend_ncol_max), max(1, min(n_segments, 5)))
            legend = ax.legend(
                frameon=False,
                ncol=int(ncol),
                loc="lower center",
                bbox_to_anchor=(0.5, 1.02),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
            )
            try:
                legend.set_in_layout(True)
            except Exception:
                pass
            try:
                legend.set_zorder(10)
            except Exception:
                pass
        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.95) if title else None)
        return fig
