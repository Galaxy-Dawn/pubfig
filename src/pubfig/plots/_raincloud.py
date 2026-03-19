"""Raincloud plot (Matplotlib)."""

from __future__ import annotations

from typing import Literal, Optional, Sequence, TYPE_CHECKING

import numpy as np
from scipy.stats import gaussian_kde

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import apply_cartesian_axis_controls, coerce_linewidth, coerce_marker_size, normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba, darken_color
from ..themes import Theme, theme_context
from ._distribution_utils import normalize_features

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _resolve_half(orientation: str, half: Optional[str]) -> str:
    if half is None:
        return "upper" if orientation == "vertical" else "right"

    resolved = str(half).lower()
    allowed = {"vertical": {"upper", "lower"}, "horizontal": {"left", "right"}}
    if resolved not in allowed[orientation]:
        raise ValueError(f"half must be one of {sorted(allowed[orientation])} for orientation={orientation!r}.")
    return resolved


def _default_point_offset(orientation: str, half: str, violin_width: float) -> float:
    if orientation == "vertical":
        return -0.18 if half == "upper" else 0.18
    return -0.18 if half == "right" else 0.18


def _kde_profile(
    feature: np.ndarray,
    *,
    violin_points: int,
    violin_bandwidth_method: Optional[float | str],
    violin_support_extend_ratio: float,
) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray(feature, dtype=float).ravel()
    if values.size == 0:
        return np.array([], dtype=float), np.array([], dtype=float)

    value_min = float(np.min(values))
    value_max = float(np.max(values))
    span = max(value_max - value_min, 1e-6)
    pad = span * float(violin_support_extend_ratio)
    support = np.linspace(value_min - pad, value_max + pad, int(violin_points))

    if values.size < 2 or np.allclose(values, values[0]):
        density = np.exp(-0.5 * ((support - float(np.mean(values))) / max(span * 0.2, 1e-6)) ** 2)
        return support, density

    try:
        kde = gaussian_kde(values, bw_method=violin_bandwidth_method)
        density = kde(support)
    except Exception:
        density = np.exp(-0.5 * ((support - float(np.mean(values))) / max(span * 0.2, 1e-6)) ** 2)
    return support, np.asarray(density, dtype=float)


def raincloud(
    data,
    *,
    category_names: Optional[list[str]] = None,
    category_spacing: float = 0.8,
    orientation: Literal["vertical", "horizontal"] = "vertical",
    half: Optional[Literal["upper", "lower", "left", "right"]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    show_violin: bool = True,
    show_box: bool = True,
    show_points: bool = True,
    violin_width: float = 0.52,
    violin_points: int = 200,
    violin_bandwidth_method: Optional[float | str] = None,
    violin_support_extend_ratio: float = 0.12,
    violin_face_alpha: float = 0.24,
    violin_edge_line_width: Optional[float] = None,
    box_width: float = 0.14,
    box_offset: float = 0.0,
    box_facecolor: str = "white",
    box_edgecolor: str = "black",
    box_line_width: Optional[float] = None,
    box_show_fliers: bool = False,
    points_random_seed: int = 0,
    points_jitter: float = 0.08,
    points_offset: Optional[float] = None,
    points_size: Optional[float] = None,
    points_marker: str = "o",
    points_alpha: float = 0.52,
    points_edgecolor: str = "none",
    points_edge_line_width: float = 0.0,
    points_color_mode: Literal["same", "gray"] = "same",
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a raincloud plot combining half-violin, boxplot, and jittered raw points."""
    features = normalize_features(data)
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    if category_names is None:
        category_names = [f"Category {idx + 1}" for idx in range(len(features))]

    positions = np.arange(len(features), dtype=float) * float(category_spacing) + 1.0
    resolved_half = _resolve_half(str(orientation), half)
    resolved_points_offset = (
        _default_point_offset(str(orientation), resolved_half, float(violin_width))
        if points_offset is None
        else float(points_offset)
    )

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_points_size = (
            float(coerce_marker_size(t, kind="scatter")) * 0.58 if points_size is None else float(points_size)
        )
        resolved_violin_edge_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.72
            if violin_edge_line_width is None
            else float(violin_edge_line_width)
        )
        resolved_box_line_width = (
            float(coerce_linewidth(t, kind="axis")) * 0.88 if box_line_width is None else float(box_line_width)
        )
        rng = np.random.default_rng(int(points_random_seed))
        half_width = float(violin_width) / 2.0

        for idx, feature in enumerate(features):
            feat = np.asarray(feature, dtype=float).ravel()
            if feat.size == 0:
                continue

            pos = float(positions[idx])
            color = colors[idx % len(colors)]

            if bool(show_violin):
                support, density_vals = _kde_profile(
                    feat,
                    violin_points=int(violin_points),
                    violin_bandwidth_method=violin_bandwidth_method,
                    violin_support_extend_ratio=float(violin_support_extend_ratio),
                )
                density_peak = float(np.max(density_vals)) if density_vals.size else 1.0
                profile = half_width * (density_vals / max(density_peak, 1e-9))

                if orientation == "vertical":
                    if resolved_half == "upper":
                        start, end = np.full_like(profile, pos), pos + profile
                    else:
                        start, end = pos - profile, np.full_like(profile, pos)
                    ax.fill_betweenx(
                        support,
                        start,
                        end,
                        facecolor=color_to_rgba(color, alpha=float(violin_face_alpha)),
                        edgecolor=color,
                        linewidth=resolved_violin_edge_line_width,
                    )
                else:
                    if resolved_half == "right":
                        start, end = np.full_like(profile, pos), pos + profile
                    else:
                        start, end = pos - profile, np.full_like(profile, pos)
                    ax.fill_between(
                        support,
                        start,
                        end,
                        facecolor=color_to_rgba(color, alpha=float(violin_face_alpha)),
                        edgecolor=color,
                        linewidth=resolved_violin_edge_line_width,
                    )

            if bool(show_points):
                jitter = rng.uniform(-float(points_jitter), float(points_jitter), size=feat.size)
                scatter_color = (
                    color_to_rgba("0.35", alpha=float(points_alpha))
                    if points_color_mode == "gray"
                    else color_to_rgba(darken_color(color, factor=0.78), alpha=float(points_alpha))
                )
                if orientation == "vertical":
                    ax.scatter(
                        np.full(feat.size, pos + resolved_points_offset, dtype=float) + jitter,
                        feat,
                        s=resolved_points_size**2,
                        marker=str(points_marker),
                        color=scatter_color,
                        edgecolor=points_edgecolor,
                        linewidth=float(points_edge_line_width),
                        zorder=3,
                    )
                else:
                    ax.scatter(
                        feat,
                        np.full(feat.size, pos + resolved_points_offset, dtype=float) + jitter,
                        s=resolved_points_size**2,
                        marker=str(points_marker),
                        color=scatter_color,
                        edgecolor=points_edgecolor,
                        linewidth=float(points_edge_line_width),
                        zorder=3,
                    )

        if bool(show_box):
            box_positions = positions + float(box_offset)
            bp = ax.boxplot(
                features,
                patch_artist=True,
                widths=float(box_width),
                showfliers=bool(box_show_fliers),
                positions=box_positions,
                orientation=str(orientation),
            )
            for patch in bp["boxes"]:
                patch.set_facecolor(box_facecolor)
                patch.set_edgecolor(box_edgecolor)
                patch.set_linewidth(resolved_box_line_width)
            for key in ("whiskers", "caps", "medians"):
                for item in bp.get(key, []):
                    item.set_color(box_edgecolor)
                    item.set_linewidth(resolved_box_line_width)

        categorical_margin = max(
            0.32,
            half_width + abs(float(resolved_points_offset)) + float(points_jitter) + 0.08,
        )
        if orientation == "vertical":
            ax.set_xticks(positions, labels=category_names)
            ax.set_xlim(float(positions[0] - categorical_margin), float(positions[-1] + categorical_margin))
            ax.set_ylabel("Value")
            ax.set_xlabel("")
        else:
            ax.set_yticks(positions, labels=category_names)
            ax.set_ylim(float(positions[0] - categorical_margin), float(positions[-1] + categorical_margin))
            ax.set_xlabel("Value")
            ax.set_ylabel("")

        if title:
            title_above(ax, title, y=1.06)

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
