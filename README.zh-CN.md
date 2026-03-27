# pubfig

<div align="center">

  <img src="LOGO.png" alt="pubfig logo" width="100%"/>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"/>
    <img src="https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square" alt="Matplotlib 3.8+"/>
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
    <a href="https://github.com/Galaxy-Dawn/pubfig"><img src="https://img.shields.io/github/stars/Galaxy-Dawn/pubfig?style=flat-square" alt="GitHub Stars"/></a>
  </p>

  <strong>语言</strong>: <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.md">English</a> | <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.zh-CN.md">中文</a>

</div>

> 基于 Matplotlib 的出版级科研绘图。

## 亮点

- **更接近论文图的默认风格** — 标题、图例、字体和线宽默认更紧凑、更干净。
- **常见图形集中在一个库里** — 统计图、分布图、降维图、评估曲线、热图与流向图都统一在同一套绘图接口之下。
- **更省事的导出规格控制** — `save_figure(...)` 直接支持 `single`/`double` 栏宽、矢量格式、位图 DPI 和裁边。
- **Matplotlib 原生工作流** — 所有绘图函数都返回 Matplotlib `Figure` 对象，便于接入现有分析脚本。
- **显式布局控制** — 可精细控制刻度朝向、边框/网格显示、调色板、图例与各图专属布局参数。

## 近期更新

- **2026-03-25**: 面板优先的 Figma 链路继续打磨 — 面板导出现在默认产出不带标题的干净资产，便于在 Figma 里做整图级标题编排；`pubfig-sync` 默认关闭共享标题 / 图例占位；`bridge` / `watch` 也会直接暴露 bundle 来源信息和手动兜底对应的打包文件路径。
- **2026-03-20**: Figma 本地桥接自动化同步 — 增加由桥接驱动的 `pubfig figma bridge|sync|watch` 工作流，升级 `pubfig-sync` 的桥接连接模式，并支持在一次插件连接后由命令行触发矢量导入 / 刷新。
- **2026-03-20**: Figma 插件 v2 工作流打磨 — 增加 `auto` / `hero_top` 重新布局预设，补齐共享标题 / 图例占位，并改进刷新行为，使用户在 Figma 中手调过的位置默认能更稳定地保留下来。

<details>
<summary><strong>查看更早更新</strong></summary>

- **2026-03-20**: CLI + Figma 插件工作流 — 新增 `pubfig figma package|validate|inspect`，引入单文件的 Figma bundle JSON 格式，并提供 `figma-plugin/pubfig-sync` 插件脚手架，用于节点级导入与刷新。
- **2026-03-20**: Figma 优先的面板导出工作流 — 新增 `export_panel(...)` 和 `export_panels(...)`，用于稳定导出子图资产；同时增加最小化的 `panel-index.json` 同步索引，并补充 Codex + Figma MCP 的多面板精修路径说明。
- **2026-03-20**: 与 pubtab 风格对齐并刷新首页结构 — 按照 pubtab 的首页组织方式重排 README，补上居中徽章、语言切换、亮点、带日期的近期更新、精选示例和图库头图。
- **2026-03-20**: 默认完整安装与元信息简化 — 将 `pip install pubfig` 调整为默认安装完整绘图栈，移除主安装路径上的用户可见额外依赖选项，并同步统一包元信息、GitHub About 和 README 文案。
- **2026-03-19**: 新增 raincloud 并刷新图库 — 增加 `raincloud(...)`，优化其默认样式，接入图库，并重新导出整套图像产物。
- **2026-03-19**: 更新 PCA biplot 与 radar 默认示例 — 扩展 `pca_biplot(...)` 的载荷面板模式和分组椭圆，刷新 radar 默认示例，统一字体处理，并重新导出图库。

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
means = np.array([
    [0.78, 0.96],
    [0.88, 1.08],
    [0.84, 1.00],
], dtype=float)

data = rng.normal(loc=means[..., None], scale=0.08, size=(3, 2, 18))
data = np.clip(data, 0.0, None)

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
- `series_names`：图例名称
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

#### 如何保存 PNG / SVG / PDF

`pf.save_figure(fig, "figure1")` 传入的是**不带扩展名**的基础路径，默认会写出：

- `figure1.pdf`
- `figure1.svg`
- `figure1.png`

如果你想显式指定导出格式，可以这样写：

```python
pf.save_figure(fig, "figure1", vector_formats=("pdf",), raster_formats=())
pf.save_figure(fig, "figure1", vector_formats=("svg",), raster_formats=("png",))
```

#### 按图类型速查

下面这些行给的是最短可用调用。真正导出时，直接复用 Quick Start 里的
`pf.save_figure(fig, "name")` 即可。

默认假设你已经写了：

```python
import numpy as np
import pubfig as pf
```

##### 类别与统计

| 图 | 最小调用 | 常改参数 |
|----|----------|----------|
| <a id="recipe-bar"></a>`bar` | `pf.bar(np.array([3, 5, 4]), category_names=["A", "B", "C"])` | `category_names`, `title`, `color_palette` |
| <a id="recipe-bar-scatter"></a>`bar_scatter` | `pf.bar_scatter(np.random.default_rng(0).normal(size=(3, 2, 20)))` | `category_names`, `series_names`, `show_statistics` |
| <a id="recipe-stacked_bar"></a>`stacked_bar` | `pf.stacked_bar(np.array([[[3, 2], [4, 1]], [[2, 3], [3, 2]]], dtype=float), group_names=["Batch 1", "Batch 2"])` | `group_names`, `normalize`, `title` |
| <a id="recipe-paired"></a>`paired` | `pf.paired(np.array([1.0, 2.0, 2.5, 3.0]), np.array([1.3, 2.1, 2.9, 3.2]))` | `x_labels`, `y_label`, `title` |

##### 分布

| 图 | 最小调用 | 常改参数 |
|----|----------|----------|
| <a id="recipe-box"></a>`box` | `pf.box(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `show_means`, `title` |
| <a id="recipe-violin"></a>`violin` | `pf.violin(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `show_box`, `show_points` |
| <a id="recipe-strip"></a>`strip` | `pf.strip(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `jitter`, `title` |
| <a id="recipe-raincloud"></a>`raincloud` | `pf.raincloud(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `orientation`, `title` |
| <a id="recipe-density"></a>`density` | `pf.density(np.random.default_rng(0).normal(size=400))` | `title`, `color_palette`, `bins` |
| <a id="recipe-histogram"></a>`histogram` | `pf.histogram(np.random.default_rng(0).normal(size=400), show_kde=True)` | `bins`, `show_kde`, `title` |
| <a id="recipe-ridgeline"></a>`ridgeline` | `pf.ridgeline([np.random.default_rng(0).normal(loc=i, size=200) for i in range(4)], category_names=["S1", "S2", "S3", "S4"])` | `category_names`, `offset_step`, `title` |

##### 趋势与关系

| 图 | 最小调用 | 常改参数 |
|----|----------|----------|
| <a id="recipe-area"></a>`area` | `pf.area(np.random.default_rng(0).random((20, 3)), series_names=["A", "B", "C"])` | `series_names`, `x`, `title` |
| <a id="recipe-line"></a>`line` | `pf.line(np.sin(np.linspace(0, 2 * np.pi, 100)), x=np.linspace(0, 2 * np.pi, 100))` | `x_label`, `y_label`, `series_names`, `title` |
| <a id="recipe-scatter"></a>`scatter` | `pf.scatter(np.random.default_rng(0).normal(size=60), np.random.default_rng(1).normal(size=60))` | `labels`, `x_label`, `y_label` |
| <a id="recipe-bubble"></a>`bubble` | `pf.bubble(np.random.default_rng(0).normal(size=30), np.random.default_rng(1).normal(size=30), np.random.default_rng(2).uniform(1, 10, size=30))` | `labels`, `size_label`, `title` |
| <a id="recipe-contour2d"></a>`contour2d` | `pf.contour2d(np.random.default_rng(0).normal(size=500), np.random.default_rng(1).normal(size=500))` | `bins`, `colorscale`, `title` |
| <a id="recipe-radar"></a>`radar` | `pf.radar([[0.8, 0.7, 0.9, 0.75], [0.65, 0.85, 0.7, 0.8]], categories=["Speed", "Accuracy", "Recall", "Stability"], series_names=["Model A", "Model B"])` | `categories`, `series_names`, `title` |

##### 矩阵与多变量

| 图 | 最小调用 | 常改参数 |
|----|----------|----------|
| <a id="recipe-heatmap"></a>`heatmap` | `pf.heatmap(np.random.default_rng(0).uniform(size=(4, 4)))` | `category_names`, `title`, 颜色范围相关参数 |
| <a id="recipe-corr_matrix"></a>`corr_matrix` | `pf.corr_matrix(np.random.default_rng(0).normal(size=(60, 4)), variable_names=["A", "B", "C", "D"])` | `variable_names`, `method`, `title` |
| <a id="recipe-clustermap"></a>`clustermap` | `pf.clustermap(np.random.default_rng(0).uniform(size=(8, 6)))` | `row_category_names`, `column_category_names`, `title` |
| <a id="recipe-dimreduce"></a>`dimreduce` | `fig, _ = pf.dimreduce(np.random.default_rng(0).normal(size=(40, 8)), cluster_id=np.repeat([0, 1], 20))` | `cluster_id`, `labels`, `n_components` |
| <a id="recipe-pca_biplot"></a>`pca_biplot` | `pf.pca_biplot(np.random.default_rng(0).normal(size=(40, 5)), labels=np.repeat(["A", "B"], 20), variable_names=["V1", "V2", "V3", "V4", "V5"])` | `labels`, `variable_names`, `loading_panel` |
| <a id="recipe-parallel_coordinates"></a>`parallel_coordinates` | `pf.parallel_coordinates(np.random.default_rng(0).uniform(size=(20, 4)), variable_names=["W", "X", "Y", "Z"])` | `variable_names`, `color_col`, `title` |

##### 评估与 flow

| 图 | 最小调用 | 常改参数 |
|----|----------|----------|
| <a id="recipe-roc"></a>`roc` | `pf.roc([np.array([0.0, 0.1, 0.3, 1.0])], [np.array([0.0, 0.7, 0.9, 1.0])], series_names=["Model A"])` | `series_names`, `baseline`, `title` |
| <a id="recipe-pr_curve"></a>`pr_curve` | `pf.pr_curve([np.array([1.0, 0.9, 0.8, 0.6])], [np.array([0.1, 0.4, 0.7, 1.0])], series_names=["Model A"])` | `series_names`, `title`, `xlim` / `ylim` |
| <a id="recipe-sankey"></a>`sankey` | `pf.sankey([0, 0, 1], [2, 3, 3], [10, 5, 8], node_names=["Input A", "Input B", "Path 1", "Outcome"])` | `node_names`, `title`, `color_palette` |

对于 `bar_scatter(...)`，显著性标注相关的间距参数现在统一使用更明确的按方向命名：

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

#### 快速开始

1. 第一次使用时，在 Figma 桌面版里进入 **Plugins → Development → Import plugin from manifest...**，选择本仓库里的 `figma-plugin/pubfig-sync/manifest.json` 完成安装。之后可从 **Plugins → Development → pubfig-sync** 重新打开。
2. 在插件里点一次 **Connect Bridge**。
3. 从 Python 导出面板。
4. 在终端运行 `pubfig figma push <panel_dir> --figure-id <id>`。
5. 如果桥接路径失败，就把刚写出的 bundle 载入插件，走手动兜底路径。

```bash
pubfig figma push panels --figure-id figure-01
```

#### 最小示例

现在面板导出默认就是**不带标题的干净图形资产**，这样子图标题可以留在
Figma 的整图装配层处理。如果你确实要保留面板内嵌标题，再显式传
`include_title=True`。

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)

panels = {
    "a": pf.bar(rng.uniform(0.4, 0.9, size=3), category_names=["A", "B", "C"]),
    "b": pf.scatter(rng.normal(size=40), rng.normal(size=40)),
}

pf.export_panels(panels, "panels", overwrite=True)  # 默认导出不带标题的干净面板
```

```bash
pubfig figma push panels --figure-id figure-01
```

这会先写出 `a.svg`、`b.svg`、`panel-index.json` 之类的面板资产，然后用
`push` 作为默认的面板优先交接命令把它们送到 Figma。

#### 刷新规则

- `figure_id` 保持稳定时，会原地刷新现有图稿。
- 换一个新的 `figure_id` 时，会导入成一张新的图稿。

#### 常见问题 / 排障

**Connect Bridge 是做什么的？**  
它会把当前打开的 Figma 插件和你的本地终端工作流连起来，后续 `push` 才知道该
刷新哪个活动会话。

**`pubfig figma push` 会自动做什么？**  
它是默认的面向 agent 的主命令，会自动确保本地桥接可用、选择最新连接的
会话、写出 bundle 文件，然后执行同步 / 刷新。

**`.pubfig-figma.json` 是什么？**  
它就是一张图稿的 Figma 交接 bundle 文件。保留这份文件，就能做手动导入、
刷新、排障或恢复。

**bridge 失败时怎么手动兜底？**  
如果 bridge 刷新卡住，就把最新写出的 `.pubfig-figma.json` bundle 文件载入
`pubfig-sync`，再用 **Import as New**、**Manual Refresh** 或 **Refresh + Relayout**。

**什么时候用 `pubfig figma package`？**  
当你只想先写出一个独立 bundle 文件、暂时不立刻 push 到 Figma 时，用这个
**次级** 命令。

```bash
pubfig figma package panels --figure-id figure-01
```

**高级命令放在哪里？**  
只有在正常 `push` 路径之外，你确实需要更细的控制或排障时，再用这些高级命令：

```bash
pubfig figma sync figure-01.pubfig-figma.json --session latest
pubfig figma watch figure-01.pubfig-figma.json --session latest
pubfig figma bridge status
```

如果你在本地使用 Codex，也可以继续让配套 skill `pubfig-figma-workflow` 协调
面板导出 → Figma 导入 → MCP 审阅这一整条链路。

## 图类型分组

### 类别与统计图

| 函数 | 说明 | 示例 |
|------|------|------|
| `bar` | 简单柱状图与分组柱状图 | [示例](#recipe-bar) |
| `bar_scatter` | 带原始点和显著性标注的分组柱状图 | [示例](#recipe-bar-scatter) |
| `stacked_bar` | 横向堆叠柱状图 | [示例](#recipe-stacked_bar) |
| `paired` | 配对点图 | [示例](#recipe-paired) |

### 分布图

| 函数 | 说明 | 示例 |
|------|------|------|
| `box` | 箱线图 | [示例](#recipe-box) |
| `violin` | 小提琴图 | [示例](#recipe-violin) |
| `strip` | 条带散点图 | [示例](#recipe-strip) |
| `raincloud` | 半小提琴 + 箱线图 + 原始点的云雨图 | [示例](#recipe-raincloud) |
| `density` | 带核密度估计的密度图 | [示例](#recipe-density) |
| `histogram` | 可选核密度曲线的直方图 | [示例](#recipe-histogram) |
| `ridgeline` | 山峦图 | [示例](#recipe-ridgeline) |

### 趋势与关系图

| 函数 | 说明 | 示例 |
|------|------|------|
| `line` | 可带 CI 的折线图 | [示例](#recipe-line) |
| `area` | 堆叠面积图 | [示例](#recipe-area) |
| `scatter` | 支持分组绘制的散点图 | [示例](#recipe-scatter) |
| `bubble` | 气泡图 | [示例](#recipe-bubble) |
| `contour2d` | 带边缘分布的二维等高线图 | [示例](#recipe-contour2d) |
| `radar` | 雷达图 | [示例](#recipe-radar) |

### 矩阵、嵌入与多变量图

| 函数 | 说明 | 示例 |
|------|------|------|
| `heatmap` | 热图 | [示例](#recipe-heatmap) |
| `corr_matrix` | 相关性热图 | [示例](#recipe-corr_matrix) |
| `clustermap` | 聚类热图 | [示例](#recipe-clustermap) |
| `dimreduce` | 降维散点图 | [示例](#recipe-dimreduce) |
| `pca_biplot` | 支持载荷与分组椭圆的 PCA 双标图 | [示例](#recipe-pca_biplot) |
| `parallel_coordinates` | 平行坐标图 | [示例](#recipe-parallel_coordinates) |

### 评估与流向图

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

### 图尺寸规格

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

你也可以按名称获取调色板：

```python
palette = pf.get_palette("science")
palette = pf.get_palette("carto_blugrn")
```

这些期刊风格 palette 都应理解为**受其启发的调色板**，不是期刊官方强制标准色。在 `pubfig` 里，`NATURE`、`SCIENCE`、`LANCET`、`JAMA` 这些色卡来自社区里常用的 **ggsci 衍生调色板**，而不是出版社发布的唯一配色规范。

来源说明：ggsci 将这些 palette 分别表述为受 NPG / Nature Publishing Group、AAAS / Science、Lancet journals 和 JAMA 图形风格启发。可参考 [pal_npg](https://nanx.me/ggsci/reference/pal_npg.html)、[pal_aaas](https://nanx.me/ggsci/reference/pal_aaas.html)、[pal_lancet](https://nanx.me/ggsci/reference/pal_lancet.html)、[pal_jama](https://nanx.me/ggsci/reference/pal_jama.html)。

如果你想直接查看所有调色板的实际颜色，可以看 [`docs/palette-gallery.zh-CN.md`](docs/palette-gallery.zh-CN.md)。

[![精选调色板预览](examples/palettes/featured-palettes.png)](docs/palette-gallery.zh-CN.md)

## 图库与示例

`examples/` 下面的文件主要分成两类：

- 可运行的示例脚本
- README 和调色板文档会直接用到的渲染产物

如果你只想抓主入口，先看这几个：

- `examples/gallery.py` —— 快速浏览支持的图类型
- `examples/export_gallery.py` —— 把图库导出到 `output_figures/`
- `examples/figma_panels_demo.py` —— 导出多个 pubfig 面板给 Figma 使用
- `examples/figma_workflow_demo.md` —— 面板优先的 pubfig → Figma 工作流说明
- `examples/generate_palette_gallery.py` —— 重新生成调色板预览图与图库文档

进阶 / 次要入口：

- `examples/export_gallery_mpl.py` —— 更聚焦的 Matplotlib 导出示例
- `figma-plugin/pubfig-sync/` —— Figma 插件脚手架，用于面板导入与刷新
- [`docs/palette-gallery.zh-CN.md`](docs/palette-gallery.zh-CN.md) —— 内置与 Plotly 派生调色板的可视化总览

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

### 重新导出图库

```bash
python examples/export_gallery.py
```

## 许可证

MIT
