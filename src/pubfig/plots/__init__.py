"""Plot functions."""

from .bar import bar, bar_scatter, stacked_bar
from .dimreduction import dimreduce, pca_biplot
from .distribution import box, density, histogram, raincloud, ridgeline, strip, violin
from .evaluation import pr_curve, roc
from .flow import parallel_coordinates, sankey
from .heatmap import clustermap, corr_matrix, heatmap
from .line import area, line
from .radar import radar
from .scatter import bubble, contour2d, paired, scatter

__all__ = [
    "bar",
    "bar_scatter",
    "stacked_bar",
    "box",
    "density",
    "histogram",
    "raincloud",
    "strip",
    "ridgeline",
    "violin",
    "line",
    "area",
    "radar",
    "scatter",
    "bubble",
    "contour2d",
    "paired",
    "heatmap",
    "corr_matrix",
    "clustermap",
    "dimreduce",
    "pca_biplot",
    "roc",
    "pr_curve",
    "sankey",
    "parallel_coordinates",
]
