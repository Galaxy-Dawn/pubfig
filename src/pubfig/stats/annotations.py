"""Significance test and bracket annotations (Matplotlib)."""

from __future__ import annotations

from typing import Any, Literal, Sequence, TYPE_CHECKING

import numpy as np
from scipy.stats import mannwhitneyu, wilcoxon

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes


def _significance_label(
    p: float,
    *,
    style: Literal["stars", "p_threshold"],
    p_threshold_nonsig_label: str,
    stars_symbol: str,
    stars_text_mode: Literal["plain", "mathtext"],
    stars_mathtext_command: str,
) -> str:
    """Return the bracket label for a p-value."""
    if style == "p_threshold":
        if p < 0.001:
            return "p<0.001"
        if p < 0.01:
            return "p<0.01"
        if p < 0.05:
            return "p<0.05"
        return str(p_threshold_nonsig_label)

    # style == "stars"
    def _stars(n: int) -> str:
        if stars_text_mode == "plain":
            return str(stars_symbol) * int(n)
        # Mathtext: keep stars tight by grouping each command to avoid operator spacing.
        cmd = str(stars_mathtext_command)
        if not cmd.startswith("\\"):
            cmd = "\\" + cmd
        return "$" + "".join("{" + cmd + "}" for _ in range(int(n))) + "$"

    if p < 0.001:
        return _stars(3)
    if p < 0.01:
        return _stars(2)
    if p < 0.05:
        return _stars(1)
    return "n.s."


def add_significance_brackets(
    ax: "Axes",
    *,
    data: np.ndarray,
    x_positions: np.ndarray,
    bar_width: float,
    mean_data: np.ndarray,
    errors: np.ndarray,
    num_categories: int,
    num_groups: int,
    orientation: Literal["vertical", "horizontal"] = "vertical",
    method: Literal["mannwhitneyu", "wilcoxon"] = "mannwhitneyu",
    annotation_mode: Literal["all", "binary"] = "all",
    label_style: Literal["stars", "p_threshold"] = "stars",
    pairs: list[tuple[int, int]] | None = None,
    category_indices: Sequence[int] | None = None,
    bar_centers: np.ndarray | None = None,
    ref_position: int = 0,
    height_step: float = 0.025,
    pairs_height_step_multiplier: float = 1.8,
    stack_disjoint_pairs: bool = True,
    vertical_line_length_ratio: float | None = None,
    label_y_offset_ratio: float = 0.55,
    label_y_offset_ratio_horizontal: float = 0.5,
    label_y_offset_ratio_ns: float = 0.7,
    label_y_offset_ratio_ns_horizontal: float = 0.12,
    label_y_offset_ratio_stars: float = 0.5,
    label_y_offset_ratio_stars_horizontal: float = 0.5,
    label_offset_points_horizontal: float = 0.0,
    label_lane_gap_points_horizontal: float = 0.0,
    label_min_clearance_points: float = 1.0,
    y_padding: float = 0.03,
    show_ns: bool = False,
    ns_label: str = "n.s.",
    p_threshold_nonsig_label: str = "n.s.",
    stars_symbol: str = "*",
    stars_render_mode: Literal["text", "markers"] = "text",
    stars_text_mode: Literal["plain", "mathtext"] = "plain",
    stars_mathtext_command: str = "\\ast",
    stars_marker: Any = (5, 2),
    stars_marker_size: float = 6.0,
    stars_marker_spacing_points: float = 4.0,
    stars_marker_line_width: float = 0.9,
    label_vertical_alignment: Literal["bottom", "center", "baseline", "center_baseline"] = "bottom",
    stars_label_vertical_alignment: Literal["bottom", "center", "baseline", "center_baseline"] = "center",
    label_rotation: float | None = None,
    label_horizontal_alignment: Literal["center", "left", "right"] | None = None,
    horizontal_label_side: Literal["right", "left"] = "right",
    line_width: float = 1.2,
    font_size: int = 9,
    font_size_ns: int = 7,
    color: str = "black",
    line_alpha: float = 0.85,
    text_alpha: float = 0.85,
    font_family: str = "Arial",
) -> float | None:
    """Add significance brackets to a grouped bar chart on a Matplotlib Axes.

    Notes:
        - This function expects `data` to be a 3D array: (categories, groups, repeats).
        - All lengths are in data coordinates.
        - Use `category_indices` to restrict which categories receive brackets. When None,
          all categories are annotated.
        - When `pairs` contains multiple comparisons, set `stack_disjoint_pairs=True` (default)
          to allow comparisons that do not overlap in x-range to share the same y-height.
        - Stars are rendered by repeating `stars_symbol` (default: \"*\"). If you see font-specific
          placement issues (e.g. \"*\" looks like superscript in some fonts), adjust
          `stars_render_mode` and/or `label_y_offset_ratio*`.
        - When `stars_render_mode=\"markers\"`, stars are drawn as marker paths (not text), which
          avoids font glyph baseline issues.
        - `label_rotation` controls the rotation (degrees) applied to text labels (including `n.s.`).
          When None, defaults to 0 for `orientation="vertical"` and 90 for `orientation="horizontal"`.
        - `label_horizontal_alignment` controls the text horizontal alignment (ha). When None, defaults
          to "center". This avoids visual y-shifts for rotated horizontal labels; use
          `horizontal_label_side` plus x-offset/clearance to control left-right placement instead.
        - `horizontal_label_side` controls which side of the bracket line the label is placed on for
          `orientation="horizontal"`. "right" places labels outside the bars; "left" places labels
          toward the bars.
        - `label_offset_points_horizontal` adds an explicit screen-space gap, in points, between the
          bracket line and the label for `orientation="horizontal"`. This is more visually stable
          than relying only on data-coordinate offsets derived from `height_step`.
        - `label_lane_gap_points_horizontal` adds additional screen-space spacing, in points, between
          neighboring horizontal label lanes based on bracket stack level.
    """
    x_positions = np.asarray(x_positions, dtype=float)
    if label_rotation is None:
        label_rotation = 0.0 if orientation == "vertical" else 90.0
    if label_horizontal_alignment is None:
        label_horizontal_alignment = "center"
    enabled_categories: set[int] | None = None
    if category_indices is not None:
        enabled_categories = set()
        for j in category_indices:
            jj = int(j)
            if jj < 0:
                jj = jj + int(num_categories)
            if not (0 <= jj < int(num_categories)):
                raise ValueError("category_indices out of range")
            enabled_categories.add(jj)

    step = float(height_step)
    if pairs is not None and len(pairs) > 1:
        step = step * float(pairs_height_step_multiplier)
    max_annotation_y: float | None = None

    def _draw_bracket(*, x0: float, x1: float, y: float, label: str, lane_idx: int = 0) -> None:
        nonlocal max_annotation_y
        is_ns = label == ns_label
        is_stars_text = (not is_ns) and label_style == "stars" and stars_render_mode == "text"
        effective_label_vertical_alignment = (
            "center" if orientation == "horizontal" else str(label_vertical_alignment)
        )
        effective_stars_label_vertical_alignment = (
            "center" if orientation == "horizontal" else str(stars_label_vertical_alignment)
        )
        # Make end-cap length proportional to the bracket span, i.e. the horizontal segment length.
        # Note: x and y are different units; this is a visual heuristic to keep bracket geometry
        # consistent when bar spacing changes.
        cap_len = 0.0
        if vertical_line_length_ratio is not None:
            cap_len = abs(float(x1) - float(x0)) * float(vertical_line_length_ratio)

        category_center = (float(x0) + float(x1)) / 2.0
        if orientation == "vertical":
            if float(cap_len) <= 0:
                # Horizontal-only annotation line (no end-caps).
                ax.plot(
                    [x0, x1],
                    [y, y],
                    color=color,
                    alpha=float(line_alpha),
                    linewidth=float(line_width),
                    clip_on=False,
                    zorder=10,
                )
                y_line_top = float(y)
                if is_ns:
                    y_text = y + float(step) * float(label_y_offset_ratio_ns_horizontal)
                else:
                    y_text = y + float(step) * float(
                        label_y_offset_ratio_stars_horizontal if is_stars_text else label_y_offset_ratio_horizontal
                    )
            else:
                ax.plot(
                    [x0, x0, x1, x1],
                    [y, y + cap_len, y + cap_len, y],
                    color=color,
                    alpha=float(line_alpha),
                    linewidth=float(line_width),
                    clip_on=False,
                    zorder=10,
                )
                y_line_top = float(y) + float(cap_len)
                y_text = (y + cap_len) + float(step) * (
                    float(label_y_offset_ratio_ns)
                    if is_ns
                    else float(label_y_offset_ratio_stars if is_stars_text else label_y_offset_ratio)
                )

            if float(label_min_clearance_points) > 0:
                fig = ax.figure
                dy_px = float(label_min_clearance_points) * float(fig.dpi) / 72.0
                x_disp, y_disp = ax.transData.transform((category_center, float(y_line_top)))
                _, y_clear = ax.transData.inverted().transform((x_disp, y_disp + dy_px))
                y_text = max(float(y_text), float(y_clear))
            label_x, label_y = category_center, float(y_text)
            max_annotation_y = float(label_y) if max_annotation_y is None else max(max_annotation_y, float(label_y))
        else:
            # Horizontal orientation: bars extend along x, categories/groups are on y.
            if float(cap_len) <= 0:
                # Vertical-only annotation line (no end-caps).
                ax.plot(
                    [y, y],
                    [x0, x1],
                    color=color,
                    alpha=float(line_alpha),
                    linewidth=float(line_width),
                    clip_on=False,
                    zorder=10,
                )
                x_line_end = float(y)
            else:
                ax.plot(
                    [y, y + cap_len, y + cap_len, y],
                    [x0, x0, x1, x1],
                    color=color,
                    alpha=float(line_alpha),
                    linewidth=float(line_width),
                    clip_on=False,
                    zorder=10,
                )
                x_line_end = float(y) + float(cap_len)

            if is_ns:
                offset_data = float(step) * float(label_y_offset_ratio_ns_horizontal)
            else:
                offset_data = float(step) * float(
                    label_y_offset_ratio_stars_horizontal if is_stars_text else label_y_offset_ratio_horizontal
                )
            if float(cap_len) > 0:
                offset_data = float(step) * (
                    float(label_y_offset_ratio_ns)
                    if is_ns
                    else float(label_y_offset_ratio_stars if is_stars_text else label_y_offset_ratio)
                )

            offset_data_points = 0.0
            if float(label_offset_points_horizontal) > 0:
                fig = ax.figure
                dx_px = float(label_offset_points_horizontal) * float(fig.dpi) / 72.0
                x_disp, y_disp = ax.transData.transform((float(x_line_end), category_center))
                if horizontal_label_side == "left":
                    x_off, _ = ax.transData.inverted().transform((x_disp - dx_px, y_disp))
                    offset_data_points = abs(float(x_off) - float(x_line_end))
                else:
                    x_off, _ = ax.transData.inverted().transform((x_disp + dx_px, y_disp))
                    offset_data_points = abs(float(x_off) - float(x_line_end))
            offset_data = max(float(offset_data), float(offset_data_points))

            lane_gap_data = 0.0
            if int(lane_idx) > 0 and float(label_lane_gap_points_horizontal) > 0:
                fig = ax.figure
                dx_px = float(label_lane_gap_points_horizontal) * float(fig.dpi) / 72.0 * float(lane_idx)
                x_disp, y_disp = ax.transData.transform((float(x_line_end), category_center))
                if horizontal_label_side == "left":
                    x_lane, _ = ax.transData.inverted().transform((x_disp - dx_px, y_disp))
                    lane_gap_data = abs(float(x_lane) - float(x_line_end))
                else:
                    x_lane, _ = ax.transData.inverted().transform((x_disp + dx_px, y_disp))
                    lane_gap_data = abs(float(x_lane) - float(x_line_end))
            offset_data = float(offset_data) + float(lane_gap_data)

            if horizontal_label_side == "left":
                x_text = float(x_line_end) - float(offset_data)
            else:
                x_text = float(x_line_end) + float(offset_data)

            if float(label_min_clearance_points) > 0:
                fig = ax.figure
                dx_px = float(label_min_clearance_points) * float(fig.dpi) / 72.0
                x_disp, y_disp = ax.transData.transform((float(x_line_end), category_center))
                if horizontal_label_side == "left":
                    x_clear, _ = ax.transData.inverted().transform((x_disp - dx_px, y_disp))
                    x_text = min(float(x_text), float(x_clear))
                else:
                    x_clear, _ = ax.transData.inverted().transform((x_disp + dx_px, y_disp))
                    x_text = max(float(x_text), float(x_clear))
            label_x, label_y = float(x_text), category_center
            # For horizontal plots, return the furthest-right extent so callers can expand xlim.
            extent = max(float(x_line_end), float(label_x))
            max_annotation_y = float(extent) if max_annotation_y is None else max(max_annotation_y, float(extent))

        # For star labels, rendering as marker paths avoids the "superscript-looking" glyph
        # placement issue of ASCII '*' in some fonts (notably Arial).
        if (
            (not is_ns)
            and label_style == "stars"
            and stars_render_mode == "markers"
            and isinstance(stars_symbol, str)
            and len(stars_symbol) == 1
            and set(label) == {stars_symbol}
        ):
            n = int(len(label))
            if n > 0:
                fig = ax.figure
                # Convert point offsets to display pixels, then back to data coords.
                d_px = float(stars_marker_spacing_points) * float(fig.dpi) / 72.0
                x_disp, y_disp = ax.transData.transform((float(label_x), float(label_y)))
                inv = ax.transData.inverted()
                for k in range(n):
                    offset = (float(k) - (float(n) - 1.0) / 2.0) * d_px
                    if orientation == "vertical":
                        xk, _ = inv.transform((x_disp + offset, y_disp))
                        ax.scatter(
                            [float(xk)],
                            [float(label_y)],
                            marker=stars_marker,
                            s=float(stars_marker_size) ** 2,
                            c=[color],
                            alpha=float(text_alpha),
                            linewidths=float(stars_marker_line_width),
                            clip_on=False,
                            zorder=11,
                        )
                    else:
                        _, yk = inv.transform((x_disp, y_disp + offset))
                        ax.scatter(
                            [float(label_x)],
                            [float(yk)],
                            marker=stars_marker,
                            s=float(stars_marker_size) ** 2,
                            c=[color],
                            alpha=float(text_alpha),
                            linewidths=float(stars_marker_line_width),
                            clip_on=False,
                            zorder=11,
                        )
                # max_annotation_y already updated above for orientation
                return

        text_label = label
        text_rotation = float(label_rotation)
        text_rotation_mode = "default" if orientation == "horizontal" else "anchor"

        ax.text(
            float(label_x),
            float(label_y),
            text_label,
            ha=str(label_horizontal_alignment),
            va=str(effective_stars_label_vertical_alignment if is_stars_text else effective_label_vertical_alignment),
            fontsize=(font_size_ns if is_ns else font_size),
            color=color,
            alpha=float(text_alpha),
            fontfamily=font_family,
            rotation=float(text_rotation),
            rotation_mode=str(text_rotation_mode),
            zorder=11,
        )
        # max_annotation_y already updated above for orientation

    if bar_centers is not None:
        bc = np.asarray(bar_centers, dtype=float)
        if bc.shape != (int(num_categories), int(num_groups)):
            raise ValueError("bar_centers must have shape (num_categories, num_groups)")
    else:
        bc = None

    def _bar_center(j: int, i: int) -> float:
        if bc is not None:
            return float(bc[int(j), int(i)])
        # Backward-compatible fallback (assumes a fixed grouped offset of 0.4).
        return float(x_positions[j] - 0.4 + (i + 0.5) * bar_width)

    if pairs is not None:
        # Explicit comparisons; best for multi-group plots to avoid clutter and overlap.
        for j in range(num_categories):
            if enabled_categories is not None and int(j) not in enabled_categories:
                continue
            base_y = float(np.max(mean_data[j, :] + errors[j, :]))
            # Track which x-intervals are already used at each stacked height level so that
            # disjoint comparisons (e.g. (0,1) and (2,3)) can share the same y-height.
            levels: list[list[tuple[float, float]]] = []
            for (i0, i1) in pairs:
                g0 = int(i0) if i0 >= 0 else int(i0) + int(num_groups)
                g1 = int(i1) if i1 >= 0 else int(i1) + int(num_groups)
                if not (0 <= g0 < num_groups and 0 <= g1 < num_groups):
                    raise ValueError("pair indices out of range")
                ref_data = data[j, g0, :]
                comp_data = data[j, g1, :]
                if method == "mannwhitneyu":
                    _, p_val = mannwhitneyu(ref_data, comp_data, alternative="two-sided")
                else:
                    res = wilcoxon(ref_data, comp_data, alternative="two-sided")
                    p_val = res.pvalue

                signif_text = _significance_label(
                    float(p_val),
                    style=label_style,
                    p_threshold_nonsig_label=str(p_threshold_nonsig_label),
                    stars_symbol=str(stars_symbol),
                    stars_text_mode=stars_text_mode,
                    stars_mathtext_command=str(stars_mathtext_command),
                )
                if signif_text == "n.s.":
                    signif_text = ns_label
                    if not show_ns:
                        continue

                x0 = _bar_center(j, g0)
                x1 = _bar_center(j, g1)
                x_left = min(float(x0), float(x1))
                x_right = max(float(x0), float(x1))

                level_idx = 0
                if bool(stack_disjoint_pairs):
                    # Find first level where this interval does not overlap existing intervals.
                    for k, level in enumerate(levels):
                        overlaps = False
                        for (a, b) in level:
                            if not (x_right <= float(a) or x_left >= float(b)):
                                overlaps = True
                                break
                        if not overlaps:
                            level_idx = k
                            break
                    else:
                        level_idx = len(levels)

                    while len(levels) <= level_idx:
                        levels.append([])
                    levels[level_idx].append((x_left, x_right))
                else:
                    # Old behavior: always stack in the given order.
                    level_idx = len(levels)
                    levels.append([(x_left, x_right)])

                y1 = base_y + y_padding + float(level_idx) * step
                _draw_bracket(
                    x0=x_left,
                    x1=x_right,
                    y=float(y1),
                    label=signif_text,
                    lane_idx=int(level_idx),
                )
        return max_annotation_y

    if annotation_mode == "all":
        for j in range(num_categories):
            if enabled_categories is not None and int(j) not in enabled_categories:
                continue
            ref_data = data[j, 0, :]
            base_y = float(np.max(mean_data[j, :] + errors[j, :]))
            bracket_idx = 0
            for i in range(1, num_groups):
                comp_data = data[j, i, :]
                if method == "mannwhitneyu":
                    _, p_val = mannwhitneyu(ref_data, comp_data, alternative="two-sided")
                else:
                    res = wilcoxon(ref_data, comp_data, alternative="two-sided")
                    p_val = res.pvalue

                signif_text = _significance_label(
                    float(p_val),
                    style=label_style,
                    p_threshold_nonsig_label=str(p_threshold_nonsig_label),
                    stars_symbol=str(stars_symbol),
                    stars_text_mode=stars_text_mode,
                    stars_mathtext_command=str(stars_mathtext_command),
                )
                if signif_text == "n.s.":
                    signif_text = ns_label
                    if not show_ns:
                        continue

                y1 = base_y + y_padding + bracket_idx * step
                bracket_idx += 1

                x_ref = _bar_center(j, 0)
                x_comp = _bar_center(j, i)
                _draw_bracket(
                    x0=min(x_ref, x_comp),
                    x1=max(x_ref, x_comp),
                    y=float(y1),
                    label=signif_text,
                    lane_idx=int(bracket_idx - 1),
                )

    elif annotation_mode == "binary":
        for j in range(num_categories):
            if enabled_categories is not None and int(j) not in enabled_categories:
                continue
            rp = ref_position if ref_position >= 0 else ref_position + num_groups
            ref_data = data[j, rp, :]
            mask = np.arange(num_groups) != rp
            other_means = mean_data[j, mask]
            min_idx = int(np.argmin(other_means))
            comp_pos = int(np.where(mask)[0][min_idx])
            base_y = float(np.max(mean_data[j, [rp, comp_pos]] + errors[j, [rp, comp_pos]]))
            comp_data = data[j, comp_pos, :]
            if method == "mannwhitneyu":
                _, p_val = mannwhitneyu(ref_data, comp_data, alternative="two-sided")
            else:
                res = wilcoxon(ref_data, comp_data, alternative="two-sided")
                p_val = res.pvalue

            signif_text = _significance_label(
                float(p_val),
                style=label_style,
                p_threshold_nonsig_label=str(p_threshold_nonsig_label),
                stars_symbol=str(stars_symbol),
                stars_text_mode=stars_text_mode,
                stars_mathtext_command=str(stars_mathtext_command),
            )
            if signif_text == "n.s.":
                signif_text = ns_label
                if not show_ns:
                    continue

            y1 = base_y + y_padding + step
            x_ref = _bar_center(j, int(rp))
            x_comp = _bar_center(j, int(comp_pos))
            _draw_bracket(
                x0=min(x_ref, x_comp),
                x1=max(x_ref, x_comp),
                y=float(y1),
                label=signif_text,
                lane_idx=0,
            )

    return max_annotation_y
