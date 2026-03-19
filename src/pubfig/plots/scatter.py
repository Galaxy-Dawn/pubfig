"""Scatter plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._compat import _require
from .._mpl_utils import get_fig_ax, resolve_cmap, resolve_design_dpi, resolve_figsize_inches
from .._style import apply_cartesian_axis_controls, coerce_linewidth, legend_below_title, normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _resolve_range(lo: Optional[float], hi: Optional[float], arr: np.ndarray) -> Optional[tuple[float, float]]:
    if lo is not None and hi is not None:
        return (float(lo), float(hi))
    if lo is not None:
        return (float(lo), float(np.max(arr)))
    if hi is not None:
        return (float(np.min(arr)), float(hi))
    return None


def scatter(
    x: np.ndarray,
    y: np.ndarray,
    *,
    labels: Optional[np.ndarray] = None,
    x_label: str = "X",
    y_label: str = "Y",
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    scatter_size: float = 3.8,
    scatter_alpha: float = 0.72,
    scatter_marker: str = "o",
    group_marker_styles: Optional[Sequence[str]] = None,
    scatter_edgecolor: str = "white",
    scatter_edge_line_width: float = 0.2,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 4,
    show_y_equal_x: bool = False,
    y_equal_x_color: str = "0.65",
    y_equal_x_linestyle: str = "--",
    y_equal_x_line_width: Optional[float] = None,
    show_regression: bool = False,
    regression_color: str = "0.45",
    regression_linestyle: str = "-",
    regression_line_width: Optional[float] = None,
    regression_n_points: int = 300,
    stat_p_threshold: float = 0.001,
    stat_text_position: tuple[float, float] = (0.95, 0.05),
    stat_text_ha: str = "right",
    stat_text_va: str = "bottom",
    stat_p_decimals: int = 4,
    stat_text_font_size: Optional[int] = None,
    regression_text_position: tuple[float, float] = (0.05, 0.95),
    regression_text_ha: str = "left",
    regression_text_va: str = "top",
    regression_r2_decimals: int = 4,
    regression_text_font_size: Optional[int] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a 2D scatter plot with optional regression and y=x line.

    Args:
        x: X coordinates.
        y: Y coordinates.
        labels: Optional class / group labels used for color grouping and legend entries.
        x_label: X-axis label.
        y_label: Y-axis label.
        x_min: Optional lower bound of the x-axis.
        x_max: Optional upper bound of the x-axis.
        y_min: Optional lower bound of the y-axis.
        y_max: Optional upper bound of the y-axis.
        title: Optional plot title.
        color_palette: Optional palette used for grouped points.
        scatter_size: Marker diameter-like control in Matplotlib points. The plotted marker area
            is `scatter_size**2` (Matplotlib convention).
        scatter_alpha: Marker face alpha for points.
        scatter_marker: Marker style used when `labels` is not provided.
        group_marker_styles: Marker styles cycled across groups when `labels` is provided.
            If None, uses a Nature-like filled cycle: circle, square, diamond, triangle, inverted triangle.
        scatter_edgecolor: Marker edge color (e.g. "white" gives clean separation on dense plots).
        scatter_edge_line_width: Marker edge line width in points.
        legend_show: Whether to draw the legend when `labels` is provided.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns (only used when `legend_ncol` is None).

        show_y_equal_x: If True, draw a `y=x` reference line using `x_min/x_max` (or data range)
            and add a Wilcoxon signed-rank test annotation for `(y-x) > 0` (non-zero diffs only).
        y_equal_x_color: Color of the `y=x` line.
        y_equal_x_linestyle: Linestyle of the `y=x` line (e.g. "--").
        y_equal_x_line_width: Optional line width override for the `y=x` line.

        show_regression: If True, fit an OLS regression (statsmodels) and overlay a fitted line plus R^2.
        regression_color: Color of the regression line.
        regression_linestyle: Linestyle of the regression line.
        regression_line_width: Optional line width override for the regression line.
        regression_n_points: Number of x samples used to draw the fitted regression line.

        stat_p_threshold: P-value threshold used to switch the annotation from `p = ...` to `p < ...`.
        stat_text_position: (x, y) in axes coordinates (0..1) for the p-value text when `show_y_equal_x=True`.
        stat_text_ha: Horizontal alignment for the p-value text.
        stat_text_va: Vertical alignment for the p-value text.
        stat_p_decimals: Decimal places for the p-value text when formatted as `p = ...`.
        stat_text_font_size: Optional font size override for the p-value annotation.

        regression_text_position: (x, y) in axes coordinates (0..1) for the R^2 text when `show_regression=True`.
        regression_text_ha: Horizontal alignment for the R^2 text.
        regression_text_va: Vertical alignment for the R^2 text.
        regression_r2_decimals: Decimal places for the R^2 annotation.
        regression_text_font_size: Optional font size override for the R^2 annotation.
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    colors = normalize_palette(color_palette, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_ref_line_width = (
            float(y_equal_x_line_width)
            if y_equal_x_line_width is not None
            else float(coerce_linewidth(t, kind="ref")) * 0.7
        )
        resolved_regression_line_width = (
            float(regression_line_width)
            if regression_line_width is not None
            else float(coerce_linewidth(t, kind="data")) * 0.75
        )
        resolved_stat_text_font_size = (
            max(5, int(t.axis.tick_font_size) - 1) if stat_text_font_size is None else int(stat_text_font_size)
        )
        resolved_regression_text_font_size = (
            max(5, int(t.axis.tick_font_size) - 1)
            if regression_text_font_size is None
            else int(regression_text_font_size)
        )
        resolved_group_marker_styles = list(group_marker_styles) if group_marker_styles is not None else ["o", "s", "D", "^", "v"]

        if labels is not None:
            labels = np.asarray(labels)
            uniq = list(dict.fromkeys(labels.tolist()))
            for i, lab in enumerate(uniq):
                mask = labels == lab
                ax.scatter(
                    x[mask],
                    y[mask],
                    s=float(scatter_size) ** 2,
                    label=str(lab),
                    marker=str(resolved_group_marker_styles[i % len(resolved_group_marker_styles)]),
                    color=color_to_rgba(colors[i % len(colors)], alpha=float(scatter_alpha)),
                    edgecolor=scatter_edgecolor,
                    linewidth=float(scatter_edge_line_width),
                )
        else:
            ax.scatter(
                x,
                y,
                s=float(scatter_size) ** 2,
                marker=str(scatter_marker),
                color=color_to_rgba(colors[0], alpha=float(scatter_alpha)),
                edgecolor=scatter_edgecolor,
                linewidth=float(scatter_edge_line_width),
            )

        if show_y_equal_x:
            lo = float(x_min) if x_min is not None else float(np.min(x))
            hi = float(x_max) if x_max is not None else float(np.max(x))
            ax.plot(
                [lo, hi],
                [lo, hi],
                color=y_equal_x_color,
                linewidth=resolved_ref_line_width,
                linestyle=y_equal_x_linestyle,
            )

            from scipy import stats as sp_stats

            diff = y - x
            non_zero = diff[diff != 0]
            if len(non_zero) > 0:
                res = sp_stats.wilcoxon(non_zero, alternative="greater", zero_method="wilcox")
                if float(res.pvalue) < float(stat_p_threshold):
                    p_text = f"p < {stat_p_threshold}"
                else:
                    p_text = f"p = {float(res.pvalue):.{int(stat_p_decimals)}f}"
                ax.text(
                    float(stat_text_position[0]),
                    float(stat_text_position[1]),
                    p_text,
                    transform=ax.transAxes,
                    ha=stat_text_ha,
                    va=stat_text_va,
                    fontsize=resolved_stat_text_font_size,
                )

        if show_regression:
            _require("statsmodels", "stats")
            import statsmodels.api as sm

            X_mat = sm.add_constant(x)
            model = sm.OLS(y, X_mat).fit()
            x_fit = np.linspace(float(x.min()), float(x.max()), int(regression_n_points))
            y_fit = model.params[0] + model.params[1] * x_fit
            ax.plot(
                x_fit,
                y_fit,
                color=regression_color,
                linewidth=resolved_regression_line_width,
                linestyle=regression_linestyle,
            )
            ax.text(
                float(regression_text_position[0]),
                float(regression_text_position[1]),
                f"R\u00b2 = {float(model.rsquared):.{int(regression_r2_decimals)}f}",
                transform=ax.transAxes,
                ha=regression_text_ha,
                va=regression_text_va,
                fontsize=resolved_regression_text_font_size,
            )

        x_range = _resolve_range(x_min, x_max, x)
        y_range = _resolve_range(y_min, y_max, y)
        if x_range is not None:
            ax.set_xlim(*x_range)
        if y_range is not None:
            ax.set_ylim(*y_range)

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            title_above(ax, title)
        if labels is not None and bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(uniq), int(legend_ncol_max)))
            legend_below_title(ax, ncol=ncol)

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        fig.tight_layout()
        return fig


def contour2d(
    x: np.ndarray,
    y: np.ndarray,
    *,
    bins: int = 50,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    colorscale: Optional[str] = None,
    fallback_figsize_inches: tuple[float, float] = (6.4, 4.8),
    grid_width_ratios: tuple[float, float] = (4.0, 1.0),
    grid_height_ratios: tuple[float, float] = (1.0, 4.0),
    grid_hspace: float = 0.05,
    grid_wspace: float = 0.05,
    contour_levels: Optional[int] = None,
    contour_min_levels: int = 10,
    contour_levels_divisor: int = 4,
    marginal_alpha: float = 0.5,
    marginal_edgecolor: str = "none",
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
) -> "Figure":
    """Create a 2D histogram contour plot with marginal histograms.

    Args:
        x: X coordinates.
        y: Y coordinates.
        bins: Number of histogram bins per axis.
        title: Optional plot title.
        color_palette: Optional palette used for the marginal histograms.
        colorscale: Optional colormap name for the contour surface.
        fallback_figsize_inches: Used only when `width/height` are not provided and
            `resolve_figsize_inches(...)` cannot infer a size. Matplotlib default is (6.4, 4.8).
        grid_width_ratios: (main, right-marginal) width ratio for the 2x2 GridSpec.
        grid_height_ratios: (top-marginal, main) height ratio for the 2x2 GridSpec.
        grid_hspace: Vertical spacing between GridSpec cells.
        grid_wspace: Horizontal spacing between GridSpec cells.

        contour_levels: Explicit number of filled contour levels. If None, it is computed as
            `max(contour_min_levels, bins // contour_levels_divisor)` to match the previous behavior.
        contour_min_levels: Minimum contour level count when `contour_levels` is None.
        contour_levels_divisor: Divisor used in the default contour level heuristic.

        marginal_alpha: Alpha for marginal histograms.
        marginal_edgecolor: Edge color for marginal histogram bars.
        tick_direction: Override tick direction on the main x/y axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines on the main panel to form a full box.
        show_x_grid: Whether to show dashed major grid lines on the main panel x-axis.
        show_y_grid: Whether to show dashed major grid lines on the main panel y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
    """
    import matplotlib.pyplot as plt
    from matplotlib import gridspec

    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    colors = list(color_palette) if color_palette is not None else list(DEFAULT)
    cmap = resolve_cmap(colorscale or "viridis")

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        figsize = resolve_figsize_inches(width_px=width, height_px=height, design_dpi=dpi) or tuple(
            float(v) for v in fallback_figsize_inches
        )
        fig = plt.figure(figsize=figsize)
        gs = gridspec.GridSpec(
            2,
            2,
            width_ratios=[float(v) for v in grid_width_ratios],
            height_ratios=[float(v) for v in grid_height_ratios],
            hspace=float(grid_hspace),
            wspace=float(grid_wspace),
        )
        ax_histx = fig.add_subplot(gs[0, 0])
        ax_histy = fig.add_subplot(gs[1, 1])
        ax_main = fig.add_subplot(gs[1, 0])

        # Main contour from histogram2d.
        hist, xedges, yedges = np.histogram2d(x, y, bins=int(bins))
        xcent = (xedges[:-1] + xedges[1:]) / 2
        ycent = (yedges[:-1] + yedges[1:]) / 2
        Xc, Yc = np.meshgrid(xcent, ycent, indexing="xy")
        if contour_levels is None:
            n_levels = max(int(contour_min_levels), int(bins) // max(1, int(contour_levels_divisor)))
        else:
            n_levels = int(contour_levels)
        ax_main.contourf(Xc, Yc, hist.T, levels=int(n_levels), cmap=cmap)

        # Marginals.
        ax_histx.hist(
            x,
            bins=int(bins),
            color=color_to_rgba(colors[0], alpha=float(marginal_alpha)),
            edgecolor=marginal_edgecolor,
        )
        ax_histy.hist(
            y,
            bins=int(bins),
            orientation="horizontal",
            color=color_to_rgba(colors[0], alpha=float(marginal_alpha)),
            edgecolor=marginal_edgecolor,
        )

        ax_histx.set_xticks([])
        ax_histx.set_yticks([])
        ax_histy.set_xticks([])
        ax_histy.set_yticks([])

        if title:
            fig.suptitle(
                str(title),
                y=0.985,
                fontsize=float(t.title_font_size),
                color=str(t.font_color),
                fontfamily=t.font_family,
                fontweight="semibold",
            )
            fig.subplots_adjust(top=0.9)

        t.apply_axes(ax_main)
        apply_cartesian_axis_controls(
            ax_main,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        for a in (ax_histx, ax_histy):
            a.set_facecolor(t.background_color)
            for spine in a.spines.values():
                spine.set_visible(False)

        return fig


def paired(
    before: np.ndarray,
    after: np.ndarray,
    *,
    pair_names: Optional[list[str]] = None,
    x_labels: tuple[str, str] = ("Before", "After"),
    x_positions: tuple[float, float] = (0.0, 1.0),
    y_label: str = "Value",
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    link_color: str = "0.6",
    link_linewidth_min: float = 0.5,
    link_linewidth_scale: float = 0.75,
    dot_size: float = 25.0,
    zorder_link: int = 1,
    zorder_points: int = 2,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a paired (before/after) connected dot plot.

    Args:
        before: Values for the first condition.
        after: Values for the second condition.
        pair_names: Optional labels for each paired observation.
        x_labels: Labels shown for the two conditions on the x-axis.
        x_positions: (x_before, x_after) positions for the two conditions.
        y_label: Y-axis label.
        title: Optional plot title.
        color_palette: Optional two-color palette for the two conditions.
        link_color: Color for the connecting line segments.
        link_linewidth_min: Minimum linewidth (points) for the connecting lines.
        link_linewidth_scale: Scale factor applied to `theme.axis.line_width` to obtain the
            connecting line linewidth before applying the minimum.
        dot_size: Marker area in points^2 for the paired dots (Matplotlib `scatter(s=...)`).
        zorder_link: Z-order for connecting lines.
        zorder_points: Z-order for points.
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    before = np.asarray(before, dtype=float)
    after = np.asarray(after, dtype=float)
    colors = normalize_palette(color_palette, fallback=DEFAULT)

    n = len(before)
    if pair_names is None:
        pair_names = [f"Pair {i + 1}" for i in range(n)]
    if len(pair_names) != n:
        raise ValueError("pair_names length must match the number of paired observations.")

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        link_lw = max(float(link_linewidth_min), float(t.axis.line_width) * float(link_linewidth_scale))
        for i in range(n):
            xb, xa = float(x_positions[0]), float(x_positions[1])
            ax.plot([xb, xa], [before[i], after[i]], color=link_color, linewidth=link_lw, zorder=int(zorder_link))
            ax.scatter(
                [xb, xa],
                [before[i], after[i]],
                color=[colors[0], colors[1 % len(colors)]],
                s=float(dot_size),
                zorder=int(zorder_points),
            )

        xb, xa = float(x_positions[0]), float(x_positions[1])
        ax.set_xticks([xb, xa], labels=list(x_labels))
        ax.set_ylabel(y_label)
        if title:
            ax.set_title(title, loc="center", fontfamily=t.font_family)

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        fig.tight_layout()
        return fig


def bubble(
    x: np.ndarray,
    y: np.ndarray,
    size: np.ndarray,
    *,
    labels: Optional[np.ndarray] = None,
    x_label: str = "X",
    y_label: str = "Y",
    size_label: str = "Size",
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    max_marker_size: int = 30,
    marker_alpha: float = 0.6,
    marker_edgecolor: str = "white",
    marker_edge_line_width: float = 0.4,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 6,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a bubble chart (scatter with size encoding).

    Args:
        x: X coordinates.
        y: Y coordinates.
        size: Bubble size variable.
        labels: Optional class / group labels used for color grouping and legend entries.
        x_label: X-axis label.
        y_label: Y-axis label.
        size_label: Label describing the size encoding.
        title: Optional plot title.
        color_palette: Optional palette used for grouped bubbles.
        max_marker_size: Maximum marker size parameter in Matplotlib points. Marker area scales as
            `max_marker_size**2` at the maximum of `size`.
        marker_alpha: Marker face alpha.
        marker_edgecolor: Marker edge color.
        marker_edge_line_width: Marker edge line width in points.
        legend_show: Whether to draw the legend when `labels` is provided.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns (only used when `legend_ncol` is None).
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    size = np.asarray(size, dtype=float)
    colors = normalize_palette(color_palette, fallback=DEFAULT)

    s = np.full_like(size, float(max_marker_size) ** 2)
    if np.max(size) > 0:
        s = (size / float(np.max(size))) * float(max_marker_size) ** 2

    def _marker_radius_points(max_area: float) -> float:
        if max_area <= 0:
            return 0.0
        return float(np.sqrt(max_area / np.pi)) + float(marker_edge_line_width) * 0.5

    def _resolve_axis_padding(data_min: float, data_max: float, axis_px: float, radius_px: float) -> float:
        raw_span = float(data_max - data_min)
        base_span = raw_span if raw_span > 0 else max(abs(data_min), abs(data_max), 1.0)
        if axis_px <= 2.0 * radius_px + 1e-9:
            return 0.08 * base_span
        exact_pad = (radius_px * base_span / axis_px) / max(1e-9, 1.0 - 2.0 * radius_px / axis_px)
        return max(float(exact_pad), 0.04 * base_span)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        if labels is not None:
            labels = np.asarray(labels)
            uniq = np.unique(labels)
            for i, lab in enumerate(uniq):
                mask = labels == lab
                ax.scatter(
                    x[mask],
                    y[mask],
                    s=s[mask],
                    label=str(lab),
                    color=color_to_rgba(colors[i % len(colors)], alpha=float(marker_alpha)),
                    edgecolor=marker_edgecolor,
                    linewidth=float(marker_edge_line_width),
                )
        else:
            ax.scatter(
                x,
                y,
                s=s,
                color=color_to_rgba(colors[0], alpha=float(marker_alpha)),
                edgecolor=marker_edgecolor,
                linewidth=float(marker_edge_line_width),
            )

        data_x_min = float(np.min(x)) if x.size else 0.0
        data_x_max = float(np.max(x)) if x.size else 1.0
        data_y_min = float(np.min(y)) if y.size else 0.0
        data_y_max = float(np.max(y)) if y.size else 1.0

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            title_above(ax, title)
        if labels is not None and bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(uniq), int(legend_ncol_max)))
            legend_below_title(ax, ncol=ncol)

        # Size legend is intentionally omitted (publication figures often annotate separately).
        _ = size_label

        def _apply_marker_safe_limits() -> None:
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            bbox = ax.get_window_extent(renderer=renderer)
            marker_radius_px = _marker_radius_points(float(np.max(s)) if s.size else 0.0) * float(fig.dpi) / 72.0
            x_pad = _resolve_axis_padding(data_x_min, data_x_max, float(bbox.width), marker_radius_px)
            y_pad = _resolve_axis_padding(data_y_min, data_y_max, float(bbox.height), marker_radius_px)
            ax.set_xlim(data_x_min - x_pad, data_x_max + x_pad)
            ax.set_ylim(data_y_min - y_pad, data_y_max + y_pad)

        setattr(ax, "_pubfig_post_layout", _apply_marker_safe_limits)

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        fig.tight_layout()
        try:
            _apply_marker_safe_limits()
        except Exception:
            x_span = float(np.ptp(x)) if x.size else 1.0
            y_span = float(np.ptp(y)) if y.size else 1.0
            x_pad = 0.08 * (x_span if x_span > 0 else max(abs(data_x_min), abs(data_x_max), 1.0))
            y_pad = 0.08 * (y_span if y_span > 0 else max(abs(data_y_min), abs(data_y_max), 1.0))
            ax.set_xlim(data_x_min - x_pad, data_x_max + x_pad)
            ax.set_ylim(data_y_min - y_pad, data_y_max + y_pad)
        return fig
