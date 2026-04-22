"""Stable plot registry for agent-first CLI rendering."""

from __future__ import annotations

from collections.abc import Callable

from .plots import (
    area,
    bar,
    bar_scatter,
    bland_altman,
    box,
    bubble,
    calibration,
    circular_grouped_bar,
    circular_stacked_bar,
    clustermap,
    contour2d,
    corr_matrix,
    density,
    dimreduce,
    donut,
    dumbbell,
    ecdf,
    forest_plot,
    grouped_scatter,
    heatmap,
    hexbin,
    histogram,
    line,
    paired,
    parallel_coordinates,
    pca_biplot,
    pr_curve,
    qq,
    radar,
    radial_hierarchy,
    raincloud,
    ridgeline,
    roc,
    sankey,
    scatter,
    stacked_bar,
    stacked_ratio_barh,
    strip,
    upset,
    violin,
    volcano,
)


PLOT_REGISTRY: dict[str, Callable[..., object]] = {
    "bar": bar,
    "bar_scatter": bar_scatter,
    "stacked_bar": stacked_bar,
    "stacked_ratio_barh": stacked_ratio_barh,
    "donut": donut,
    "dumbbell": dumbbell,
    "forest_plot": forest_plot,
    "grouped_scatter": grouped_scatter,
    "upset": upset,
    "ecdf": ecdf,
    "qq": qq,
    "bland_altman": bland_altman,
    "box": box,
    "density": density,
    "hexbin": hexbin,
    "histogram": histogram,
    "raincloud": raincloud,
    "strip": strip,
    "ridgeline": ridgeline,
    "violin": violin,
    "line": line,
    "area": area,
    "radial_hierarchy": radial_hierarchy,
    "circular_stacked_bar": circular_stacked_bar,
    "circular_grouped_bar": circular_grouped_bar,
    "radar": radar,
    "scatter": scatter,
    "volcano": volcano,
    "bubble": bubble,
    "contour2d": contour2d,
    "paired": paired,
    "heatmap": heatmap,
    "corr_matrix": corr_matrix,
    "clustermap": clustermap,
    "dimreduce": dimreduce,
    "pca_biplot": pca_biplot,
    "roc": roc,
    "pr_curve": pr_curve,
    "calibration": calibration,
    "sankey": sankey,
    "parallel_coordinates": parallel_coordinates,
}


def list_plot_kinds() -> list[str]:
    """Return the stable CLI plot kinds."""
    return list(PLOT_REGISTRY.keys())


def get_plot_callable(kind: str) -> Callable[..., object]:
    """Resolve a plot kind to its callable."""
    try:
        return PLOT_REGISTRY[str(kind)]
    except KeyError as error:
        raise KeyError(f"Unknown plot kind: {kind}") from error


__all__ = ["PLOT_REGISTRY", "get_plot_callable", "list_plot_kinds"]
