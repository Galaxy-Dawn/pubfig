"""Line plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import (
    apply_cartesian_axis_controls,
    coerce_linewidth,
    coerce_marker_size,
    legend_below_title,
    normalize_palette,
    title_above,
)
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba, darken_color
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def line(
    data,
    *,
    x: Optional[np.ndarray] = None,
    series_names: Optional[list[str]] = None,
    x_label: str = "Time",
    y_label: str = "Value",
    line_width: Optional[float] = None,
    line_alpha: float = 0.9,
    marker_size: Optional[float] = None,
    marker: str | None = "auto",
    marker_size_scale: float = 0.9,
    marker_face_alpha: Optional[float] = None,
    marker_edge_color: Optional[str] = None,
    marker_edge_line_width: float = 0.2,
    ci: Optional[float] = None,
    ci_default_level: float = 0.95,
    ci_band_alpha: float = 0.14,
    ci_band_line_width: float = 0.0,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 6,
    title: Optional[str] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    color_palette: Optional[Sequence[str]] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a line chart with optional confidence interval bands.

    Args:
        data: 1D/2D array, list of 1D arrays, or 3D array
              (n_series, n_points, n_repeats) for auto mean+CI.
        x: Optional x coordinates shared by all series.
        series_names: Labels for each plotted series.
        x_label: X-axis label.
        y_label: Y-axis label.
        line_width: Line width for each line. If None, derive from the active theme.
        line_alpha: Alpha for the line trace.
        marker: Marker style passed to Matplotlib (e.g. "o", "s", "D", "^", None).
            Use `"auto"` to cycle filled markers across series.
        marker_size: Marker size control (see `marker_size_scale`).
        marker_size_scale: Scale factor applied to `marker_size` before passing to
            Matplotlib's `markersize`.
        marker_face_alpha: Alpha for marker faces. If None, reuse `line_alpha`.
        marker_edge_color: Marker edge color. If None, use a darker version of each series color.
        marker_edge_line_width: Marker edge line width in points.
        ci: Confidence level (e.g. 0.95) for CI bands. Only used with 3D data.
        ci_default_level: Confidence level used when `ci` is None and `data` is 3D.
            Default 0.95 preserves the legacy behavior.
        ci_band_alpha: Alpha for the CI band fill (only used with 3D data).
        ci_band_line_width: Line width for the CI band edge (0 disables band edges).
        legend_show: Whether to draw the legend.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns; actual columns is
            min(n_series, legend_ncol_max) (only used when `legend_ncol` is None).
        title: Optional plot title.
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        color_palette: Optional palette used for the series.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    colors = normalize_palette(color_palette, fallback=DEFAULT)

    if isinstance(data, np.ndarray) and data.ndim == 3:
        return _line_with_ci(
            data,
            x=x,
            series_names=series_names,
            colors=colors,
            ci_level=float(ci) if ci is not None else float(ci_default_level),
            ci_band_alpha=float(ci_band_alpha),
            ci_band_line_width=float(ci_band_line_width),
            x_label=x_label,
            y_label=y_label,
            line_width=line_width,
            line_alpha=float(line_alpha),
            marker=marker,
            marker_size=marker_size,
            marker_size_scale=float(marker_size_scale),
            marker_face_alpha=marker_face_alpha,
            marker_edge_color=marker_edge_color,
            marker_edge_line_width=float(marker_edge_line_width),
            legend_show=bool(legend_show),
            legend_ncol=int(legend_ncol) if legend_ncol is not None else None,
            legend_ncol_max=int(legend_ncol_max),
            title=title,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
            theme=theme,
            width=width,
            height=height,
            ax=ax,
        )

    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            features = [data]
        elif data.ndim == 2:
            features = [data[:, i] for i in range(data.shape[1])]
        else:
            raise ValueError("Input data must be 1D, 2D, or 3D array.")
    elif isinstance(data, list):
        features = data
    else:
        raise ValueError("Input must be a list of arrays or ndarray.")

    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(len(features))]

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_line_width = (
            float(line_width)
            if line_width is not None
            else max(float(t.axis.line_width) * 0.9, float(coerce_linewidth(t, kind="data")) * 0.65)
        )
        resolved_marker_size = (
            float(marker_size) if marker_size is not None else float(coerce_marker_size(t, kind="line"))
        )
        resolved_marker_face_alpha = float(line_alpha) if marker_face_alpha is None else float(marker_face_alpha)
        marker_cycle = ["s", "o", "D", "^"]

        for idx, feature in enumerate(features):
            x_vals = x if x is not None else np.arange(len(feature))
            c = colors[idx % len(colors)]
            resolved_marker = marker_cycle[idx % len(marker_cycle)] if marker == "auto" else marker
            resolved_marker_edge_color = (
                darken_color(c, factor=0.75) if marker_edge_color is None else str(marker_edge_color)
            )
            ax.plot(
                x_vals,
                feature,
                label=series_names[idx],
                color=color_to_rgba(c, alpha=float(line_alpha)),
                linewidth=resolved_line_width,
                marker=resolved_marker,
                markersize=resolved_marker_size * float(marker_size_scale),
                markerfacecolor=color_to_rgba(c, alpha=resolved_marker_face_alpha),
                markeredgecolor=resolved_marker_edge_color,
                markeredgewidth=float(marker_edge_line_width),
            )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            title_above(ax, title)
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(features), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol))

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


def _line_with_ci(
    data: np.ndarray,
    *,
    x: Optional[np.ndarray],
    series_names: Optional[list[str]],
    colors: list[str],
    ci_level: float,
    ci_band_alpha: float,
    ci_band_line_width: float,
    x_label: str,
    y_label: str,
    line_width: Optional[float],
    line_alpha: float,
    marker: str | None,
    marker_size: Optional[float],
    marker_size_scale: float,
    marker_face_alpha: Optional[float],
    marker_edge_color: Optional[str],
    marker_edge_line_width: float,
    legend_show: bool,
    legend_ncol: Optional[int],
    legend_ncol_max: int,
    title: Optional[str],
    tick_direction: str | None,
    show_full_box: Optional[bool],
    show_x_grid: Optional[bool],
    show_y_grid: Optional[bool],
    theme: Optional[Theme],
    width: Optional[int],
    height: Optional[int],
    ax: Optional["Axes"],
) -> "Figure":
    """Line chart with CI bands from 3D data (n_series, n_points, n_repeats)."""
    from scipy import stats

    if not (0 < float(ci_level) < 1):
        raise ValueError("ci must be in (0, 1)")

    n_series, n_points, n_repeats = data.shape
    mean = np.mean(data, axis=2)
    sem = np.std(data, axis=2, ddof=1) / np.sqrt(n_repeats)
    t_val = stats.t.ppf((1 + float(ci_level)) / 2, df=n_repeats - 1)

    if x is None:
        x = np.arange(n_points)
    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(n_series)]

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_line_width = (
            float(line_width)
            if line_width is not None
            else max(float(t.axis.line_width) * 0.9, float(coerce_linewidth(t, kind="data")) * 0.65)
        )
        resolved_marker_size = (
            float(marker_size) if marker_size is not None else float(coerce_marker_size(t, kind="line"))
        )
        resolved_marker_face_alpha = float(line_alpha) if marker_face_alpha is None else float(marker_face_alpha)
        marker_cycle = ["s", "o", "D", "^"]

        for i in range(n_series):
            c = colors[i % len(colors)]
            resolved_marker = marker_cycle[i % len(marker_cycle)] if marker == "auto" else marker
            resolved_marker_edge_color = (
                darken_color(c, factor=0.75) if marker_edge_color is None else str(marker_edge_color)
            )
            upper = mean[i] + t_val * sem[i]
            lower = mean[i] - t_val * sem[i]
            ax.fill_between(
                x,
                lower,
                upper,
                color=color_to_rgba(c, alpha=float(ci_band_alpha)),
                linewidth=float(ci_band_line_width),
            )
            ax.plot(
                x,
                mean[i],
                label=series_names[i],
                color=color_to_rgba(c, alpha=float(line_alpha)),
                linewidth=resolved_line_width,
                marker=resolved_marker,
                markersize=resolved_marker_size * float(marker_size_scale),
                markerfacecolor=color_to_rgba(c, alpha=resolved_marker_face_alpha),
                markeredgecolor=resolved_marker_edge_color,
                markeredgewidth=float(marker_edge_line_width),
            )

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            title_above(ax, title)
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(n_series, int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol))

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


def area(
    data,
    *,
    x: Optional[np.ndarray] = None,
    series_names: Optional[list[str]] = None,
    x_label: str = "Time",
    y_label: str = "Value",
    stacked: bool = True,
    stacked_alpha: float = 0.6,
    unstacked_alpha: float = 0.35,
    unstacked_line_width: float = 1.5,
    unstacked_baseline: float = 0.0,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 6,
    title: Optional[str] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    color_palette: Optional[Sequence[str]] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create an area chart (optionally stacked).

    Args:
        data: 1D/2D array or list of 1D arrays.
        x: Optional x coordinates shared by all series.
        series_names: Labels for each plotted area series.
        x_label: X-axis label.
        y_label: Y-axis label.
        stacked: If True, use `Axes.stackplot`; otherwise, fill each series from a
            baseline and overlay a line trace.
        stacked_alpha: Alpha for stacked areas (only used when `stacked=True`).
        unstacked_alpha: Alpha for each filled area (only used when `stacked=False`).
        unstacked_line_width: Line width for the outline trace (only used when `stacked=False`).
        unstacked_baseline: Baseline y-value used when filling each series (only used when
            `stacked=False`). Default 0.0 preserves legacy behavior.
        legend_show: Whether to draw the legend.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns; actual columns is
            min(n_series, legend_ncol_max).
        title: Optional plot title.
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        color_palette: Optional palette used for the series.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            features = [data]
        elif data.ndim == 2:
            features = [data[:, i] for i in range(data.shape[1])]
        else:
            raise ValueError("Data must be 1D or 2D array.")
    elif isinstance(data, list):
        features = data
    else:
        raise ValueError("Input must be a list of arrays or ndarray.")

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(len(features))]

    if x is None:
        x = np.arange(len(features[0]))

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        if stacked:
            ax.stackplot(
                x,
                *features,
                labels=series_names,
                colors=[
                    color_to_rgba(colors[i % len(colors)], alpha=float(stacked_alpha))
                    for i in range(len(features))
                ],
            )
        else:
            for i, feat in enumerate(features):
                c = colors[i % len(colors)]
                ax.fill_between(
                    x,
                    float(unstacked_baseline),
                    feat,
                    color=color_to_rgba(c, alpha=float(unstacked_alpha)),
                    label=series_names[i],
                )
                ax.plot(x, feat, color=c, linewidth=float(unstacked_line_width))

        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if title:
            title_above(ax, title)
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(features), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol))

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
