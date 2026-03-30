"""Grouped scatter comparison plots (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import (
    apply_cartesian_axis_controls,
    coerce_linewidth,
    coerce_marker_size,
    normalize_palette,
    title_above,
)
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba, darken_color
from ..stats.annotations import add_significance_brackets
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _coerce_grouped_data(data: np.ndarray) -> np.ndarray:
    arr = np.asarray(data, dtype=float)
    if arr.ndim == 2:
        return arr[None, :, :]
    if arr.ndim == 3:
        return arr
    raise ValueError("data must be a 2D or 3D numpy array")


def _resolve_names(provided: Optional[Sequence[str]], size: int, prefix: str) -> list[str]:
    if provided is None:
        return [f"{prefix} {idx + 1}" for idx in range(size)]
    names = [str(item) for item in provided]
    if len(names) != int(size):
        raise ValueError(f"{prefix.lower()} names must match data shape")
    return names


def _normalize_top_annotations(
    top_annotations: Optional[Sequence[str] | Sequence[Sequence[str]]],
    *,
    n_categories: int,
    n_groups: int,
) -> list[list[str]] | None:
    if top_annotations is None:
        return None
    if n_categories == 1 and len(top_annotations) == n_groups and all(
        not isinstance(item, (list, tuple, np.ndarray)) for item in top_annotations
    ):
        return [[str(item) for item in top_annotations]]

    rows = [[str(item) for item in row] for row in top_annotations]  # type: ignore[arg-type]
    if len(rows) != int(n_categories):
        raise ValueError("top_annotations must match the number of categories")
    for row in rows:
        if len(row) != int(n_groups):
            raise ValueError("Each top_annotations row must match the number of groups")
    return rows




def _pairwise_center_gap_px(ax: "Axes", xs: Sequence[float]) -> float:
    if len(xs) < 2:
        return float("inf")
    centers_px = [float(ax.transData.transform((float(x), 0.0))[0]) for x in xs]
    gaps = [float(centers_px[idx + 1] - centers_px[idx]) for idx in range(len(centers_px) - 1)]
    return min(gaps) if gaps else float("inf")


def _fit_top_annotation_rows(
    ax: "Axes",
    *,
    row_texts: Sequence[Sequence[object]],
    row_xs: Sequence[Sequence[float]],
    pad_px: float = 6.0,
    min_font_size: float = 5.0,
) -> None:
    fig = ax.figure
    try:
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
    except Exception:
        return

    for texts, xs in zip(row_texts, row_xs, strict=True):
        if len(texts) < 2:
            continue
        center_gap_px = float(_pairwise_center_gap_px(ax, xs))
        if not np.isfinite(center_gap_px) or center_gap_px <= 1.0:
            continue
        for _ in range(8):
            widths = [float(txt.get_window_extent(renderer=renderer).width) for txt in texts]
            overflow = max(
                0.0,
                max(
                    0.5 * float(widths[idx] + widths[idx + 1]) + float(pad_px) - float(center_gap_px)
                    for idx in range(len(widths) - 1)
                ),
            )
            if overflow <= 0.5:
                break
            current_sizes = [float(txt.get_fontsize()) for txt in texts]
            next_size = max(float(min(current_sizes) - 0.6), float(min_font_size))
            if next_size >= min(current_sizes) - 1e-6:
                break
            for txt in texts:
                txt.set_fontsize(float(next_size))
            try:
                fig.canvas.draw()
                renderer = fig.canvas.get_renderer()
            except Exception:
                break


def _tapered_jitter_offsets(
    y_points: np.ndarray,
    *,
    max_jitter: float,
    rng: np.random.Generator,
) -> np.ndarray:
    values = np.asarray(y_points, dtype=float).reshape(-1)
    n_points = int(values.size)
    if n_points <= 1 or float(max_jitter) <= 0.0:
        return np.zeros(n_points, dtype=float)

    order = np.argsort(values, kind="mergesort")
    percentiles = np.linspace(0.0, 1.0, n_points)
    scales_sorted = np.sin(np.pi * percentiles)
    scales = np.empty(n_points, dtype=float)
    scales[order] = scales_sorted
    random_offsets = rng.uniform(low=-1.0, high=1.0, size=n_points)
    return random_offsets * float(max_jitter) * scales


def grouped_scatter(
    data: np.ndarray,
    *,
    category_names: Optional[Sequence[str]] = None,
    group_names: Optional[Sequence[str]] = None,
    x_label: str = "Categories",
    y_label: str = "Value",
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    summary: str = "mean",
    summary_marker: str = "tick",
    category_spacing: float = 1.1,
    grouped_total_span: float = 0.72,
    jitter: float = 0.0,
    jitter_profile: str = "uniform",
    point_size: Optional[float] = None,
    point_alpha: float = 0.72,
    point_edge_line_width: Optional[float] = None,
    point_face_alpha: float = 0.78,
    summary_line_width: Optional[float] = None,
    top_annotations: Optional[Sequence[str] | Sequence[Sequence[str]]] = None,
    top_annotation_font_size: Optional[int] = None,
    top_annotation_y_axes: float = 0.985,
    top_annotation_bbox_facecolor: str = "white",
    top_annotation_bbox_alpha: float = 0.94,
    show_statistics: bool = False,
    statistics_pairs: list[tuple[int, int]] | None = None,
    statistics_method: str = "mannwhitneyu",
    significance_label_style: str = "stars",
    significance_show_ns: bool = True,
    significance_ns_label: str = "n.s.",
    significance_height_step: float = 0.028,
    significance_y_padding: float = 0.02,
    significance_vertical_line_length_ratio: float | None = None,
    value_min: Optional[float] = None,
    value_max: Optional[float] = None,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    random_seed: int | None = 0,
    theme: Optional[Theme] = None,
    width: Optional[int] = 900,
    height: Optional[int] = 420,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a grouped strip/scatter plot with summary markers and optional significance brackets.

    Args:
        data: 2D ``(groups, repeats)`` or 3D ``(categories, groups, repeats)`` array.
        category_names: Names for the outer categories.
        group_names: Names for each group/method.
        x_label: X-axis label.
        y_label: Y-axis label.
        title: Optional title shown above the plot.
        color_palette: Optional palette used for group colors.
        summary: ``mean`` or ``median``.
        summary_marker: ``tick`` (short horizontal line), ``dot``, or ``line``.
        category_spacing: Distance between adjacent categories.
        grouped_total_span: Total x-span occupied by each category's groups.
        jitter: Horizontal jitter applied to each raw point. Defaults to ``0.0`` so each group forms a clean vertical column.
        jitter_profile: ``uniform`` for constant-width jitter, or ``tapered`` to expand in the middle and collapse at the tails.
        point_size: Raw point marker size in points.
        point_alpha: Edge alpha for raw points.
        point_edge_line_width: Raw point edge width in points.
        point_face_alpha: Face alpha for raw points.
        summary_line_width: Summary marker width.
        top_annotations: Optional per-group numeric labels shown near the top of the axes.
        top_annotation_font_size: Font size for top annotations.
        top_annotation_y_axes: Y location for top annotations in axes coordinates.
        top_annotation_bbox_facecolor: Background fill behind top annotations.
        top_annotation_bbox_alpha: Background alpha behind top annotations.
        show_statistics: Whether to add significance brackets.
        statistics_pairs: Explicit group index pairs to compare.
        statistics_method: ``mannwhitneyu`` or ``wilcoxon``.
        significance_label_style: ``stars`` or ``p_threshold``.
        significance_show_ns: Whether to render non-significant comparisons.
        significance_ns_label: Label used for non-significant comparisons.
        significance_height_step: Vertical step between stacked significance lanes.
        significance_y_padding: Padding above the highest summary value before brackets start.
        significance_vertical_line_length_ratio: Optional bracket end-cap ratio.
        value_min: Optional lower bound for the y-axis.
        value_max: Optional upper bound for the y-axis.
        legend_show: Whether to render a legend.
        legend_ncol: Legend columns. Defaults to the number of groups up to 6.
        tick_direction: Override tick direction.
        show_full_box: Whether to show top/right spines.
        show_x_grid: Whether to show x-axis grid lines.
        show_y_grid: Whether to show y-axis grid lines.
        random_seed: Seed for deterministic jitter.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes.
    """
    arr = _coerce_grouped_data(data)
    n_categories, n_groups, n_repeats = arr.shape
    if n_repeats == 0:
        raise ValueError("data must contain at least one repeat per group")
    if summary not in {"mean", "median"}:
        raise ValueError("summary must be 'mean' or 'median'")
    if summary_marker not in {"tick", "dot", "line"}:
        raise ValueError("summary_marker must be one of: tick, dot, line")
    if jitter_profile not in {"uniform", "tapered"}:
        raise ValueError("jitter_profile must be one of: 'uniform', 'tapered'")

    categories = _resolve_names(category_names, n_categories, "Category")
    groups = _resolve_names(group_names, n_groups, "Group")
    annotations = _normalize_top_annotations(top_annotations, n_categories=n_categories, n_groups=n_groups)
    centers = np.arange(n_categories, dtype=float) * float(category_spacing)
    bar_width = float(grouped_total_span) / float(n_groups)
    group_centers = np.empty((n_categories, n_groups), dtype=float)
    for j in range(n_categories):
        for i in range(n_groups):
            group_centers[j, i] = float(centers[j] - float(grouped_total_span) / 2.0 + (i + 0.5) * bar_width)

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    reducer = np.nanmean if summary == "mean" else np.nanmedian
    summary_values = reducer(arr, axis=2)
    spread = np.nanstd(arr, axis=2)

    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        raise ValueError("data must contain at least one finite value")
    data_min = float(np.min(finite))
    data_max = float(np.max(finite))
    data_span = max(data_max - data_min, 1e-9)
    y_min = float(value_min) if value_min is not None else data_min - data_span * 0.08
    y_max = float(value_max) if value_max is not None else data_max + data_span * 0.18

    rng = np.random.default_rng(random_seed)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_point_size = float(point_size) if point_size is not None else float(coerce_marker_size(t, kind="scatter"))
        resolved_summary_line_width = (
            float(summary_line_width)
            if summary_line_width is not None
            else float(coerce_linewidth(t, kind="data")) * 1.15
        )
        resolved_edge_width = (
            float(point_edge_line_width)
            if point_edge_line_width is not None
            else max(float(t.axis.line_width) * 0.45, 0.28)
        )

        legend_handles: list[Line2D] = []
        for i, group_name in enumerate(groups):
            color = str(colors[i % len(colors)])
            edge = darken_color(color, factor=0.82)
            for j in range(n_categories):
                x_center = float(group_centers[j, i])
                y_points = arr[j, i, :]
                if float(jitter) > 0.0:
                    if jitter_profile == "tapered":
                        x_offsets = _tapered_jitter_offsets(
                            y_points,
                            max_jitter=float(jitter),
                            rng=rng,
                        )
                    else:
                        x_offsets = rng.normal(loc=0.0, scale=float(jitter), size=n_repeats)
                    x_points = float(x_center) + np.asarray(x_offsets, dtype=float)
                else:
                    x_points = np.full(n_repeats, fill_value=float(x_center), dtype=float)
                ax.scatter(
                    x_points,
                    y_points,
                    s=float(resolved_point_size) ** 2,
                    facecolors=color_to_rgba(color, alpha=float(point_face_alpha)),
                    edgecolors=color_to_rgba(edge, alpha=float(point_alpha)),
                    linewidths=float(resolved_edge_width),
                    zorder=3,
                )

                summary_y = float(summary_values[j, i])
                if summary_marker == "tick":
                    tick_half = float(bar_width) * 0.22
                    ax.plot(
                        [x_center - tick_half, x_center + tick_half],
                        [summary_y, summary_y],
                        color=edge,
                        linewidth=float(resolved_summary_line_width),
                        solid_capstyle="round",
                        zorder=4,
                    )
                elif summary_marker == "line":
                    ax.plot(
                        [x_center, x_center],
                        [float(np.nanmin(y_points)), float(np.nanmax(y_points))],
                        color=edge,
                        linewidth=float(resolved_summary_line_width) * 0.9,
                        alpha=0.7,
                        zorder=2,
                    )
                    ax.scatter(
                        [x_center],
                        [summary_y],
                        s=(float(resolved_point_size) * 1.25) ** 2,
                        facecolors=color,
                        edgecolors=edge,
                        linewidths=float(resolved_edge_width),
                        zorder=4,
                    )
                else:
                    ax.scatter(
                        [x_center],
                        [summary_y],
                        s=(float(resolved_point_size) * 1.35) ** 2,
                        facecolors=color,
                        edgecolors=edge,
                        linewidths=float(resolved_edge_width),
                        zorder=4,
                    )

            legend_handles.append(
                Line2D(
                    [0],
                    [0],
                    marker="o",
                    linestyle="none",
                    markersize=float(resolved_point_size),
                    markerfacecolor=color_to_rgba(color, alpha=0.88),
                    markeredgecolor=edge,
                    markeredgewidth=float(resolved_edge_width),
                    label=str(group_name),
                )
            )

        ax.set_xticks(centers, labels=categories)
        ax.set_xlim(float(centers[0] - category_spacing * 0.55), float(centers[-1] + category_spacing * 0.55))
        ax.set_ylim(float(y_min), float(y_max))
        ax.set_xlabel(str(x_label))
        ax.set_ylabel(str(y_label))

        annotation_y = None
        if show_statistics and n_groups >= 2:
            max_annotation = add_significance_brackets(
                ax,
                data=arr,
                x_positions=centers,
                bar_width=bar_width,
                mean_data=summary_values,
                errors=np.zeros_like(spread),
                num_categories=n_categories,
                num_groups=n_groups,
                orientation="vertical",
                method=str(statistics_method),
                label_style=str(significance_label_style),
                pairs=statistics_pairs,
                bar_centers=group_centers,
                height_step=float(significance_height_step),
                y_padding=float(significance_y_padding),
                vertical_line_length_ratio=significance_vertical_line_length_ratio,
                show_ns=bool(significance_show_ns),
                ns_label=str(significance_ns_label),
                line_width=max(float(t.axis.line_width), 0.8),
                font_size=max(8, int(t.axis.tick_font_size)),
                font_size_ns=max(7, int(t.axis.tick_font_size) - 1),
                font_family=str(t.font_family),
            )
            if max_annotation is not None:
                annotation_y = float(max_annotation) + max(data_span * 0.045, 0.018)
                if value_max is None:
                    extra = max(data_span * 0.08, 0.03)
                    ax.set_ylim(float(y_min), max(float(ax.get_ylim()[1]), float(annotation_y) + float(extra)))

        if annotations is not None:
            annotation_base = float(annotation_y) if annotation_y is not None else float(data_max)
            header_gap = max(data_span * 0.05, 0.025)
            header_height = max(data_span * 0.08, 0.032)
            header_bottom = float(annotation_base) + float(header_gap)
            header_top = float(header_bottom) + float(header_height)
            if value_max is None:
                ax.set_ylim(
                    float(y_min),
                    max(float(ax.get_ylim()[1]), float(header_top) + max(data_span * 0.05, 0.025)),
                )
            y0, y1 = ax.get_ylim()
            y_span = float(y1) - float(y0)
            desired_top = float(y0) + y_span * float(top_annotation_y_axes)
            delta = max(float(desired_top) - float(header_top), 0.0)
            header_bottom += float(delta)
            header_top += float(delta)
            header_center = 0.5 * (float(header_bottom) + float(header_top))
            font_size = int(top_annotation_font_size) if top_annotation_font_size is not None else max(7, int(t.axis.tick_font_size) - 1)
            annotation_row_texts: list[list[object]] = []
            annotation_row_xs: list[list[float]] = []
            cell_width = float(bar_width) * 0.96
            for j in range(n_categories):
                row_texts: list[object] = []
                row_xs: list[float] = []
                for i in range(n_groups):
                    x_pos = float(group_centers[j, i])
                    left = float(x_pos) - float(cell_width) * 0.5
                    rect = Rectangle(
                        (left, float(header_bottom)),
                        float(cell_width),
                        float(header_height),
                        facecolor=str(top_annotation_bbox_facecolor),
                        edgecolor="0.82",
                        linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
                        alpha=float(top_annotation_bbox_alpha),
                        zorder=5,
                        clip_on=False,
                    )
                    ax.add_patch(rect)
                    txt = ax.text(
                        x_pos,
                        float(header_center),
                        str(annotations[j][i]),
                        ha="center",
                        va="center",
                        fontsize=font_size,
                        clip_on=False,
                        zorder=6,
                    )
                    try:
                        txt.set_in_layout(True)
                    except Exception:
                        pass
                    row_texts.append(txt)
                    row_xs.append(float(x_pos))
                annotation_row_texts.append(row_texts)
                annotation_row_xs.append(row_xs)
            _fit_top_annotation_rows(
                ax,
                row_texts=annotation_row_texts,
                row_xs=annotation_row_xs,
                pad_px=6.0,
                min_font_size=5.0,
            )

        if title:
            title_above(ax, str(title), y=1.08)

        if bool(legend_show):
            legend = ax.legend(
                handles=legend_handles,
                frameon=False,
                ncol=int(legend_ncol) if legend_ncol is not None else min(int(n_groups), 6),
                loc="upper center",
                bbox_to_anchor=(0.5, 1.04 if title else 1.10),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
                handletextpad=0.4,
                columnspacing=1.1,
            )
            try:
                legend.set_in_layout(True)
                legend.set_zorder(10)
            except Exception:
                pass
            for text in legend.get_texts():
                text.set_color("black")

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid if show_x_grid is not None else False,
            show_y_grid=show_y_grid if show_y_grid is not None else True,
        )
        fig.tight_layout()
        return fig
