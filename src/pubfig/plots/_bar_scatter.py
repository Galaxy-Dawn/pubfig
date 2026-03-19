"""Grouped bar + scatter (Matplotlib)."""

from __future__ import annotations

from typing import Literal, Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._param_aliases import resolve_scalar_alias
from .._style import apply_cartesian_axis_controls, coerce_linewidth, normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba, darken_color
from ..stats.annotations import add_significance_brackets
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _points_to_value_axis_data_delta(
    ax: "Axes",
    *,
    points: float,
    orientation: Literal["vertical", "horizontal"],
) -> float:
    """Convert a screen-space point offset to data units along the value axis."""
    if float(points) <= 0:
        return 0.0

    fig = ax.figure
    delta_px = float(points) * float(fig.dpi) / 72.0
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    x_ref = 0.5 * (float(x0) + float(x1))
    y_ref = 0.5 * (float(y0) + float(y1))

    x_disp, y_disp = ax.transData.transform((x_ref, y_ref))
    if orientation == "vertical":
        _, y_shift = ax.transData.inverted().transform((x_disp, y_disp + delta_px))
        return abs(float(y_shift) - float(y_ref))

    x_shift, _ = ax.transData.inverted().transform((x_disp + delta_px, y_disp))
    return abs(float(x_shift) - float(x_ref))


def _scatter_visual_radius_points(*, scatter_size_points: float, edge_line_width_points: float) -> float:
    """Approximate the visible radius of a circular scatter marker in points."""
    area_points2 = float(scatter_size_points) ** 2
    face_radius = float(np.sqrt(area_points2 / np.pi))
    edge_radius = 0.5 * float(edge_line_width_points)
    return face_radius + edge_radius


def bar_scatter(
    data: np.ndarray,
    *,
    category_names: Optional[list[str]] = None,
    series_names: Optional[list[str]] = None,
    category_spacing: float = 0.75,
    x_label: str = "Categories",
    y_label: str = "Values",
    orientation: Literal["vertical", "horizontal"] = "vertical",
    auto_swap_axis_labels: bool = True,
    value_min: Optional[float] = None,
    value_max: Optional[float] = None,
    y_min: Optional[float] = None,
    y_max: Optional[float] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    error_mode: Literal["std", "sem"] = "std",
    bar_width: str | float = "auto",
    grouped_total_span: float = 0.6,
    grouped_left_offset: Optional[float] = None,
    bar_width_ratio: float = 0.8,
    bar_edgecolor: str = "none",
    bar_line_width: float = 0.0,
    bar_zorder: int = 2,
    error_color: str = "black",
    error_bar_width: float = 0.8,
    errorbar_bw_reference: float = 0.5,
    errorbar_linewidth_min: float = 0.35,
    error_zorder: int = 7,
    error_cap_width_ratio: float = 0.25,
    error_draw_bottom_cap: bool = True,
    scatter_std: float = 0.28,
    scatter_jitter_max: float = 0.8,
    scatter_size: int = 3,
    scatter_size_scale_with_bar_width: bool = True,
    scatter_size_bw_reference: float = 0.4,
    scatter_size_bw_power: float = 1.0,
    scatter_size_min: float = 1.0,
    # Nature-like default: light gray points with slightly darker outline
    # so raw samples are visible but don't compete with bar colors.
    scatter_face_color: Optional[str] = "0.78",
    scatter_face_alpha: float = 0.35,
    scatter_edge_color: Optional[str] = "0.55",
    scatter_edge_darken_factor: float = 0.8,
    scatter_alpha: float = 1.0,
    scatter_edge_line_width: float = 0.3,
    scatter_zorder: int = 5,
    value_dtick: Optional[float] = None,
    value_nticks: Optional[int] = None,
    y_dtick: Optional[float] = None,
    tick_direction: Literal["in", "out", "inout"] | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    show_statistics: bool = True,
    statistics_method: Literal["mannwhitneyu", "wilcoxon"] = "mannwhitneyu",
    annotation_mode: Literal["all", "binary"] = "all",
    significance_label_style: Literal["stars", "p_threshold"] = "stars",
    significance_bar_pairs: list[tuple[int, int]] | None = None,
    significance_category_indices: Sequence[int] | None = None,
    significance_pairs_height_step_multiplier: float = 2.8,
    significance_pairs_height_step_multiplier_horizontal: float | None = 1.0,
    significance_stack_disjoint_pairs: bool = True,
    significance_show_ns: bool = True,
    significance_ns_label: str = "n.s.",
    significance_p_threshold_nonsig_label: str = "n.s.",
    significance_stars_symbol: str = "*",
    significance_stars_render_mode: Literal["text", "markers"] = "text",
    significance_stars_text_mode: Literal["plain", "mathtext"] = "plain",
    significance_stars_mathtext_command: str = "\\ast",
    significance_stars_marker: object = (5, 2),
    significance_stars_marker_size: float = 6.0,
    significance_stars_marker_spacing_points: float = 4.0,
    significance_stars_marker_line_width: float = 0.9,
    significance_label_vertical_alignment: Literal["bottom", "center", "baseline", "center_baseline"] = "bottom",
    significance_stars_label_vertical_alignment: Literal["bottom", "center", "baseline", "center_baseline"] = "center",
    significance_label_rotation: float | None = None,
    significance_label_horizontal_alignment: Literal["center", "left", "right"] | None = None,
    significance_label_side_horizontal: Literal["left", "right"] = "right",
    ref_position: int = 0,
    height_step: float = 0.04,
    vertical_line_length_ratio: float | None = None,
    bracket_linewidth_min: float = 0.4,
    bracket_linewidth_axis_ratio: float = 0.8,
    bracket_y_padding_min: float = 0.02,
    bracket_y_padding_min_horizontal: float | None = 0.01,
    bracket_y_padding_height_step_multiplier: float = 1.4,
    bracket_y_padding_height_step_multiplier_horizontal: float | None = 0.6,
    significance_label_y_offset_ratio: float = 0.18,
    significance_label_y_offset_ratio_horizontal: float = 0.26,
    significance_label_y_offset_ratio_ns: float = 0.3,
    significance_label_y_offset_ratio_ns_horizontal: float = 0.16,
    significance_label_y_offset_ratio_stars: float = 0.18,
    significance_label_y_offset_ratio_stars_horizontal: float = 0.26,
    significance_label_offset_points_horizontal: float = 18.0,
    significance_label_lane_gap_points_horizontal: float = 10.0,
    significance_label_min_clearance_points: float = 1.0,
    significance_label_min_clearance_points_horizontal: float | None = 12.0,
    significance_scatter_clearance_points: float = 1.0,
    significance_font_size: int | None = None,
    significance_font_size_ns: int | None = None,
    significance_color: str = "black",
    significance_line_alpha: float = 0.85,
    significance_text_alpha: float = 0.85,
    auto_y_max_multiplier: float = 1.15,
    auto_y_max_include_statistics: bool = True,
    auto_y_max_stats_margin_height_step_multiplier: float = 0.8,
    legend_show: bool = True,
    legend_gap: float = 0.07,
    legend_y_anchor_min: float = 1.02,
    legend_y_anchor_no_title: float = 1.18,
    legend_above_stats_margin_axes: float = 0.04,
    legend_columnspacing: float = 1.6,
    legend_handlelength: float = 1.4,
    legend_handletextpad: float = 0.4,
    legend_borderaxespad: float = 0.0,
    legend_include_significance: bool = False,
    legend_sig_label: str = "Asterisks: 1 = p < 0.05   2 = p < 0.01   3 = p < 0.001",
    legend_sig_spacer_markersize: float = 16.0,
    random_seed: int | None = 0,
    theme: Optional[Theme] = None,
    width: Optional[int] = 1200,
    height: Optional[int] = 400,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a grouped bar chart with scatter points and error bars.

    Data conventions:
        - 2D: shape (n_categories, n_groups). Bars only, no scatter/error.
        - 3D: shape (n_categories, n_groups, n_repeats). Bars=mean, scatter=raw repeats,
          error bars=std/sem (controlled by `error_mode`).

    Args:
        category_names: Labels for the categorical axis (rows / grouped categories).
        series_names: Legend labels for the repeated series within each category (columns).
        category_spacing: Distance between adjacent categorical groups in axis units.
            Use values below 1.0 for a denser, more compact layout.
        x_label: X axis label.
        y_label: Y axis label.
        orientation: Plot orientation. "vertical" uses vertical bars (default). "horizontal" rotates
            the plot by 90 degrees using horizontal bars.
        auto_swap_axis_labels: If True and `orientation="horizontal"`, swap `x_label`/`y_label` so
            the default labels remain correct ("Values" on x, "Categories" on y).
        value_min: Lower limit for the value axis (y when vertical, x when horizontal). If None, uses 0.
        value_max: Upper limit for the value axis (y when vertical, x when horizontal). If None, uses
            `auto_y_max_multiplier` * max(mean+err).
        y_min: Backward-compatible alias of `value_min`.
        y_max: Backward-compatible alias of `value_max`.
        title: Plot title.
        color_palette: Bar colors (cycled by group).
        error_mode: Error definition for 3D data: \"std\" or \"sem\".

        bar_width: Per-group spacing in data units. Use \"auto\" to compute from `grouped_total_span`.
        grouped_total_span: Total horizontal span reserved per category when `bar_width=\"auto\"`.
        grouped_left_offset: Left offset used to center grouped bars within each category.
            If None, defaults to `grouped_total_span / 2`.
        bar_width_ratio: Actual bar width as a fraction of per-group spacing (`bar_width`).
        bar_edgecolor: Bar edge color (\"none\" disables borders).
        bar_line_width: Bar edge line width (points).
        bar_zorder: Z-order for bars.

        error_color: Error bar color.
        error_bar_width: Thickness multiplier relative to theme axis line width.
        errorbar_bw_reference: Reference `bar_width` used to normalize error bar thickness scaling.
        errorbar_linewidth_min: Minimum error bar line width (points).
        error_zorder: Z-order for error bars.
        error_cap_width_ratio: Cap length as a fraction of the bar width (data units).
        error_draw_bottom_cap: If True, draw the bottom cap (\"I\" bottom bar).

        scatter_std: Jitter spread coefficient (relative to `bar_width`).
        scatter_jitter_max: Upper bound for jitter coefficient (prevents extreme spread).
        scatter_size: Point size control (Matplotlib uses `scatter_size**2`).
        scatter_size_scale_with_bar_width: If True, adapt point size based on bar spacing so
            points remain visually balanced when `num_groups` changes (more groups -> narrower bars).
        scatter_size_bw_reference: Reference `bar_width` used for scatter size scaling when
            `scatter_size_scale_with_bar_width=True`. For `grouped_total_span=0.8`, two groups
            implies `bar_width=0.4`, which is a good default.
        scatter_size_bw_power: Exponent applied to the `bar_width` ratio when scaling scatter size.
            1.0 means size is proportional to bar width; 0.5 is a milder scaling.
        scatter_size_min: Minimum scatter marker size (in points, prior to squaring).
        scatter_face_color: Optional override for scatter face color. If None, uses the
            corresponding bar color for that group.
        scatter_face_alpha: Alpha applied to the *face color* of points (RGBA fill).
        scatter_edge_color: Optional override for scatter edge color. If None, uses a darkened
            version of the group bar color (or `scatter_face_color` when provided).
        scatter_edge_darken_factor: Darkening factor for point edges relative to bar color.
        scatter_alpha: Global scatter alpha (applied on top of face RGBA).
        scatter_edge_line_width: Scatter edge line width (points).
        scatter_zorder: Z-order for scatter points.

        value_dtick: If set, enforce a fixed major tick step on the value axis.
        value_nticks: If set (and `value_dtick` is None), set an approximate number of major ticks
            on the value axis.
        y_dtick: Backward-compatible alias of `value_dtick` for the vertical orientation.
        tick_direction: Override tick direction ("in", "out", "inout") on both axes.

        show_statistics: If True, draw significance brackets for vertical 3D grouped bars with >=2 groups.
            Horizontal bar+scatter charts intentionally skip significance annotations even when this
            is True.
        statistics_method: Statistical test used for pairwise comparisons.
        annotation_mode: How to annotate significance (e.g. stars).
        significance_label_style: Label style used for significance brackets. Use \"p_threshold\"
            to print labels like `p<0.001` directly on the figure (no legend needed).
        significance_bar_pairs: Explicit bar-index pairs to compare, e.g. `[(0, 1), (2, 3)]`.
            Default is None, which resolves to `[(0, 1), (0, 2), ...]` (first bar vs all others).
            Overlapping pairs are automatically stacked in height; non-overlapping pairs can share
            the same height when `significance_stack_disjoint_pairs=True`.
        significance_category_indices: Optional list of category indices to annotate. Use this
            when only some conditions should show comparisons (e.g. only Cond B and Cond C). If None,
            all categories are annotated.
        significance_pairs_height_step_multiplier: When `significance_bar_pairs` contains multiple
            comparisons, multiply `height_step` by this factor to ensure labels/brackets do not
            overlap visually.
        significance_pairs_height_step_multiplier_horizontal: Optional override for
            `significance_pairs_height_step_multiplier` when `orientation="horizontal"`. Use a smaller
            value to make multiple bracket levels more compact in horizontal plots. Pass None to
            disable the override.
        significance_stack_disjoint_pairs: If True (default), allow disjoint comparisons such as
            `(0, 1)` and `(2, 3)` to share the same y-height instead of stacking above each other.
        significance_show_ns: If True, draw non-significant comparisons as `significance_ns_label`.
        significance_ns_label: Label used when a comparison is non-significant (default: \"n.s.\").
        significance_p_threshold_nonsig_label: Label to use when `significance_label_style="p_threshold"`
            and the p-value is not below 0.05.
        significance_stars_symbol: Glyph used for star-style significance labels. Default uses the
            ASCII \"*\" for maximum font compatibility.
        significance_stars_render_mode: How to draw star labels. \"markers\" draws stars as marker
            paths (not text), which avoids font glyph baseline issues; \"text\" uses repeated
            `significance_stars_symbol`.
        significance_stars_text_mode: When `significance_stars_render_mode=\"text\"`, choose
            \"mathtext\" (default) to render as `${\\ast}{\\ast}...$` (avoids operator spacing and
            usually looks less superscript-like), or \"plain\" to use repeated `significance_stars_symbol`.
        significance_stars_mathtext_command: Mathtext command used when `significance_stars_text_mode=\"mathtext\"`
            (default: \"\\\\ast\").
        significance_stars_marker: Marker spec used when `significance_stars_render_mode=\"markers\"`.
            Defaults to `(5, 2)` (an asterisk-like marker).
        significance_stars_marker_size: Star marker size (points) when using marker rendering.
        significance_stars_marker_spacing_points: Horizontal spacing (points) between multiple stars.
        significance_stars_marker_line_width: Stroke width (points) for star markers when using marker rendering.
        significance_label_vertical_alignment: Vertical alignment used for significance labels.
            Only applies to text-rendered labels (e.g. \"n.s.\" or when `significance_stars_render_mode=\"text\"`).
        significance_stars_label_vertical_alignment: Vertical alignment used for text-rendered star labels.
            Default \"center\" helps avoid ASCII \"*\" looking like superscript in some fonts.
        significance_label_rotation: Text label rotation in degrees. When None, defaults to 0 for
            `orientation="vertical"` and 90 for `orientation="horizontal"`.
        significance_label_horizontal_alignment: Text label horizontal alignment (ha). When None,
            defaults to "center". For horizontal plots, keep this at "center" unless you explicitly
            want a visual vertical shift of the rotated label.
        significance_label_side_horizontal: Which side of the bracket line to place labels for
            `orientation="horizontal"`. "left" places labels toward the bars; "right" places labels
            outside the bars.
        ref_position: Reference group index for comparisons.
        height_step: Vertical step (in data units) between stacked bracket levels.
        vertical_line_length_ratio: Bracket vertical segment length proportional to the horizontal
            bracket span (`abs(x1-x0)`), i.e. `vertical_length = vertical_line_length_ratio * abs(x1-x0)`.
            Set to 0 or None for horizontal-only brackets.
        bracket_linewidth_min: Minimum bracket line width (points).
        bracket_linewidth_axis_ratio: Bracket thickness multiplier relative to axis line width.
        bracket_y_padding_min: Minimum padding above the highest points before drawing brackets (data units).
        bracket_y_padding_min_horizontal: Optional override for `bracket_y_padding_min` when
            `orientation="horizontal"`. Use a smaller value for tighter horizontal layouts. Pass None
            to disable the override.
        bracket_y_padding_height_step_multiplier: Extra padding as a multiple of `height_step`.
        bracket_y_padding_height_step_multiplier_horizontal: Optional override for
            `bracket_y_padding_height_step_multiplier` when `orientation="horizontal"`. Pass None to
            disable the override.
        significance_label_y_offset_ratio: Text vertical offset ratio for significant labels when
            brackets have vertical end-caps (multiplied by `height_step`).
        significance_label_y_offset_ratio_horizontal: Text vertical offset ratio when brackets are
            horizontal-only (no vertical end-caps).
        significance_label_y_offset_ratio_ns: Text vertical offset ratio for non-significant labels
            (applied when `significance_show_ns=True`).
        significance_label_y_offset_ratio_ns_horizontal: Text vertical offset ratio for non-significant
            labels when brackets are horizontal-only (no vertical end-caps).
        significance_label_y_offset_ratio_stars: Text vertical offset ratio for star labels (applied when
            `significance_label_style=\"stars\"` and `significance_stars_render_mode=\"text\"`).
        significance_label_y_offset_ratio_stars_horizontal: Star label offset ratio for horizontal-only brackets.
        significance_label_offset_points_horizontal: Explicit screen-space gap, in points, between the
            horizontal significance line and its label. This is the most reliable control for the
            visible line-to-label distance in horizontal plots.
        significance_label_lane_gap_points_horizontal: Additional screen-space gap, in points, added
            between neighboring horizontal label lanes so adjacent `n.s.` / stars do not crowd each other.
        significance_label_min_clearance_points: Minimum vertical clearance (in points) between the bracket
            line and its label text, applied in screen space (robust to y-axis scaling).
        significance_label_min_clearance_points_horizontal: Override for `significance_label_min_clearance_points`
            when `orientation=\"horizontal\"`. Increase this to push star / n.s. labels further away from the
            bracket line without changing bracket spacing in data units. Pass None to disable the override.
        significance_scatter_clearance_points: Extra clearance, in screen points, added on top of the
            visible scatter-marker radius when computing the bracket baseline. Increase this if raw
            points still visually touch significance lines.
        significance_font_size: Font size (pt) for significance labels (stars / p-threshold text). If None,
            uses the theme base font size.
        significance_font_size_ns: Font size (pt) for non-significant label text (default auto: base - 1).
        significance_color: Color for significance lines and labels.
        significance_line_alpha: Alpha for significance lines (horizontal brackets).
        significance_text_alpha: Alpha for significance label text.
        auto_y_max_multiplier: Auto y max multiplier when `y_max` is None.
        auto_y_max_include_statistics: If True, expand the auto y max to include significance annotations
            so brackets/labels stay inside the axes (reduces overlap with legend/title regions).
        auto_y_max_stats_margin_height_step_multiplier: Extra top margin above the highest significance
            label, expressed as a multiple of `height_step`.

        legend_show: Whether to show legend.
        legend_gap: Vertical gap from title to legend anchor (axes coords).
        legend_y_anchor_min: Minimum legend y anchor when a title exists.
        legend_y_anchor_no_title: Legend y anchor used when no title exists.
        legend_above_stats_margin_axes: Extra vertical margin (axes coordinates) to keep legend
            above the highest significance annotation.
        legend_columnspacing: Legend column spacing (points).
        legend_handlelength: Legend handle length (relative units).
        legend_handletextpad: Legend handle/text padding (points).
        legend_borderaxespad: Legend padding to axes (fraction of font-size; Matplotlib default units).
        legend_include_significance: If True, include a significance key entry in the legend.
        legend_sig_label: Text used to explain significance stars in the legend.
        legend_sig_spacer_markersize: Spacer size used to separate legend sections.

        random_seed: Random seed used for jitter generation (3D scatter only).
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.

    Notes:
        Error cap width is drawn in *data units* (not points), so it scales naturally with
        bar width changes. Control this with `error_cap_width_ratio`.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim not in (2, 3):
        raise ValueError("Data must be 2D or 3D array.")

    vmin = resolve_scalar_alias(value_min, y_min, primary_name="value_min", legacy_name="y_min")
    vmax = resolve_scalar_alias(value_max, y_max, primary_name="value_max", legacy_name="y_max")

    if (value_dtick is not None) and (y_dtick is not None) and (float(value_dtick) != float(y_dtick)):
        raise ValueError("value_dtick and y_dtick are both provided but different; please pass only one.")
    vdtick = value_dtick
    if vdtick is None and y_dtick is not None:
        if orientation == "vertical":
            vdtick = y_dtick
        else:
            raise ValueError("y_dtick is only valid for vertical orientation; use value_dtick instead.")

    if data.ndim == 3:
        mean_data = np.mean(data, axis=2)
        std_data = np.std(data, axis=2, ddof=1)
        errors = std_data / np.sqrt(data.shape[2]) if error_mode == "sem" else std_data
    else:
        mean_data = data
        errors = np.zeros_like(data)

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    num_categories, num_groups = mean_data.shape
    if category_names is None:
        category_names = [f"Category {i + 1}" for i in range(num_categories)]
    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(num_groups)]

    category_positions = np.arange(num_categories, dtype=float) * float(category_spacing)
    resolved_grouped_left_offset = (
        float(grouped_total_span) / 2.0 if grouped_left_offset is None else float(grouped_left_offset)
    )
    if bar_width == "auto":
        bw = float(grouped_total_span) / float(num_groups)
    else:
        bw = float(bar_width)
    rng = np.random.default_rng(random_seed)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        axis_lw = coerce_linewidth(t, kind="axis")
        bw_scale = float(bw) / float(errorbar_bw_reference)
        eb_lw = max(float(errorbar_linewidth_min), float(axis_lw) * float(error_bar_width) * float(bw_scale))
        bracket_lw = max(float(bracket_linewidth_min), float(axis_lw) * float(bracket_linewidth_axis_ratio))
        scatter_bw_scale = float(bw) / max(1e-12, float(scatter_size_bw_reference))
        scatter_size_points = float(scatter_size)
        if bool(scatter_size_scale_with_bar_width):
            scatter_size_points = scatter_size_points * float(scatter_bw_scale) ** float(scatter_size_bw_power)
        scatter_size_points = max(float(scatter_size_min), float(scatter_size_points))

        # Horizontal bar+scatter is kept annotation-free by default: Nature-like horizontal summary
        # charts are cleaner without significance brackets in this library.
        statistics_enabled = bool(show_statistics) and orientation == "vertical"

        if orientation == "horizontal" and auto_swap_axis_labels:
            x_label, y_label = y_label, x_label

        for i in range(num_groups):
            c = colors[i % len(colors)]
            pos = category_positions - float(resolved_grouped_left_offset) + (i + 0.5) * float(bw)

            if orientation == "vertical":
                ax.bar(
                    pos,
                    mean_data[:, i],
                    width=float(bw) * float(bar_width_ratio),
                    color=c,
                    edgecolor=str(bar_edgecolor),
                    linewidth=float(bar_line_width),
                    label=series_names[i],
                    zorder=int(bar_zorder),
                )
            else:
                ax.barh(
                    pos,
                    mean_data[:, i],
                    height=float(bw) * float(bar_width_ratio),
                    color=c,
                    edgecolor=str(bar_edgecolor),
                    linewidth=float(bar_line_width),
                    label=series_names[i],
                    zorder=int(bar_zorder),
                )

            # Error bars (manually drawn so cap width can be in data units).
            cap_half = 0.5 * float(bw) * float(bar_width_ratio) * float(np.clip(error_cap_width_ratio, 0.0, 1.0))
            y = mean_data[:, i]
            yerr = errors[:, i]
            if orientation == "vertical":
                ax.vlines(
                    pos,
                    y - yerr,
                    y + yerr,
                    colors=str(error_color),
                    linewidth=float(eb_lw),
                    zorder=int(error_zorder),
                )
                ax.hlines(
                    y + yerr,
                    pos - cap_half,
                    pos + cap_half,
                    colors=str(error_color),
                    linewidth=float(eb_lw),
                    zorder=int(error_zorder),
                )
                if bool(error_draw_bottom_cap):
                    ax.hlines(
                        y - yerr,
                        pos - cap_half,
                        pos + cap_half,
                        colors=str(error_color),
                        linewidth=float(eb_lw),
                        zorder=int(error_zorder),
                    )
            else:
                ax.hlines(
                    pos,
                    y - yerr,
                    y + yerr,
                    colors=str(error_color),
                    linewidth=float(eb_lw),
                    zorder=int(error_zorder),
                )
                ax.vlines(
                    y + yerr,
                    pos - cap_half,
                    pos + cap_half,
                    colors=str(error_color),
                    linewidth=float(eb_lw),
                    zorder=int(error_zorder),
                )
                if bool(error_draw_bottom_cap):
                    ax.vlines(
                        y - yerr,
                        pos - cap_half,
                        pos + cap_half,
                        colors=str(error_color),
                        linewidth=float(eb_lw),
                        zorder=int(error_zorder),
                    )

            if data.ndim == 3:
                for j in range(num_categories):
                    vals = data[j, i, :]
                    jitter_scale = min(abs(float(scatter_std)), float(scatter_jitter_max))
                    jitter = (rng.random(data.shape[2]) - 0.5) * (jitter_scale * float(bw))
                    base_face = str(scatter_face_color) if scatter_face_color is not None else str(c)
                    face_c = color_to_rgba(base_face, alpha=float(scatter_face_alpha))
                    if scatter_edge_color is not None:
                        edge_c = str(scatter_edge_color)
                    else:
                        edge_c = (
                            darken_color(c, factor=float(scatter_edge_darken_factor))
                            if scatter_face_color is None
                            else base_face
                        )
                    if orientation == "vertical":
                        ax.scatter(
                            np.full(data.shape[2], float(pos[j])) + jitter,
                            vals,
                            s=float(scatter_size_points) ** 2,
                            marker="o",
                            facecolors=[face_c],
                            edgecolors=[edge_c],
                            alpha=float(scatter_alpha),
                            linewidths=float(scatter_edge_line_width),
                            zorder=int(scatter_zorder),
                        )
                    else:
                        ax.scatter(
                            vals,
                            np.full(data.shape[2], float(pos[j])) + jitter,
                            s=float(scatter_size_points) ** 2,
                            marker="o",
                            facecolors=[face_c],
                            edgecolors=[edge_c],
                            alpha=float(scatter_alpha),
                            linewidths=float(scatter_edge_line_width),
                            zorder=int(scatter_zorder),
                        )

        # Highest bracket label coordinate along the value axis (y for vertical, x for horizontal).
        max_significance_value_data: float | None = None
        if statistics_enabled and (data.ndim == 3) and num_groups > 1:
            if significance_bar_pairs is not None:
                resolved_pairs = list(significance_bar_pairs)
            else:
                resolved_pairs = [(0, i) for i in range(1, num_groups)]

            base_sig_fs = int(significance_font_size) if significance_font_size is not None else max(
                7, int(getattr(t, "font_size", 7))
            )
            base_sig_ns_fs = (
                int(significance_font_size_ns)
                if significance_font_size_ns is not None
                else max(5, base_sig_fs - 1)
            )
            pairs_multiplier = float(significance_pairs_height_step_multiplier)
            if orientation == "horizontal" and significance_pairs_height_step_multiplier_horizontal is not None:
                pairs_multiplier = float(significance_pairs_height_step_multiplier_horizontal)

            # Convert the visible scatter-marker radius from screen points to data units so the
            # significance baseline clears the marker envelope, not just the raw point centers.
            fig.canvas.draw()
            scatter_visual_radius_points = _scatter_visual_radius_points(
                scatter_size_points=float(scatter_size_points),
                edge_line_width_points=float(scatter_edge_line_width),
            )
            scatter_clearance_data = _points_to_value_axis_data_delta(
                ax,
                points=float(scatter_visual_radius_points) + float(significance_scatter_clearance_points),
                orientation=orientation,
            )
            scatter_max = np.max(data, axis=2) + float(scatter_clearance_data)
            if orientation == "horizontal" and significance_label_side_horizontal == "left":
                effective_step = float(height_step)
                if len(resolved_pairs) > 1:
                    effective_step = effective_step * float(pairs_multiplier)
                label_offset_ratio_max = max(
                    float(significance_label_y_offset_ratio_horizontal),
                    float(significance_label_y_offset_ratio_ns_horizontal),
                    float(significance_label_y_offset_ratio_stars_horizontal),
                )
                label_offset_data = float(effective_step) * float(label_offset_ratio_max)
                label_extent_points = 0.5 * max(
                    float(base_sig_fs),
                    float(base_sig_ns_fs),
                    float(significance_stars_marker_size),
                )
                label_extent_data = _points_to_value_axis_data_delta(
                    ax,
                    points=float(label_extent_points),
                    orientation=orientation,
                )
                scatter_max = (
                    scatter_max
                    + float(label_offset_data)
                    + float(label_extent_data)
                    + float(scatter_clearance_data)
                )
            errors_for_brackets = np.maximum(errors, scatter_max - mean_data)
            bar_centers = np.stack(
                [
                    category_positions - float(resolved_grouped_left_offset) + (i + 0.5) * float(bw)
                    for i in range(num_groups)
                ],
                axis=1,
            )

            pad_min = float(bracket_y_padding_min)
            if orientation == "horizontal" and bracket_y_padding_min_horizontal is not None:
                pad_min = float(bracket_y_padding_min_horizontal)
            pad_mult = float(bracket_y_padding_height_step_multiplier)
            if orientation == "horizontal" and bracket_y_padding_height_step_multiplier_horizontal is not None:
                pad_mult = float(bracket_y_padding_height_step_multiplier_horizontal)

            max_significance_value_data = add_significance_brackets(
                ax,
                data=data,
                x_positions=category_positions,
                bar_width=float(bw),
                mean_data=mean_data,
                errors=errors_for_brackets,
                num_categories=num_categories,
                num_groups=num_groups,
                orientation=orientation,
                method=statistics_method,
                annotation_mode=annotation_mode,
                label_style=significance_label_style,
                pairs=resolved_pairs,
                category_indices=significance_category_indices,
                bar_centers=bar_centers,
                ref_position=int(ref_position),
                height_step=float(height_step),
                pairs_height_step_multiplier=float(pairs_multiplier),
                stack_disjoint_pairs=bool(significance_stack_disjoint_pairs),
                vertical_line_length_ratio=(None if vertical_line_length_ratio is None else float(vertical_line_length_ratio)),
                label_y_offset_ratio=float(significance_label_y_offset_ratio),
                label_y_offset_ratio_horizontal=float(significance_label_y_offset_ratio_horizontal),
                label_y_offset_ratio_ns=float(significance_label_y_offset_ratio_ns),
                label_y_offset_ratio_ns_horizontal=float(significance_label_y_offset_ratio_ns_horizontal),
                label_y_offset_ratio_stars=float(significance_label_y_offset_ratio_stars),
                label_y_offset_ratio_stars_horizontal=float(significance_label_y_offset_ratio_stars_horizontal),
                label_offset_points_horizontal=float(significance_label_offset_points_horizontal),
                label_lane_gap_points_horizontal=float(significance_label_lane_gap_points_horizontal),
                label_min_clearance_points=float(
                    (
                        significance_label_min_clearance_points_horizontal
                        if (orientation == "horizontal" and significance_label_min_clearance_points_horizontal is not None)
                        else significance_label_min_clearance_points
                    )
                ),
                y_padding=max(float(pad_min), float(height_step) * float(pad_mult)),
                show_ns=bool(significance_show_ns),
                ns_label=str(significance_ns_label),
                p_threshold_nonsig_label=str(significance_p_threshold_nonsig_label),
                stars_symbol=str(significance_stars_symbol),
                stars_render_mode=significance_stars_render_mode,
                stars_text_mode=significance_stars_text_mode,
                stars_mathtext_command=str(significance_stars_mathtext_command),
                stars_marker=significance_stars_marker,
                stars_marker_size=float(significance_stars_marker_size),
                stars_marker_spacing_points=float(significance_stars_marker_spacing_points),
                stars_marker_line_width=float(significance_stars_marker_line_width),
                label_vertical_alignment=significance_label_vertical_alignment,
                stars_label_vertical_alignment=significance_stars_label_vertical_alignment,
                label_rotation=significance_label_rotation,
                label_horizontal_alignment=significance_label_horizontal_alignment,
                horizontal_label_side=("left" if significance_label_side_horizontal == "left" else "right"),
                line_width=float(bracket_lw),
                font_size=int(base_sig_fs),
                font_size_ns=int(base_sig_ns_fs),
                color=str(significance_color),
                line_alpha=float(significance_line_alpha),
                text_alpha=float(significance_text_alpha),
            )

        auto_value_max = float(np.max(mean_data + errors)) * float(auto_y_max_multiplier) if mean_data.size else 1.0
        if (
            bool(auto_y_max_include_statistics)
            and (vmax is None)
            and (max_significance_value_data is not None)
            and np.isfinite(float(max_significance_value_data))
        ):
            auto_value_max = max(
                float(auto_value_max),
                float(max_significance_value_data)
                + float(height_step) * float(auto_y_max_stats_margin_height_step_multiplier),
            )
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        if orientation == "vertical":
            ax.set_xticks(category_positions, labels=category_names)
            ax.set_xlim(
                float(category_positions[0] - float(grouped_total_span) / 2.0 - 0.15),
                float(category_positions[-1] + float(grouped_total_span) / 2.0 + 0.15),
            )
            ax.set_ylim(vmin if vmin is not None else 0, vmax if vmax is not None else auto_value_max)
        else:
            ax.set_yticks(category_positions, labels=category_names)
            ax.set_ylim(
                float(category_positions[0] - float(grouped_total_span) / 2.0 - 0.15),
                float(category_positions[-1] + float(grouped_total_span) / 2.0 + 0.15),
            )
            ax.set_xlim(vmin if vmin is not None else 0, vmax if vmax is not None else auto_value_max)

        if vdtick is not None or value_nticks is not None:
            import matplotlib.ticker as mticker

            axis = ax.yaxis if orientation == "vertical" else ax.xaxis
            if vdtick is not None:
                axis.set_major_locator(mticker.MultipleLocator(float(vdtick)))
            else:
                axis.set_major_locator(mticker.MaxNLocator(nbins=int(value_nticks)))
        if title:
            title_above(ax, title)

        if legend_show:
            # Legend row centered below the title.
            gap = float(legend_gap)
            title_text = ax.get_title()
            if title_text:
                title_y = float(getattr(ax.title, "get_position")()[1])
                y_anchor = max(float(legend_y_anchor_min), title_y - gap)
            else:
                y_anchor = float(legend_y_anchor_no_title)
            if max_significance_value_data is not None and orientation == "vertical":
                # Convert the highest significance y (data coords) to axes coords and ensure
                # legend sits above it with a safety margin.
                x_ref = float(category_positions[0]) if len(category_positions) > 0 else 0.0
                _, sig_y_axes = ax.transAxes.inverted().transform(
                    ax.transData.transform((x_ref, float(max_significance_value_data)))
                )
                y_anchor = max(float(y_anchor), float(sig_y_axes) + float(legend_above_stats_margin_axes))

            handles, labels = ax.get_legend_handles_labels()
            if legend_include_significance and statistics_enabled and (data.ndim == 3) and num_groups > 1:
                from matplotlib.lines import Line2D

                sig_handle = Line2D([], [], linewidth=0.0, alpha=0.0)
                spacer_handle = Line2D(
                    [],
                    [],
                    linewidth=0.0,
                    marker="s",
                    markersize=float(legend_sig_spacer_markersize),
                    markerfacecolor="none",
                    markeredgecolor="none",
                )
                handles = [sig_handle, spacer_handle] + list(handles)
                labels = [str(legend_sig_label), ""] + list(labels)

            leg = ax.legend(
                handles=handles,
                labels=labels,
                frameon=False,
                ncol=len(labels),
                loc="upper center",
                bbox_to_anchor=(0.5, float(y_anchor)),
                borderaxespad=float(legend_borderaxespad),
                columnspacing=float(legend_columnspacing),
                handlelength=float(legend_handlelength),
                handletextpad=float(legend_handletextpad),
                fontsize=int(getattr(t, "legend_font_size", 6)),
                prop={"family": t.font_family, "size": float(getattr(t, "legend_font_size", 6))},
            )
            try:
                leg.set_in_layout(True)
                leg.set_zorder(10)
            except Exception:
                pass
        else:
            leg = ax.get_legend()
            if leg is not None:
                leg.remove()

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
