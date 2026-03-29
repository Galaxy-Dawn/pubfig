"""Comparison-oriented plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
from matplotlib.transforms import blended_transform_factory

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


def dumbbell(
    start: np.ndarray,
    end: np.ndarray,
    *,
    category_names: Optional[Sequence[str]] = None,
    left_label: str = "Start",
    right_label: str = "End",
    x_label: str = "Value",
    title: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_desc: bool = False,
    connector_color: str = "0.78",
    connector_line_width: Optional[float] = None,
    left_color: Optional[str] = None,
    right_color: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    left_marker: str = "o",
    right_marker: str = "o",
    marker_size: Optional[float] = None,
    show_delta_labels: bool = False,
    delta_label_fmt: str = "+.2f",
    delta_label_position: str = "right",
    row_band_alpha: float = 0.035,
    row_band_color: str = "0.55",
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
    """Create a horizontal dumbbell plot for paired comparisons.

    Args:
        start: First value for each category.
        end: Second value for each category.
        category_names: Labels for each row.
        left_label: Legend label for the first endpoint.
        right_label: Legend label for the second endpoint.
        x_label: X-axis label.
        title: Optional plot title.
        sort_by: Optional row ordering: ``start``, ``end``, ``delta``, or ``abs_delta``.
        sort_desc: Whether to reverse the selected ordering.
        connector_color: Connector line color.
        connector_line_width: Connector line width override.
        left_color: Optional color override for the first endpoint.
        right_color: Optional color override for the second endpoint.
        color_palette: Optional palette used when endpoint colors are not provided.
        left_marker: Marker style for the first endpoint.
        right_marker: Marker style for the second endpoint.
        marker_size: Marker size override.
        show_delta_labels: Whether to annotate per-row deltas.
        delta_label_fmt: Format specifier applied to ``end - start``.
        delta_label_position: ``right`` or ``midpoint``.
        row_band_alpha: Alternating row band alpha.
        row_band_color: Alternating row band color.
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
    start_arr = np.asarray(start, dtype=float).reshape(-1)
    end_arr = np.asarray(end, dtype=float).reshape(-1)
    if start_arr.shape != end_arr.shape:
        raise ValueError("start and end must have the same shape")
    if start_arr.size == 0:
        raise ValueError("start and end must contain at least one value")

    if category_names is None:
        names = [f"Category {i + 1}" for i in range(start_arr.size)]
    else:
        names = [str(item) for item in category_names]
        if len(names) != int(start_arr.size):
            raise ValueError("category_names must match the length of start/end")

    deltas = end_arr - start_arr
    if sort_by is not None:
        key = str(sort_by).lower()
        if key == "start":
            order_values = start_arr
        elif key == "end":
            order_values = end_arr
        elif key == "delta":
            order_values = deltas
        elif key == "abs_delta":
            order_values = np.abs(deltas)
        else:
            raise ValueError("sort_by must be one of: start, end, delta, abs_delta")
        order = np.argsort(order_values)
        if bool(sort_desc):
            order = order[::-1]
        start_arr = start_arr[order]
        end_arr = end_arr[order]
        deltas = deltas[order]
        names = [names[int(idx)] for idx in order]

    colors = normalize_palette(color_palette, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_connector_line_width = (
            float(connector_line_width)
            if connector_line_width is not None
            else float(coerce_linewidth(t, kind="ref")) * 0.72
        )
        resolved_marker_size = (
            float(marker_size) if marker_size is not None else float(coerce_marker_size(t, kind="paired"))
        )
        resolved_left_color = colors[0] if left_color is None else str(left_color)
        resolved_right_color = colors[1 % len(colors)] if right_color is None else str(right_color)
        positions = np.arange(start_arr.size, dtype=float)

        for idx, y_pos in enumerate(positions):
            if idx % 2 == 0 and float(row_band_alpha) > 0:
                ax.axhspan(
                    float(y_pos) - 0.5,
                    float(y_pos) + 0.5,
                    color=str(row_band_color),
                    alpha=float(row_band_alpha),
                    zorder=0,
                )

        for idx, y_pos in enumerate(positions):
            ax.plot(
                [float(start_arr[idx]), float(end_arr[idx])],
                [float(y_pos), float(y_pos)],
                color=str(connector_color),
                linewidth=resolved_connector_line_width,
                solid_capstyle="round",
                zorder=1,
            )

        ax.scatter(
            start_arr,
            positions,
            s=float(resolved_marker_size) ** 2,
            color=color_to_rgba(resolved_left_color, alpha=0.95),
            edgecolor=darken_color(resolved_left_color, factor=0.78),
            linewidth=float(t.axis.line_width) * 0.4,
            marker=str(left_marker),
            label=str(left_label),
            zorder=3,
        )
        ax.scatter(
            end_arr,
            positions,
            s=float(resolved_marker_size) ** 2,
            color=color_to_rgba(resolved_right_color, alpha=0.95),
            edgecolor=darken_color(resolved_right_color, factor=0.78),
            linewidth=float(t.axis.line_width) * 0.4,
            marker=str(right_marker),
            label=str(right_label),
            zorder=4,
        )

        value_min = float(min(np.min(start_arr), np.min(end_arr)))
        value_max = float(max(np.max(start_arr), np.max(end_arr)))
        span = max(value_max - value_min, 1e-9)
        pad = span * 0.10
        ax.set_xlim(value_min - pad * 0.25, value_max + pad)

        if bool(show_delta_labels):
            for idx, y_pos in enumerate(positions):
                if str(delta_label_position) == "midpoint":
                    x_pos = (float(start_arr[idx]) + float(end_arr[idx])) * 0.5
                    ha = "center"
                else:
                    x_pos = max(float(start_arr[idx]), float(end_arr[idx])) + pad * 0.06
                    ha = "left"
                ax.text(
                    x_pos,
                    float(y_pos),
                    format(float(deltas[idx]), str(delta_label_fmt)),
                    va="center",
                    ha=ha,
                    fontsize=max(5, int(t.axis.tick_font_size) - 1),
                )

        ax.set_yticks(positions, labels=names)
        ax.invert_yaxis()
        ax.set_xlabel(str(x_label))
        ax.set_ylabel("")
        if title:
            title_above(ax, title, y=1.05)
        if bool(legend_show):
            legend_below_title(ax, ncol=2, y_if_no_title=1.12, gap=0.07)

        t.apply_axes(ax)
        ax.tick_params(axis="y", length=0)
        if hasattr(ax, "spines") and "left" in ax.spines:
            ax.spines["left"].set_visible(False)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid if show_x_grid is not None else True,
            show_y_grid=show_y_grid,
        )
        fig.tight_layout()
        return fig


def forest_plot(
    effect: np.ndarray,
    ci_low: np.ndarray,
    ci_high: np.ndarray,
    *,
    labels: Sequence[str],
    group_labels: Optional[Sequence[str]] = None,
    right_labels: Optional[Sequence[str]] = None,
    is_summary: Optional[Sequence[bool]] = None,
    x_label: str = "Effect size",
    title: Optional[str] = None,
    reference: float = 0.0,
    x_scale: str = "linear",
    x_min: Optional[float] = None,
    x_max: Optional[float] = None,
    color_palette: Optional[Sequence[str]] = None,
    point_color: Optional[str] = None,
    summary_color: Optional[str] = None,
    ci_color: str = "0.35",
    marker: str = "s",
    summary_marker: str = "D",
    marker_size: Optional[float] = None,
    summary_marker_size_scale: float = 1.35,
    ci_line_width: Optional[float] = None,
    ci_cap_size: float = 2.6,
    reference_color: str = "0.72",
    reference_line_width: Optional[float] = None,
    reference_linestyle: str = "--",
    row_band_alpha: float = 0.03,
    row_band_color: str = "0.55",
    auto_right_labels: bool = True,
    right_label_decimals: int = 2,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a publication-style forest plot.

    Args:
        effect: Point estimates.
        ci_low: Lower confidence interval bounds.
        ci_high: Upper confidence interval bounds.
        labels: Per-row labels.
        group_labels: Optional per-row group headers. A new header is inserted when the value changes.
        right_labels: Optional per-row right-side text column.
        is_summary: Optional boolean flags marking summary rows; these use a larger diamond marker.
        x_label: X-axis label.
        title: Optional plot title.
        reference: Vertical reference line (e.g. 0 for differences, 1 for odds ratios).
        x_scale: ``linear`` or ``log``.
        x_min: Optional x-axis minimum.
        x_max: Optional x-axis maximum.
        color_palette: Optional palette used when explicit colors are not provided.
        point_color: Color for standard rows.
        summary_color: Color for summary rows.
        ci_color: Confidence interval line color.
        marker: Marker for standard rows.
        summary_marker: Marker for summary rows.
        marker_size: Base marker size.
        summary_marker_size_scale: Scale factor applied to summary-row markers.
        ci_line_width: CI line width override.
        ci_cap_size: CI cap size in points.
        reference_color: Reference line color.
        reference_line_width: Reference line width override.
        reference_linestyle: Reference line style.
        row_band_alpha: Alternating row band alpha.
        row_band_color: Alternating row band color.
        auto_right_labels: If True and ``right_labels`` is None, auto-generate ``estimate [low, high]`` labels.
        right_label_decimals: Decimal places used for auto-generated right labels.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    effect_arr = np.asarray(effect, dtype=float).reshape(-1)
    ci_low_arr = np.asarray(ci_low, dtype=float).reshape(-1)
    ci_high_arr = np.asarray(ci_high, dtype=float).reshape(-1)
    n = int(effect_arr.size)
    if n == 0:
        raise ValueError("effect, ci_low, and ci_high must contain at least one row")
    if ci_low_arr.shape != effect_arr.shape or ci_high_arr.shape != effect_arr.shape:
        raise ValueError("effect, ci_low, and ci_high must have the same shape")
    if len(labels) != n:
        raise ValueError("labels must match the length of effect")
    if np.any(ci_low_arr > effect_arr) or np.any(ci_high_arr < effect_arr):
        raise ValueError("each effect must lie within [ci_low, ci_high]")
    if str(x_scale) not in {"linear", "log"}:
        raise ValueError("x_scale must be 'linear' or 'log'")
    if str(x_scale) == "log" and (
        np.any(ci_low_arr <= 0) or np.any(ci_high_arr <= 0) or float(reference) <= 0
    ):
        raise ValueError("log-scale forest plots require positive ci bounds and a positive reference")

    groups = None if group_labels is None else [str(item) for item in group_labels]
    if groups is not None and len(groups) != n:
        raise ValueError("group_labels must match the length of effect")

    summary_flags = np.zeros(n, dtype=bool) if is_summary is None else np.asarray(is_summary, dtype=bool).reshape(-1)
    if summary_flags.shape != effect_arr.shape:
        raise ValueError("is_summary must match the length of effect")

    if right_labels is None and bool(auto_right_labels):
        right_texts: list[str | None] = [
            f"{effect_arr[i]:.{int(right_label_decimals)}f} [{ci_low_arr[i]:.{int(right_label_decimals)}f}, {ci_high_arr[i]:.{int(right_label_decimals)}f}]"
            for i in range(n)
        ]
    elif right_labels is not None:
        if len(right_labels) != n:
            raise ValueError("right_labels must match the length of effect")
        right_texts = [str(item) for item in right_labels]
    else:
        right_texts = [None] * n

    rows: list[dict[str, object]] = []
    last_group: Optional[str] = None
    for idx, label in enumerate(labels):
        group = None if groups is None else groups[idx]
        if group is not None and group != last_group:
            rows.append({"kind": "header", "text": group})
            last_group = group
        rows.append(
            {
                "kind": "item",
                "index": idx,
                "label": str(label),
                "right_label": right_texts[idx],
                "summary": bool(summary_flags[idx]),
            }
        )

    colors = normalize_palette(color_palette, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_point_color = colors[0] if point_color is None else str(point_color)
        resolved_summary_color = colors[1 % len(colors)] if summary_color is None else str(summary_color)
        resolved_marker_size = (
            float(marker_size) if marker_size is not None else float(coerce_marker_size(t, kind="paired"))
        )
        resolved_ci_line_width = (
            float(ci_line_width) if ci_line_width is not None else float(coerce_linewidth(t, kind="errorbar")) * 0.8
        )
        resolved_reference_line_width = (
            float(reference_line_width)
            if reference_line_width is not None
            else float(coerce_linewidth(t, kind="ref")) * 0.72
        )

        y_positions = np.arange(len(rows), 0, -1, dtype=float)
        tick_labels: list[str] = []
        item_row_counter = 0
        right_text_transform = blended_transform_factory(ax.transAxes, ax.transData)
        left_text_transform = blended_transform_factory(ax.transAxes, ax.transData)

        for row_idx, (row, y_pos) in enumerate(zip(rows, y_positions)):
            kind = str(row["kind"])
            if kind == "header":
                tick_labels.append("")
                txt = ax.text(
                    -0.04,
                    float(y_pos),
                    str(row["text"]),
                    transform=left_text_transform,
                    ha="left",
                    va="center",
                    fontweight="semibold",
                    fontsize=int(t.axis.label_font_size),
                    clip_on=False,
                )
                try:
                    txt.set_in_layout(True)
                except Exception:
                    pass
                continue

            tick_labels.append(str(row["label"]))
            item_index = int(row["index"])
            if item_row_counter % 2 == 0 and float(row_band_alpha) > 0:
                ax.axhspan(
                    float(y_pos) - 0.5,
                    float(y_pos) + 0.5,
                    color=str(row_band_color),
                    alpha=float(row_band_alpha),
                    zorder=0,
                )
            is_summary_row = bool(row["summary"])
            row_color = resolved_summary_color if is_summary_row else resolved_point_color
            xerr = np.array(
                [[float(effect_arr[item_index] - ci_low_arr[item_index])], [float(ci_high_arr[item_index] - effect_arr[item_index])]],
                dtype=float,
            )
            ax.errorbar(
                [float(effect_arr[item_index])],
                [float(y_pos)],
                xerr=xerr,
                fmt=str(summary_marker if is_summary_row else marker),
                markersize=float(resolved_marker_size) * (float(summary_marker_size_scale) if is_summary_row else 1.0),
                color=str(ci_color),
                ecolor=str(ci_color),
                elinewidth=resolved_ci_line_width,
                capsize=float(ci_cap_size),
                markerfacecolor=color_to_rgba(row_color, alpha=0.95),
                markeredgecolor=darken_color(row_color, factor=0.78),
                markeredgewidth=float(t.axis.line_width) * 0.4,
                zorder=3,
            )
            if row["right_label"] is not None:
                txt = ax.text(
                    1.02,
                    float(y_pos),
                    str(row["right_label"]),
                    transform=right_text_transform,
                    ha="left",
                    va="center",
                    fontsize=max(5, int(t.axis.tick_font_size) - 1),
                    clip_on=False,
                )
                try:
                    txt.set_in_layout(True)
                except Exception:
                    pass
            item_row_counter += 1

        if str(x_scale) == "log":
            data_min = float(np.min(ci_low_arr))
            data_max = float(np.max(ci_high_arr))
            ax.set_xscale("log")
            ax.set_xlim(
                float(x_min) if x_min is not None else data_min / 1.18,
                float(x_max) if x_max is not None else data_max * 1.18,
            )
        else:
            data_min = float(np.min(ci_low_arr))
            data_max = float(np.max(ci_high_arr))
            data_span = max(data_max - data_min, 1e-9)
            data_pad = data_span * 0.10
            ax.set_xlim(
                float(x_min) if x_min is not None else data_min - data_pad,
                float(x_max) if x_max is not None else data_max + data_pad,
            )

        ax.axvline(
            float(reference),
            color=str(reference_color),
            linewidth=resolved_reference_line_width,
            linestyle=str(reference_linestyle),
            zorder=1,
        )
        ax.set_yticks(y_positions, labels=tick_labels)
        ax.set_ylim(float(np.min(y_positions) - 0.7), float(np.max(y_positions) + 0.7))
        ax.set_xlabel(str(x_label))
        ax.set_ylabel("")
        if title:
            title_above(ax, title, y=1.05)

        t.apply_axes(ax)
        ax.tick_params(axis="y", length=0)
        if hasattr(ax, "spines") and "left" in ax.spines:
            ax.spines["left"].set_visible(False)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid if show_x_grid is not None else True,
            show_y_grid=show_y_grid,
        )
        fig.tight_layout(rect=(0.0, 0.0, 0.88, 1.0))
        return fig


__all__ = ["dumbbell", "forest_plot"]
