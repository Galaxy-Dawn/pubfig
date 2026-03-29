"""Specialized scientific plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Callable, Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_cmap, resolve_design_dpi
from .._style import apply_cartesian_axis_controls, coerce_linewidth, legend_below_title, title_above
from ..colors.utils import color_to_rgba, darken_color
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _style_colorbar(
    cb,  # type: ignore[valid-type]
    *,
    theme: Theme,
    label: str,
    outline_line_width: float,
    tick_font_size: Optional[int],
    label_font_size: Optional[int],
    tick_width: Optional[float],
    tick_length: Optional[float],
) -> None:
    cb.set_label(
        str(label),
        fontsize=int(theme.axis.label_font_size if label_font_size is None else tick_font_size or label_font_size),
    )
    try:
        cb.outline.set_linewidth(float(outline_line_width))
    except Exception:
        pass
    try:
        cb.ax.tick_params(
            labelsize=int(theme.axis.tick_font_size if tick_font_size is None else tick_font_size),
            width=float(theme.axis.tick_width if tick_width is None else tick_width),
            length=float(max(0.0, theme.axis.tick_length * 0.5) if tick_length is None else tick_length),
        )
    except Exception:
        pass


def hexbin(
    x: np.ndarray,
    y: np.ndarray,
    *,
    c: Optional[np.ndarray] = None,
    reduce: str = "count",
    gridsize: int = 32,
    mincnt: int = 1,
    extent: Optional[tuple[float, float, float, float]] = None,
    colorscale: str = "Blues",
    log_color_scale: bool = False,
    cbar: bool = True,
    cbar_label: Optional[str] = None,
    cbar_outline_line_width: float = 0.45,
    cbar_tick_font_size: Optional[int] = None,
    cbar_label_font_size: Optional[int] = None,
    cbar_tick_width: Optional[float] = None,
    cbar_tick_length: Optional[float] = None,
    x_label: str = "X",
    y_label: str = "Y",
    title: Optional[str] = None,
    show_y_equal_x: bool = False,
    y_equal_x_color: str = "0.72",
    y_equal_x_linestyle: str = "--",
    y_equal_x_line_width: Optional[float] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a hexbin plot for dense scatter data.

    Args:
        x: X coordinates.
        y: Y coordinates.
        c: Optional values reduced inside each hexagon.
        reduce: ``count``, ``mean``, ``sum``, ``median``, ``max``, or ``min``.
        gridsize: Hexagon grid size.
        mincnt: Minimum count needed to render a bin.
        extent: Optional (xmin, xmax, ymin, ymax).
        colorscale: Matplotlib colormap name.
        log_color_scale: Whether to use logarithmic color scaling for counts.
        cbar: Whether to draw a colorbar.
        cbar_label: Optional colorbar label. If None, a sensible default is chosen from ``reduce``.
        cbar_outline_line_width: Colorbar outline thickness.
        cbar_tick_font_size: Optional colorbar tick font size override.
        cbar_label_font_size: Optional colorbar label font size override.
        cbar_tick_width: Optional colorbar tick width override.
        cbar_tick_length: Optional colorbar tick length override.
        x_label: X-axis label.
        y_label: Y-axis label.
        title: Optional plot title.
        show_y_equal_x: Whether to draw a y=x reference line.
        y_equal_x_color: Reference line color.
        y_equal_x_linestyle: Reference line style.
        y_equal_x_line_width: Reference line width override.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    x_arr = np.asarray(x, dtype=float).reshape(-1)
    y_arr = np.asarray(y, dtype=float).reshape(-1)
    if x_arr.shape != y_arr.shape:
        raise ValueError("x and y must have the same shape")
    if x_arr.size == 0:
        raise ValueError("x and y must contain at least one value")

    reduce_key = str(reduce).lower()
    reducers: dict[str, Optional[Callable[[np.ndarray], float]]] = {
        "count": None,
        "mean": np.mean,
        "sum": np.sum,
        "median": np.median,
        "max": np.max,
        "min": np.min,
    }
    if reduce_key not in reducers:
        raise ValueError("reduce must be one of: count, mean, sum, median, max, min")
    c_arr = None if c is None else np.asarray(c, dtype=float).reshape(-1)
    if c_arr is not None and c_arr.shape != x_arr.shape:
        raise ValueError("c must match the shape of x and y")
    if reduce_key != "count" and c_arr is None:
        raise ValueError("c must be provided when reduce is not 'count'")

    cmap = resolve_cmap(colorscale)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_ref_line_width = (
            float(y_equal_x_line_width)
            if y_equal_x_line_width is not None
            else float(coerce_linewidth(t, kind="ref")) * 0.72
        )

        kwargs: dict[str, object] = {
            "gridsize": int(gridsize),
            "mincnt": int(mincnt),
            "cmap": cmap,
        }
        if extent is not None:
            kwargs["extent"] = tuple(float(v) for v in extent)
        if reduce_key == "count":
            if bool(log_color_scale):
                kwargs["bins"] = "log"
            hb = ax.hexbin(x_arr, y_arr, **kwargs)
        else:
            hb = ax.hexbin(
                x_arr,
                y_arr,
                C=c_arr,
                reduce_C_function=reducers[reduce_key],
                **kwargs,
            )

        if bool(cbar):
            if cbar_label is None:
                label = "log10(count)" if reduce_key == "count" and bool(log_color_scale) else reduce_key.title()
            else:
                label = str(cbar_label)
            cb = fig.colorbar(hb, ax=ax, pad=0.03, shrink=0.92)
            _style_colorbar(
                cb,
                theme=t,
                label=label,
                outline_line_width=float(cbar_outline_line_width),
                tick_font_size=cbar_tick_font_size,
                label_font_size=cbar_label_font_size,
                tick_width=cbar_tick_width,
                tick_length=cbar_tick_length,
            )

        if bool(show_y_equal_x):
            lo = float(min(np.min(x_arr), np.min(y_arr)))
            hi = float(max(np.max(x_arr), np.max(y_arr)))
            ax.plot(
                [lo, hi],
                [lo, hi],
                color=str(y_equal_x_color),
                linewidth=resolved_ref_line_width,
                linestyle=str(y_equal_x_linestyle),
                zorder=3,
            )

        ax.set_xlabel(str(x_label))
        ax.set_ylabel(str(y_label))
        if title:
            title_above(ax, title)

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


def volcano(
    log2_fc: np.ndarray,
    p_values: np.ndarray,
    *,
    labels: Optional[Sequence[str]] = None,
    fc_threshold: float = 1.0,
    p_threshold: float = 0.05,
    title: Optional[str] = None,
    x_label: str = "log2 fold change",
    y_label: str = "-log10(p)",
    ns_color: str = "0.72",
    up_color: str = "#C44E52",
    down_color: str = "#4C72B0",
    point_size: float = 4.2,
    point_alpha: float = 0.8,
    label_top_n: int = 8,
    label_font_size: Optional[int] = None,
    label_fc_min: Optional[float] = None,
    label_score: str = "combined",
    show_threshold_lines: bool = True,
    threshold_line_color: str = "0.72",
    threshold_line_width: Optional[float] = None,
    threshold_line_style: str = "--",
    symmetric_xlim: bool = True,
    legend_show: bool = True,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a volcano plot from log2 fold changes and p-values.

    Args:
        log2_fc: Log2 fold changes.
        p_values: Raw p-values in (0, 1].
        labels: Optional point labels used for top-hit annotations.
        fc_threshold: Absolute log2 fold-change threshold.
        p_threshold: P-value threshold.
        title: Optional plot title.
        x_label: X-axis label.
        y_label: Y-axis label.
        ns_color: Color for non-significant points.
        up_color: Color for significantly up-regulated points.
        down_color: Color for significantly down-regulated points.
        point_size: Marker size in points.
        point_alpha: Marker alpha.
        label_top_n: Maximum number of points to annotate.
        label_font_size: Optional annotation font size override.
        label_fc_min: Optional minimum absolute fold change required for annotations.
        label_score: ``combined``, ``p``, or ``fc``.
        show_threshold_lines: Whether to draw threshold guide lines.
        threshold_line_color: Threshold line color.
        threshold_line_width: Threshold line width override.
        threshold_line_style: Threshold line style.
        symmetric_xlim: Whether to make x-axis limits symmetric around zero.
        legend_show: Whether to draw the legend.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    fc_arr = np.asarray(log2_fc, dtype=float).reshape(-1)
    p_arr = np.asarray(p_values, dtype=float).reshape(-1)
    if fc_arr.shape != p_arr.shape:
        raise ValueError("log2_fc and p_values must have the same shape")
    if fc_arr.size == 0:
        raise ValueError("log2_fc and p_values must contain at least one value")
    if np.any(p_arr <= 0) or np.any(p_arr > 1):
        raise ValueError("p_values must be in the interval (0, 1]")
    if labels is not None and len(labels) != int(fc_arr.size):
        raise ValueError("labels must match the length of log2_fc")

    neglog10_p = -np.log10(np.clip(p_arr, 1e-300, 1.0))
    significant = p_arr <= float(p_threshold)
    up_mask = significant & (fc_arr >= float(fc_threshold))
    down_mask = significant & (fc_arr <= -float(fc_threshold))
    ns_mask = ~(up_mask | down_mask)

    score_key = str(label_score).lower()
    if score_key not in {"combined", "p", "fc"}:
        raise ValueError("label_score must be one of: combined, p, fc")

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_threshold_line_width = (
            float(threshold_line_width)
            if threshold_line_width is not None
            else float(coerce_linewidth(t, kind="ref")) * 0.72
        )
        resolved_label_font_size = (
            max(5, int(t.axis.tick_font_size) - 1) if label_font_size is None else int(label_font_size)
        )

        if np.any(ns_mask):
            ax.scatter(
                fc_arr[ns_mask],
                neglog10_p[ns_mask],
                s=float(point_size) ** 2,
                color=color_to_rgba(ns_color, alpha=float(point_alpha) * 0.9),
                edgecolor="none",
                label="Not significant",
                zorder=1,
            )
        if np.any(down_mask):
            ax.scatter(
                fc_arr[down_mask],
                neglog10_p[down_mask],
                s=float(point_size) ** 2,
                color=color_to_rgba(down_color, alpha=float(point_alpha)),
                edgecolor=darken_color(down_color, factor=0.78),
                linewidth=float(t.axis.line_width) * 0.2,
                label="Down",
                zorder=2,
            )
        if np.any(up_mask):
            ax.scatter(
                fc_arr[up_mask],
                neglog10_p[up_mask],
                s=float(point_size) ** 2,
                color=color_to_rgba(up_color, alpha=float(point_alpha)),
                edgecolor=darken_color(up_color, factor=0.78),
                linewidth=float(t.axis.line_width) * 0.2,
                label="Up",
                zorder=3,
            )

        if bool(show_threshold_lines):
            threshold_y = -np.log10(float(p_threshold))
            ax.axhline(
                threshold_y,
                color=str(threshold_line_color),
                linewidth=resolved_threshold_line_width,
                linestyle=str(threshold_line_style),
                zorder=0,
            )
            ax.axvline(
                float(fc_threshold),
                color=str(threshold_line_color),
                linewidth=resolved_threshold_line_width,
                linestyle=str(threshold_line_style),
                zorder=0,
            )
            ax.axvline(
                -float(fc_threshold),
                color=str(threshold_line_color),
                linewidth=resolved_threshold_line_width,
                linestyle=str(threshold_line_style),
                zorder=0,
            )

        if labels is not None and int(label_top_n) > 0:
            label_mask = up_mask | down_mask
            if label_fc_min is not None:
                label_mask &= np.abs(fc_arr) >= float(label_fc_min)
            candidate_indices = np.flatnonzero(label_mask)
            if candidate_indices.size > 0:
                if score_key == "p":
                    scores = neglog10_p[candidate_indices]
                elif score_key == "fc":
                    scores = np.abs(fc_arr[candidate_indices])
                else:
                    scores = neglog10_p[candidate_indices] * np.abs(fc_arr[candidate_indices])
                top_order = candidate_indices[np.argsort(scores)[::-1][: int(label_top_n)]]
                x_span = max(float(np.max(fc_arr) - np.min(fc_arr)), 1e-9)
                y_span = max(float(np.max(neglog10_p) - np.min(neglog10_p)), 1e-9)
                for idx in top_order:
                    x_offset = 0.015 * x_span if fc_arr[idx] >= 0 else -0.015 * x_span
                    ha = "left" if fc_arr[idx] >= 0 else "right"
                    ax.text(
                        float(fc_arr[idx] + x_offset),
                        float(neglog10_p[idx] + 0.012 * y_span),
                        str(labels[idx]),
                        ha=ha,
                        va="bottom",
                        fontsize=resolved_label_font_size,
                    )

        x_abs_max = float(np.max(np.abs(fc_arr))) if fc_arr.size else 1.0
        x_pad = max(0.25, x_abs_max * 0.08)
        if bool(symmetric_xlim):
            ax.set_xlim(-(x_abs_max + x_pad), x_abs_max + x_pad)
        else:
            ax.set_xlim(float(np.min(fc_arr) - x_pad), float(np.max(fc_arr) + x_pad))
        y_max = float(np.max(neglog10_p)) if neglog10_p.size else 1.0
        ax.set_ylim(0.0, y_max * 1.08 + 0.1)
        ax.set_xlabel(str(x_label))
        ax.set_ylabel(str(y_label))
        if title:
            title_above(ax, title)
        if bool(legend_show):
            legend_below_title(ax, ncol=3, y_if_no_title=1.12, gap=0.07)

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


__all__ = ["hexbin", "volcano"]
