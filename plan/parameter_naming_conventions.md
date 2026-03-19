# pubfig Parameter Naming Conventions (Plots)

目标：让不同图类型之间 **同名同义**（legend/alpha/line width 等），降低记忆成本。

## Legend（统一前缀 `legend_`）

推荐统一使用：
- `legend_show: bool`：是否绘制 legend（只在该图有 legend 场景下生效）。
- `legend_ncol: Optional[int]`：显式指定 legend 列数（优先级最高）。
- `legend_ncol_max: int`：当 `legend_ncol is None` 时，legend 列数的上限（常见逻辑：`min(n_series, legend_ncol_max)`）。

如果某个图需要更精细控制 legend（位置/间距/字体/handle），统一前缀仍为 `legend_`：
- `legend_loc`, `legend_bbox_to_anchor`, `legend_frameon`, `legend_font_size`,
  `legend_columnspacing`, `legend_handlelength`, `legend_handletextpad`, `legend_borderaxespad`

## Alpha（统一后缀 `_alpha`）

规则：
- 任何透明度参数都用 `*_alpha`（范围 0..1，语义=Matplotlib alpha）。
- 如果需要区分 fill/edge：用 `*_face_alpha` / `*_edge_alpha`。

例子：
- `scatter_alpha`, `fill_alpha`, `marker_alpha`, `ridge_fill_alpha`

## Line width（统一后缀 `_line_width`）

规则：
- 所有“线宽”参数统一命名为 `*_line_width`（单位=points）。
- 不使用 `*_linewidth`（避免和 Matplotlib artist kwargs 混淆）。

例子：
- `grid_line_width`, `surface_line_width`, `cbar_outline_line_width`, `node_line_width`,
  `scatter_edge_line_width`, `ci_band_line_width`

## Edge line width（统一后缀 `_edge_line_width`）

规则：
- marker/bar 的边线宽统一为 `*_edge_line_width`。

例子：
- `scatter_edge_line_width`, `marker_edge_line_width`, `score_edge_line_width`

## 说明

- 本约定优先保证“用户可控”和“跨图一致”；默认值保持旧行为不变。
- Theme 内部字段也尽量遵守同一命名（例如 `grid_line_width`）。

