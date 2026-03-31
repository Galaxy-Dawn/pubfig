"""Evaluation metric plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np
from sklearn.calibration import calibration_curve as sk_calibration_curve

from .._mpl_utils import get_fig_ax, resolve_design_dpi, resolve_figsize_inches
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


def _normalize_metric_series(data) -> list[np.ndarray]:
    arr = np.asarray(data)
    if isinstance(data, np.ndarray):
        if arr.ndim == 1:
            return [np.asarray(arr, dtype=float).reshape(-1)]
        if arr.ndim == 2:
            return [np.asarray(arr[:, idx], dtype=float).reshape(-1) for idx in range(arr.shape[1])]
    return [np.asarray(item, dtype=float).reshape(-1) for item in data]


def _resolve_truth_series(y_true, n_series: int) -> list[np.ndarray]:
    if isinstance(y_true, np.ndarray):
        if y_true.ndim == 1:
            base = np.asarray(y_true, dtype=float).reshape(-1)
            return [base.copy() for _ in range(n_series)]
        if y_true.ndim == 2 and y_true.shape[1] == n_series:
            return [np.asarray(y_true[:, idx], dtype=float).reshape(-1) for idx in range(y_true.shape[1])]
    truth_list = [np.asarray(item, dtype=float).reshape(-1) for item in y_true]
    if len(truth_list) != int(n_series):
        raise ValueError("y_true must be 1D, a 2D array with one column per series, or a list matching y_prob")
    return truth_list


def _calibration_bin_edges(prob: np.ndarray, *, n_bins: int, strategy: str) -> np.ndarray:
    mode = str(strategy).lower()
    if mode == "uniform":
        return np.linspace(0.0, 1.0, int(n_bins) + 1)
    if mode == "quantile":
        edges = np.quantile(prob, np.linspace(0.0, 1.0, int(n_bins) + 1))
        edges = np.unique(edges)
        if edges.size < 2:
            return np.linspace(0.0, 1.0, int(n_bins) + 1)
        if edges[0] > 0.0:
            edges = np.concatenate([[0.0], edges])
        if edges[-1] < 1.0:
            edges = np.concatenate([edges, [1.0]])
        return edges
    raise ValueError("strategy must be 'uniform' or 'quantile'")


def _expected_calibration_error(y_true: np.ndarray, y_prob: np.ndarray, *, n_bins: int, strategy: str) -> float:
    edges = _calibration_bin_edges(y_prob, n_bins=int(n_bins), strategy=str(strategy))
    bin_ids = np.digitize(y_prob, edges[1:-1], right=True)
    total = float(y_prob.size)
    ece = 0.0
    for idx in range(len(edges) - 1):
        mask = bin_ids == idx
        if not np.any(mask):
            continue
        acc = float(np.mean(y_true[mask]))
        conf = float(np.mean(y_prob[mask]))
        ece += abs(acc - conf) * (float(np.sum(mask)) / total)
    return float(ece)


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


def calibration(
    y_true,
    y_prob,
    *,
    series_names: Optional[Sequence[str]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    n_bins: int = 10,
    strategy: str = "quantile",
    show_hist: bool = True,
    show_perfect: bool = True,
    show_ece: bool = True,
    line_width: Optional[float] = None,
    hist_alpha: float = 0.18,
    hist_bins: int = 18,
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
    """Create a calibration / reliability diagram.

    Args:
        y_true: Binary ground-truth labels. Can be 1D (shared across series), 2D
            with one column per series, or a list of 1D arrays.
        y_prob: Predicted probabilities. Can be 1D, 2D, or a list of 1D arrays.
        series_names: Labels for the series shown in the legend.
        title: Optional plot title.
        color_palette: Optional palette used for the curves and histogram overlays.
        n_bins: Number of calibration bins.
        strategy: Bin strategy: ``"uniform"`` or ``"quantile"``.
        show_hist: Whether to include a lower probability histogram panel when `ax` is None.
        show_perfect: Whether to draw the perfect-calibration diagonal.
        show_ece: Whether to append ECE to legend labels.
        line_width: Curve line width override.
        hist_alpha: Alpha for histogram overlays.
        hist_bins: Number of histogram bins in the lower panel.
        legend_show: Whether to draw the legend.
        legend_ncol: Explicit legend column count.
        legend_ncol_max: Upper bound for legend columns when auto-resolving.
        tick_direction: Override tick direction on both axes.
        show_full_box: If True, show top/right spines to form a full box.
        show_x_grid: Whether to show dashed major grid lines on the x-axis.
        show_y_grid: Whether to show dashed major grid lines on the y-axis.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes for drawing the main reliability panel.
    """
    prob_list = _normalize_metric_series(y_prob)
    truth_list = _resolve_truth_series(y_true, len(prob_list))
    if series_names is None:
        names = [f"Series {idx + 1}" for idx in range(len(prob_list))]
    else:
        names = [str(name) for name in series_names]
        if len(names) != len(prob_list):
            raise ValueError("series_names must match the number of probability series")

    colors = normalize_palette(color_palette, fallback=DEFAULT)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        hist_ax = None
        if ax is None:
            import matplotlib.pyplot as plt

            figsize = resolve_figsize_inches(
                width_px=width,
                height_px=height,
                design_dpi=dpi,
                default_aspect_ratio=0.82,
            )
            if bool(show_hist):
                fig = plt.figure(figsize=figsize)
                grid = fig.add_gridspec(2, 1, height_ratios=(3.6, 1.0), hspace=0.08)
                ax = fig.add_subplot(grid[0, 0])
                hist_ax = fig.add_subplot(grid[1, 0], sharex=ax)
            else:
                fig, ax = get_fig_ax(ax=None, width_px=width, height_px=height, design_dpi=dpi)
        else:
            fig = ax.figure

        resolved_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.75 if line_width is None else float(line_width)
        )
        perfect_line_width = float(coerce_linewidth(t, kind="ref")) * 0.7

        for idx, (truth, prob, name) in enumerate(zip(truth_list, prob_list, names, strict=True)):
            truth_arr = np.asarray(truth, dtype=float).reshape(-1)
            prob_arr = np.clip(np.asarray(prob, dtype=float).reshape(-1), 0.0, 1.0)
            if truth_arr.shape != prob_arr.shape:
                raise ValueError("Each y_true series must match the corresponding y_prob series length")
            fraction_pos, mean_pred = sk_calibration_curve(
                truth_arr.astype(int),
                prob_arr,
                n_bins=int(n_bins),
                strategy=str(strategy),
            )
            label = str(name)
            if bool(show_ece):
                ece = _expected_calibration_error(truth_arr.astype(int), prob_arr, n_bins=int(n_bins), strategy=str(strategy))
                label = f"{label} (ECE={ece:.3f})"
            ax.plot(
                mean_pred,
                fraction_pos,
                color=colors[idx % len(colors)],
                linewidth=resolved_line_width,
                marker="o",
                markersize=max(float(t.axis.tick_font_size) * 0.28, 2.2),
                label=label,
            )
            if hist_ax is not None:
                hist_ax.hist(
                    prob_arr,
                    bins=int(hist_bins),
                    range=(0.0, 1.0),
                    color=colors[idx % len(colors)],
                    alpha=float(hist_alpha),
                    histtype="stepfilled",
                    linewidth=max(float(t.axis.line_width) * 0.45, 0.35),
                )

        if bool(show_perfect):
            ax.plot([0.0, 1.0], [0.0, 1.0], color="0.70", linestyle="--", linewidth=perfect_line_width, zorder=0)

        ax.set_xlim(0.0, 1.0)
        ax.set_ylim(0.0, 1.0)
        ax.set_xlabel("Predicted probability" if hist_ax is None else "")
        ax.set_ylabel("Observed frequency")
        if title:
            title_above(ax, title)
        if bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(prob_list), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol))

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid if show_y_grid is not None else True,
        )

        if hist_ax is not None:
            hist_ax.set_xlim(0.0, 1.0)
            hist_ax.set_xlabel("Predicted probability")
            hist_ax.set_ylabel("Count")
            t.apply_axes(hist_ax)
            apply_cartesian_axis_controls(
                hist_ax,
                tick_direction=tick_direction,
                show_full_box=show_full_box,
                show_x_grid=show_x_grid if show_x_grid is not None else False,
                show_y_grid=show_y_grid if show_y_grid is not None else False,
            )
            hist_ax.spines["top"].set_visible(False)
            try:
                ax.tick_params(axis="x", labelbottom=False)
            except Exception:
                pass

        if hist_ax is not None:
            fig.subplots_adjust(
                top=0.90 if (title or legend_show) else 0.97,
                bottom=0.13,
                left=0.12,
                right=0.97,
                hspace=0.08,
            )
        else:
            fig.tight_layout()
        return fig
