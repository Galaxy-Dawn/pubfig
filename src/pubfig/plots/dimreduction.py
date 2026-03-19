"""Dimensionality reduction plot functions (Matplotlib)."""

from __future__ import annotations

import warnings
from typing import Literal, Optional, TYPE_CHECKING

import numpy as np
from matplotlib.patches import Ellipse

from .._compat import _require
from .._mpl_utils import get_fig_ax, resolve_cmap, resolve_design_dpi
from .._style import apply_cartesian_axis_controls, legend_below_title, normalize_palette, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def dimreduce(
    data: np.ndarray,
    *,
    n_components: int = 2,
    cluster_id: Optional[np.ndarray] = None,
    labels: Optional[np.ndarray] = None,
    model: str = "tsne",
    title: Optional[str] = None,
    colorscale: Optional[str] = None,
    marker_size: Optional[int] = None,
    marker_size_2d_default: int = 5,
    marker_size_3d_default: int = 3,
    marker_alpha: float = 0.85,
    perplexity: int = 50,
    tsne_random_state: int = 42,
    label_max_points: int = 200,
    colorbar: bool = True,
    colorbar_label: str = "Cluster",
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> tuple["Figure", object]:
    """Create a dimensionality reduction scatter plot (2D or 3D).

    Args:
        data: 2D array `(n_samples, n_features)`.
        n_components: Output dimensionality (`2` or `3`).
        cluster_id: Optional numeric cluster assignments used for color encoding.
        labels: Optional per-point text labels. Only rendered in 2D and only when the point
            count is small enough (`label_max_points`).
        model: Dimensionality-reduction backend. Only `tsne` is supported.
        title: Optional plot title.
        colorscale: Optional colormap name used when `cluster_id` is provided.
        marker_size: Explicit scatter marker size. If None, use the 2D/3D defaults below.
        marker_size_2d_default: Default marker size when `n_components=2`.
        marker_size_3d_default: Default marker size when `n_components=3`.
        marker_alpha: Marker alpha.
        perplexity: t-SNE perplexity.
        tsne_random_state: Random seed for t-SNE.
        label_max_points: Maximum number of labels to draw directly on the plot.
        colorbar: Whether to draw a colorbar when `cluster_id` is provided.
        colorbar_label: Colorbar label text.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.

    Returns:
        Tuple of (Figure, fitted reducer).
    """
    if not isinstance(data, np.ndarray):
        raise ValueError("Input data must be a NumPy array.")
    if n_components not in (2, 3):
        raise ValueError("n_components must be 2 or 3.")

    if marker_size is None:
        marker_size = int(marker_size_2d_default) if n_components == 2 else int(marker_size_3d_default)

    if model != "tsne":
        raise ValueError("Only model='tsne' is supported.")

    _require("sklearn", "dimreduction")
    from sklearn.manifold import TSNE

    reducer = TSNE(n_components=n_components, random_state=int(tsne_random_state), perplexity=int(perplexity))
    reduced = reducer.fit_transform(data)
    default_title = f"{'3D ' if n_components == 3 else ''}t-SNE Plot"

    cmap = resolve_cmap(colorscale or "viridis")
    title = title or default_title

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        projection = "3d" if n_components == 3 else None
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi, projection=projection)

        if cluster_id is None:
            if n_components == 2:
                ax.scatter(
                    reduced[:, 0],
                    reduced[:, 1],
                    s=float(marker_size) ** 2,
                    color=DEFAULT[0],
                    alpha=float(marker_alpha),
                )
            else:
                ax.scatter(
                    reduced[:, 0],
                    reduced[:, 1],
                    reduced[:, 2],
                    s=float(marker_size) ** 2,
                    color=DEFAULT[0],
                    alpha=float(marker_alpha),
                )
        else:
            cid = np.asarray(cluster_id, dtype=float)
            if n_components == 2:
                sc = ax.scatter(
                    reduced[:, 0],
                    reduced[:, 1],
                    c=cid,
                    cmap=cmap,
                    s=float(marker_size) ** 2,
                    alpha=float(marker_alpha),
                )
            else:
                sc = ax.scatter(
                    reduced[:, 0],
                    reduced[:, 1],
                    reduced[:, 2],
                    c=cid,
                    cmap=cmap,
                    s=float(marker_size) ** 2,
                    alpha=float(marker_alpha),
                )
            if bool(colorbar):
                fig.colorbar(sc, ax=ax).set_label(str(colorbar_label))

        if labels is not None and n_components == 2:
            labels = np.asarray(labels)
            if labels.size <= int(label_max_points):  # keep large plots usable
                for (x0, y0), lab in zip(reduced[:, :2], labels):
                    ax.text(float(x0), float(y0), str(lab), fontsize=t.axis.tick_font_size)

        if n_components == 2:
            ax.set_xlabel("Component 1")
            ax.set_ylabel("Component 2")
        else:
            ax.set_xlabel("Component 1")
            ax.set_ylabel("Component 2")
            ax.set_zlabel("Component 3")

        ax.set_title(title, loc="center", fontfamily=t.font_family)
        t.apply_axes(ax)
        if n_components == 2:
            apply_cartesian_axis_controls(
                ax,
                tick_direction=tick_direction,
                show_full_box=show_full_box,
                show_x_grid=show_x_grid,
                show_y_grid=show_y_grid,
            )
        try:
            fig.tight_layout()
        except Exception:
            pass
        return fig, reducer


def pca_biplot(
    data: np.ndarray,
    *,
    variable_names: Optional[list[str]] = None,
    labels: Optional[np.ndarray] = None,
    title: Optional[str] = None,
    color_palette: Optional[list[str]] = None,
    arrow_color: Optional[str] = None,
    score_marker_size: float = 20.0,
    score_alpha: float = 0.85,
    score_edgecolor: str = "white",
    score_edge_line_width: float = 0.5,
    biplot_scale_ratio: float = 0.8,
    arrow_width: float = 0.0,
    arrow_head_width_ratio: float = 0.03,
    arrow_alpha: float = 1.0,
    loading_text_scale: float = 1.1,
    loading_panel: Literal["overlay", "separate", "none"] = "none",
    show_group_ellipse: bool = True,
    ellipse_confidence: float = 0.95,
    ellipse_linestyle: str = "--",
    ellipse_fill: bool = False,
    ellipse_fill_alpha: float = 0.5,
    ellipse_line_width: Optional[float] = None,
    pc_label_decimals: int = 1,
    legend_show: bool = True,
    legend_ncol: Optional[int] = None,
    legend_ncol_max: int = 6,
    tick_direction: str | None = None,
    show_full_box: Optional[bool] = None,
    show_x_grid: Optional[bool] = None,
    show_y_grid: Optional[bool] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a PCA biplot (scores + loading arrows).

    Args:
        data: 2D array `(n_samples, n_features)`.
        variable_names: Labels for loading arrows / variables.
        labels: Optional class labels used to color score points and build the legend.
        title: Optional plot title.
        color_palette: Optional palette used for classes and arrows.
        arrow_color: Optional override for loading arrow/text color. Defaults to black.
        score_marker_size: Marker size for the score scatter.
        score_alpha: Alpha for score points.
        score_edgecolor: Edge color for score points.
        score_edge_line_width: Edge line width for score points.
        biplot_scale_ratio: Scaling factor applied to the loading vectors.
        arrow_width: Arrow shaft width passed to Matplotlib.
        arrow_head_width_ratio: Arrow head width as a fraction of the max score extent.
        arrow_alpha: Alpha for loading text. Arrow shafts/heads are rendered opaque.
        loading_text_scale: Multiplicative offset used for variable text placement.
        loading_panel: How to render loading arrows. Use `"overlay"` to draw them on top of
            the scores (legacy behavior), `"separate"` to place them in a dedicated right-hand
            panel, or `"none"` to hide loadings entirely.
        show_group_ellipse: Whether to draw a confidence ellipse for each label group.
            Only applies when `labels` is provided.
        ellipse_confidence: Confidence level used to size the group ellipse.
        ellipse_linestyle: Line style for ellipse outlines.
        ellipse_fill: Whether to fill the inside of each ellipse with a translucent
            version of the group color.
        ellipse_fill_alpha: Alpha used for ellipse fills.
        ellipse_line_width: Optional line width for ellipse outlines. If None, infer from theme.
        pc_label_decimals: Decimal places for explained-variance percentages in axis labels.
        legend_show: Whether to draw the class legend when `labels` is provided.
        legend_ncol: Explicit legend column count. If None, uses `legend_ncol_max`.
        legend_ncol_max: Upper bound for legend columns.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    _require("sklearn", "dimreduction")
    from sklearn.decomposition import PCA

    data = np.asarray(data, dtype=float)
    n_samples, n_features = data.shape
    if variable_names is None:
        variable_names = [f"Variable {i + 1}" for i in range(n_features)]
    mode = str(loading_panel).strip().lower()
    if mode not in {"overlay", "separate", "none"}:
        raise ValueError("loading_panel must be 'overlay', 'separate', or 'none'")
    confidence = float(ellipse_confidence)
    if not (0.0 < confidence < 1.0):
        raise ValueError("ellipse_confidence must be in (0, 1)")

    pca = PCA(n_components=2)
    scores = pca.fit_transform(data)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    colors = normalize_palette(color_palette, fallback=DEFAULT)
    arrow_color = arrow_color or "#000000"

    def _ellipse_quantile_df2(conf: float) -> float:
        return float(-2.0 * np.log1p(-conf))

    def _draw_group_ellipse(
        target_ax,  # type: ignore[valid-type]
        group_scores: np.ndarray,
        *,
        color: str,
    ) -> tuple[float, float, float, float] | None:
        if group_scores.shape[0] < 2:
            return None
        cov = np.cov(group_scores[:, :2], rowvar=False)
        if not np.all(np.isfinite(cov)):
            return None
        eigenvalues, eigenvectors = np.linalg.eigh(cov)
        order = np.argsort(eigenvalues)[::-1]
        eigenvalues = np.clip(eigenvalues[order], a_min=0.0, a_max=None)
        eigenvectors = eigenvectors[:, order]
        if float(eigenvalues.max(initial=0.0)) <= 0.0:
            return None

        scale = np.sqrt(_ellipse_quantile_df2(confidence))
        width = float(2.0 * scale * np.sqrt(eigenvalues[0]))
        height = float(2.0 * scale * np.sqrt(eigenvalues[1]))
        center = np.mean(group_scores[:, :2], axis=0)
        angle = float(np.degrees(np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])))

        if bool(ellipse_fill):
            target_ax.add_patch(
                Ellipse(
                    xy=(float(center[0]), float(center[1])),
                    width=width,
                    height=height,
                    angle=angle,
                    facecolor=color_to_rgba(color, alpha=float(ellipse_fill_alpha)),
                    edgecolor="none",
                    linewidth=0.0,
                    zorder=1.0,
                )
            )

        target_ax.add_patch(
            Ellipse(
                xy=(float(center[0]), float(center[1])),
                width=width,
                height=height,
                angle=angle,
                facecolor="none",
                edgecolor=color,
                linestyle=str(ellipse_linestyle),
                linewidth=(
                    float(ellipse_line_width)
                    if ellipse_line_width is not None
                    else max(0.8, float(t.axis.line_width))
                ),
                zorder=2.0,
            )
        )

        theta = np.deg2rad(angle)
        a = width / 2.0
        b = height / 2.0
        x_extent = float(np.sqrt((a * np.cos(theta)) ** 2 + (b * np.sin(theta)) ** 2))
        y_extent = float(np.sqrt((a * np.sin(theta)) ** 2 + (b * np.cos(theta)) ** 2))
        return (
            float(center[0]) - x_extent,
            float(center[0]) + x_extent,
            float(center[1]) - y_extent,
            float(center[1]) + y_extent,
        )

    def _draw_loadings(
        target_ax,  # type: ignore[valid-type]
        *,
        scale_factor: float,
        max_extent: float,
        draw_axis_labels: bool,
        clip_to_axes: bool,
    ) -> list[tuple[float, float]]:
        if mode == "none":
            return []
        label_positions: list[tuple[float, float]] = []
        arrow_line_width = float(arrow_width) if float(arrow_width) > 0 else max(0.8, float(t.axis.line_width))
        arrow_mutation_scale = max(8.0, 420.0 * float(arrow_head_width_ratio))
        text_offset_points = max(1.0, 2.2 * float(loading_text_scale))
        for i in range(n_features):
            x1 = float(loadings[i, 0] * scale_factor)
            y1 = float(loadings[i, 1] * scale_factor)
            target_ax.annotate(
                "",
                xy=(x1, y1),
                xytext=(0.0, 0.0),
                arrowprops={
                    "arrowstyle": "-|>",
                    "color": arrow_color,
                    "lw": arrow_line_width,
                    "shrinkA": 0.0,
                    "shrinkB": 0.0,
                    "mutation_scale": arrow_mutation_scale,
                },
                annotation_clip=bool(clip_to_axes),
            )

            end_disp = np.asarray(target_ax.transData.transform((x1, y1)), dtype=float)
            origin_disp = np.asarray(target_ax.transData.transform((0.0, 0.0)), dtype=float)
            direction_disp = end_disp - origin_disp
            norm_disp = float(np.linalg.norm(direction_disp))
            if norm_disp > 1e-12:
                unit_disp = direction_disp / norm_disp
            else:
                unit_disp = np.asarray([0.0, 1.0], dtype=float)
            offset_points = unit_disp * text_offset_points
            text_ha = "left" if offset_points[0] >= 0 else "right"
            text_va = "bottom" if offset_points[1] >= 0 else "top"

            target_ax.annotate(
                variable_names[i],
                xy=(x1, y1),
                xytext=(float(offset_points[0]), float(offset_points[1])),
                textcoords="offset points",
                ha=text_ha,
                va=text_va,
                color=color_to_rgba(arrow_color, alpha=float(arrow_alpha)),
                fontsize=t.axis.tick_font_size,
                annotation_clip=bool(clip_to_axes),
            )

            px_to_disp = float(target_ax.figure.dpi) / 72.0
            label_anchor_disp = end_disp + offset_points * px_to_disp
            label_anchor_data = target_ax.transData.inverted().transform(label_anchor_disp)
            label_positions.append((float(label_anchor_data[0]), float(label_anchor_data[1])))
        if draw_axis_labels:
            target_ax.axhline(0.0, color="0.82", linewidth=max(0.4, float(t.axis.line_width) * 0.8), zorder=0)
            target_ax.axvline(0.0, color="0.82", linewidth=max(0.4, float(t.axis.line_width) * 0.8), zorder=0)
            target_ax.set_xlim(-float(max_extent), float(max_extent))
            target_ax.set_ylim(-float(max_extent), float(max_extent))
            target_ax.set_xticks([])
            target_ax.set_yticks([])
            target_ax.set_xlabel("")
            target_ax.set_ylabel("")
            target_ax.set_title(
                "Loadings",
                fontsize=float(t.axis.label_font_size),
                fontweight="semibold",
                fontfamily=t.font_family,
            )
            for spine in target_ax.spines.values():
                spine.set_visible(False)
        return label_positions

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        loading_ax = None
        ellipse_bounds: list[tuple[float, float, float, float]] = []

        if labels is not None:
            labels = np.asarray(labels)
            uniq = np.unique(labels)
            for i, lab in enumerate(uniq):
                mask = labels == lab
                group_color = colors[i % len(colors)]
                if bool(show_group_ellipse):
                    bounds = _draw_group_ellipse(ax, scores[mask, :2], color=group_color)
                    if bounds is not None:
                        ellipse_bounds.append(bounds)
                ax.scatter(
                    scores[mask, 0],
                    scores[mask, 1],
                    s=float(score_marker_size),
                    label=str(lab),
                    color=group_color,
                    alpha=float(score_alpha),
                    edgecolor=str(score_edgecolor),
                    linewidth=float(score_edge_line_width),
                    zorder=3.0,
                )
        else:
            ax.scatter(
                scores[:, 0],
                scores[:, 1],
                s=float(score_marker_size),
                color=colors[0],
                alpha=float(score_alpha),
                edgecolor=str(score_edgecolor),
                linewidth=float(score_edge_line_width),
                zorder=3.0,
            )

        max_score = float(np.abs(scores[:, :2]).max()) if scores.size else 1.0
        max_load = float(np.abs(loadings).max()) if loadings.size else 1.0
        overlay_scale = (max_score / max_load) * float(biplot_scale_ratio) if max_load > 0 else 1.0
        panel_extent = max(1.0, float(biplot_scale_ratio))
        panel_scale = (float(panel_extent) / max_load) * float(biplot_scale_ratio) if max_load > 0 else 1.0

        if mode == "overlay":
            overlay_label_positions = _draw_loadings(
                ax,
                scale_factor=overlay_scale,
                max_extent=max_score,
                draw_axis_labels=False,
                clip_to_axes=False,
            )
            x_parts = [scores[:, 0], np.asarray([pt[0] for pt in overlay_label_positions], dtype=float)]
            y_parts = [scores[:, 1], np.asarray([pt[1] for pt in overlay_label_positions], dtype=float)]
            if ellipse_bounds:
                x_parts.append(
                    np.asarray(
                        [bound[0] for bound in ellipse_bounds] + [bound[1] for bound in ellipse_bounds],
                        dtype=float,
                    )
                )
                y_parts.append(
                    np.asarray(
                        [bound[2] for bound in ellipse_bounds] + [bound[3] for bound in ellipse_bounds],
                        dtype=float,
                    )
                )
            x_values = np.concatenate(x_parts)
            y_values = np.concatenate(y_parts)
            x_span = float(np.ptp(x_values)) if x_values.size else 1.0
            y_span = float(np.ptp(y_values)) if y_values.size else 1.0
            x_pad = max(0.35, x_span * 0.08)
            y_pad_lower = max(0.35, y_span * 0.08)
            y_pad_upper = max(0.55, y_span * 0.16)
            ax.set_xlim(float(np.min(x_values)) - x_pad, float(np.max(x_values)) + x_pad)
            ax.set_ylim(float(np.min(y_values)) - y_pad_lower, float(np.max(y_values)) + y_pad_upper)
        elif mode == "separate":
            loading_ax = fig.add_axes([0.76, 0.22, 0.18, 0.18])
            _draw_loadings(
                loading_ax,
                scale_factor=panel_scale,
                max_extent=panel_extent,
                draw_axis_labels=True,
                clip_to_axes=False,
            )

        var1 = float(pca.explained_variance_ratio_[0] * 100)
        var2 = float(pca.explained_variance_ratio_[1] * 100)
        ax.set_xlabel(f"PC1 ({var1:.{int(pc_label_decimals)}f}%)")
        ax.set_ylabel(f"PC2 ({var2:.{int(pc_label_decimals)}f}%)")
        if title:
            title_above(ax, title)
        if labels is not None and bool(legend_show):
            ncol = int(legend_ncol) if legend_ncol is not None else max(1, min(len(uniq), int(legend_ncol_max)))
            legend_below_title(ax, ncol=int(ncol), gap=0.02 if mode == "overlay" else 0.02)

        if loading_ax is not None:
            def _apply_biplot_layout() -> None:
                pos = ax.get_position()
                main_width = float(pos.width) * 0.72
                gap = float(pos.width) * 0.06
                panel_width = float(pos.width) - main_width - gap
                ax.set_position([float(pos.x0), float(pos.y0), main_width, float(pos.height)])
                loading_ax.set_position(
                    [
                        float(pos.x0) + main_width + gap,
                        float(pos.y0) + float(pos.height) * 0.17,
                        max(0.12, panel_width),
                        float(pos.height) * 0.46,
                    ]
                )
            setattr(ax, "_pubfig_post_layout", _apply_biplot_layout)

        t.apply_axes(ax)
        apply_cartesian_axis_controls(
            ax,
            tick_direction=tick_direction,
            show_full_box=show_full_box,
            show_x_grid=show_x_grid,
            show_y_grid=show_y_grid,
        )
        if loading_ax is not None:
            loading_ax.set_facecolor(t.background_color)
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="This figure includes Axes that are not compatible with tight_layout*",
                category=UserWarning,
            )
            fig.tight_layout()
        callback = getattr(ax, "_pubfig_post_layout", None)
        if callable(callback):
            callback()
        return fig
