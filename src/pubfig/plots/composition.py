"""Composition and grouped comparison plots (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import apply_cartesian_axis_controls, normalize_palette, title_above
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
        fig.tight_layout()
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


__all__ = ["donut", "grouped_scatter", "stacked_ratio_barh"]
