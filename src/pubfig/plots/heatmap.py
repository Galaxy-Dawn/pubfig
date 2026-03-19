"""Heatmap plot functions (Matplotlib)."""

from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_cmap, resolve_design_dpi
from .._style import title_above
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def _style_colorbar(
    cb,  # type: ignore[valid-type]
    *,
    theme: Theme,
    label: str,
    outline_line_width: float,
    tick_font_size: Optional[int],
    label_font_size: Optional[int],
    tick_width: Optional[float],
    tick_length: Optional[float],
) -> None:
    """Apply a lightweight publication style to a Matplotlib colorbar."""
    cb.set_label(
        str(label),
        fontsize=int(theme.axis.label_font_size if label_font_size is None else label_font_size),
    )
    try:
        cb.outline.set_linewidth(float(outline_line_width))
    except Exception:
        pass
    try:
        cb.ax.tick_params(
            labelsize=int(theme.axis.tick_font_size if tick_font_size is None else tick_font_size),
            width=float(theme.axis.tick_width if tick_width is None else tick_width),
            length=float(max(0.0, theme.axis.tick_length * 0.5) if tick_length is None else tick_length),
        )
    except Exception:
        pass


def _apply_heatmap_cell_borders(
    ax,  # type: ignore[valid-type]
    *,
    shape: tuple[int, int],
    cell_border_line_width: float,
    cell_border_color: str,
) -> None:
    """Add optional thin separators between heatmap cells."""
    if float(cell_border_line_width) <= 0:
        return

    ax.set_xticks(np.arange(shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color=str(cell_border_color), linestyle="-", linewidth=float(cell_border_line_width))
    ax.tick_params(which="minor", bottom=False, left=False)


def heatmap(
    data: np.ndarray,
    *,
    x_label: Optional[str] = None,
    y_label: Optional[str] = None,
    category_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    colorscale: str = "Blues",
    zmin: Optional[float] = None,
    zmax: Optional[float] = None,
    annotate: bool = False,
    annotate_fmt: Optional[str] = None,
    annotate_fmt_normalize: str = ".2f",
    annotate_fmt_raw: str = ".0f",
    annotate_text_color_high: str = "white",
    annotate_text_color_low: str = "black",
    annotate_text_color_pivot: str = "mid",
    normalize: bool = False,
    imshow_origin: str = "upper",
    imshow_aspect_square: str = "equal",
    imshow_aspect_rect: str = "auto",
    imshow_interpolation: str = "nearest",
    cell_border_line_width: float = 0.0,
    cell_border_color: str = "white",
    cbar: bool = True,
    cbar_label: str = "Value",
    cbar_outline_line_width: float = 0.45,
    cbar_shrink: float = 0.9,
    cbar_pad: float = 0.03,
    cbar_tick_font_size: Optional[int] = None,
    cbar_label_font_size: Optional[int] = None,
    cbar_tick_width: Optional[float] = None,
    cbar_tick_length: Optional[float] = None,
    tick_rotation: float = 0.0,
    tick_ha: str = "right",
    tick_length: float = 0.0,
    show_spines: bool = False,
    annotate_font_size: Optional[int] = None,
    annotate_font_size_scale: float = 0.9,
    confusion_xlabel_default: str = "Predicted",
    confusion_ylabel_default: str = "Actual",
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a heatmap (also supports confusion matrix mode).

    Args:
        data: 2D array.
        x_label: X axis label. If `category_names` is provided and `x_label` is None, uses
            `confusion_xlabel_default`.
        y_label: Y axis label. If `category_names` is provided and `y_label` is None, uses
            `confusion_ylabel_default`.
        category_names: Optional shared tick labels for both axes (confusion-matrix style).
        title: Optional plot title.
        colorscale: Colormap name (passed through pubfig's colormap resolver).
        zmin: Lower bound for color scaling. If None, uses min(data).
        zmax: Upper bound for color scaling. If None, uses max(data).
        annotate: If True, annotate each cell with its numeric value.
        annotate_fmt: Explicit format specifier (e.g. \".2f\"). If None, uses
            `annotate_fmt_normalize` when `normalize=True`, else `annotate_fmt_raw`.
        annotate_fmt_normalize: Default annotation format when `normalize=True`.
        annotate_fmt_raw: Default annotation format when `normalize=False`.
        annotate_text_color_high: Text color used for cells above the pivot.
        annotate_text_color_low: Text color used for cells below the pivot.
        annotate_text_color_pivot: Pivot rule for switching colors: \"mid\" uses
            midpoint of (vmin, vmax); otherwise treated as a numeric threshold.
        normalize: If True, normalize each row to sum to 1 (composition view).
        imshow_origin: Origin passed to `imshow` (\"upper\" or \"lower\").
        imshow_aspect_square: Aspect used when the matrix is square.
        imshow_aspect_rect: Aspect used when the matrix is not square.
        imshow_interpolation: Interpolation mode passed to `imshow`.
        cell_border_line_width: Optional separator line width between adjacent cells.
        cell_border_color: Separator color used when `cell_border_line_width > 0`.
        cbar: If True, draw a colorbar.
        cbar_label: Colorbar label text.
        cbar_outline_line_width: Colorbar outline thickness (points).
        cbar_shrink: Colorbar shrink factor.
        cbar_pad: Colorbar padding in figure coordinates.
        cbar_tick_font_size: Optional colorbar tick font size override.
        cbar_label_font_size: Optional colorbar label font size override.
        cbar_tick_width: Optional colorbar tick width override.
        cbar_tick_length: Optional colorbar tick length override.
        tick_rotation: Rotation angle for x tick labels when `category_names` is provided.
        tick_ha: Horizontal alignment for rotated x tick labels.
        tick_length: Tick length override. A value of `0` removes tick marks for cleaner heatmaps.
        show_spines: Whether to keep heatmap axes spines visible.
        annotate_font_size: Optional font size override for cell annotations.
        annotate_font_size_scale: Scale factor applied to theme tick font size when
            `annotate_font_size` is not provided.
        confusion_xlabel_default: Default x label when in confusion-matrix mode.
        confusion_ylabel_default: Default y label when in confusion-matrix mode.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError("Data must be a 2D array.")

    if normalize:
        row_sums = data.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        data = data / row_sums

    cmap = resolve_cmap(colorscale)
    vmin = float(np.min(data)) if zmin is None else float(zmin)
    vmax = float(np.max(data)) if zmax is None else float(zmax)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        aspect = str(imshow_aspect_square) if data.shape[0] == data.shape[1] else str(imshow_aspect_rect)
        im = ax.imshow(
            data,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax,
            aspect=aspect,
            origin=str(imshow_origin),
            interpolation=str(imshow_interpolation),
        )
        _apply_heatmap_cell_borders(
            ax,
            shape=data.shape,
            cell_border_line_width=float(cell_border_line_width),
            cell_border_color=str(cell_border_color),
        )
        if bool(cbar):
            cb = fig.colorbar(im, ax=ax, shrink=float(cbar_shrink), pad=float(cbar_pad))
            _style_colorbar(
                cb,
                theme=t,
                label=str(cbar_label),
                outline_line_width=float(cbar_outline_line_width),
                tick_font_size=cbar_tick_font_size,
                label_font_size=cbar_label_font_size,
                tick_width=cbar_tick_width,
                tick_length=cbar_tick_length,
            )

        if category_names is not None:
            n = len(category_names)
            ax.set_xticks(list(range(n)), labels=category_names, rotation=float(tick_rotation), ha=str(tick_ha))
            ax.set_yticks(list(range(n)), labels=category_names)
            ax.set_xlabel(x_label or str(confusion_xlabel_default))
            ax.set_ylabel(y_label or str(confusion_ylabel_default))
        else:
            ax.set_xlabel(x_label or "X")
            ax.set_ylabel(y_label or "Y")

        if annotate:
            if str(annotate_text_color_pivot) == "mid":
                pivot = (float(vmin) + float(vmax)) / 2.0
            else:
                pivot = float(annotate_text_color_pivot)
            fmt = str(annotate_fmt) if annotate_fmt is not None else (str(annotate_fmt_normalize) if normalize else str(annotate_fmt_raw))
            for i in range(data.shape[0]):
                for j in range(data.shape[1]):
                    text_color = str(annotate_text_color_high) if float(data[i, j]) > pivot else str(annotate_text_color_low)
                    ax.text(
                        j,
                        i,
                        f"{data[i, j]:{fmt}}",
                        ha="center",
                        va="center",
                        color=text_color,
                        fontsize=int(
                            max(5, round(float(t.axis.tick_font_size) * float(annotate_font_size_scale)))
                            if annotate_font_size is None
                            else annotate_font_size
                        ),
                    )

        if title:
            title_above(ax, title, y=1.05)

        t.apply_axes(ax)
        ax.tick_params(length=float(tick_length))
        if not bool(show_spines):
            for spine in ax.spines.values():
                spine.set_visible(False)
        fig.tight_layout()
        return fig


def corr_matrix(
    data: np.ndarray,
    *,
    variable_names: Optional[list[str]] = None,
    method: str = "pearson",
    title: Optional[str] = None,
    colorscale: str = "RdBu_r",
    corr_vmin: float = -1.0,
    corr_vmax: float = 1.0,
    tick_rotation: float = 45.0,
    tick_ha: str = "right",
    cbar: bool = True,
    cbar_label: str = "r",
    cbar_outline_line_width: float = 0.45,
    cbar_shrink: float = 0.9,
    cbar_pad: float = 0.03,
    cbar_tick_font_size: Optional[int] = None,
    cbar_label_font_size: Optional[int] = None,
    cbar_tick_width: Optional[float] = None,
    cbar_tick_length: Optional[float] = None,
    annotate: bool = True,
    annotate_fmt: str = ".2f",
    annotate_text_color_high: str = "white",
    annotate_text_color_low: str = "black",
    annotate_abs_threshold: float = 0.5,
    tick_length: float = 0.0,
    show_spines: bool = False,
    annotate_font_size: Optional[int] = None,
    annotate_font_size_scale: float = 0.9,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a correlation matrix heatmap.

    Args:
        data: 2D array `(n_samples, n_variables)`.
        variable_names: Optional labels for the variables shown on both axes.
        method: Correlation method: `pearson`, `spearman`, or `kendall`.
        title: Optional plot title.
        colorscale: Colormap name.
        corr_vmin: Lower bound for color scaling.
        corr_vmax: Upper bound for color scaling.
        tick_rotation: Rotation angle for x tick labels.
        tick_ha: Horizontal alignment for rotated x tick labels.
        cbar: Whether to draw a colorbar.
        cbar_label: Colorbar label text.
        cbar_outline_line_width: Colorbar outline thickness (points).
        cbar_shrink: Colorbar shrink factor.
        cbar_pad: Colorbar padding in figure coordinates.
        cbar_tick_font_size: Optional colorbar tick font size override.
        cbar_label_font_size: Optional colorbar label font size override.
        cbar_tick_width: Optional colorbar tick width override.
        cbar_tick_length: Optional colorbar tick length override.
        annotate: Whether to annotate each cell.
        annotate_fmt: Format specifier for annotated correlation values.
        annotate_text_color_high: Text color used above the absolute threshold.
        annotate_text_color_low: Text color used below the absolute threshold.
        annotate_abs_threshold: Absolute-value threshold used to switch annotation colors.
        tick_length: Tick length override. A value of `0` removes tick marks.
        show_spines: Whether to keep heatmap axes spines visible.
        annotate_font_size: Optional font size override for cell annotations.
        annotate_font_size_scale: Scale factor applied to theme tick font size when
            `annotate_font_size` is not provided.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError("Data must be a 2D array (samples x features).")

    n_features = data.shape[1]
    if variable_names is None:
        variable_names = [f"Variable {i + 1}" for i in range(n_features)]

    if method == "pearson":
        corr = np.corrcoef(data, rowvar=False)
    else:
        from scipy import stats as sp_stats

        corr = np.zeros((n_features, n_features), dtype=float)
        for i in range(n_features):
            for j in range(n_features):
                if method == "spearman":
                    corr[i, j] = sp_stats.spearmanr(data[:, i], data[:, j]).statistic
                elif method == "kendall":
                    corr[i, j] = sp_stats.kendalltau(data[:, i], data[:, j]).statistic
                else:
                    raise ValueError("method must be 'pearson', 'spearman', or 'kendall'")

    cmap = resolve_cmap(colorscale)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        im = ax.imshow(corr, cmap=cmap, vmin=float(corr_vmin), vmax=float(corr_vmax), aspect="equal", origin="upper")
        if bool(cbar):
            cb = fig.colorbar(im, ax=ax, shrink=float(cbar_shrink), pad=float(cbar_pad))
            _style_colorbar(
                cb,
                theme=t,
                label=str(cbar_label),
                outline_line_width=float(cbar_outline_line_width),
                tick_font_size=cbar_tick_font_size,
                label_font_size=cbar_label_font_size,
                tick_width=cbar_tick_width,
                tick_length=cbar_tick_length,
            )

        ax.set_xticks(list(range(n_features)), labels=variable_names, rotation=float(tick_rotation), ha=str(tick_ha))
        ax.set_yticks(list(range(n_features)), labels=variable_names)

        if bool(annotate):
            thr = float(annotate_abs_threshold)
            for i in range(n_features):
                for j in range(n_features):
                    text_color = str(annotate_text_color_high) if abs(float(corr[i, j])) > thr else str(annotate_text_color_low)
                    ax.text(
                        j,
                        i,
                        f"{corr[i, j]:{str(annotate_fmt)}}",
                        ha="center",
                        va="center",
                        color=text_color,
                        fontsize=int(
                            max(5, round(float(t.axis.tick_font_size) * float(annotate_font_size_scale)))
                            if annotate_font_size is None
                            else annotate_font_size
                        ),
                    )

        if title:
            title_above(ax, title, y=1.05)

        t.apply_axes(ax)
        ax.tick_params(length=float(tick_length))
        if not bool(show_spines):
            for spine in ax.spines.values():
                spine.set_visible(False)
        fig.tight_layout()
        return fig


def clustermap(
    data: np.ndarray,
    *,
    row_category_names: Optional[list[str]] = None,
    column_category_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    colorscale: str = "Blues",
    linkage_method: str = "ward",
    imshow_aspect: str = "auto",
    imshow_origin: str = "upper",
    tick_rotation: float = 45.0,
    tick_ha: str = "right",
    cbar: bool = True,
    cbar_label: str = "Value",
    cbar_outline_line_width: float = 0.45,
    cbar_shrink: float = 0.9,
    cbar_pad: float = 0.03,
    cbar_tick_font_size: Optional[int] = None,
    cbar_label_font_size: Optional[int] = None,
    cbar_tick_width: Optional[float] = None,
    cbar_tick_length: Optional[float] = None,
    tick_length: float = 0.0,
    show_spines: bool = False,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a heatmap with hierarchical clustering reordering.

    Note:
        This function currently reorders the heatmap but does not draw dendrograms.

    Args:
        data: 2D array.
        row_category_names: Row labels used before and after clustering reorder.
        column_category_names: Column labels used before and after clustering reorder.
        title: Optional plot title.
        colorscale: Colormap name.
        linkage_method: Linkage method passed to SciPy hierarchical clustering.
        imshow_aspect: Aspect passed to `imshow`.
        imshow_origin: Origin passed to `imshow`.
        tick_rotation: Rotation angle for x tick labels.
        tick_ha: Horizontal alignment for rotated x tick labels.
        cbar: Whether to draw a colorbar.
        cbar_label: Colorbar label text.
        cbar_outline_line_width: Colorbar outline thickness (points).
        cbar_shrink: Colorbar shrink factor.
        cbar_pad: Colorbar padding in figure coordinates.
        cbar_tick_font_size: Optional colorbar tick font size override.
        cbar_label_font_size: Optional colorbar label font size override.
        cbar_tick_width: Optional colorbar tick width override.
        cbar_tick_length: Optional colorbar tick length override.
        tick_length: Tick length override. A value of `0` removes tick marks.
        show_spines: Whether to keep heatmap axes spines visible.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    from scipy.cluster.hierarchy import leaves_list, linkage

    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError("Data must be a 2D array.")

    n_rows, n_cols = data.shape
    if row_category_names is None:
        row_category_names = [f"Row {i}" for i in range(n_rows)]
    if column_category_names is None:
        column_category_names = [f"Column {i}" for i in range(n_cols)]

    row_link = linkage(data, method=str(linkage_method))
    col_link = linkage(data.T, method=str(linkage_method))
    row_order = leaves_list(row_link)
    col_order = leaves_list(col_link)

    ordered = data[row_order][:, col_order]
    row_category_names = [row_category_names[int(i)] for i in row_order]
    column_category_names = [column_category_names[int(i)] for i in col_order]

    cmap = resolve_cmap(colorscale)

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        im = ax.imshow(ordered, cmap=cmap, aspect=str(imshow_aspect), origin=str(imshow_origin))
        if bool(cbar):
            cb = fig.colorbar(im, ax=ax, shrink=float(cbar_shrink), pad=float(cbar_pad))
            _style_colorbar(
                cb,
                theme=t,
                label=str(cbar_label),
                outline_line_width=float(cbar_outline_line_width),
                tick_font_size=cbar_tick_font_size,
                label_font_size=cbar_label_font_size,
                tick_width=cbar_tick_width,
                tick_length=cbar_tick_length,
            )

        ax.set_xticks(
            list(range(n_cols)),
            labels=column_category_names,
            rotation=float(tick_rotation),
            ha=str(tick_ha),
        )
        ax.set_yticks(list(range(n_rows)), labels=row_category_names)
        if title:
            title_above(ax, title, y=1.05)

        t.apply_axes(ax)
        ax.tick_params(length=float(tick_length))
        if not bool(show_spines):
            for spine in ax.spines.values():
                spine.set_visible(False)
        fig.tight_layout()
        return fig
