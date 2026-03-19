"""Distribution plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
from scipy.stats import gaussian_kde

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
from ._distribution_utils import normalize_features
from ._raincloud import raincloud  # noqa: F401

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

def box(
    data,
    *,
    category_names: Optional[list[str]] = None,
    category_spacing: float = 0.75,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    box_edge_color: Optional[str] = None,
    box_face_color: Optional[str] = None,
    box_face_alpha: float = 0.5,
    box_width: float = 0.5,
    cap_widths: Optional[float] = None,
    line_color: str = "black",
    line_width: Optional[float] = None,
    median_line_width: Optional[float] = None,
    show_means: bool = False,
    mean_marker: str = "D",
    mean_marker_size: float = 4.0,
    mean_marker_face_color: str = "white",
    mean_marker_edge_color: str = "black",
    mean_marker_edge_line_width: float = 0.5,
    show_fliers: bool = True,
    flier_marker: str = "o",
    flier_marker_size: float = 3.0,
    flier_face_color: str = "white",
    flier_edge_color: str = "black",
    flier_edge_line_width: float = 0.5,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create box plots for one or more features.

    Args:
        data: 1D array, 2D array (n_samples, n_features), or list of 1D arrays.
        category_names: Optional category labels shown on the categorical axis.
        category_spacing: Distance between adjacent categorical groups in axis units.
            Use values below 1.0 for a denser, more compact layout.
        title: Optional plot title.
        color_palette: Optional list of colors (one per feature). Falls back to default palette.
        box_edge_color: Color for the box outline. If None, uses a darker version of each box fill color.
        box_face_color: If set, force all boxes to use this face color (overrides `color_palette`).
        box_face_alpha: Alpha for the box fill.
        box_width: Width of each box in categorical-axis units.
        cap_widths: Width of whisker cap lines in categorical-axis units. If None,
            derives from `box_width` to keep cap lines compact.
        line_color: Color for whiskers/caps/medians/means.
        line_width: Line width (points) for all box components. If None, uses theme axis line width.
        median_line_width: Optional median line width override. If None, uses `line_width`.
        show_means: Whether to show the mean marker in the boxplot.
        mean_marker: Marker style used for the mean point.
        mean_marker_size: Marker size in points for the mean point.
        mean_marker_face_color: Marker face color for the mean point.
        mean_marker_edge_color: Marker edge color for the mean point.
        mean_marker_edge_line_width: Marker edge width for the mean point.
        show_fliers: Whether to show outlier points beyond the whiskers.
        flier_marker: Marker style used for outliers.
        flier_marker_size: Marker size in points for outliers.
        flier_face_color: Marker face color for outliers.
        flier_edge_color: Marker edge color for outliers.
        flier_edge_line_width: Marker edge width for outliers.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    features = normalize_features(data)
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    if category_names is None:
        category_names = [f"Category {i + 1}" for i in range(len(features))]
    positions = np.arange(len(features), dtype=float) * float(category_spacing) + 1.0

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        edge_lw = float(coerce_linewidth(t, kind="axis")) * 0.85 if line_width is None else float(line_width)
        resolved_median_line_width = float(edge_lw if median_line_width is None else median_line_width)
        resolved_cap_widths = float(box_width) * 0.38 if cap_widths is None else float(cap_widths)
        bp = ax.boxplot(
            features,
            patch_artist=True,
            showmeans=bool(show_means),
            showfliers=bool(show_fliers),
            widths=float(box_width),
            capwidths=float(resolved_cap_widths),
            positions=positions,
            meanprops={
                "marker": str(mean_marker),
                "markerfacecolor": str(mean_marker_face_color),
                "markeredgecolor": str(mean_marker_edge_color),
                "markeredgewidth": float(mean_marker_edge_line_width),
                "markersize": float(mean_marker_size),
            },
            flierprops={
                "marker": str(flier_marker),
                "markerfacecolor": str(flier_face_color),
                "markeredgecolor": str(flier_edge_color),
                "markeredgewidth": float(flier_edge_line_width),
                "markersize": float(flier_marker_size),
                "linestyle": "none",
            },
        )
        for patch, c in zip(bp["boxes"], colors):
            fill_color = c if box_face_color is None else box_face_color
            resolved_box_edge_color = darken_color(fill_color, factor=0.8) if box_edge_color is None else box_edge_color
            patch.set_facecolor(color_to_rgba(fill_color, alpha=float(box_face_alpha)))
            patch.set_edgecolor(resolved_box_edge_color)
            patch.set_linewidth(edge_lw)
        for k in ("whiskers", "caps", "means"):
            for item in bp.get(k, []):
                item.set_color(line_color)
                item.set_linewidth(edge_lw)
        for item in bp.get("medians", []):
            item.set_color(line_color)
            item.set_linewidth(resolved_median_line_width)

        ax.set_xticks(positions, labels=category_names)
        ax.set_xlim(float(positions[0] - 0.5), float(positions[-1] + 0.5))
        if title:
            title_above(ax, title, y=1.06)
        ax.set_ylabel("Value")

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


def density(
    data: np.ndarray,
    *,
    bins: int = 50,
    model: str = "scipy",
    title: Optional[str] = None,
    color_density: Optional[str] = None,
    color_distribution: Optional[str] = None,
    color_histogram: Optional[str] = None,
    fill_alpha: float = 0.16,
    fill_line_width: float = 0.0,
    fill_zorder: int = 1,
    density_line_width: Optional[float] = None,
    density_zorder: int = 2,
    hist_alpha: float = 0.08,
    hist_edgecolor: str = "none",
    hist_zorder: int = 0,
    baseline: float = 0.0,
    y_padding_ratio: float = 1.05,
    color_palette: Optional[Sequence[str]] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a distribution plot with density curve.

    Note:
        `model` is kept for API compatibility; the Matplotlib implementation always uses SciPy KDE.

    Args:
        data: 1D array (or (n, 1)) of samples.
        bins: Number of evaluation points for KDE and number of histogram bins.
        model: Kept for compatibility; SciPy KDE is used internally.
        title: Optional plot title.
        color_density: Fill color under the density curve. Defaults to the first palette color.
        color_distribution: Line color for the density curve. Defaults to the first palette color.
        color_histogram: Histogram bar color. Defaults to the first palette color.
        fill_alpha: Alpha for the filled density area.
        fill_line_width: Outline width for the filled density area (usually 0 for no outline).
        fill_zorder: Z-order for the filled density area.
        density_line_width: Line width for the density curve. If None, derives from the active theme.
        density_zorder: Z-order for the density curve.
        hist_alpha: Alpha for the histogram bars (used as a light backdrop).
        hist_edgecolor: Edge color for histogram bars (use "none" for no border).
        hist_zorder: Z-order for the histogram layer.
        baseline: Y-value used as the baseline for the filled density area.
        y_padding_ratio: Multiplicative headroom above the peak density (e.g., 1.1 = +10%).
        color_palette: Optional palette used when explicit colors are not given.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    if not isinstance(data, np.ndarray):
        raise ValueError("Input data must be an ndarray.")
    if data.ndim == 2 and data.shape[1] == 1:
        data = data.ravel()
    if data.ndim != 1:
        raise ValueError("Input data must be a 1D array or (n, 1).")

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    c = colors[0]
    c_fill = color_density or c
    c_line = color_distribution or darken_color(c, factor=0.82)
    c_hist = color_histogram or c

    min_val, max_val = float(np.min(data)), float(np.max(data))
    kde = gaussian_kde(data)
    density_x = np.linspace(min_val, max_val, int(bins))
    density_y = kde(density_x)
    y_peak = float(np.max(density_y)) if density_y.size else 1.0

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_density_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.72
            if density_line_width is None
            else float(density_line_width)
        )

        ax.fill_between(
            density_x,
            float(baseline),
            density_y,
            color=color_to_rgba(c_fill, alpha=float(fill_alpha)),
            linewidth=float(fill_line_width),
            zorder=int(fill_zorder),
        )
        ax.plot(
            density_x,
            density_y,
            color=c_line,
            linewidth=resolved_density_line_width,
            zorder=int(density_zorder),
        )

        # Light histogram backdrop.
        ax.hist(
            data,
            bins=int(bins),
            density=True,
            color=color_to_rgba(c_hist, alpha=float(hist_alpha)),
            edgecolor=hist_edgecolor,
            zorder=int(hist_zorder),
        )

        ax.set_xlim(min_val, max_val)
        ax.set_ylim(float(baseline), y_peak * float(y_padding_ratio))
        ax.set_xlabel("Value")
        ax.set_ylabel("Density")
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


def ridgeline(
    data,
    *,
    bins: int = 100,
    category_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    offset_step: float = 0.42,
    ridge_fill_alpha: float = 0.2,
    ridge_fill_line_width: float = 0.0,
    ridge_line_width: Optional[float] = None,
    baseline_line_width: Optional[float] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a ridgeline (joy) plot.

    Args:
        data: 1D array, 2D array, or list of 1D arrays (one per ridge).
        bins: Number of evaluation points for each KDE curve.
        category_names: Optional labels for each ridge/category.
        title: Optional plot title.
        color_palette: Optional palette (one color per ridge).
        offset_step: Vertical spacing between adjacent ridges.
        ridge_fill_alpha: Alpha for the filled ridge area.
        ridge_fill_line_width: Outline width for the filled ridge area.
        ridge_line_width: Line width for the ridge outline. If None, derives from the active theme.
        baseline_line_width: Line width for the horizontal baseline at each ridge offset.
            If None, derives from the active theme and keeps baselines lighter than outlines.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    features = normalize_features(data)
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    if category_names is None:
        category_names = [f"Category {i + 1}" for i in range(len(features))]

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_ridge_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.72
            if ridge_line_width is None
            else float(ridge_line_width)
        )
        resolved_baseline_line_width = (
            float(coerce_linewidth(t, kind="axis")) * 0.55
            if baseline_line_width is None
            else float(baseline_line_width)
        )

        offsets = np.arange(len(features)) * float(offset_step)
        n_features = len(features)
        for draw_idx in range(n_features - 1, -1, -1):
            feature = features[draw_idx]
            kde = gaussian_kde(feature)
            dx = np.linspace(float(np.min(feature)), float(np.max(feature)), int(bins))
            dy = kde(dx)
            off = float(offsets[draw_idx])
            c = colors[draw_idx % len(colors)]
            z_base = float(n_features - draw_idx)
            ax.fill_between(
                dx,
                off,
                dy + off,
                color=color_to_rgba(c, alpha=float(ridge_fill_alpha)),
                linewidth=float(ridge_fill_line_width),
                zorder=z_base,
            )
            ax.plot(dx, dy + off, color=c, linewidth=resolved_ridge_line_width, zorder=z_base + 0.2)
            ax.hlines(
                off,
                float(dx.min()),
                float(dx.max()),
                color=c,
                linewidth=resolved_baseline_line_width,
                zorder=z_base + 0.1,
            )

        ax.set_yticks(offsets, labels=category_names)
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


def histogram(
    data: np.ndarray,
    *,
    bins: int = 30,
    show_kde: bool = False,
    normalize: bool = False,
    title: Optional[str] = None,
    hist_alpha: float = 0.36,
    hist_edgecolor: str = "white",
    hist_line_width: float = 0.25,
    kde_points: int = 200,
    kde_line_width: Optional[float] = None,
    kde_label: str = "KDE",
    kde_color: Optional[str] = None,
    kde_color_index: int = 1,
    legend_show: bool = False,
    legend_ncol: int = 1,
    color_palette: Optional[Sequence[str]] = None,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a histogram with optional KDE overlay.

    Args:
        data: 1D array of samples.
        bins: Number of histogram bins.
        show_kde: If True, overlay a KDE curve.
        normalize: If True, normalize histogram to density units.
        title: Optional plot title.
        hist_alpha: Alpha for histogram bars.
        hist_edgecolor: Edge color for histogram bars.
        hist_line_width: Line width (points) for histogram bar edges.
        kde_points: Number of evaluation points for the KDE curve.
        kde_line_width: Line width for the KDE curve. If None, derives from the active theme.
        kde_label: Legend label for the KDE curve.
        kde_color: If set, use this color for the KDE curve; otherwise use `color_palette[kde_color_index]`.
        kde_color_index: Index into `color_palette` used when `kde_color` is not provided.
        legend_show: Whether to draw the legend when KDE is shown.
        legend_ncol: Number of legend columns when KDE is shown.
        color_palette: Optional palette for histogram/KDE colors.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    data = np.asarray(data, dtype=float).ravel()
    colors = normalize_palette(color_palette, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_kde_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.72 if kde_line_width is None else float(kde_line_width)
        )

        ax.hist(
            data,
            bins=int(bins),
            density=bool(normalize),
            color=color_to_rgba(colors[0], alpha=float(hist_alpha)),
            edgecolor=hist_edgecolor,
            linewidth=float(hist_line_width),
        )

        if show_kde and data.size > 1:
            kde = gaussian_kde(data)
            x_kde = np.linspace(float(np.min(data)), float(np.max(data)), int(kde_points))
            y_kde = kde(x_kde)
            if not normalize:
                bin_width = (float(np.max(data)) - float(np.min(data))) / float(bins)
                y_kde = y_kde * len(data) * bin_width
            ax.plot(
                x_kde,
                y_kde,
                color=(
                    kde_color
                    if kde_color is not None
                    else darken_color(colors[int(kde_color_index) % len(colors)], factor=0.82)
                ),
                linewidth=resolved_kde_line_width,
                label=str(kde_label),
            )
            if bool(legend_show):
                legend_below_title(ax, ncol=int(legend_ncol))

        ax.set_xlabel("Value")
        ax.set_ylabel("Density" if normalize else "Count")
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


def strip(
    data,
    *,
    category_names: Optional[list[str]] = None,
    category_spacing: float = 0.75,
    jitter: float = 0.22,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    marker_size: Optional[float] = None,
    marker: str = "o",
    point_alpha: float = 0.64,
    point_edgecolor: str = "white",
    point_edge_line_width: float = 0.25,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    random_seed: int = 42,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a strip plot showing individual data points.

    Args:
        data: 1D array, 2D array, or list of 1D arrays (one group per strip).
        category_names: Optional labels for each categorical group.
        category_spacing: Distance between adjacent categorical groups in axis units.
            Use values below 1.0 for a denser, more compact layout.
        jitter: Horizontal jitter width (in x-axis units) applied to each group.
        title: Optional plot title.
        color_palette: Optional palette (one color per group).
        marker_size: Marker size in points. If None, derives from the active theme.
        marker: Marker style for strip points.
        point_alpha: Alpha for strip points.
        point_edgecolor: Edge color for strip points.
        point_edge_line_width: Line width (points) for point edges.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        random_seed: Random seed used to generate jitter.
        ax: Optional Matplotlib Axes to draw into.
    """
    features = normalize_features(data)
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    if category_names is None:
        category_names = [f"Category {i + 1}" for i in range(len(features))]
    positions = np.arange(len(features), dtype=float) * float(category_spacing)

    rng = np.random.default_rng(int(random_seed))

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_marker_size = (
            float(coerce_marker_size(t, kind="scatter")) * 0.65 if marker_size is None else float(marker_size)
        )

        for idx, feature in enumerate(features):
            x_jitter = rng.uniform(-float(jitter) / 2, float(jitter) / 2, len(feature))
            ax.scatter(
                np.full(len(feature), positions[idx], dtype=float) + x_jitter,
                feature,
                s=resolved_marker_size**2,
                marker=str(marker),
                color=color_to_rgba(colors[idx % len(colors)], alpha=float(point_alpha)),
                edgecolor=point_edgecolor,
                linewidth=float(point_edge_line_width),
            )

        ax.set_xticks(positions, labels=category_names)
        ax.set_xlim(float(positions[0] - 0.35), float(positions[-1] + 0.35))
        ax.set_ylabel("Value")
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


def violin(
    data,
    *,
    category_names: Optional[list[str]] = None,
    category_spacing: float = 0.75,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    show_box: bool = True,
    show_points: bool = False,
    show_violin_means: bool = False,
    show_violin_extrema: bool = False,
    show_violin_medians: bool = False,
    violin_width: float = 0.56,
    violin_points: int = 200,
    violin_bandwidth_method: Optional[float | str] = None,
    violin_support_extend_ratio: float = 0.12,
    violin_face_alpha: float = 0.22,
    violin_edge_line_width: float = 0.8,
    violin_center_line_color: str = "black",
    violin_center_line_width: float = 0.7,
    box_width: float = 0.15,
    box_facecolor: str = "white",
    box_edgecolor: str = "black",
    box_line_width: float = 0.75,
    box_show_fliers: bool = False,
    points_random_seed: int = 0,
    points_jitter: float = 0.08,
    points_size: Optional[float] = None,
    points_marker: str = "o",
    points_alpha: float = 0.5,
    points_edgecolor: str = "white",
    points_edge_line_width: float = 0.2,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create violin plots.

    Args:
        data: 1D array, 2D array, or list of 1D arrays.
        category_names: Optional labels for each violin/category.
        category_spacing: Distance between adjacent categorical groups in axis units.
            Use values below 1.0 for a denser, more compact layout.
        title: Optional plot title.
        color_palette: Optional palette (one color per violin).
        show_box: If True, overlay a compact boxplot within each violin.
        show_points: If True, overlay jittered raw points.
        show_violin_means: Whether to draw a horizontal mean line inside each violin.
        show_violin_extrema: Whether to draw horizontal min/max lines inside each violin.
        show_violin_medians: Whether to draw a horizontal median line inside each violin.
        violin_width: Maximum full width of each violin in categorical-axis units.
        violin_points: Number of evaluation points used for the violin KDE support.
        violin_bandwidth_method: Bandwidth passed to `scipy.stats.gaussian_kde`.
            Accepts the same values as `bw_method`.
        violin_support_extend_ratio: Fraction of the data range added to both ends of the
            KDE support so violin tails taper smoothly instead of looking clipped.
        violin_face_alpha: Alpha for the violin body fill.
        violin_edge_line_width: Line width for violin outlines.
        violin_center_line_color: Color for mean/min/max/center lines produced by Matplotlib.
        violin_center_line_width: Line width for mean/min/max/center lines.
        box_width: Width (in x-axis units) of the overlay boxplot.
        box_facecolor: Face color for the overlay boxplot.
        box_edgecolor: Edge color for the overlay boxplot.
        box_line_width: Line width for the overlay boxplot elements.
        box_show_fliers: Whether to display outlier points in the overlay boxplot.
        points_random_seed: Random seed for point jitter when `show_points=True`.
        points_jitter: Half-width of the point jitter range (points are jittered in [-jitter, +jitter]).
        points_size: Marker size in points for points. If None, derives from the active theme.
        points_marker: Marker style used for raw points.
        points_alpha: Alpha for point markers.
        points_edgecolor: Edge color for point markers.
        points_edge_line_width: Line width for point marker edges.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    features = normalize_features(data)
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    if category_names is None:
        category_names = [f"Category {i + 1}" for i in range(len(features))]
    positions = np.arange(len(features), dtype=float) * float(category_spacing) + 1.0

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_points_size = (
            float(coerce_marker_size(t, kind="scatter")) * 0.9 if points_size is None else float(points_size)
        )
        half_width = float(violin_width) / 2.0

        for pos, feat, c in zip(positions, features, colors):
            feat = np.asarray(feat, dtype=float)
            if feat.size == 0:
                continue
            feat_min = float(np.min(feat))
            feat_max = float(np.max(feat))
            feat_span = max(feat_max - feat_min, 1e-6)
            support_pad = feat_span * float(violin_support_extend_ratio)
            y_support = np.linspace(
                feat_min - support_pad,
                feat_max + support_pad,
                int(violin_points),
            )
            kde = gaussian_kde(feat, bw_method=violin_bandwidth_method)
            density_vals = kde(y_support)
            density_peak = float(np.max(density_vals)) if density_vals.size else 1.0
            half_profile = half_width * (density_vals / max(density_peak, 1e-9))

            ax.fill_betweenx(
                y_support,
                pos - half_profile,
                pos + half_profile,
                facecolor=color_to_rgba(c, alpha=float(violin_face_alpha)),
                edgecolor=c,
                linewidth=float(violin_edge_line_width),
            )

            if bool(show_violin_means):
                mean_val = float(np.mean(feat))
                ax.hlines(
                    mean_val,
                    pos - half_width * 0.32,
                    pos + half_width * 0.32,
                    color=violin_center_line_color,
                    linewidth=float(violin_center_line_width),
                )
            if bool(show_violin_medians):
                median_val = float(np.median(feat))
                ax.hlines(
                    median_val,
                    pos - half_width * 0.34,
                    pos + half_width * 0.34,
                    color=violin_center_line_color,
                    linewidth=float(violin_center_line_width),
                )
            if bool(show_violin_extrema):
                min_val = float(np.min(feat))
                max_val = float(np.max(feat))
                ax.hlines(
                    [min_val, max_val],
                    pos - half_width * 0.22,
                    pos + half_width * 0.22,
                    color=violin_center_line_color,
                    linewidth=float(violin_center_line_width),
                )

        if show_box:
            bp = ax.boxplot(
                features,
                patch_artist=True,
                widths=float(box_width),
                showfliers=bool(box_show_fliers),
                positions=positions,
            )
            for patch in bp["boxes"]:
                patch.set_facecolor(box_facecolor)
                patch.set_edgecolor(box_edgecolor)
                patch.set_linewidth(float(box_line_width))
            for k in ("whiskers", "caps", "medians"):
                for item in bp.get(k, []):
                    item.set_color(box_edgecolor)
                    item.set_linewidth(float(box_line_width))

        if show_points:
            rng = np.random.default_rng(int(points_random_seed))
            for i, feat in enumerate(features):
                jitter = rng.uniform(-float(points_jitter), float(points_jitter), len(feat))
                ax.scatter(
                    np.full(len(feat), i + 1, dtype=float) + jitter,
                    feat,
                    s=resolved_points_size**2,
                    marker=str(points_marker),
                    color=color_to_rgba(colors[i % len(colors)], alpha=float(points_alpha)),
                    edgecolor=points_edgecolor,
                    linewidth=float(points_edge_line_width),
                )

        ax.set_xticks(positions, labels=category_names)
        ax.set_xlim(0.5, len(features) + 0.5)
        ax.set_xlim(float(positions[0] - 0.5), float(positions[-1] + 0.5))
        ax.set_ylabel("Value")
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
