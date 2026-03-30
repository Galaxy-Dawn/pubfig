"""Polar publication plots (Matplotlib)."""

from __future__ import annotations

from collections import OrderedDict
from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
from matplotlib.patches import Patch, Wedge

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _normalize_group_mapping(
    group_labels: Sequence[str],
    subgroup_groups: Sequence[str | int],
) -> tuple[list[str], list[int]]:
    groups = [str(item) for item in group_labels]
    resolved: list[int] = []
    for item in subgroup_groups:
        if isinstance(item, (int, np.integer)):
            idx = int(item)
        else:
            try:
                idx = groups.index(str(item))
            except ValueError as exc:  # pragma: no cover - defensive
                raise ValueError("subgroup_groups contains an unknown group label") from exc
        if idx < 0 or idx >= len(groups):
            raise ValueError("subgroup_groups contains an out-of-range group index")
        resolved.append(idx)
    return groups, resolved


def _upright_tangent_rotation(theta_deg: float) -> float:
    rotation = float(theta_deg) - 90.0
    while rotation > 90.0:
        rotation -= 180.0
    while rotation < -90.0:
        rotation += 180.0
    return rotation


def _outer_text_anchor(theta_deg: float) -> str:
    theta_mod = float(theta_deg) % 360.0
    return "right" if 90.0 < theta_mod < 270.0 else "left"


def _horizontal_text_align(theta_deg: float) -> tuple[str, str]:
    theta_mod = float(theta_deg) % 360.0
    if 45.0 <= theta_mod < 135.0:
        return "center", "bottom"
    if 135.0 <= theta_mod < 225.0:
        return "right", "center"
    if 225.0 <= theta_mod < 315.0:
        return "center", "top"
    return "left", "center"


def _wrap_polar_label(label: str) -> str:
    text = str(label)
    if " / " in text:
        return text.replace(" / ", "\n")
    if len(text) > 12 and "-" in text:
        return text.replace("-", "-\n", 1)
    return text


def _blend_with_white(color: str, amount: float) -> tuple[float, float, float, float]:
    rgba = np.asarray(color_to_rgba(color, alpha=1.0), dtype=float)
    white = np.array([1.0, 1.0, 1.0, 1.0], dtype=float)
    mixed = rgba * (1.0 - float(amount)) + white * float(amount)
    mixed[3] = 1.0
    return tuple(float(v) for v in mixed)


def _allocate_group_spans(
    totals: np.ndarray,
    *,
    start_angle: float,
    gap_degrees: float,
) -> list[tuple[float, float]]:
    n_groups = int(totals.size)
    usable = 360.0 - float(max(0, n_groups)) * float(gap_degrees)
    if usable <= 0:
        raise ValueError("gap_degrees is too large for the number of groups")
    spans: list[tuple[float, float]] = []
    cursor = float(start_angle)
    total_sum = float(np.sum(totals))
    for total in totals:
        span = usable * float(total) / total_sum
        spans.append((float(cursor), float(cursor + span)))
        cursor += float(span) + float(gap_degrees)
    return spans


def _ordered_group_blocks(item_groups: Sequence[str]) -> tuple[list[str], list[int], list[int]]:
    groups = [str(item) for item in item_groups]
    unique: list[str] = []
    starts: list[int] = []
    counts: list[int] = []
    idx = 0
    while idx < len(groups):
        group = groups[idx]
        start = idx
        while idx < len(groups) and groups[idx] == group:
            idx += 1
        unique.append(group)
        starts.append(start)
        counts.append(idx - start)
    return unique, starts, counts


def radial_hierarchy(
    values: np.ndarray,
    *,
    subgroup_labels: Sequence[str],
    subgroup_groups: Sequence[str | int],
    group_labels: Sequence[str],
    group_colors: Optional[Sequence[str]] = None,
    center_text: Optional[str] = None,
    title: Optional[str] = None,
    start_angle: float = 90.0,
    inner_radius: float = 0.30,
    group_ring_width: float = 0.16,
    subgroup_ring_width: float = 0.18,
    group_gap_degrees: float = 2.4,
    outer_label_radius_offset: float = 0.08,
    outer_value_radius_offset: float = 0.03,
    subgroup_label_position: str = "inside",
    show_group_labels: bool = True,
    show_outer_values: bool = True,
    center_text_font_size: Optional[int] = None,
    group_label_font_size: Optional[int] = None,
    subgroup_label_font_size: Optional[int] = None,
    value_label_font_size: Optional[int] = None,
    group_edgecolor: str = "white",
    subgroup_edgecolor: str = "white",
    legend_show: bool = False,
    theme: Optional[Theme] = None,
    width: Optional[int] = 680,
    height: Optional[int] = 680,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a two-level radial hierarchy chart.

    Args:
        values: Positive values for each subgroup wedge.
        subgroup_labels: Labels for the outer wedges.
        subgroup_groups: Group assignment per subgroup (name or group index).
        group_labels: Ordered labels for the inner ring groups.
        group_colors: Base color palette for groups.
        center_text: Optional summary text in the center.
        title: Optional title.
        start_angle: Starting angle in degrees.
        inner_radius: Radius of the center hole.
        group_ring_width: Width of the inner group ring.
        subgroup_ring_width: Width of the outer subgroup ring.
        group_gap_degrees: Gap between groups in degrees.
        outer_label_radius_offset: Extra radius for subgroup labels when positioned outside the ring.
        outer_value_radius_offset: Extra radius for outer numeric values.
        subgroup_label_position: "outside" to place subgroup labels outside the ring, or "inside" to place them inside the outer ring.
        show_group_labels: Whether to label the inner ring groups.
        show_outer_values: Whether to label outer numeric values.
        center_text_font_size: Font size for the center summary text.
        group_label_font_size: Font size for inner group labels.
        subgroup_label_font_size: Font size for outer subgroup labels.
        value_label_font_size: Font size for outer numeric values.
        group_edgecolor: Edge color for the inner ring.
        subgroup_edgecolor: Edge color for the outer ring.
        legend_show: Whether to show a small group legend.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes.
    """
    vals = np.asarray(values, dtype=float).reshape(-1)
    if vals.size == 0:
        raise ValueError("values must contain at least one element")
    if np.any(vals <= 0):
        raise ValueError("values must be positive")
    sub_labels = [str(item) for item in subgroup_labels]
    if len(sub_labels) != int(vals.size):
        raise ValueError("subgroup_labels must match the length of values")
    groups, subgroup_group_indices = _normalize_group_mapping(group_labels, subgroup_groups)
    if len(subgroup_group_indices) != int(vals.size):
        raise ValueError("subgroup_groups must match the length of values")
    if subgroup_label_position not in {"outside", "inside"}:
        raise ValueError("subgroup_label_position must be one of: 'outside', 'inside'")

    n_groups = len(groups)
    group_totals = np.zeros(n_groups, dtype=float)
    for idx, value in zip(subgroup_group_indices, vals, strict=True):
        group_totals[int(idx)] += float(value)
    group_spans = _allocate_group_spans(group_totals, start_angle=float(start_angle), gap_degrees=float(group_gap_degrees))
    palette = normalize_palette(group_colors, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        ax.set_aspect("equal")
        outer_radius = float(inner_radius) + float(group_ring_width) + float(subgroup_ring_width)
        group_fs = int(group_label_font_size) if group_label_font_size is not None else max(7, int(t.axis.tick_font_size) - 1)
        subgroup_fs = int(subgroup_label_font_size) if subgroup_label_font_size is not None else max(6, int(t.axis.tick_font_size) - 2)
        value_fs = int(value_label_font_size) if value_label_font_size is not None else max(6, int(t.axis.tick_font_size) - 3)
        center_fs = int(center_text_font_size) if center_text_font_size is not None else max(int(t.title_font_size), 11)

        handles: list[Patch] = []
        for g_idx, ((theta0, theta1), group_name) in enumerate(zip(group_spans, groups, strict=True)):
            base_color = str(palette[g_idx % len(palette)])
            inner_patch = Wedge(
                (0.0, 0.0),
                r=float(inner_radius) + float(group_ring_width),
                theta1=float(theta0),
                theta2=float(theta1),
                width=float(group_ring_width),
                facecolor=base_color,
                edgecolor=str(group_edgecolor),
                linewidth=max(float(t.axis.line_width) * 0.5, 0.45),
                zorder=2,
            )
            ax.add_patch(inner_patch)
            handles.append(Patch(facecolor=base_color, edgecolor="none", label=str(group_name)))

            subgroup_idx = [idx for idx, parent in enumerate(subgroup_group_indices) if int(parent) == int(g_idx)]
            group_values = vals[subgroup_idx]
            group_sum = float(np.sum(group_values))
            cursor = float(theta0)
            for local_idx, sub_idx in enumerate(subgroup_idx):
                span = (float(theta1) - float(theta0)) * float(vals[sub_idx]) / group_sum
                sub_theta0 = float(cursor)
                sub_theta1 = float(cursor + span)
                cursor = float(sub_theta1)
                shade = 0.15 + 0.55 * (float(local_idx) / max(1.0, float(len(subgroup_idx) - 1)))
                sub_color = _blend_with_white(base_color, amount=min(max(shade, 0.0), 0.80))
                patch = Wedge(
                    (0.0, 0.0),
                    r=float(outer_radius),
                    theta1=float(sub_theta0),
                    theta2=float(sub_theta1),
                    width=float(subgroup_ring_width),
                    facecolor=sub_color,
                    edgecolor=str(subgroup_edgecolor),
                    linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
                    zorder=3,
                )
                ax.add_patch(patch)

                theta_mid = 0.5 * (float(sub_theta0) + float(sub_theta1))
                theta_rad = np.deg2rad(float(theta_mid))
                if subgroup_label_position == "inside":
                    label_radius = float(inner_radius) + float(group_ring_width) + float(subgroup_ring_width) * 0.52
                    label_x = label_radius * float(np.cos(theta_rad))
                    label_y = label_radius * float(np.sin(theta_rad))
                    if float(sub_theta1) - float(sub_theta0) >= 7.0:
                        ax.text(
                            label_x,
                            label_y,
                            _wrap_polar_label(str(sub_labels[sub_idx])),
                            rotation=float(_upright_tangent_rotation(float(theta_mid))),
                            rotation_mode="anchor",
                            ha="center",
                            va="center",
                            fontsize=subgroup_fs,
                            linespacing=0.92,
                            zorder=4,
                        )
                else:
                    label_radius = float(outer_radius) + float(outer_label_radius_offset)
                    label_x = label_radius * float(np.cos(theta_rad))
                    label_y = label_radius * float(np.sin(theta_rad))
                    if float(sub_theta1) - float(sub_theta0) >= 6.0:
                        ax.text(
                            label_x,
                            label_y,
                            _wrap_polar_label(str(sub_labels[sub_idx])),
                            rotation=float(_upright_tangent_rotation(float(theta_mid))),
                            rotation_mode="anchor",
                            ha="center",
                            va="center",
                            fontsize=subgroup_fs,
                            linespacing=0.92,
                            zorder=4,
                        )
                value_radius = float(outer_radius) + float(outer_value_radius_offset)
                value_x = value_radius * float(np.cos(theta_rad))
                value_y = value_radius * float(np.sin(theta_rad))
                if bool(show_outer_values):
                    ax.text(
                        value_x,
                        value_y,
                        f"{int(round(float(vals[sub_idx])))}",
                        rotation=float(_upright_tangent_rotation(float(theta_mid))),
                        rotation_mode="anchor",
                        ha="center",
                        va="center",
                        fontsize=value_fs,
                        zorder=4,
                    )

            if bool(show_group_labels):
                theta_mid = 0.5 * (float(theta0) + float(theta1))
                theta_rad = np.deg2rad(float(theta_mid))
                radius = float(inner_radius) + float(group_ring_width) * 0.52
                ax.text(
                    radius * float(np.cos(theta_rad)),
                    radius * float(np.sin(theta_rad)),
                    _wrap_polar_label(str(group_name)),
                    rotation=float(_upright_tangent_rotation(float(theta_mid))),
                    rotation_mode="anchor",
                    ha="center",
                    va="center",
                    fontsize=group_fs,
                    linespacing=0.92,
                    zorder=4,
                )

        if center_text:
            ax.text(
                0.0,
                0.0,
                str(center_text),
                ha="center",
                va="center",
                fontsize=center_fs,
                linespacing=1.15,
                fontweight="semibold",
                zorder=5,
            )
        if title:
            title_above(ax, str(title), y=1.04)
        if bool(legend_show):
            legend = ax.legend(
                handles=handles,
                frameon=False,
                ncol=min(4, max(1, len(handles))),
                loc="lower center",
                bbox_to_anchor=(0.5, -0.03),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
                handlelength=1.0,
                columnspacing=0.8,
                handletextpad=0.4,
            )
            try:
                legend.set_in_layout(True)
            except Exception:
                pass

        lim = float(outer_radius) + float(outer_value_radius_offset) + 0.08
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.axis("off")
        fig.tight_layout()
        return fig


def circular_stacked_bar(
    values: np.ndarray,
    *,
    item_labels: Sequence[str],
    item_groups: Sequence[str],
    stack_labels: Optional[Sequence[str]] = None,
    stack_colors: Optional[Sequence[str]] = None,
    group_colors: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    start_angle: float = 90.0,
    inner_radius: float = 0.28,
    group_ring_width: float = 0.08,
    bar_inner_radius: float = 0.39,
    bar_max_height: float = 0.42,
    item_gap_degrees: float = 0.55,
    group_gap_degrees: float = 6.5,
    outer_label_offset: float = 0.04,
    group_label_font_size: Optional[int] = 5,
    item_label_font_size: Optional[int] = 4,
    legend_show: bool = False,
    group_legend_show: bool = False,
    theme: Optional[Theme] = None,
    width: Optional[int] = 780,
    height: Optional[int] = 780,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a circular stacked bar chart with an inner group ring.

    Args:
        values: 2D array ``(n_items, n_stacks)`` of non-negative values.
        item_labels: Labels for each outer bar.
        item_groups: Group label for each item. Consecutive identical labels form one block.
        stack_labels: Optional labels for stacked segments.
        stack_colors: Optional colors for stacked segments.
        group_colors: Optional colors for inner group blocks.
        title: Optional title.
        start_angle: Starting angle in degrees.
        inner_radius: Radius of the center hole.
        group_ring_width: Width of the inner group ring.
        bar_inner_radius: Inner radius where the stacked bars begin.
        bar_max_height: Maximum radial height of the stacked bars.
        item_gap_degrees: Gap between adjacent items.
        group_gap_degrees: Gap between group blocks.
        outer_label_offset: Extra radial offset for item labels.
        group_label_font_size: Font size for group labels.
        item_label_font_size: Font size for item labels.
        legend_show: Whether to show legends for stacks and groups.
        group_legend_show: Whether to render the second legend for group blocks.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes.
    """
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError("values must be a 2D numpy array with shape (n_items, n_stacks)")
    if np.any(arr < 0):
        raise ValueError("values must be non-negative")
    n_items, n_stacks = arr.shape
    labels = [str(item) for item in item_labels]
    if len(labels) != int(n_items):
        raise ValueError("item_labels must match the number of rows in values")
    groups = [str(item) for item in item_groups]
    if len(groups) != int(n_items):
        raise ValueError("item_groups must match the number of rows in values")
    stacks = [str(item) for item in stack_labels] if stack_labels is not None else [f"Stack {idx + 1}" for idx in range(n_stacks)]
    if len(stacks) != int(n_stacks):
        raise ValueError("stack_labels must match the number of stacked columns")

    stack_palette = normalize_palette(stack_colors, fallback=["#F5D6B3", "#F0B987", "#CFD4F1", "#5561A9"])
    group_names, group_starts, group_counts = _ordered_group_blocks(groups)
    group_palette = normalize_palette(group_colors, fallback=["#D97C6C", "#D9A56C", "#90AFC5", "#78A58E"])
    max_total = float(np.max(np.sum(arr, axis=1)))
    if max_total <= 0:
        raise ValueError("At least one row in values must have a positive total")

    total_item_gap = float(item_gap_degrees) * float(n_items)
    total_group_gap = float(group_gap_degrees) * float(len(group_names))
    usable = 360.0 - total_item_gap - total_group_gap
    if usable <= 0:
        raise ValueError("Too many items or too much angular gap for a circular stacked bar plot")
    item_span = usable / float(n_items)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        ax.set_aspect("equal")
        group_fs = int(group_label_font_size) if group_label_font_size is not None else max(7, int(t.axis.tick_font_size) - 1)
        item_fs = int(item_label_font_size) if item_label_font_size is not None else max(6, int(t.axis.tick_font_size) - 2)

        stack_handles = [Patch(facecolor=stack_palette[idx % len(stack_palette)], edgecolor="none", label=str(stacks[idx])) for idx in range(n_stacks)]
        group_handle_map: OrderedDict[str, Patch] = OrderedDict()

        group_lookup = {name: idx for idx, name in enumerate(group_names)}
        cursor = float(start_angle)
        group_ranges: list[tuple[str, float, float]] = []
        for g_name, g_start, g_count in zip(group_names, group_starts, group_counts, strict=True):
            group_theta0 = float(cursor)
            for local_item_idx in range(int(g_count)):
                item_idx = int(g_start + local_item_idx)
                theta0 = float(cursor + item_gap_degrees * 0.5)
                theta1 = float(theta0 + item_span)
                total = float(np.sum(arr[item_idx]))
                inner_cursor = float(bar_inner_radius)
                for stack_idx in range(n_stacks):
                    if total <= 0 or float(arr[item_idx, stack_idx]) <= 0:
                        continue
                    height = float(bar_max_height) * float(arr[item_idx, stack_idx]) / float(max_total)
                    patch = Wedge(
                        (0.0, 0.0),
                        r=float(inner_cursor + height),
                        theta1=float(theta0),
                        theta2=float(theta1),
                        width=float(height),
                        facecolor=stack_palette[stack_idx % len(stack_palette)],
                        edgecolor="white",
                        linewidth=max(float(t.axis.line_width) * 0.35, 0.3),
                        zorder=3,
                    )
                    ax.add_patch(patch)
                    inner_cursor += float(height)

                theta_mid = 0.5 * (float(theta0) + float(theta1))
                theta_rad = np.deg2rad(float(theta_mid))
                label_radius = float(bar_inner_radius) + float(bar_max_height) + float(outer_label_offset)
                ax.text(
                    label_radius * float(np.cos(theta_rad)),
                    label_radius * float(np.sin(theta_rad)),
                    _wrap_polar_label(str(labels[item_idx])),
                    rotation=float(_upright_tangent_rotation(float(theta_mid))),
                    rotation_mode="anchor",
                    ha="center",
                    va="center",
                    fontsize=item_fs,
                    linespacing=0.92,
                    zorder=4,
                )
                cursor += float(item_span) + float(item_gap_degrees)
            group_theta1 = float(cursor - item_gap_degrees + group_gap_degrees * 0.5)
            group_ranges.append((str(g_name), float(group_theta0), float(group_theta1)))
            cursor += float(group_gap_degrees)

        for g_name, theta0, theta1 in group_ranges:
            group_color = str(group_palette[group_lookup[g_name] % len(group_palette)])
            ring = Wedge(
                (0.0, 0.0),
                r=float(inner_radius + group_ring_width),
                theta1=float(theta0),
                theta2=float(theta1),
                width=float(group_ring_width),
                facecolor=group_color,
                edgecolor="white",
                linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
                zorder=2,
            )
            ax.add_patch(ring)
            theta_mid = 0.5 * (float(theta0) + float(theta1))
            theta_rad = np.deg2rad(float(theta_mid))
            radius = float(inner_radius) + float(group_ring_width) * 0.5
            ax.text(
                radius * float(np.cos(theta_rad)),
                radius * float(np.sin(theta_rad)),
                _wrap_polar_label(str(g_name)),
                rotation=float(_upright_tangent_rotation(float(theta_mid))),
                rotation_mode="anchor",
                ha="center",
                va="center",
                fontsize=group_fs,
                linespacing=0.92,
                zorder=4,
            )
            group_handle_map[g_name] = Patch(facecolor=group_color, edgecolor="none", label=str(g_name))

        if title:
            title_above(ax, str(title), y=1.04)
        if bool(legend_show):
            legend1 = ax.legend(
                handles=stack_handles,
                frameon=False,
                ncol=min(4, max(1, len(stack_handles))),
                loc="lower left",
                bbox_to_anchor=(-0.02, -0.08),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
                columnspacing=0.6,
                handletextpad=0.35,
                title="Peptides per protein",
            )
            try:
                legend1.set_in_layout(True)
            except Exception:
                pass
            ax.add_artist(legend1)
            if bool(group_legend_show):
                legend2 = ax.legend(
                    handles=list(group_handle_map.values()),
                    frameon=False,
                    ncol=min(5, max(1, len(group_handle_map))),
                    loc="lower center",
                    bbox_to_anchor=(0.64, -0.08),
                    prop={"family": t.font_family, "size": float(t.legend_font_size)},
                    columnspacing=0.6,
                    handletextpad=0.35,
                )
                try:
                    legend2.set_in_layout(True)
                except Exception:
                    pass

        lim = float(bar_inner_radius) + float(bar_max_height) + float(outer_label_offset) + 0.14
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.axis("off")
        fig.tight_layout()
        return fig


def circular_grouped_bar(
    values: np.ndarray,
    *,
    item_labels: Sequence[str],
    item_groups: Sequence[str],
    series_labels: Optional[Sequence[str]] = None,
    series_colors: Optional[Sequence[str]] = None,
    group_colors: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    start_angle: float = 90.0,
    inner_radius: float = 0.28,
    group_ring_width: float = 0.08,
    bar_inner_radius: float = 0.39,
    bar_max_height: float = 0.42,
    item_gap_degrees: float = 0.18,
    group_gap_degrees: float = 4.8,
    series_gap_degrees: float = 0.05,
    outer_label_offset: float = 0.03,
    group_label_font_size: Optional[int] = 5,
    item_label_font_size: Optional[int] = 4,
    legend_show: bool = False,
    legend_ncol: Optional[int] = None,
    show_group_labels: bool = True,
    show_value_labels: bool = False,
    value_label_font_size: Optional[int] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = 780,
    height: Optional[int] = 780,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a circular grouped bar chart with an inner group ring."""
    arr = np.asarray(values, dtype=float)
    if arr.ndim == 1:
        arr = arr[:, None]
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError("values must be a 2D numpy array with shape (n_items, n_series)")
    if np.any(arr < 0):
        raise ValueError("values must be non-negative")
    n_items, n_series = arr.shape
    labels = [str(item) for item in item_labels]
    if len(labels) != n_items:
        raise ValueError("item_labels must match the number of rows in values")
    groups = [str(item) for item in item_groups]
    if len(groups) != n_items:
        raise ValueError("item_groups must match the number of rows in values")
    series = [str(item) for item in series_labels] if series_labels is not None else [f"S{idx + 1}" for idx in range(n_series)]
    if len(series) != int(n_series):
        raise ValueError("series_labels must match the number of columns in values")

    group_names, group_starts, group_counts = _ordered_group_blocks(groups)
    series_palette = normalize_palette(series_colors, fallback=["#EFD2A2", "#E7AA78", "#AFC6D4", "#6E88AA"])
    group_palette = normalize_palette(group_colors, fallback=["#D97C6C", "#D9A56C", "#90AFC5", "#78A58E"])
    max_value = float(np.max(arr))
    if max_value <= 0:
        raise ValueError("At least one entry in values must be positive")

    total_item_gap = float(item_gap_degrees) * float(n_items)
    total_group_gap = float(group_gap_degrees) * float(len(group_names))
    usable = 360.0 - total_item_gap - total_group_gap
    if usable <= 0:
        raise ValueError("Too many items or too much angular gap for a circular grouped bar plot")
    item_span = usable / float(n_items)
    total_series_gap = max(0.0, float(n_series - 1)) * float(series_gap_degrees)
    bar_span = (float(item_span) - float(total_series_gap)) / float(n_series)
    if bar_span <= 0:
        raise ValueError("series_gap_degrees is too large for the number of grouped series")

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        ax.set_aspect("equal")
        group_fs = int(group_label_font_size) if group_label_font_size is not None else max(7, int(t.axis.tick_font_size) - 2)
        item_fs = int(item_label_font_size) if item_label_font_size is not None else max(6, int(t.axis.tick_font_size) - 3)
        value_fs = int(value_label_font_size) if value_label_font_size is not None else max(6, int(t.axis.tick_font_size) - 3)
        series_handles = [Patch(facecolor=series_palette[idx % len(series_palette)], edgecolor="none", label=str(series[idx])) for idx in range(n_series)]

        group_lookup = {name: idx for idx, name in enumerate(group_names)}
        cursor = float(start_angle)
        group_ranges: list[tuple[str, float, float]] = []
        for g_name, g_start, g_count in zip(group_names, group_starts, group_counts, strict=True):
            group_theta0 = float(cursor)
            for local_item_idx in range(int(g_count)):
                item_idx = int(g_start + local_item_idx)
                item_theta0 = float(cursor + item_gap_degrees * 0.5)
                item_theta1 = float(item_theta0 + item_span)
                theta_mid = 0.5 * (float(item_theta0) + float(item_theta1))
                theta_rad = np.deg2rad(float(theta_mid))
                series_cursor = float(item_theta0)
                for series_idx in range(n_series):
                    theta0 = float(series_cursor)
                    theta1 = float(theta0 + bar_span)
                    series_cursor = float(theta1 + float(series_gap_degrees))
                    height = float(bar_max_height) * float(arr[item_idx, series_idx]) / float(max_value)
                    patch = Wedge(
                        (0.0, 0.0),
                        r=float(bar_inner_radius + height),
                        theta1=float(theta0),
                        theta2=float(theta1),
                        width=float(height),
                        facecolor=series_palette[series_idx % len(series_palette)],
                        edgecolor="white",
                        linewidth=max(float(t.axis.line_width) * 0.35, 0.28),
                        zorder=3,
                    )
                    ax.add_patch(patch)

                label_radius = float(bar_inner_radius) + float(bar_max_height) + float(outer_label_offset)
                ax.text(
                    label_radius * float(np.cos(theta_rad)),
                    label_radius * float(np.sin(theta_rad)),
                    _wrap_polar_label(str(labels[item_idx])),
                    rotation=float(_upright_tangent_rotation(float(theta_mid))),
                    rotation_mode="anchor",
                    ha="center",
                    va="center",
                    fontsize=item_fs,
                    linespacing=0.92,
                    zorder=4,
                )
                if bool(show_value_labels):
                    value_radius = float(bar_inner_radius + float(bar_max_height) + 0.02)
                    ax.text(
                        value_radius * float(np.cos(theta_rad)),
                        value_radius * float(np.sin(theta_rad)),
                        f"{float(np.max(arr[item_idx])):.0f}",
                        rotation=float(_upright_tangent_rotation(float(theta_mid))),
                        rotation_mode="anchor",
                        ha="center",
                        va="center",
                        fontsize=value_fs,
                        zorder=4,
                    )
                cursor += float(item_span) + float(item_gap_degrees)
            group_theta1 = float(cursor - item_gap_degrees + group_gap_degrees * 0.5)
            group_ranges.append((str(g_name), float(group_theta0), float(group_theta1)))
            cursor += float(group_gap_degrees)

        for g_name, theta0, theta1 in group_ranges:
            group_color = str(group_palette[group_lookup[g_name] % len(group_palette)])
            ring = Wedge(
                (0.0, 0.0),
                r=float(inner_radius + group_ring_width),
                theta1=float(theta0),
                theta2=float(theta1),
                width=float(group_ring_width),
                facecolor=group_color,
                edgecolor="white",
                linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
                zorder=2,
            )
            ax.add_patch(ring)
            if bool(show_group_labels):
                theta_mid = 0.5 * (float(theta0) + float(theta1))
                theta_rad = np.deg2rad(float(theta_mid))
                radius = float(inner_radius) + float(group_ring_width) * 0.5
                ax.text(
                    radius * float(np.cos(theta_rad)),
                    radius * float(np.sin(theta_rad)),
                    _wrap_polar_label(str(g_name)),
                    rotation=float(_upright_tangent_rotation(float(theta_mid))),
                    rotation_mode="anchor",
                    ha="center",
                    va="center",
                    fontsize=group_fs,
                    linespacing=0.92,
                    zorder=4,
                )

        if title:
            title_above(ax, str(title), y=1.04)
        if bool(legend_show):
            legend = ax.legend(
                handles=series_handles,
                frameon=False,
                ncol=int(legend_ncol) if legend_ncol is not None else min(4, max(1, len(series_handles))),
                loc="lower center",
                bbox_to_anchor=(0.5, -0.04),
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
                handlelength=1.0,
                columnspacing=0.7,
                handletextpad=0.4,
            )
            try:
                legend.set_in_layout(True)
            except Exception:
                pass

        lim = float(bar_inner_radius) + float(bar_max_height) + float(outer_label_offset) + 0.14
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.axis("off")
        fig.tight_layout()
        return fig


__all__ = ["radial_hierarchy", "circular_stacked_bar", "circular_grouped_bar"]
