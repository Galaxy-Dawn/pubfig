# Parameter Renames (2026-03-10)

本次为了实现“跨图同名同义”，做了一批参数改名（默认行为不变，但**旧参数名会失效**）。

## Legend
- `legend_max_columns` -> `legend_ncol_max`
- `show_legend` -> `legend_show`
- `kde_legend_ncol` -> `legend_ncol`（仅 histogram KDE legend）

## Line width (统一用 `_line_width`)
- `ci_band_linewidth` -> `ci_band_line_width`
- `fill_linewidth` -> `fill_line_width`
- `ridge_fill_linewidth` -> `ridge_fill_line_width`
- `surface_linewidth` -> `surface_line_width`
- `grid_linewidth` -> `grid_line_width`
- `cbar_outline_linewidth` -> `cbar_outline_line_width`
- `node_linewidth` -> `node_line_width`

## Edge line width
- `scatter_edgewidth` -> `scatter_edge_line_width`
- `marker_edgewidth` -> `marker_edge_line_width`
- `score_edgewidth` -> `score_edge_line_width`

