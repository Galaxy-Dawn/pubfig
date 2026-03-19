"""Radar plot functions (Matplotlib)."""

from __future__ import annotations

from textwrap import fill
from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import normalize_palette
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def radar(
    data: list[list[float]],
    *,
    categories: Optional[list[str]] = None,
    series_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    line_width: float = 0.78,
    fill_alpha: float = 0.10,
    marker: Optional[str] = "o",
    marker_size: float = 2.2,
    marker_edge_line_width: float = 0.55,
    theta_offset: float = float(np.pi / 2),
    theta_direction: int = -1,
    grid: bool = True,
    ring_grid_linestyle: str = "--",
    ring_grid_line_width: float = 0.55,
    ring_grid_color: str = "0.78",
    spoke_grid_linestyle: str = "--",
    spoke_grid_line_width: float = 0.5,
    spoke_grid_color: str = "0.80",
    outer_ring_color: str = "black",
    outer_ring_line_width: float = 0.72,
    radial_tick_values: Optional[Sequence[float]] = None,
    radial_tick_decimals: Optional[int] = None,
    radial_label_angle: float = 15.0,
    category_label_pad: float = 3.0,
    category_label_mode: str = "tangent",
    category_label_wrap_width: Optional[int] = None,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 4,
    title_pad: float = 7.0,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a radar chart.

    Args:
        data: Sequence of series; each inner list must match the number of categories.
        categories: Axis labels around the radar.
        series_names: Labels for each radar series.
        title: Optional plot title.
        color_palette: Optional palette used for the series.
        line_width: Outline line width for each series.
        fill_alpha: Alpha for the filled area under each series polygon.
        marker: Optional marker used at category vertices. If None, markers are hidden.
        marker_size: Marker size in points.
        marker_edge_line_width: Marker edge line width in points.
        theta_offset: Polar theta offset in radians (pi/2 puts 0 at the top).
        theta_direction: Theta direction (+1 counterclockwise, -1 clockwise).
        grid: Whether to show grid lines.
        ring_grid_linestyle: Radial ring grid line style.
        ring_grid_line_width: Radial ring grid line width (points).
        ring_grid_color: Radial ring grid line color.
        spoke_grid_linestyle: Spoke grid line style.
        spoke_grid_line_width: Spoke grid line width (points).
        spoke_grid_color: Spoke grid line color.
        outer_ring_color: Color of the outer polar spine.
        outer_ring_line_width: Line width of the outer polar spine.
        radial_tick_values: Explicit radial tick values. If None, inferred from the data range.
        radial_tick_decimals: Explicit decimals for radial tick labels. If None, inferred from the scale.
        radial_label_angle: Polar angle in degrees used to place radial tick labels.
        category_label_pad: Padding between the outer ring and category labels. Smaller values place labels closer to the outer spokes.
        category_label_mode: Category label orientation mode. Use "horizontal" (or alias "horizon")
            for upright labels, or "tangent" for labels perpendicular to the corresponding spoke.
        category_label_wrap_width: Optional line width for wrapping category labels. If None, labels stay on one line.
        legend_show: Whether to draw the legend.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns (only used when `legend_ncol` is None).
        title_pad: Vertical padding between the highest category label and the title, in points.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    if not data:
        raise ValueError("data must be a non-empty list of series")

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    n_axes = len(data[0])
    if categories is None:
        categories = [f"Category {i + 1}" for i in range(n_axes)]
    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(len(data))]

    theta = np.linspace(0, 2 * np.pi, n_axes, endpoint=False)
    theta_closed = np.concatenate([theta, theta[:1]])
    data_arr = np.asarray(data, dtype=float)
    if data_arr.ndim != 2:
        raise ValueError("data must be a 2D sequence with shape (n_series, n_categories)")
    if len(categories) != n_axes:
        raise ValueError("categories must match the number of values in each series")
    if len(series_names) != len(data_arr):
        raise ValueError("series_names must match the number of series")

    def _resolve_default_radial_ticks(r_max_value: float) -> np.ndarray:
        return np.asarray([0.25, 0.50, 0.75], dtype=float) * float(r_max_value)

    def _normalize_tangent_rotation(display_angle_deg: float) -> float:
        rotation = float(display_angle_deg - 90.0)
        while rotation <= -180.0:
            rotation += 360.0
        while rotation > 180.0:
            rotation -= 360.0
        if rotation > 90.0:
            rotation -= 180.0
        elif rotation < -90.0:
            rotation += 180.0
        return rotation

    def _horizontal_label_offset_points(display_angle_deg: float) -> tuple[float, float]:
        angle = np.deg2rad(float(display_angle_deg))
        radial_gap = 8.0 + 1.8 * float(category_label_pad)
        dx = radial_gap * float(np.cos(angle))
        dy = radial_gap * float(np.sin(angle))
        return float(dx), float(dy)

    def _resolve_horizontal_text_alignment(display_angle_deg: float) -> tuple[str, str]:
        angle = np.deg2rad(float(display_angle_deg))
        cos_v = float(np.cos(angle))
        sin_v = float(np.sin(angle))
        ha = "left" if cos_v > 0.3 else "right" if cos_v < -0.3 else "center"
        va = "bottom" if sin_v > 0.3 else "top" if sin_v < -0.3 else "center"
        return ha, va

    def _wrap_category_label(label: str) -> str:
        if category_label_wrap_width is None:
            return label
        return fill(label, width=max(1, int(category_label_wrap_width)))

    def _style_category_labels() -> None:
        mode = str(category_label_mode).strip().lower()
        if mode == "horizon":
            mode = "horizontal"
        if mode not in {"horizontal", "tangent"}:
            raise ValueError("category_label_mode must be 'horizontal', 'horizon', or 'tangent'")

        ax.set_xticks(theta, labels=[""] * len(categories))
        setattr(ax, "_pubfig_category_label_mode", mode)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi, projection="polar")

        ax.set_theta_offset(float(theta_offset))
        ax.set_theta_direction(int(theta_direction))

        r_max = max(1.0, float(np.max(data_arr)) * 1.08)
        radial_ticks = (
            np.asarray(radial_tick_values, dtype=float)
            if radial_tick_values is not None
            else _resolve_default_radial_ticks(r_max)
        )
        resolved_tick_decimals = (
            int(radial_tick_decimals)
            if radial_tick_decimals is not None
            else (2 if r_max <= 1.0 else 1)
        )

        handles = []
        labels = []
        for idx, row in enumerate(data_arr):
            r = np.asarray(row, dtype=float)
            if r.size != n_axes:
                raise ValueError("All series must have the same length as categories")
            r_closed = np.concatenate([r, r[:1]])
            c = colors[idx % len(colors)]
            line_kwargs: dict[str, object] = {
                "color": c,
                "linewidth": float(line_width),
                "label": series_names[idx],
                "zorder": 3,
            }
            marker_enabled = marker is not None and str(marker).lower() not in {"", "none", "null"}
            if marker_enabled:
                line_kwargs.update(
                    {
                        "marker": str(marker),
                        "markersize": float(marker_size),
                        "markerfacecolor": c,
                        "markeredgecolor": c,
                        "markeredgewidth": float(marker_edge_line_width),
                    }
                )
            line = ax.plot(
                theta_closed,
                r_closed,
                **line_kwargs,
            )[0]
            ax.fill(
                theta_closed,
                r_closed,
                color=color_to_rgba(c, alpha=float(fill_alpha)),
                linewidth=0.0,
                zorder=2,
            )
            handles.append(line)
            labels.append(str(series_names[idx]))

        ax.tick_params(axis="x", pad=float(category_label_pad))
        ax.set_ylim(0.0, r_max)
        ax.set_yticks(radial_ticks)
        ax.set_yticklabels([f"{tick:.{resolved_tick_decimals}f}" for tick in radial_ticks])
        ax.set_rlabel_position(float(radial_label_angle))
        legend = None
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(data_arr), int(legend_ncol_max)))
            legend = fig.legend(
                handles,
                labels,
                frameon=False,
                ncol=int(ncol),
                loc="lower center",
                bbox_to_anchor=(0.5, 0.03),
                handlelength=2.1,
                columnspacing=1.0,
                handletextpad=0.4,
                prop={"family": t.font_family, "size": float(t.legend_font_size)},
            )
            try:
                legend.set_in_layout(True)
            except Exception:
                pass
            try:
                legend.set_zorder(10)
            except Exception:
                pass

        t.apply_axes(ax)
        show_spoke_grid = bool(grid) and float(spoke_grid_line_width) > 0.0 and str(spoke_grid_color).lower() != "none"
        if show_spoke_grid:
            ax.xaxis.grid(
                True,
                linestyle=str(spoke_grid_linestyle),
                linewidth=float(spoke_grid_line_width),
                color=str(spoke_grid_color),
                alpha=1.0,
            )
        else:
            ax.xaxis.grid(False)
        ax.yaxis.grid(
            bool(grid),
            linestyle=str(ring_grid_linestyle),
            linewidth=float(ring_grid_line_width),
            color=str(ring_grid_color),
            alpha=1.0,
        )
        ax.spines["polar"].set_color(str(outer_ring_color))
        ax.spines["polar"].set_linewidth(float(outer_ring_line_width))
        ax.set_facecolor("#FCFCFD")
        ax.tick_params(axis="y", pad=0.6, length=0.0)
        ax.tick_params(axis="x", length=0.0)
        for tick in ax.get_yticklabels():
            tick.set_fontsize(max(5, int(t.axis.tick_font_size) - 1))
            tick.set_color("0.45")
        _style_category_labels()

        def _render_category_labels() -> None:
            for text in getattr(ax, "_pubfig_category_texts", []):
                try:
                    text.remove()
                except Exception:
                    pass

            mode = getattr(ax, "_pubfig_category_label_mode", "horizontal")
            label_radius = float(r_max) * 1.002
            texts = []
            renderer = fig.canvas.get_renderer()
            _ = renderer

            for angle_rad, label in zip(theta, categories):
                display_angle = (np.degrees(float(theta_offset) + float(theta_direction) * angle_rad)) % 360.0
                rotation = 0.0
                ha = "center"
                va = "center"
                if mode == "tangent":
                    rotation = _normalize_tangent_rotation(display_angle)
                    angle = np.deg2rad(float(display_angle))
                    radial_gap = 7.0 + 1.5 * float(category_label_pad)
                    offset_points = (
                        float(radial_gap * np.cos(angle)),
                        float(radial_gap * np.sin(angle)),
                    )
                else:
                    offset_points = _horizontal_label_offset_points(display_angle)
                    ha, va = _resolve_horizontal_text_alignment(display_angle)

                anchor_disp = ax.transData.transform((float(angle_rad), float(label_radius)))
                dx_px = float(offset_points[0]) * float(fig.dpi) / 72.0
                dy_px = float(offset_points[1]) * float(fig.dpi) / 72.0
                x_fig, y_fig = fig.transFigure.inverted().transform((anchor_disp[0] + dx_px, anchor_disp[1] + dy_px))

                text = fig.text(
                    float(x_fig),
                    float(y_fig),
                    _wrap_category_label(str(label)),
                    ha=ha,
                    va=va,
                    rotation=rotation,
                    rotation_mode="anchor" if mode == "tangent" else None,
                    color=str(t.font_color),
                    fontsize=max(6, int(t.axis.tick_font_size)),
                    fontfamily=t.font_family,
                    zorder=10,
                )
                texts.append(text)

            setattr(ax, "_pubfig_category_texts", texts)

        def _render_title() -> None:
            existing = getattr(ax, "_pubfig_title_text", None)
            if existing is not None:
                try:
                    existing.remove()
                except Exception:
                    pass
                setattr(ax, "_pubfig_title_text", None)

            if not title:
                return

            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            category_texts = getattr(ax, "_pubfig_category_texts", [])
            highest_label_top = max(
                (
                    fig.transFigure.inverted().transform_bbox(text.get_window_extent(renderer=renderer)).y1
                    for text in category_texts
                ),
                default=0.94,
            )
            title_y = min(0.992, float(highest_label_top) + (float(title_pad) / 72.0 / float(fig.get_figheight())))
            title_text = fig.text(
                0.5,
                float(title_y),
                str(title),
                ha="center",
                va="bottom",
                color=str(t.font_color),
                fontsize=float(t.title_font_size),
                fontfamily=t.font_family,
                fontweight="semibold",
                zorder=11,
            )
            setattr(ax, "_pubfig_title_text", title_text)

        def _apply_radar_layout() -> None:
            top = 0.84 if title else 0.92
            bottom = 0.19 if legend is not None else 0.08
            available_width = 0.78
            available_height = max(0.10, top - bottom)
            side = min(float(available_width), float(available_height))
            x0 = 0.5 - side / 2.0
            y0 = bottom + (available_height - side) / 2.0
            ax.set_position([x0, y0, side, side])
            if legend is not None:
                legend.set_bbox_to_anchor((0.5, 0.045), transform=fig.transFigure)
            fig.canvas.draw()
            _render_category_labels()
            _render_title()

        setattr(ax, "_pubfig_post_layout", _apply_radar_layout)
        try:
            fig.tight_layout()
        except Exception:
            pass
        _apply_radar_layout()
        return fig
