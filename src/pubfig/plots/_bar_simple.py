"""Simple and grouped bar charts (Matplotlib)."""

from __future__ import annotations

from typing import Literal, Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import apply_cartesian_axis_controls, legend_below_title, normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def bar(
    data: np.ndarray,
    *,
    category_names: Optional[list[str]] = None,
    series_names: Optional[list[str]] = None,
    category_spacing: float = 0.75,
    x_label: str = "Categories",
    y_label: str = "Values",
    orientation: Literal["vertical", "horizontal"] = "vertical",
    auto_swap_axis_labels: bool = True,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    value_dtick: Optional[float] = None,
    value_nticks: Optional[int] = None,
    tick_direction: Literal["in", "out", "inout"] | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    bar_width_1d: float = 0.7,
    bar_edgecolor: str = "none",
    bar_line_width: float = 0.0,
    grouped_total_span: float = 0.6,
    grouped_left_offset: Optional[float] = None,
    grouped_bar_width_ratio: float = 0.8,
    grouped_bar_edgecolor: str = "none",
    grouped_bar_line_width: float = 0.0,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 6,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a bar chart (simple or grouped).

    Args:
        data: 1D (simple bars) or 2D (grouped) array.
        category_names: Category labels for the categorical axis. For 1D input this labels each
            bar; for 2D input this labels each grouped category.
        series_names: Legend labels for grouped bars (2D).
        category_spacing: Distance between adjacent categorical groups in axis units.
            Use values below 1.0 for a denser, more compact layout.
        x_label: X axis label.
        y_label: Y axis label.
        orientation: Plot orientation. "vertical" uses vertical bars (default). "horizontal" rotates
            the plot by 90 degrees using horizontal bars.
        auto_swap_axis_labels: If True and `orientation="horizontal"`, swap `x_label`/`y_label` so
            the default labels remain correct ("Values" on x, "Categories" on y).
        title: Optional plot title.
        color_palette: List of colors.
        value_dtick: If set, enforce a fixed major tick step on the value axis.
        value_nticks: If set (and `value_dtick` is None), set an approximate number of major ticks
            on the value axis.
        tick_direction: Override tick direction ("in", "out", "inout") on both axes.
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.

        bar_width_1d: Bar width for 1D charts (data units).
        bar_edgecolor: Edge color for 1D bars (use "none" to remove borders).
        bar_line_width: Edge line width for 1D bars.

        grouped_total_span: Total horizontal span reserved per category for grouped bars.
        grouped_left_offset: Left offset used to center grouped bars within each category.
            If None, defaults to `grouped_total_span / 2`.
        grouped_bar_width_ratio: Each bar width as a fraction of per-group spacing.
        grouped_bar_edgecolor: Edge color for grouped bars.
        grouped_bar_line_width: Edge line width for grouped bars.

        legend_show: Whether to show the legend for grouped (2D) bars.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns (only used when `legend_ncol` is None).

        theme: Optional Theme override.
        width: Figure width in pixels (design DPI space).
        height: Figure height in pixels (design DPI space).
        ax: Optional Matplotlib Axes to draw into.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim not in (1, 2):
        raise ValueError("Data must be a 1D or 2D array.")

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    resolved_grouped_left_offset = (
        float(grouped_total_span) / 2.0 if grouped_left_offset is None else float(grouped_left_offset)
    )

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        if orientation == "horizontal" and auto_swap_axis_labels:
            x_label, y_label = y_label, x_label

        if data.ndim == 1:
            n = int(data.shape[0])
            if category_names is None:
                category_names = [f"Category {i + 1}" for i in range(n)]
            pos = np.arange(n, dtype=float) * float(category_spacing)
            if orientation == "vertical":
                ax.bar(
                    pos,
                    data,
                    color=[colors[i % len(colors)] for i in range(n)],
                    edgecolor=str(bar_edgecolor),
                    linewidth=float(bar_line_width),
                    width=float(bar_width_1d),
                )
                ax.set_xticks(pos, labels=category_names)
            else:
                ax.barh(
                    pos,
                    data,
                    color=[colors[i % len(colors)] for i in range(n)],
                    edgecolor=str(bar_edgecolor),
                    linewidth=float(bar_line_width),
                    height=float(bar_width_1d),
                )
                ax.set_yticks(pos, labels=category_names)
        else:
            num_categories, num_groups = data.shape
            if category_names is None:
                category_names = [f"Category {i + 1}" for i in range(num_categories)]
            if series_names is None:
                series_names = [f"Series {i + 1}" for i in range(num_groups)]

            category_positions = np.arange(num_categories, dtype=float) * float(category_spacing)
            bw = float(grouped_total_span) / float(num_groups)
            for i in range(num_groups):
                pos = category_positions - float(resolved_grouped_left_offset) + (i + 0.5) * bw
                if orientation == "vertical":
                    ax.bar(
                        pos,
                        data[:, i],
                        width=bw * float(grouped_bar_width_ratio),
                        color=colors[i % len(colors)],
                        edgecolor=str(grouped_bar_edgecolor),
                        linewidth=float(grouped_bar_line_width),
                        label=series_names[i],
                    )
                else:
                    ax.barh(
                        pos,
                        data[:, i],
                        height=bw * float(grouped_bar_width_ratio),
                        color=colors[i % len(colors)],
                        edgecolor=str(grouped_bar_edgecolor),
                        linewidth=float(grouped_bar_line_width),
                        label=series_names[i],
                    )
            if orientation == "vertical":
                ax.set_xticks(category_positions, labels=category_names)
            else:
                ax.set_yticks(category_positions, labels=category_names)

        if data.ndim == 1:
            outer_half_width = max(float(bar_width_1d), 0.5) / 2.0
            outer_padding = max(0.12, 0.18 * float(category_spacing), 0.12 * float(bar_width_1d))
            lower = float(pos[0] - outer_half_width - outer_padding)
            upper = float(pos[-1] + outer_half_width + outer_padding)
        else:
            lower = float(category_positions[0] - float(grouped_total_span) / 2.0 - 0.15)
            upper = float(category_positions[-1] + float(grouped_total_span) / 2.0 + 0.15)
        if orientation == "vertical":
            ax.set_xlim(lower, upper)
        else:
            ax.set_ylim(lower, upper)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            title_above(ax, title, y=1.06)
        if data.ndim == 2 and bool(legend_show):
            n = len(series_names) if series_names is not None else 0
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(int(n), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol), gap=0.015, y_if_no_title=1.12)

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        if value_dtick is not None or value_nticks is not None:
            import matplotlib.ticker as mticker

            axis = ax.yaxis if orientation == "vertical" else ax.xaxis
            if value_dtick is not None:
                axis.set_major_locator(mticker.MultipleLocator(float(value_dtick)))
            else:
                axis.set_major_locator(mticker.MaxNLocator(nbins=int(value_nticks)))
        fig.tight_layout()
        return fig
