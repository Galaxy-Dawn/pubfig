"""Flow and relationship plot functions (Matplotlib)."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Optional, Sequence, TYPE_CHECKING

import numpy as np

from .._mpl_utils import get_fig_ax, resolve_cmap, resolve_design_dpi
from .._style import coerce_linewidth, title_above
from ..colors.palettes import DEFAULT
from ..colors.utils import color_to_rgba
from ..themes import Theme, theme_context

if TYPE_CHECKING:  # pragma: no cover
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def parallel_coordinates(
    data: np.ndarray,
    *,
    variable_names: Optional[list[str]] = None,
    color_col: Optional[int] = None,
    colorscale: str = "cividis",
    title: Optional[str] = None,
    line_color: str = DEFAULT[0],
    line_alpha: float = 0.14,
    line_width: Optional[float] = None,
    color_line_width: Optional[float] = None,
    color_line_alpha: float = 0.45,
    y_min: float = 0.0,
    y_max: float = 1.0,
    tick_rotation: float = 0.0,
    tick_ha: str = "center",
    y_label: str = "Normalized value",
    colorbar: bool = True,
    colorbar_label_font_size: Optional[int] = None,
    colorbar_tick_font_size: Optional[int] = None,
    colorbar_outline_line_width: float = 0.4,
    axis_vline_color: str = "0.88",
    axis_vline_line_width: float = 0.5,
    axis_vline_zorder: int = 0,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a parallel coordinates plot.

    Args:
        data: 2D array `(n_samples, n_variables)`.
        variable_names: Labels for each plotted dimension / variable.
        color_col: Optional column index used to color lines by value.
        colorscale: Colormap name used when `color_col` is set.
        title: Optional plot title.
        line_color: Color used when `color_col` is None.
        line_alpha: Alpha used when `color_col` is None.
        line_width: Line width used when `color_col` is None. If None, derives from the active theme.
        color_line_width: Line width used when `color_col` is set. If None, derives from the active theme.
        color_line_alpha: Alpha used when `color_col` is set.
        y_min: Minimum y in normalized space.
        y_max: Maximum y in normalized space.
        tick_rotation: Rotation angle for dimension labels.
        tick_ha: Horizontal alignment for rotated ticks.
        y_label: Y axis label text.
        colorbar: Whether to draw a colorbar when `color_col` is set.
        colorbar_label_font_size: Optional colorbar label font size override.
        colorbar_tick_font_size: Optional colorbar tick font size override.
        colorbar_outline_line_width: Colorbar outline thickness.
        axis_vline_color: Color of faint vertical guide lines at each variable axis.
        axis_vline_line_width: Line width of variable guide lines.
        axis_vline_zorder: Z-order of variable guide lines.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    from matplotlib.collections import LineCollection
    from matplotlib.colors import Normalize
    import matplotlib as mpl

    data = np.asarray(data, dtype=float)
    if data.ndim != 2:
        raise ValueError("data must be a 2D array (n_samples, n_features)")
    n_samples, n_features = data.shape
    if variable_names is None:
        variable_names = [f"Variable {i + 1}" for i in range(n_features)]

    mins = np.min(data, axis=0)
    maxs = np.max(data, axis=0)
    denom = maxs - mins
    denom[denom == 0] = 1.0
    normed = (data - mins) / denom

    x = np.arange(n_features, dtype=float)
    segments = [np.column_stack([x, normed[i]]) for i in range(n_samples)]

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)
        resolved_line_width = float(coerce_linewidth(t, kind="data")) * 0.55 if line_width is None else float(line_width)
        resolved_color_line_width = (
            float(coerce_linewidth(t, kind="data")) * 0.6 if color_line_width is None else float(color_line_width)
        )

        for xv in x:
            ax.axvline(
                float(xv),
                color=str(axis_vline_color),
                linewidth=float(axis_vline_line_width),
                zorder=int(axis_vline_zorder),
            )

        if color_col is None:
            lc = LineCollection(
                segments,
                colors=[color_to_rgba(str(line_color), alpha=float(line_alpha))],
                linewidths=resolved_line_width,
            )
            ax.add_collection(lc)
        else:
            cc = int(color_col)
            if not (0 <= cc < n_features):
                raise ValueError("color_col out of range")
            cmap = mpl.colormaps.get_cmap(resolve_cmap(colorscale))
            vals = data[:, cc]
            norm = Normalize(vmin=float(np.min(vals)), vmax=float(np.max(vals)))
            lc = LineCollection(
                segments,
                cmap=cmap,
                norm=norm,
                linewidths=resolved_color_line_width,
                alpha=float(color_line_alpha),
            )
            lc.set_array(vals)
            ax.add_collection(lc)
            if bool(colorbar):
                cb = fig.colorbar(lc, ax=ax, pad=0.03, shrink=0.9)
                cb.set_label(
                    variable_names[cc],
                    fontsize=int(t.axis.label_font_size if colorbar_label_font_size is None else colorbar_label_font_size),
                )
                cb.outline.set_linewidth(float(colorbar_outline_line_width))
                cb.ax.tick_params(
                    labelsize=int(t.axis.tick_font_size if colorbar_tick_font_size is None else colorbar_tick_font_size),
                    width=float(t.axis.tick_width),
                    length=float(max(0.0, t.axis.tick_length * 0.5)),
                )

        ax.set_xlim(float(x.min()) - 0.02, float(x.max()) + 0.02)
        ax.set_ylim(float(y_min), float(y_max))
        ax.set_xticks(x, labels=variable_names)
        ax.set_ylabel(str(y_label))
        if title:
            title_above(ax, title)

        t.apply_axes(ax)
        for tick_label in ax.get_xticklabels():
            tick_label.set_rotation(float(tick_rotation))
            tick_label.set_horizontalalignment(str(tick_ha))
            tick_label.set_fontstyle("normal")
        fig.tight_layout()
        return fig


@dataclass(frozen=True)
class _Link:
    source: int
    target: int
    value: float


def sankey(
    source: list[int],
    target: list[int],
    value: list[float],
    *,
    node_names: Optional[list[str]] = None,
    title: Optional[str] = None,
    color_palette: Optional[Sequence[str]] = None,
    x_margin: float = 0.03,
    y_margin: float = 0.018,
    node_width: float = 0.028,
    node_pad: float = 0.018,
    axes_span: float = 1.0,
    unit_default: float = 1.0,
    link_alpha: float = 0.18,
    link_zorder: int = 1,
    curve_strength: float = 0.42,
    dag_dx_fallback: float = 0.05,
    node_face_alpha: float = 0.9,
    node_edgecolor: str = "0.25",
    node_line_width: float = 0.4,
    node_zorder: int = 2,
    node_text_zorder: int = 3,
    node_label_fontsize: Optional[int] = None,
    theme: Optional[Theme] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    ax: Optional["Axes"] = None,
) -> "Figure":
    """Create a Sankey diagram (DAG only).

    Note:
        Cyclic graphs are not supported.

    Args:
        source: Source node indices for each link.
        target: Target node indices for each link.
        value: Link weights.
        node_names: Labels for each node.
        title: Optional plot title.
        color_palette: Optional palette used for nodes and links.
        x_margin: Left/right padding in axes coordinates.
        y_margin: Top/bottom padding in axes coordinates.
        node_width: Node rectangle width in axes coordinates.
        node_pad: Vertical spacing between nodes in a layer.
        axes_span: Effective axes span used for layout.
        unit_default: Fallback scaling factor when total flow is zero.
        link_alpha: Alpha for link patches.
        link_zorder: Z-order for link patches.
        curve_strength: Cubic-Bezier curvature strength for links.
        dag_dx_fallback: Fallback horizontal spacing when a DAG layer delta collapses.
        node_face_alpha: Alpha for node fills.
        node_edgecolor: Node border color.
        node_line_width: Node border line width.
        node_zorder: Z-order for node rectangles.
        node_text_zorder: Z-order for node labels.
        node_label_fontsize: Optional font size override for node labels.
        theme: Optional pubfig Theme.
        width: Figure width in pixels.
        height: Figure height in pixels.
        ax: Optional Matplotlib Axes to draw into.
    """
    from matplotlib.patches import PathPatch, Rectangle
    from matplotlib.path import Path

    if not (len(source) == len(target) == len(value)):
        raise ValueError("source, target, and value must have the same length")

    links = [_Link(int(s), int(t), float(v)) for s, t, v in zip(source, target, value)]
    n_nodes = 0
    if links:
        n_nodes = max(max(lnk.source, lnk.target) for lnk in links) + 1
    if node_names is None:
        node_names = [f"Node {i}" for i in range(n_nodes)]
    if len(node_names) != n_nodes:
        raise ValueError("node_names length must match the number of nodes")

    colors = list(color_palette) if color_palette is not None else list(DEFAULT)

    in_flow = np.zeros(n_nodes, dtype=float)
    out_flow = np.zeros(n_nodes, dtype=float)
    outgoing: list[list[int]] = [[] for _ in range(n_nodes)]
    incoming: list[list[int]] = [[] for _ in range(n_nodes)]
    indegree = np.zeros(n_nodes, dtype=int)

    for idx, lnk in enumerate(links):
        out_flow[lnk.source] += lnk.value
        in_flow[lnk.target] += lnk.value
        outgoing[lnk.source].append(idx)
        incoming[lnk.target].append(idx)
        indegree[lnk.target] += 1

    node_value = np.maximum(in_flow, out_flow)

    # Topological order (detect cycles).
    q: deque[int] = deque([i for i in range(n_nodes) if indegree[i] == 0])
    topo: list[int] = []
    indeg = indegree.copy()
    while q:
        u = q.popleft()
        topo.append(u)
        for li in outgoing[u]:
            v = links[li].target
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
    if len(topo) != n_nodes and n_nodes > 0:
        raise ValueError("Cyclic Sankey is not supported (graph contains a cycle)")

    layer = np.zeros(n_nodes, dtype=int)
    for u in topo:
        for li in outgoing[u]:
            v = links[li].target
            layer[v] = max(int(layer[v]), int(layer[u]) + 1)
    max_layer = int(layer.max()) if n_nodes > 0 else 0

    nodes_by_layer: dict[int, list[int]] = {i: [] for i in range(max_layer + 1)}
    for i in range(n_nodes):
        nodes_by_layer[int(layer[i])].append(i)
    for layer_idx in nodes_by_layer:
        nodes_by_layer[layer_idx].sort(key=lambda n: float(node_value[n]), reverse=True)

    # Compute a global scale that fits all layers.
    scales: list[float] = []
    for nodes in nodes_by_layer.values():
        if not nodes:
            continue
        total = float(np.sum(node_value[nodes]))
        if total <= 0:
            continue
        avail = float(axes_span) - 2 * float(y_margin) - float(node_pad) * (len(nodes) - 1)
        scales.append(avail / total)
    unit = min(scales) if scales else float(unit_default)

    # Node boxes.
    x_left = np.zeros(n_nodes, dtype=float)
    y0 = np.zeros(n_nodes, dtype=float)
    y1 = np.zeros(n_nodes, dtype=float)
    h = node_value * unit

    avail_x = float(axes_span) - 2 * float(x_margin) - float(node_width)
    for n in range(n_nodes):
        frac = (float(layer[n]) / float(max_layer)) if max_layer > 0 else 0.0
        x_left[n] = float(x_margin) + frac * avail_x

    for nodes in nodes_by_layer.values():
        if not nodes:
            continue
        total_h = float(np.sum(h[nodes])) + node_pad * (len(nodes) - 1)
        rem = max(0.0, float(axes_span) - 2 * float(y_margin) - total_h)
        y = float(axes_span) - float(y_margin) - rem / 2
        for n in nodes:
            y1[n] = y
            y0[n] = y - float(h[n])
            y = y0[n] - float(node_pad)

    # Link segment allocation.
    out_cursor = y1.copy()
    in_cursor = y1.copy()
    link_seg: list[tuple[int, float, float, float, float]] = []  # (link_idx, sy0, sy1, ty0, ty1)

    y_center = (y0 + y1) / 2
    for src in range(n_nodes):
        outgoing[src].sort(key=lambda li: float(y_center[links[li].target]), reverse=True)
    for tgt in range(n_nodes):
        incoming[tgt].sort(key=lambda li: float(y_center[links[li].source]), reverse=True)

    # Pre-allocate target segments first (stable lookup by link index).
    ty0 = np.zeros(len(links), dtype=float)
    ty1 = np.zeros(len(links), dtype=float)
    for tgt in range(n_nodes):
        for li in incoming[tgt]:
            thick = float(links[li].value) * unit
            ty1[li] = in_cursor[tgt]
            ty0[li] = in_cursor[tgt] - thick
            in_cursor[tgt] = ty0[li]

    for src in range(n_nodes):
        for li in outgoing[src]:
            thick = float(links[li].value) * unit
            sy1 = out_cursor[src]
            sy0 = out_cursor[src] - thick
            out_cursor[src] = sy0
            link_seg.append((li, sy0, sy1, float(ty0[li]), float(ty1[li])))

    with theme_context(theme) as t:
        dpi = resolve_design_dpi(t.name)
        fig, ax = get_fig_ax(ax=ax, width_px=width, height_px=height, design_dpi=dpi)

        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis("off")

        # Draw links behind nodes.
        for li, sy0_i, sy1_i, ty0_i, ty1_i in link_seg:
            lnk = links[li]
            src = lnk.source
            tgt = lnk.target
            x0 = float(x_left[src] + node_width)
            x1 = float(x_left[tgt])
            dx = x1 - x0
            if dx <= 0:
                # Should not happen in DAG layout, but keep it safe.
                x1 = x0 + float(dag_dx_fallback)
                dx = x1 - x0

            c1x = x0 + dx * float(curve_strength)
            c2x = x1 - dx * float(curve_strength)

            verts = [
                (x0, sy0_i),
                (c1x, sy0_i),
                (c2x, ty0_i),
                (x1, ty0_i),
                (x1, ty1_i),
                (c2x, ty1_i),
                (c1x, sy1_i),
                (x0, sy1_i),
                (x0, sy0_i),
            ]
            codes = [
                Path.MOVETO,
                Path.CURVE4,
                Path.CURVE4,
                Path.CURVE4,
                Path.LINETO,
                Path.CURVE4,
                Path.CURVE4,
                Path.CURVE4,
                Path.CLOSEPOLY,
            ]
            src_color = colors[src % len(colors)]
            patch = PathPatch(
                Path(verts, codes),
                facecolor=color_to_rgba(src_color, alpha=float(link_alpha)),
                edgecolor="none",
                zorder=int(link_zorder),
            )
            ax.add_patch(patch)

        # Draw nodes.
        for n in range(n_nodes):
            rect = Rectangle(
                (float(x_left[n]), float(y0[n])),
                float(node_width),
                float(max(0.0, y1[n] - y0[n])),
                facecolor=color_to_rgba(colors[n % len(colors)], alpha=float(node_face_alpha)),
                edgecolor=str(node_edgecolor),
                linewidth=float(node_line_width),
                zorder=int(node_zorder),
            )
            ax.add_patch(rect)
            ax.text(
                float(x_left[n] + node_width / 2),
                float((y0[n] + y1[n]) / 2),
                node_names[n],
                ha="center",
                va="center",
                fontsize=int(
                    max(5, int(t.axis.tick_font_size) - 1) if node_label_fontsize is None else node_label_fontsize
                ),
                zorder=int(node_text_zorder),
            )

        if title:
            title_above(ax, title, y=1.08)

        return fig
