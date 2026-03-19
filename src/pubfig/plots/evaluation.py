"""Evaluation metric plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_design_dpi
from .._style import (
    apply_cartesian_axis_controls,
    coerce_linewidth,
    legend_below_title,
    normalize_palette,
    title_above,
)
from ..colors.palettes import DEFAULT
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def roc(
    fpr,
    tpr,
    *,
    series_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    line_width: Optional[float] = None,
    auc_decimals: int = 3,
    baseline: bool = True,
    baseline_x: tuple[float, float] = (0.0, 1.0),
    baseline_y: tuple[float, float] = (0.0, 1.0),
    baseline_color: str = "0.72",
    baseline_line_width: Optional[float] = None,
    baseline_alpha: float = 0.9,
    baseline_linestyle: str = "--",
    xlim: tuple[float, float] = (0.0, 1.0),
    ylim: tuple[float, float] = (0.0, 1.0),
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 4,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create an ROC curve plot.

    Args:
        fpr: False-positive-rate array or list of arrays.
        tpr: True-positive-rate array or list of arrays.
        series_names: Labels for each ROC curve shown in the legend.
        title: Optional plot title.
        color_palette: Optional palette used for the curves.
        line_width: Line width for each ROC curve. If None, derives from the active theme.
        auc_decimals: Decimal places for AUC shown in the legend label.
        baseline: Whether to draw the diagonal baseline.
        baseline_x: X coordinates for the baseline segment (data units).
        baseline_y: Y coordinates for the baseline segment (data units).
        baseline_color: Baseline line color.
        baseline_line_width: Baseline line width. If None, derives from the active theme.
        baseline_alpha: Alpha for the baseline.
        baseline_linestyle: Baseline line style (e.g. \"--\").
        xlim: X axis limits.
        ylim: Y axis limits.
        legend_show: Whether to draw the legend.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns (only used when `legend_ncol` is None).
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    fpr_list = [fpr] if isinstance(fpr, np.ndarray) and fpr.ndim == 1 else list(fpr)
    tpr_list = [tpr] if isinstance(tpr, np.ndarray) and tpr.ndim == 1 else list(tpr)

    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(len(fpr_list))]

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.75 if line_width is None else float(line_width)
        )
        resolved_baseline_line_width = (
            float(coerce_linewidth(t, kind="ref")) * 0.7 if baseline_line_width is None else float(baseline_line_width)
        )

        for i, (fp, tp) in enumerate(zip(fpr_list, tpr_list)):
            fp = np.asarray(fp, dtype=float)
            tp = np.asarray(tp, dtype=float)
            auc_val = float(np.trapezoid(tp, fp))
            ax.plot(
                fp,
                tp,
                label=f"{series_names[i]} (AUC={auc_val:.{int(auc_decimals)}f})",
                color=colors[i % len(colors)],
                linewidth=resolved_line_width,
            )

        if bool(baseline):
            ax.plot(
                list(baseline_x),
                list(baseline_y),
                color=str(baseline_color),
                linewidth=resolved_baseline_line_width,
                alpha=float(baseline_alpha),
                linestyle=str(baseline_linestyle),
            )
        ax.set_xlim(float(xlim[0]), float(xlim[1]))
        ax.set_ylim(float(ylim[0]), float(ylim[1]))
        ax.set_xlabel("False Positive Rate")
        ax.set_ylabel("True Positive Rate")
        if title:
            title_above(ax, title)
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(fpr_list), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol))

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


def pr_curve(
    precision,
    recall,
    *,
    series_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    line_width: Optional[float] = None,
    ap_decimals: int = 3,
    xlim: tuple[float, float] = (0.0, 1.0),
    ylim: tuple[float, float] = (0.0, 1.0),
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 4,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a Precision-Recall curve plot.

    Args:
        precision: Precision array or list of arrays.
        recall: Recall array or list of arrays.
        series_names: Labels for each PR curve shown in the legend.
        title: Optional plot title.
        color_palette: Optional palette used for the curves.
        line_width: Line width for each PR curve. If None, derives from the active theme.
        ap_decimals: Decimal places for AP shown in the legend label.
        xlim: X axis limits (recall).
        ylim: Y axis limits (precision).
        legend_show: Whether to draw the legend.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns (only used when `legend_ncol` is None).
        tick_direction: Override tick direction on both axes ("in", "out", "inout").
        show_full_box: If True, show top/right spines to form a full box; if False, hide them.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    colors = normalize_palette(color_palette, fallback=DEFAULT)
    p_list = [precision] if isinstance(precision, np.ndarray) and precision.ndim == 1 else list(precision)
    r_list = [recall] if isinstance(recall, np.ndarray) and recall.ndim == 1 else list(recall)

    if series_names is None:
        series_names = [f"Series {i + 1}" for i in range(len(p_list))]

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.75 if line_width is None else float(line_width)
        )

        for i, (p, r) in enumerate(zip(p_list, r_list)):
            p = np.asarray(p, dtype=float)
            r = np.asarray(r, dtype=float)
            ap = float(np.trapezoid(p, r))
            ax.plot(
                r,
                p,
                label=f"{series_names[i]} (AP={abs(ap):.{int(ap_decimals)}f})",
                color=colors[i % len(colors)],
                linewidth=resolved_line_width,
            )

        ax.set_xlim(float(xlim[0]), float(xlim[1]))
        ax.set_ylim(float(ylim[0]), float(ylim[1]))
        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        if title:
            title_above(ax, title)
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(p_list), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol))

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
