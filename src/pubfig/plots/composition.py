"""Composition and grouped comparison plots (Matplotlib)."""

from __future__ import annotations

from collections import Counter
from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi, resolve_figsize_inches
from .._style import apply_cartesian_axis_controls, coerce_linewidth, normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba, darken_color
from ..themes import Theme, theme_context
from ._grouped_scatter import grouped_scatter

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def donut(
    values: np.ndarray,
    *,
    labels: Optional[Sequence[str]] = None,
    colors: Optional[Sequence[str]] = None,
    center_text: Optional[str] = None,
    title: Optional[str] = None,
    start_angle: float = 90.0,
    ring_width: float = 0.42,
    show_counts: bool = True,
    show_percents: bool = True,
    min_label_percent: float = 4.0,
    label_font_size: Optional[int] = None,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = 520,
    height: Optional[int] = 420,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a publication-style donut chart.

    Args:
        values: Positive values for each wedge.
        labels: Optional wedge labels.
        colors: Optional palette.
        center_text: Optional multiline text shown in the donut hole.
        title: Optional title.
        start_angle: Starting angle in degrees.
        ring_width: Width of the donut ring in axes-radius units.
        show_counts: Whether to show absolute counts inside wedges.
        show_percents: Whether to show percentages inside wedges.
        min_label_percent: Minimum wedge percentage required before inside labels are shown.
        label_font_size: Optional font size for inside labels.
        legend_show: Whether to show the legend.
        legend_ncol: Legend columns.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes.
    """
    arr = np.asarray(values, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("values must contain at least one element")
    if np.any(arr < 0):
        raise ValueError("values must be non-negative")
    total = float(np.sum(arr))
    if total <= 0:
        raise ValueError("values must sum to a positive number")

    wedge_labels = [str(item) for item in labels] if labels is not None else [f"Group {idx + 1}" for idx in range(arr.size)]
    if len(wedge_labels) != int(arr.size):
        raise ValueError("labels must match the length of values")

    palette = normalize_palette(colors, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        wedge_colors = [palette[idx % len(palette)] for idx in range(arr.size)]
        wedges, _ = ax.pie(
            arr,
            startangle=float(start_angle),
            counterclock=False,
            colors=wedge_colors,
            wedgeprops={"width": float(ring_width), "edgecolor": "white", "linewidth": max(float(t.axis.line_width) * 0.75, 0.6)},
        )
        ax.set_aspect("equal")

        inner_radius = 1.0 - float(ring_width)
        text_radius = inner_radius + float(ring_width) * 0.52
        font_size = int(label_font_size) if label_font_size is not None else max(8, int(t.axis.tick_font_size))
        for wedge, value in zip(wedges, arr, strict=True):
            percent = float(value) / float(total) * 100.0
            if percent < float(min_label_percent):
                continue
            theta = np.deg2rad((float(wedge.theta1) + float(wedge.theta2)) * 0.5)
            x = float(text_radius * np.cos(theta))
            y = float(text_radius * np.sin(theta))
            parts: list[str] = []
            if bool(show_counts):
                parts.append(f"{int(round(float(value)))}")
            if bool(show_percents):
                parts.append(f"({percent:.1f}%)")
            if not parts:
                continue
            txt = ax.text(
                x,
                y,
                "\n".join(parts),
                ha="center",
                va="center",
                fontsize=font_size,
                zorder=5,
            )
            try:
                txt.set_in_layout(True)
            except Exception:
                pass

        if center_text:
            center = ax.text(
                0.0,
                0.0,
                str(center_text),
                ha="center",
                va="center",
                fontsize=max(int(t.title_font_size), 11),
                fontweight="semibold",
                linespacing=1.15,
            )
            try:
                center.set_in_layout(True)
            except Exception:
                pass

        if title:
            title_above(ax, str(title), y=1.07)
        if bool(legend_show):
            legend = ax.legend(
                wedges,
                wedge_labels,
                frameon=False,
                ncol=int(legend_ncol) if legend_ncol is not None else min(int(arr.size), 4),
                loc="upper center",
                bbox_to_anchor=(0.5, 1.04 if title else 1.12),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
                handlelength=1.2,
                columnspacing=0.8,
                handletextpad=0.45,
            )
            try:
                legend.set_in_layout(True)
                legend.set_zorder(10)
            except Exception:
                pass

        ax.set_axis_off()
        fig.subplots_adjust(
            top=0.90 if title else 0.96,
            bottom=0.12,
            left=0.10,
            right=0.98,
            wspace=0.08,
            hspace=0.08,
        )
        return fig


def stacked_ratio_barh(
    positive: np.ndarray,
    *,
    negative: Optional[np.ndarray] = None,
    labels: Optional[Sequence[str]] = None,
    group_labels: Optional[Sequence[str]] = None,
    positive_label: str = "Positive",
    negative_label: str = "Negative",
    colors: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    x_label: str = "Ratio",
    show_percent_labels: bool = True,
    normalize: bool = True,
    group_backgrounds: bool = True,
    group_background_alpha: float = 0.12,
    group_background_palette: Optional[Sequence[str]] = None,
    bar_height: float = 0.82,
    label_font_size: Optional[int] = None,
    legend_show: bool = True,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = 760,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a horizontal positive/negative ratio chart.

    Args:
        positive: Positive values or percentages.
        negative: Optional negative values. If omitted, uses ``100 - positive``.
        labels: Row labels.
        group_labels: Optional group label for each row. Consecutive rows with the same value share a background band.
        positive_label: Legend label for the positive segment.
        negative_label: Legend label for the negative segment.
        colors: Optional pair of colors ``(positive, negative)``.
        title: Optional title.
        x_label: X-axis label.
        show_percent_labels: Whether to print percentages inside the bars.
        normalize: Whether to normalize rows to 100.
        group_backgrounds: Whether to tint consecutive groups.
        group_background_alpha: Alpha for group background bands.
        group_background_palette: Optional palette used for group shading.
        bar_height: Height of each horizontal bar.
        label_font_size: Optional font size for percentage labels.
        legend_show: Whether to render the legend.
        tick_direction: Override tick direction.
        show_full_box: Whether to show top/right spines.
        show_x_grid: Whether to show x-axis grid lines.
        show_y_grid: Whether to show y-axis grid lines.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels. Auto-scales with the number of rows when omitted.
        ax: Optional Matplotlib Axes.
    """
    pos = np.asarray(positive, dtype=float).reshape(-1)
    if pos.size == 0:
        raise ValueError("positive must contain at least one element")
    neg = (100.0 - pos) if negative is None else np.asarray(negative, dtype=float).reshape(-1)
    if neg.shape != pos.shape:
        raise ValueError("negative must match the length of positive")
    if np.any(pos < 0) or np.any(neg < 0):
        raise ValueError("positive and negative values must be non-negative")

    row_labels = [str(item) for item in labels] if labels is not None else [f"Item {idx + 1}" for idx in range(pos.size)]
    if len(row_labels) != int(pos.size):
        raise ValueError("labels must match the length of positive")

    groups = [str(item) for item in group_labels] if group_labels is not None else [""] * int(pos.size)
    if len(groups) != int(pos.size):
        raise ValueError("group_labels must match the length of positive")

    totals = pos + neg
    if np.any(totals <= 0):
        raise ValueError("Each row must sum to a positive value")
    if normalize:
        pos = pos / totals * 100.0
        neg = neg / totals * 100.0

    palette = normalize_palette(colors, fallback=["#F3D3B8", "#ECECEC"])
    bg_palette = normalize_palette(group_background_palette, fallback=["#F8E7E7", "#E8F0E7", "#EFEAE2"])
    n_rows = pos.size
    if height is None:
        height = max(420, int(46 * n_rows + 90))

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        y = np.arange(n_rows, dtype=float)

        if bool(group_backgrounds) and any(groups):
            start = 0
            band_idx = 0
            while start < n_rows:
                end = start + 1
                while end < n_rows and groups[end] == groups[start]:
                    end += 1
                if groups[start]:
                    ax.axhspan(
                        float(start) - 0.5,
                        float(end - 1) + 0.5,
                        color=color_to_rgba(bg_palette[band_idx % len(bg_palette)], alpha=float(group_background_alpha)),
                        zorder=0,
                    )
                    band_idx += 1
                start = end

        pos_color = str(palette[0])
        neg_color = str(palette[1 % len(palette)])
        ax.barh(
            y,
            pos,
            height=float(bar_height),
            color=pos_color,
            edgecolor=darken_color(pos_color, factor=0.88),
            linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
            label=str(positive_label),
            zorder=2,
        )
        ax.barh(
            y,
            neg,
            left=pos,
            height=float(bar_height),
            color=neg_color,
            edgecolor=darken_color(neg_color, factor=0.90),
            linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
            label=str(negative_label),
            zorder=2,
        )

        font_size = int(label_font_size) if label_font_size is not None else max(8, int(t.axis.tick_font_size))
        if bool(show_percent_labels):
            for idx in range(n_rows):
                if float(pos[idx]) >= 7.0:
                    ax.text(float(pos[idx]) * 0.5, float(y[idx]), f"{pos[idx]:.0f}%", ha="center", va="center", fontsize=font_size, zorder=3)
                if float(neg[idx]) >= 7.0:
                    ax.text(float(pos[idx] + neg[idx] * 0.5), float(y[idx]), f"{neg[idx]:.0f}%", ha="center", va="center", fontsize=font_size, zorder=3)

        ax.set_yticks(y, labels=row_labels)
        ax.invert_yaxis()
        ax.set_xlim(0.0, 100.0)
        ax.set_xlabel(str(x_label))
        ax.set_ylabel("")
        if title:
            title_above(ax, str(title), y=1.06)
        if bool(legend_show):
            legend = ax.legend(
                frameon=False,
                ncol=2,
                loc="upper center",
                bbox_to_anchor=(0.5, 1.03 if title else 1.10),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
                handletextpad=0.45,
                columnspacing=0.8,
            )
            try:
                legend.set_in_layout(True)
                legend.set_zorder(10)
            except Exception:
                pass

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid if show_x_grid is not None else True,
            show_y_grid=show_y_grid if show_y_grid is not None else False,
        )
        fig.tight_layout()
        return fig


def _normalize_upset_memberships(
    memberships,
    *,
    set_names: Optional[Sequence[str]] = None,
) -> tuple[np.ndarray, list[str]]:
    if isinstance(memberships, np.ndarray):
        matrix = np.asarray(memberships)
        if matrix.ndim != 2:
            raise ValueError("membership matrix must be 2D")
        membership_matrix = matrix.astype(bool)
        names = [str(item) for item in set_names] if set_names is not None else [f"Set {idx + 1}" for idx in range(matrix.shape[1])]
        if len(names) != membership_matrix.shape[1]:
            raise ValueError("set_names must match the number of columns")
        return membership_matrix, names

    items = list(memberships)
    if not items:
        raise ValueError("memberships must contain at least one item")

    if set_names is None:
        names: list[str] = []
        for item in items:
            for name in item:
                label = str(name)
                if label not in names:
                    names.append(label)
    else:
        names = [str(item) for item in set_names]

    index = {name: idx for idx, name in enumerate(names)}
    membership_matrix = np.zeros((len(items), len(names)), dtype=bool)
    for row_idx, item in enumerate(items):
        for name in item:
            label = str(name)
            if label not in index:
                raise ValueError(f"Unknown set label: {label}")
            membership_matrix[row_idx, index[label]] = True
    return membership_matrix, names


def upset(
    memberships,
    *,
    set_names: Optional[Sequence[str]] = None,
    min_size: int = 1,
    sort_by: str = "size",
    sort_sets: bool = False,
    max_intersections: Optional[int] = 12,
    title: Optional[str] = None,
    show_counts: bool = True,
    matrix_dot_size: float = 4.6,
    bar_color: Optional[str] = None,
    matrix_color: str = "0.22",
    inactive_dot_color: str = "0.86",
    connector_color: str = "0.60",
    row_guide_color: str = "0.88",
    row_guide_line_width: float = 1.0,
    row_band_color: str = "none",
    set_size_bar_height: float = 0.60,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = 820,
    height: Optional[int] = 560,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a publication-style UpSet plot for set intersections.

    Args:
        memberships: Either a boolean membership matrix with shape `(n_items, n_sets)`
            or a list where each item is a list/tuple of set names.
        set_names: Optional set labels. Required when the membership matrix columns do
            not already have names and recommended for stable ordering.
        min_size: Minimum intersection size to display.
        sort_by: ``"size"`` or ``"degree"``.
        sort_sets: If True, sort set rows by descending set size.
        max_intersections: Optional maximum number of intersections to display.
        title: Optional plot title.
        show_counts: Whether to print counts above the intersection bars.
        matrix_dot_size: Dot size in Matplotlib points.
        bar_color: Optional color override for the intersection bars.
        matrix_color: Color of active membership dots.
        inactive_dot_color: Color of inactive dots.
        connector_color: Color of vertical connectors in the membership matrix.
        row_guide_color: Color of horizontal row guides in the intersection matrix.
        row_guide_line_width: Line width of horizontal row guides.
        row_band_color: Optional background band color for matrix rows. Use ``"none"``
            for the cleaner default with no row shading.
        set_size_bar_height: Height of the left set-size bars.
        tick_direction: Override tick direction.
        show_full_box: Whether to show top/right spines on data axes.
        show_x_grid: Whether to show grid lines on the bar axis.
        show_y_grid: Whether to show grid lines on the bar axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes. UpSet uses a multi-axis layout and does not support drawing into an existing axis.
    """
    if ax is not None:
        raise ValueError("upset does not support drawing into an existing axis")

    membership_matrix, names = _normalize_upset_memberships(memberships, set_names=set_names)
    if membership_matrix.shape[1] == 0:
        raise ValueError("memberships must contain at least one set")

    if bool(sort_sets):
        set_sizes = membership_matrix.sum(axis=0)
        order = np.argsort(-set_sizes, kind="stable")
        membership_matrix = membership_matrix[:, order]
        names = [names[int(idx)] for idx in order]

    signature_counter: Counter[tuple[int, ...]] = Counter()
    for row in membership_matrix:
        active = tuple(np.flatnonzero(row).tolist())
        if active:
            signature_counter[active] += 1

    intersections: list[tuple[tuple[int, ...], int]] = [
        (signature, count) for signature, count in signature_counter.items() if int(count) >= int(min_size)
    ]
    if not intersections:
        raise ValueError("No intersections remain after applying min_size")

    mode = str(sort_by).lower()
    if mode == "size":
        intersections.sort(key=lambda item: (-item[1], -len(item[0]), item[0]))
    elif mode == "degree":
        intersections.sort(key=lambda item: (-len(item[0]), -item[1], item[0]))
    else:
        raise ValueError("sort_by must be 'size' or 'degree'")

    if max_intersections is not None:
        intersections = intersections[: int(max_intersections)]

    set_sizes = membership_matrix.sum(axis=0)
    bar_fill = str(bar_color or DEFAULT[0])

    with theme_context(theme) as t:
        import matplotlib.pyplot as plt

        dpi = resolve_design_dpi(t.name)
        figsize = resolve_figsize_inches(
            width_px=width,
            height_px=height,
            design_dpi=dpi,
            default_aspect_ratio=0.68,
        )
        fig = plt.figure(figsize=figsize)
        grid = fig.add_gridspec(
            2,
            2,
            width_ratios=(1.15, 3.4),
            height_ratios=(2.4, 1.2),
            wspace=0.08,
            hspace=0.08,
        )
        corner_ax = fig.add_subplot(grid[0, 0])
        bar_ax = fig.add_subplot(grid[0, 1])
        matrix_ax = fig.add_subplot(grid[1, 1], sharex=bar_ax)
        size_ax = fig.add_subplot(grid[1, 0], sharey=matrix_ax)

        x_positions = np.arange(len(intersections), dtype=float)
        counts = np.array([count for _, count in intersections], dtype=float)
        signatures = [signature for signature, _ in intersections]
        y_positions = np.arange(len(names), dtype=float)


        resolved_bar_line_width = float(coerce_linewidth(t, kind="data")) * 0.55
        row_band_enabled = str(row_band_color).strip().lower() not in {"", "none", "transparent"}
        bar_ax.bar(
            x_positions,
            counts,
            color=color_to_rgba(bar_fill, alpha=0.9),
            edgecolor=darken_color(bar_fill, factor=0.82),
            linewidth=resolved_bar_line_width,
            width=0.72,
        )
        if bool(show_counts):
            count_pad = max(float(np.max(counts)) * 0.03, 0.5)
            for xpos, count in zip(x_positions, counts, strict=True):
                bar_ax.text(
                    float(xpos),
                    float(count) + count_pad,
                    f"{int(count)}",
                    ha="center",
                    va="bottom",
                    fontsize=max(5, int(t.axis.tick_font_size) - 1),
                )
        if title:
            title_above(bar_ax, str(title), y=1.05)

        bar_ax.set_ylabel("Intersection size")
        bar_ax.set_xticks([])
        t.apply_axes(bar_ax)
        apply_cartesian_axis_controls(
            bar_ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=False,
            show_y_grid=show_y_grid if show_y_grid is not None else True,
        )

        if row_band_enabled:
            for ypos in y_positions:
                matrix_ax.axhspan(
                    float(ypos) - 0.5,
                    float(ypos) + 0.5,
                    color=str(row_band_color),
                    zorder=-2,
                )

        for xpos, signature in zip(x_positions, signatures, strict=True):
            active = np.array(signature, dtype=int)
            matrix_ax.scatter(
                np.full_like(y_positions, fill_value=float(xpos), dtype=float),
                y_positions,
                s=float(matrix_dot_size) ** 2,
                color=str(inactive_dot_color),
                zorder=1,
            )
            matrix_ax.scatter(
                np.full(active.shape, fill_value=float(xpos), dtype=float),
                active.astype(float),
                s=float(matrix_dot_size) ** 2,
                color=str(matrix_color),
                zorder=3,
            )
            if active.size >= 2:
                matrix_ax.plot(
                    [float(xpos), float(xpos)],
                    [float(np.min(active)), float(np.max(active))],
                    color=str(connector_color),
                    linewidth=max(float(t.axis.line_width) * 0.85, 0.8),
                    zorder=2,
                )

        matrix_ax.set_yticks(y_positions)
        matrix_ax.set_yticklabels([])
        matrix_ax.set_ylim(-0.36, float(len(names) - 0.24))
        matrix_ax.invert_yaxis()
        matrix_ax.margins(y=0.0)
        matrix_ax.set_xlabel("Intersections")
        matrix_ax.set_xticks(x_positions)
        matrix_ax.set_xticklabels([])
        t.apply_axes(matrix_ax)
        matrix_ax.tick_params(axis="y", which="both", left=False, labelleft=False)
        matrix_ax.spines["right"].set_visible(False)
        matrix_ax.spines["top"].set_visible(False)
        matrix_ax.grid(False)

        for ypos in y_positions:
            matrix_ax.axhline(
                float(ypos),
                color=str(row_guide_color),
                linewidth=float(row_guide_line_width),
                zorder=0,
            )

        size_bars = size_ax.barh(
            y_positions,
            set_sizes,
            color=color_to_rgba(bar_fill, alpha=0.78),
            edgecolor=darken_color(bar_fill, factor=0.82),
            linewidth=resolved_bar_line_width,
            height=float(set_size_bar_height),
            align="center",
            zorder=2,
        )
        size_ax.set_yticks(y_positions, labels=names)
        size_ax.set_ylim(matrix_ax.get_ylim())
        size_ax.margins(y=0.0)
        size_ax.set_xlabel("Set size")
        max_set_size = float(np.max(set_sizes)) if set_sizes.size else 1.0
        value_pad = max(max_set_size * 0.035, 1.0)
        size_ax.set_xlim(max_set_size + value_pad * 2.8, 0.0)
        size_tick_positions = np.linspace(0.0, max_set_size, num=3)
        size_ax.set_xticks(size_tick_positions)
        size_ax.tick_params(axis="x", which="both", bottom=True, labelbottom=False)
        for bar, value in zip(size_bars.patches, set_sizes, strict=True):
            ypos = float(bar.get_y()) + float(bar.get_height()) * 0.5
            text_x = value_pad * 0.90
            size_ax.text(
                text_x,
                ypos,
                f"{int(value)}",
                ha="right",
                va="center",
                fontsize=max(5, int(t.axis.tick_font_size) - 1),
                color="black",
                zorder=4,
            )
        t.apply_axes(size_ax)
        size_ax.tick_params(axis="y", pad=8)
        apply_cartesian_axis_controls(
            size_ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid if show_x_grid is not None else False,
            show_y_grid=False,
        )
        size_ax.spines["top"].set_visible(False)
        size_ax.spines["right"].set_visible(False)
        bar_ax.tick_params(axis="x", which="both", bottom=False, labelbottom=False)

        corner_ax.set_axis_off()
        fig.subplots_adjust(
            top=0.90 if title else 0.96,
            bottom=0.12,
            left=0.10,
            right=0.98,
            wspace=0.08,
            hspace=0.08,
        )
        return fig


__all__ = ["donut", "grouped_scatter", "stacked_ratio_barh", "upset"]
