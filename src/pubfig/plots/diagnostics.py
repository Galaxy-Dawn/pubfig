"""Diagnostic and distribution-comparison plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
from scipy import stats as sp_stats

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import (
    apply_cartesian_axis_controls,
    coerce_linewidth,
    legend_below_title,
    normalize_palette,
    title_above,
)
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba, darken_color
from ..themes import Theme, theme_context
from ._distribution_utils import normalize_features

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _prepare_grouped_series(
    values,
    *,
    group=None,
    series_names: Optional[Sequence[str]] = None,
) -> tuple[list[np.ndarray], list[str]]:
    if group is not None:
        value_arr = np.asarray(values, dtype=float).reshape(-1)
        group_arr = np.asarray(group)
        if value_arr.shape[0] != group_arr.shape[0]:
            raise ValueError("values and group must have the same length")
        unique_groups = list(dict.fromkeys(group_arr.tolist()))
        features = [value_arr[group_arr == label] for label in unique_groups]
        names = [str(label) for label in unique_groups]
    else:
        features = normalize_features(values)
        if series_names is not None:
            names = [str(name) for name in series_names]
            if len(names) != len(features):
                raise ValueError("series_names must match the number of series")
        else:
            names = [f"Series {idx + 1}" for idx in range(len(features))]

    cleaned = [np.asarray(feature, dtype=float).reshape(-1) for feature in features]
    if any(feature.size == 0 for feature in cleaned):
        raise ValueError("each series must contain at least one value")
    return cleaned, names


def ecdf(
    values,
    *,
    group=None,
    series_names: Optional[Sequence[str]] = None,
    color_palette: Optional[Sequence[str]] = None,
    x_label: str = "Value",
    y_label: str = "Cumulative probability",
    title: Optional[str] = None,
    complementary: bool = False,
    show_median: bool = False,
    line_width: Optional[float] = None,
    line_alpha: float = 0.95,
    median_line_width: Optional[float] = None,
    median_line_alpha: float = 0.35,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 4,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create an empirical cumulative distribution function plot.

    Args:
        values: 1D array, 2D array (n_samples, n_series), or list of 1D arrays.
        group: Optional 1D group labels for tidy-form input; when provided, `values`
            must be 1D and points are split by `group`.
        series_names: Optional per-series labels when `group` is not provided.
        color_palette: Optional palette used for ECDF curves.
        x_label: X-axis label.
        y_label: Y-axis label.
        title: Optional plot title.
        complementary: If True, plot the complementary ECDF (1 - F(x)).
        show_median: Whether to draw a vertical line at each series median.
        line_width: ECDF line width override.
        line_alpha: ECDF line alpha.
        median_line_width: Median-reference line width override.
        median_line_alpha: Median-reference line alpha.
        legend_show: Whether to draw the legend for multiple series.
        legend_ncol: Explicit legend column count.
        legend_ncol_max: Upper bound for legend columns when auto-resolving.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    features, names = _prepare_grouped_series(values, group=group, series_names=series_names)
    colors = normalize_palette(color_palette, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.75 if line_width is None else float(line_width)
        )
        resolved_median_line_width = (
            float(coerce_linewidth(t, kind="ref")) * 0.65
            if median_line_width is None
            else float(median_line_width)
        )

        for idx, (feature, name) in enumerate(zip(features, names)):
            sorted_values = np.sort(np.asarray(feature, dtype=float).reshape(-1))
            probs = np.arange(1, sorted_values.size + 1, dtype=float) / float(sorted_values.size)
            if bool(complementary):
                probs = 1.0 - probs
            color = colors[idx % len(colors)]
            ax.step(
                sorted_values,
                probs,
                where="post",
                linewidth=resolved_line_width,
                color=color_to_rgba(color, alpha=float(line_alpha)),
                label=str(name),
            )
            if bool(show_median):
                ax.axvline(
                    float(np.median(sorted_values)),
                    color=str(color),
                    linewidth=resolved_median_line_width,
                    alpha=float(median_line_alpha),
                    linestyle="--",
                    zorder=0,
                )

        ax.set_xlabel(str(x_label))
        ax.set_ylabel(str(y_label))
        ax.set_ylim(0.0, 1.0)
        if title:
            title_above(ax, title)
        if bool(legend_show) and len(features) > 1:
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(features), int(legend_ncol_max)))
            legend_below_title(ax, ncol=ncol)

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid if show_y_grid is not None else True,
        )
        fig.tight_layout()
        return fig


def qq(
    values,
    *,
    against: str | Sequence[float] = "normal",
    fit_line: bool = True,
    line: str = "quartile",
    point_size: float = 2.6,
    point_alpha: float = 0.82,
    point_color: Optional[str] = None,
    line_color: str = "0.40",
    line_width: Optional[float] = None,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    title: Optional[str] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a quantile-quantile plot against a reference distribution or sample.

    Args:
        values: 1D array of observed values.
        against: ``"normal"`` or a 1D reference sample array.
        fit_line: Whether to draw a reference line.
        line: Reference-line mode: ``"quartile"``, ``"fit"``, or ``"identity"``.
        point_size: Marker size in Matplotlib points.
        point_alpha: Marker alpha.
        point_color: Optional point color override.
        line_color: Reference-line color.
        line_width: Reference-line width override.
        x_label: Optional x-axis label.
        y_label: Optional y-axis label.
        title: Optional plot title.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    observed = np.asarray(values, dtype=float).reshape(-1)
    if observed.size < 2:
        raise ValueError("values must contain at least two points")

    if str(against).lower() == "normal":
        theoretical, ordered = sp_stats.probplot(observed, dist="norm", fit=False)
        theoretical = np.asarray(theoretical, dtype=float)
        ordered = np.asarray(ordered, dtype=float)
        default_x_label = "Theoretical quantiles"
    else:
        reference = np.sort(np.asarray(against, dtype=float).reshape(-1))
        if reference.size != observed.size:
            probs = (np.arange(1, observed.size + 1, dtype=float) - 0.5) / float(observed.size)
            theoretical = np.quantile(reference, probs)
        else:
            theoretical = reference
        ordered = np.sort(observed)
        default_x_label = "Reference quantiles"

    if str(line).lower() == "quartile":
        qx = np.quantile(theoretical, [0.25, 0.75])
        qy = np.quantile(ordered, [0.25, 0.75])
        slope = float((qy[1] - qy[0]) / max(qx[1] - qx[0], 1e-12))
        intercept = float(qy[0] - slope * qx[0])
    elif str(line).lower() == "fit":
        slope, intercept = np.polyfit(theoretical, ordered, 1)
        slope = float(slope)
        intercept = float(intercept)
    elif str(line).lower() == "identity":
        slope = 1.0
        intercept = 0.0
    else:
        raise ValueError("line must be one of: quartile, fit, identity")

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_point_color = DEFAULT[0] if point_color is None else str(point_color)
        resolved_line_width = (
            float(coerce_linewidth(t, kind="ref")) * 0.72 if line_width is None else float(line_width)
        )

        ax.scatter(
            theoretical,
            ordered,
            s=float(point_size) ** 2,
            color=color_to_rgba(resolved_point_color, alpha=float(point_alpha)),
            edgecolor=darken_color(resolved_point_color, factor=0.82),
            linewidth=float(t.axis.line_width) * 0.22,
            zorder=3,
        )

        if bool(fit_line):
            x_line = np.linspace(float(np.min(theoretical)), float(np.max(theoretical)), 256)
            y_line = slope * x_line + intercept
            ax.plot(x_line, y_line, color=str(line_color), linewidth=resolved_line_width, zorder=2)

        ax.set_xlabel(str(default_x_label if x_label is None else x_label))
        default_y_label = "Sample quantiles" if str(against).lower() == "normal" else "Observed quantiles"
        ax.set_ylabel(str(default_y_label if y_label is None else y_label))
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


def bland_altman(
    x,
    y,
    *,
    x_label: str = "Mean of two measurements",
    y_label: str = "Difference",
    title: Optional[str] = None,
    point_size: float = 3.8,
    point_alpha: float = 0.78,
    point_color: Optional[str] = None,
    line_color: str = "0.45",
    line_width: Optional[float] = None,
    limits_of_agreement: float = 1.96,
    show_mean_diff: bool = True,
    show_limits: bool = True,
    annotate_stats: bool = True,
    annotation_position: tuple[float, float] = (0.04, 0.96),
    annotation_font_size: Optional[int] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a Bland–Altman agreement plot for paired measurements.

    Args:
        x: First 1D measurement array.
        y: Second 1D measurement array.
        x_label: X-axis label.
        y_label: Y-axis label.
        title: Optional plot title.
        point_size: Marker size in Matplotlib points.
        point_alpha: Marker alpha.
        point_color: Optional point color override.
        line_color: Color used for mean-difference and limits-of-agreement lines.
        line_width: Reference-line width override.
        limits_of_agreement: Multiplier applied to the standard deviation (typically 1.96).
        show_mean_diff: Whether to draw the mean-difference line.
        show_limits: Whether to draw upper/lower limits of agreement.
        annotate_stats: Whether to annotate the bias and limits in axes coordinates.
        annotation_position: (x, y) position in axes coordinates for the annotation block.
        annotation_font_size: Optional annotation font-size override.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box.
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
    if x_arr.size < 2:
        raise ValueError("x and y must contain at least two paired observations")

    mean_vals = (x_arr + y_arr) * 0.5
    diff_vals = y_arr - x_arr
    bias = float(np.mean(diff_vals))
    std = float(np.std(diff_vals, ddof=1))
    loa = float(limits_of_agreement) * std
    upper = bias + loa
    lower = bias - loa

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_point_color = DEFAULT[0] if point_color is None else str(point_color)
        resolved_line_width = (
            float(coerce_linewidth(t, kind="ref")) * 0.72 if line_width is None else float(line_width)
        )
        resolved_annotation_font_size = (
            max(5, int(t.axis.tick_font_size) - 1) if annotation_font_size is None else int(annotation_font_size)
        )

        ax.scatter(
            mean_vals,
            diff_vals,
            s=float(point_size) ** 2,
            color=color_to_rgba(resolved_point_color, alpha=float(point_alpha)),
            edgecolor=darken_color(resolved_point_color, factor=0.82),
            linewidth=float(t.axis.line_width) * 0.35,
            zorder=3,
        )

        if bool(show_mean_diff):
            ax.axhline(bias, color=str(line_color), linewidth=resolved_line_width, linestyle="-", zorder=1)
        if bool(show_limits):
            ax.axhline(upper, color=str(line_color), linewidth=resolved_line_width, linestyle="--", zorder=1)
            ax.axhline(lower, color=str(line_color), linewidth=resolved_line_width, linestyle="--", zorder=1)

        if bool(annotate_stats):
            text = f"Bias = {bias:.2f}\nLoA = [{lower:.2f}, {upper:.2f}]"
            ax.text(
                float(annotation_position[0]),
                float(annotation_position[1]),
                text,
                transform=ax.transAxes,
                ha="left",
                va="top",
                fontsize=resolved_annotation_font_size,
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
            show_y_grid=show_y_grid if show_y_grid is not None else True,
        )
        fig.tight_layout()
        return fig


__all__ = ["ecdf", "qq", "bland_altman"]
