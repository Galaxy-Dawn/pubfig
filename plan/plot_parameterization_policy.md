# pubfig Plot Parameterization Policy

目标：让用户能够对每个图的视觉呈现进行“精细可控”，并避免在函数体内部写死风格/版式数值。

## 规则

1) **禁止在 plot 函数体内写死风格/版式数值**
- 例子（应参数化）：alpha、linewidth、markersize、capsize、rotation、legend spacing、zorder、padding、shrink、pad 等。
- 允许保留（非风格，算法/结构常量）：数组维度判断（如 `ndim==2`）、`axis` 参数、topological ordering 逻辑等。

2) **所有可调项必须暴露为 keyword-only 参数**
- 默认值必须保持“旧行为不变”（兼容已有脚本）。
- 参数名应尽量语义化（例如 `error_cap_width_ratio` 而不是 `k1`）。

3) **每个新增参数必须在 docstring 的 Args 里解释清楚**
- 写清：作用对象（bar/points/legend/…）、单位（points/data units/axes coords）、推荐范围、与其他参数的关系。

4) **尽量不在 API 层引入复杂对象**
- 优先使用明确的 kwargs；必要时再提供 dataclass style config（但不能替代 kwargs）。

## 当前覆盖状态（2026-03-10）

已完成“主要 hardcode 风格数值”参数化并补充 docstring 的模块：
- `src/pubfig/plots/line.py`
- `src/pubfig/plots/scatter.py`
- `src/pubfig/plots/distribution.py`
- `src/pubfig/plots/evaluation.py`
- `src/pubfig/plots/heatmap.py`
- `src/pubfig/plots/flow.py`
- `src/pubfig/plots/radar.py`
- `src/pubfig/plots/surface.py`
- `src/pubfig/plots/dimreduction.py`
- bar 系列已拆分为小文件：
  - `src/pubfig/plots/_bar_simple.py`
  - `src/pubfig/plots/_bar_scatter.py`
  - `src/pubfig/plots/_bar_stacked.py`
  - `src/pubfig/plots/bar.py` 仅 re-export

尚需继续清理/统一的点：
- “参数命名一致性”（例如不同文件里 legend 相关参数的命名可以统一）。
- “主题联动”与“显式参数”的优先级约定（建议：显式参数 > theme > module defaults）。
- 对 `sankey(...)` 的 layout 参数很多，后续可补一份 `plan/sankey_layout_notes.md` 帮助用户理解各参数对布局的影响。

