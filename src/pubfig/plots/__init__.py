"""Plot functions."""

from .bar import bar, bar_scatter, stacked_bar
from .comparison import dumbbell, forest_plot
from .composition import donut, grouped_scatter, stacked_ratio_barh, upset
from .diagnostics import bland_altman, ecdf, qq
from .dimreduction import dimreduce, pca_biplot
from .distribution import box, density, histogram, raincloud, ridgeline, strip, violin
from .evaluation import calibration, pr_curve, roc
from .flow import parallel_coordinates, sankey
from .heatmap import clustermap, corr_matrix, heatmap
from .line import area, line
from .polar import circular_grouped_bar, circular_stacked_bar, radial_hierarchy
from .radar import radar
from .specialized import hexbin, volcano
from .scatter import bubble, contour2d, paired, scatter

__all__ = [
    "bar",
    "bar_scatter",
    "stacked_bar",
    "dumbbell",
    "forest_plot",
    "donut",
    "grouped_scatter",
    "stacked_ratio_barh",
    "upset",
    "ecdf",
    "qq",
    "bland_altman",
    "box",
    "density",
    "histogram",
    "raincloud",
    "strip",
    "ridgeline",
    "violin",
    "line",
    "area",
    "radial_hierarchy",
    "circular_stacked_bar",
    "circular_grouped_bar",
    "radar",
    "hexbin",
    "volcano",
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
    "calibration",
    "sankey",
    "parallel_coordinates",
]
