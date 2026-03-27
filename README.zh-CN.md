# pubfig

<div align="center">

  <img src="LOGO.png" alt="pubfig logo" width="100%"/>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"/>
    <img src="https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square" alt="Matplotlib 3.8+"/>
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
    <a href="https://github.com/Galaxy-Dawn/pubfig"><img src="https://img.shields.io/github/stars/Galaxy-Dawn/pubfig?style=flat-square" alt="GitHub Stars"/></a>
  </p>

  <strong>Language</strong>: <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.md">English</a> | <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.zh-CN.md">中文</a>

</div>

> 基于 Matplotlib 的出版级科研绘图。

## 亮点

- **论文导向默认值** — 更紧凑的标题、更干净的图例、显式字体处理，以及更接近论文风格的线宽。
- **常见图形集中在一个库里** — 统计图、分布图、降维图、评估曲线、热图与 flow 图都在同一个 API 表面之下。
- **面向投稿的导出接口** — `save_figure(...)` 支持 `single`/`double` 栏宽、vector 格式、raster DPI 和 trim。
- **Matplotlib 原生工作流** — 所有绘图函数都返回 Matplotlib `Figure` 对象，便于接入现有分析脚本。
- **显式布局控制** — 可精细控制刻度朝向、box/grid 显示、palette、legend 与各图专属布局参数。

## Recent News

- **2026-03-25**: Panel-first Figma 链路继续打磨 — panel 导出现在默认产出无 title 的干净资产，便于在 Figma 里做整图级标题编排；`pubfig-sync` 默认关闭 shared title / legend placeholders；bridge/watch 也会直接暴露 bundle provenance 和 manual fallback 对应的 bundle 路径。
- **2026-03-20**: Figma 本地 bridge 自动化同步 — 增加 bridge 驱动的 `pubfig figma bridge|sync|watch` 工作流，升级 `pubfig-sync` 的 bridge connection mode，并支持在一次 plugin 连接后由 CLI 触发矢量导入/刷新。
- **2026-03-20**: Figma plugin v2 工作流打磨 — 增加 `auto` / `hero_top` relayout presets，补齐 shared title / legend placeholders，并改进 refresh 行为，使用户在 Figma 中手调过的位置默认能更稳定地保留下来。

<details>
<summary><strong>View older changelog</strong></summary>

- **2026-03-20**: CLI + Figma plugin 工作流 — 新增 `pubfig figma package|validate|inspect`，引入单文件的 Figma bundle JSON 格式，并提供 `figma-plugin/pubfig-sync` 插件脚手架，用于节点级导入与刷新。
- **2026-03-20**: Figma-first panel 导出工作流 — 新增 `export_panel(...)` 和 `export_panels(...)`，用于稳定导出 subplot 资产；同时增加最小化的 `panel-index.json` 同步索引，并补充 Codex + Figma MCP 的多 panel 精修路径说明。
- **2026-03-20**: 与 pubtab 风格对齐并刷新首页结构 — 按照 pubtab 的首页组织方式重排 README，补上居中 badges、语言切换、highlights、带日期的 recent news、精选示例和 gallery hero 图。
- **2026-03-20**: 默认完整安装与元信息简化 — 将 `pip install pubfig` 调整为默认安装完整绘图栈，移除主安装路径上的用户可见 extras，并同步统一包元信息、GitHub About 和 README 文案。
- **2026-03-19**: 新增 raincloud 并刷新 gallery — 增加 `raincloud(...)`，优化其默认样式，接入 gallery，并重新导出整套图像产物。
- **2026-03-19**: 更新 PCA biplot 与 radar 默认示例 — 扩展 `pca_biplot(...)` 的 loading panel 模式和 group ellipses，刷新 radar 默认示例，统一字体处理，并重新导出 gallery。

</details>

## 示例

### 精选展示

<p align="center">
  <a href="examples/bar_scatter.png"><img src="examples/bar_scatter.png" width="48%" alt="Bar scatter 示例"></a>
  <a href="examples/raincloud.png"><img src="examples/raincloud.png" width="48%" alt="Raincloud 示例"></a>
</p>
<p align="center">
  <a href="examples/line.png"><img src="examples/line.png" width="48%" alt="Line 示例"></a>
  <a href="examples/radar.png"><img src="examples/radar.png" width="48%" alt="Radar 示例"></a>
</p>

<details>
<summary><strong>完整图库</strong></summary>

<p align="center">
  <img src="examples/gallery-hero.png" width="100%" alt="完整 gallery 总览">
</p>

</details>

## 快速开始

```bash
pip install pubfig
```

### Python 快速上手

先用**最少参数**跑通第一张图：

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)
data = rng.normal(size=(3, 2, 20))

fig = pf.bar_scatter(data)
pf.save_figure(fig, "figure1")
```

这已经足够导出你的第一张图。第一次使用时，你**不需要先理解**布局、导出或投稿风格相关参数。

#### 下一步最常用的参数

等最小例子跑通之后，通常最先需要补的就是这几个参数：

```python
fig = pf.bar_scatter(
    data,
    category_names=["Condition A", "Condition B", "Condition C"],
    series_names=["Ctrl", "Treatment"],
    title="Bar + Scatter",
)

pf.save_figure(fig, "figure1", spec="nature", width="single")
```

- `category_names`：x 轴分组名称
- `series_names`：legend 名称
- `title`：图标题
- `spec` / `width`：期刊风格导出预设

像 `aspect_ratio`、`vector_formats`、`raster_formats`、`trim` 这类参数，只有在你已经明确知道自己为什么要改时再加。

#### 去哪里看详细参数

如果你想看某一类图的详细参数，建议从这里开始：

```python
help(pf.bar_scatter)
help(pf.line)
help(pf.heatmap)
```

也可以直接看 [`examples/`](examples/) 里的可运行示例。

#### 按图类型看的最小示例

<a id="recipe-bar-scatter"></a>
**`bar_scatter`** —— 适合做分组比较，并同时保留原始散点。

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)
data = rng.normal(size=(3, 2, 20))

fig = pf.bar_scatter(data)
pf.save_figure(fig, "bar_scatter_demo")
```

下一步最常改的参数：`category_names`、`series_names`、`show_statistics`。

<a id="recipe-line"></a>
**`line`** —— 适合展示时间趋势或有序位置上的变化。

```python
import numpy as np
import pubfig as pf

x = np.linspace(0, 2 * np.pi, 100)
fig = pf.line(np.sin(x), x=x)
pf.save_figure(fig, "line_demo")
```

下一步最常改的参数：`x_label`、`y_label`、`series_names`、`title`。

<a id="recipe-heatmap"></a>
**`heatmap`** —— 适合矩阵数据，比如相关矩阵或混淆矩阵。

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)
matrix = rng.uniform(size=(4, 4))

fig = pf.heatmap(matrix)
pf.save_figure(fig, "heatmap_demo")
```

下一步最常改的参数：`category_names`、`title`、颜色范围相关参数。

#### 其余图类型的 compact recipes

下面这些示例都默认先有同样的共享准备：

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)
```

<a id="recipe-bar"></a>
**`bar`** —— 最基础的类别柱状图。

```python
fig = pf.bar(np.array([3, 5, 4]), category_names=["A", "B", "C"])
pf.save_figure(fig, "bar_demo")
```

下一步最常改的参数：`category_names`、`title`、`color_palette`。

<a id="recipe-stacked_bar"></a>
**`stacked_bar`** —— 适合看每组内部成分占比。

```python
data = np.array([[[3, 2], [4, 1]], [[2, 3], [3, 2]]], dtype=float)
fig = pf.stacked_bar(data, group_names=["Batch 1", "Batch 2"])
pf.save_figure(fig, "stacked_bar_demo")
```

下一步最常改的参数：`group_names`、`normalize`、`title`。

<a id="recipe-paired"></a>
**`paired`** —— 适合 before/after 这种配对样本比较。

```python
before = np.array([1.0, 2.0, 2.5, 3.0])
after = before + np.array([0.3, 0.1, 0.4, 0.2])
fig = pf.paired(before, after)
pf.save_figure(fig, "paired_demo")
```

下一步最常改的参数：`x_labels`、`y_label`、`title`。

<a id="recipe-box"></a>
**`box`** —— 适合快速看分组分布概况。

```python
data = rng.normal(size=(80, 3))
fig = pf.box(data, category_names=["A", "B", "C"])
pf.save_figure(fig, "box_demo")
```

下一步最常改的参数：`category_names`、`show_means`、`title`。

<a id="recipe-violin"></a>
**`violin`** —— 适合看完整分布形状。

```python
data = rng.normal(size=(80, 3))
fig = pf.violin(data, category_names=["A", "B", "C"])
pf.save_figure(fig, "violin_demo")
```

下一步最常改的参数：`category_names`、`show_box`、`show_points`。

<a id="recipe-strip"></a>
**`strip`** —— 适合保留原始点的分类散点。

```python
data = rng.normal(size=(80, 3))
fig = pf.strip(data, category_names=["A", "B", "C"])
pf.save_figure(fig, "strip_demo")
```

下一步最常改的参数：`category_names`、`jitter`、`title`。

<a id="recipe-raincloud"></a>
**`raincloud`** —— 把 violin、box 和 raw points 合在一起。

```python
data = rng.normal(size=(80, 3))
fig = pf.raincloud(data, category_names=["A", "B", "C"])
pf.save_figure(fig, "raincloud_demo")
```

下一步最常改的参数：`category_names`、`orientation`、`title`。

<a id="recipe-density"></a>
**`density`** —— 单一连续分布的 KDE 曲线。

```python
samples = rng.normal(size=400)
fig = pf.density(samples)
pf.save_figure(fig, "density_demo")
```

下一步最常改的参数：`title`、`color_palette`、`bins`。

<a id="recipe-histogram"></a>
**`histogram`** —— 直方图，可选叠加 KDE。

```python
samples = rng.normal(size=400)
fig = pf.histogram(samples, show_kde=True)
pf.save_figure(fig, "histogram_demo")
```

下一步最常改的参数：`bins`、`show_kde`、`title`。

<a id="recipe-ridgeline"></a>
**`ridgeline`** —— 多组分布沿 y 轴堆叠展开。

```python
data = [rng.normal(loc=i, size=200) for i in range(4)]
fig = pf.ridgeline(data, category_names=["S1", "S2", "S3", "S4"])
pf.save_figure(fig, "ridgeline_demo")
```

下一步最常改的参数：`category_names`、`offset_step`、`title`。

<a id="recipe-area"></a>
**`area`** —— 堆叠面积图，适合看累计趋势。

```python
fig = pf.area(rng.random((20, 3)), series_names=["A", "B", "C"])
pf.save_figure(fig, "area_demo")
```

下一步最常改的参数：`series_names`、`x`、`title`。

<a id="recipe-scatter"></a>
**`scatter`** —— 两个变量之间的关系图。

```python
x = rng.normal(size=60)
y = 0.5 * x + rng.normal(scale=0.3, size=60)
fig = pf.scatter(x, y)
pf.save_figure(fig, "scatter_demo")
```

下一步最常改的参数：`labels`、`x_label`、`y_label`。

<a id="recipe-bubble"></a>
**`bubble`** —— 用点大小编码第三个变量。

```python
x = rng.normal(size=30)
y = rng.normal(size=30)
size = rng.uniform(1, 10, size=30)
fig = pf.bubble(x, y, size)
pf.save_figure(fig, "bubble_demo")
```

下一步最常改的参数：`labels`、`size_label`、`title`。

<a id="recipe-contour2d"></a>
**`contour2d`** —— 稠密散点的 contour + marginal 视图。

```python
x = rng.normal(size=500)
y = 0.6 * x + rng.normal(scale=0.5, size=500)
fig = pf.contour2d(x, y)
pf.save_figure(fig, "contour2d_demo")
```

下一步最常改的参数：`bins`、`colorscale`、`title`。

<a id="recipe-radar"></a>
**`radar`** —— 多个 series 在同一组指标上对比。

```python
fig = pf.radar(
    [[0.8, 0.7, 0.9, 0.75], [0.65, 0.85, 0.7, 0.8]],
    categories=["Speed", "Accuracy", "Recall", "Stability"],
    series_names=["Model A", "Model B"],
)
pf.save_figure(fig, "radar_demo")
```

下一步最常改的参数：`categories`、`series_names`、`title`。

<a id="recipe-corr_matrix"></a>
**`corr_matrix`** —— 从特征表直接生成相关性热图。

```python
data = rng.normal(size=(60, 4))
fig = pf.corr_matrix(data, variable_names=["A", "B", "C", "D"])
pf.save_figure(fig, "corr_matrix_demo")
```

下一步最常改的参数：`variable_names`、`method`、`title`。

<a id="recipe-clustermap"></a>
**`clustermap`** —— 行列同时聚类的热图。

```python
data = rng.uniform(size=(8, 6))
fig = pf.clustermap(data)
pf.save_figure(fig, "clustermap_demo")
```

下一步最常改的参数：`row_category_names`、`column_category_names`、`title`。

<a id="recipe-dimreduce"></a>
**`dimreduce`** —— 高维样本的 t-SNE 可视化。

```python
data = rng.normal(size=(40, 8))
fig, _ = pf.dimreduce(data, cluster_id=np.repeat([0, 1], 20))
pf.save_figure(fig, "dimreduce_demo")
```

下一步最常改的参数：`cluster_id`、`labels`、`n_components`。

<a id="recipe-pca_biplot"></a>
**`pca_biplot`** —— PCA scores + loading arrows。

```python
data = rng.normal(size=(40, 5))
labels = np.repeat(["A", "B"], 20)
fig = pf.pca_biplot(data, labels=labels, variable_names=["V1", "V2", "V3", "V4", "V5"])
pf.save_figure(fig, "pca_biplot_demo")
```

下一步最常改的参数：`labels`、`variable_names`、`loading_panel`。

<a id="recipe-parallel_coordinates"></a>
**`parallel_coordinates`** —— 一行一个样本的多变量 profile。

```python
data = rng.uniform(size=(20, 4))
fig = pf.parallel_coordinates(data, variable_names=["W", "X", "Y", "Z"])
pf.save_figure(fig, "parallel_coordinates_demo")
```

下一步最常改的参数：`variable_names`、`color_col`、`title`。

<a id="recipe-roc"></a>
**`roc`** —— 一个或多个模型的 ROC 曲线。

```python
fpr = [np.array([0.0, 0.1, 0.3, 1.0]), np.array([0.0, 0.2, 0.4, 1.0])]
tpr = [np.array([0.0, 0.7, 0.9, 1.0]), np.array([0.0, 0.6, 0.85, 1.0])]
fig = pf.roc(fpr, tpr, series_names=["Model A", "Model B"])
pf.save_figure(fig, "roc_demo")
```

下一步最常改的参数：`series_names`、`baseline`、`title`。

<a id="recipe-pr_curve"></a>
**`pr_curve`** —— 一个或多个模型的 Precision-Recall 曲线。

```python
precision = [np.array([1.0, 0.9, 0.8, 0.6]), np.array([1.0, 0.85, 0.72, 0.5])]
recall = [np.array([0.1, 0.4, 0.7, 1.0]), np.array([0.1, 0.4, 0.7, 1.0])]
fig = pf.pr_curve(precision, recall, series_names=["Model A", "Model B"])
pf.save_figure(fig, "pr_curve_demo")
```

下一步最常改的参数：`series_names`、`title`、`xlim` / `ylim`。

<a id="recipe-sankey"></a>
**`sankey`** —— 离散阶段之间的 flow 图。

```python
fig = pf.sankey(
    [0, 0, 1, 1, 2, 3],
    [2, 3, 2, 3, 4, 5],
    [10, 5, 8, 3, 12, 11],
    node_names=["Input A", "Input B", "Path 1", "Path 2", "Outcome +", "Outcome -"],
)
pf.save_figure(fig, "sankey_demo")
```

下一步最常改的参数：`node_names`、`title`、`color_palette`。

对于 `bar_scatter(...)`，显著性标注相关的 spacing 参数现在统一使用更明确的按 orientation 命名：

```python
fig = pf.bar_scatter(
    data,
    show_statistics=True,
    significance_ns_label_offset_ratio_vertical=0.08,
    significance_stars_label_offset_ratio_vertical=-0.12,
    significance_label_offset_ratio_vertical=0.07,
)
```

### pubfig → Figma

#### 这条链路能给你什么

`pubfig` 负责导出干净的 panel 图形资产，Figma 继续负责整张 publication figure 的
拼版、收尾和最终 polish。

日常使用时，主命令固定就是 `pubfig figma push`。

#### Quick Start

1. 第一次使用时，在 Figma Desktop 里进入 **Plugins → Development → Import plugin from manifest...**，选择本仓库里的 `figma-plugin/pubfig-sync/manifest.json` 完成安装。之后可从 **Plugins → Development → pubfig-sync** 重新打开。
2. 在 plugin 里点一次 **Connect Bridge**。
3. 从 Python 导出 panels。
4. 在终端运行 `pubfig figma push <panel_dir> --figure-id <id>`。
5. 如果 bridge 路径失败，就把刚写出的 bundle 载入 plugin，走 manual fallback。

```bash
pubfig figma push panels --figure-id figure-01
```

#### Minimal example

现在 panel 导出默认就是**不带 title 的干净图形资产**，这样 subplot title 可以留在
Figma 的整图装配层处理。如果你确实要保留 panel 内嵌标题，再显式传
`include_title=True`。

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)

panels = {
    "a": pf.bar(rng.uniform(0.4, 0.9, size=3), category_names=["A", "B", "C"]),
    "b": pf.scatter(rng.normal(size=40), rng.normal(size=40)),
}

pf.export_panels(panels, "panels", overwrite=True)  # 默认导出 title-free art
```

```bash
pubfig figma push panels --figure-id figure-01
```

这会先写出 `a.svg`、`b.svg`、`panel-index.json` 之类的 panel 资产，然后用
`push` 作为默认的 panel-first 交接命令把它们送到 Figma。

#### How refresh works

- `figure_id` 保持稳定时，会原地 refresh 现有 figure。
- 换一个新的 `figure_id` 时，会导入成一张新的 figure。

#### FAQ / Troubleshooting

**Connect Bridge 是做什么的？**  
它会把当前打开的 Figma plugin 和你的本地终端工作流连起来，后续 `push` 才知道该
刷新哪个 live session。

**`pubfig figma push` 会自动做什么？**  
它是默认的 agent-first 主命令，会自动确保本地 bridge 可用、选择最新连接的
session、写出 bundle，然后执行 sync / refresh。

**`.pubfig-figma.json` 是什么？**  
它就是一张 figure 的 Figma 交接 bundle。保留这份文件，就能做 manual import、
refresh、debug 或 recovery。

**bridge 失败时怎么 manual fallback？**  
如果 bridge refresh 卡住，就把最新写出的 `.pubfig-figma.json` bundle 载入
`pubfig-sync`，再用 **Import as New**、**Manual Refresh** 或 **Refresh + Relayout**。

**什么时候用 `pubfig figma package`？**  
当你只想先写出一个独立 bundle、暂时不立刻 push 到 Figma 时，用这个
**secondary** 命令。

```bash
pubfig figma package panels --figure-id figure-01
```

**高级命令放在哪里？**  
只有在正常 `push` 路径之外，你确实需要更细的控制或排障时，再用这些 advanced 命令：

```bash
pubfig figma sync figure-01.pubfig-figma.json --session latest
pubfig figma watch figure-01.pubfig-figma.json --session latest
pubfig figma bridge status
```

如果你在本地使用 Codex，也可以继续让配套 skill `pubfig-figma-workflow` 协调
panel 导出 → Figma 导入 → MCP review 这一整条链路。

## 图类型分组

### 类别与统计图

| 函数 | 说明 | 示例 |
|------|------|------|
| `bar` | 简单柱状图与分组柱状图 | [示例](#recipe-bar) |
| `bar_scatter` | 带原始点和显著性标注的分组柱状图 | [示例](#recipe-bar-scatter) |
| `stacked_bar` | 横向 stacked bar | [示例](#recipe-stacked_bar) |
| `paired` | 配对点图 | [示例](#recipe-paired) |

### 分布图

| 函数 | 说明 | 示例 |
|------|------|------|
| `box` | 箱线图 | [示例](#recipe-box) |
| `violin` | 小提琴图 | [示例](#recipe-violin) |
| `strip` | 条带散点图 | [示例](#recipe-strip) |
| `raincloud` | half-violin + box + raw-point 的云雨图 | [示例](#recipe-raincloud) |
| `density` | 带 KDE 的密度图 | [示例](#recipe-density) |
| `histogram` | 可选 KDE 的直方图 | [示例](#recipe-histogram) |
| `ridgeline` | Ridgeline 图 | [示例](#recipe-ridgeline) |

### 趋势与关系图

| 函数 | 说明 | 示例 |
|------|------|------|
| `line` | 可带 CI 的折线图 | [示例](#recipe-line) |
| `area` | 堆叠面积图 | [示例](#recipe-area) |
| `scatter` | 支持分组工作流的散点图 | [示例](#recipe-scatter) |
| `bubble` | 气泡图 | [示例](#recipe-bubble) |
| `contour2d` | 带边缘分布的 2D contour 图 | [示例](#recipe-contour2d) |
| `radar` | 雷达图 | [示例](#recipe-radar) |

### 矩阵、嵌入与多变量图

| 函数 | 说明 | 示例 |
|------|------|------|
| `heatmap` | 热图 | [示例](#recipe-heatmap) |
| `corr_matrix` | 相关性热图 | [示例](#recipe-corr_matrix) |
| `clustermap` | 聚类热图 | [示例](#recipe-clustermap) |
| `dimreduce` | 降维散点图 | [示例](#recipe-dimreduce) |
| `pca_biplot` | 支持 loadings 与 group ellipses 的 PCA biplot | [示例](#recipe-pca_biplot) |
| `parallel_coordinates` | 平行坐标图 | [示例](#recipe-parallel_coordinates) |

### 评估与 Flow 图

| 函数 | 说明 | 示例 |
|------|------|------|
| `roc` | 带 AUC 的 ROC 曲线 | [示例](#recipe-roc) |
| `pr_curve` | 带 AP 的 Precision-Recall 曲线 | [示例](#recipe-pr_curve) |
| `sankey` | Sankey 图 | [示例](#recipe-sankey) |

## 主题、规格与配色

### 内置主题

`pubfig` 当前内置这些主题：

- `default`
- `nature`
- `science`
- `cell`

```python
pf.set_default_theme("science")
```

### Figure Specs

在导出时，`save_figure(...)` 支持这些命名规格：

- `nature`
- `science`
- `cell`

宽度支持以下写法：

- `"single"`
- `"double"`
- 数值毫米，例如 `120`
- 字符串毫米，例如 `"120mm"`

### 内置调色板

内置调色板包括：

- `DEFAULT`
- `NATURE`
- `SCIENCE`
- `LANCET`
- `JAMA`

```python
from pubfig import NATURE, show_palette

show_palette(NATURE).show()
```

你也可以按名称获取 palette：

```python
palette = pf.get_palette("science")
palette = pf.get_palette("carto_blugrn")
```

这些期刊风格 palette 都应理解为 **inspired palettes**，不是期刊官方强制标准色。在 `pubfig` 里，`NATURE`、`SCIENCE`、`LANCET`、`JAMA` 这些色卡来自社区里常用的 **ggsci-derived community palettes**，而不是出版社发布的唯一配色规范。

来源说明：ggsci 将这些 palette 分别表述为受 NPG / Nature Publishing Group、AAAS / Science、Lancet journals 和 JAMA 图形风格启发。可参考 [pal_npg](https://nanx.me/ggsci/reference/pal_npg.html)、[pal_aaas](https://nanx.me/ggsci/reference/pal_aaas.html)、[pal_lancet](https://nanx.me/ggsci/reference/pal_lancet.html)、[pal_jama](https://nanx.me/ggsci/reference/pal_jama.html)。

如果你想直接查看所有 palette 的实际颜色，可以看 [`docs/palette-gallery.zh-CN.md`](docs/palette-gallery.zh-CN.md)。

[![精选 palette 预览](examples/palettes/featured-palettes.png)](docs/palette-gallery.zh-CN.md)

## Gallery 与示例

示例入口包括：

- `examples/gallery.py` —— 快速浏览支持的图类型
- `examples/export_gallery.py` —— 把 gallery 导出到 `output_figures/`
- `examples/export_gallery_mpl.py` —— 更聚焦的 Matplotlib 导出示例
- `examples/figma_panels_demo.py` —— 导出多个 pubfig panel，并生成 `panel-index.json` 同步文件
- `examples/figma_workflow_demo.md` —— panel-first 的 pubfig → Figma 工作流说明
- `figma-plugin/pubfig-sync/` —— Figma plugin 脚手架，用于 panel 导入与刷新
- `examples/generate_palette_gallery.py` —— 重新生成 palette 预览图与 gallery 文档
- [`docs/palette-gallery.zh-CN.md`](docs/palette-gallery.zh-CN.md) —— 内置与 Plotly 派生 palette 的可视化总览

## 开发

### 可编辑安装

```bash
pip install -e .[dev]
```

### 运行测试

```bash
pytest
```

### Lint

```bash
ruff check src tests examples
```

### 重导 Gallery

```bash
python examples/export_gallery.py
```

## 许可证

MIT
