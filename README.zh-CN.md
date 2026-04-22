# pubfig

<div align="center">

  <img src="LOGO.png" alt="pubfig logo" width="100%"/>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"/>
    <a href="https://pypi.org/project/pubfig/"><img src="https://img.shields.io/pypi/v/pubfig?style=flat-square&logo=pypi&logoColor=white" alt="PyPI version"/></a>
    <a href="https://pypi.org/project/pubfig/"><img src="https://img.shields.io/badge/pip%20install-pubfig-3775A9?style=flat-square&logo=pypi&logoColor=white" alt="pip install pubfig"/></a>
    <img src="https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square" alt="Matplotlib 3.8+"/>
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
    <a href="https://github.com/Galaxy-Dawn/pubfig"><img src="https://img.shields.io/github/stars/Galaxy-Dawn/pubfig?style=flat-square" alt="GitHub Stars"/></a>
  </p>

  <strong>语言</strong>: <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.md">English</a> | <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.zh-CN.md">中文</a>

</div>

> 面向论文主图的科研绘图库：既能快速出单图，也能走 panel-first 的 Figma 拼版链路。

`pubfig` 是一个基于 Matplotlib 的科研绘图库，面向那些希望图一开始就更接近论文最终效果的研究者。它把常见科研图类型、面向期刊的导出规格，以及面向大图拼版的 Figma 工作流放在同一套接口里，减少手工重排和重复出图。

**项目链接**：[PyPI](https://pypi.org/project/pubfig/) · [GitHub](https://github.com/Galaxy-Dawn/pubfig) · [示例](examples/)

## 亮点

- **默认就更像论文图，而不是空白画布** — 标题、图例、字体、线宽和间距都从更接近 publication figure 的基线出发。
- **常见科研图类型统一在一套 API 里** — 统计图、分布图、趋势图、降维图、评估曲线、热图和 flow 图都能用一致的调用方式生成。
- **导出规格更省事** — `save_figure(...)` 和 `batch_export(...)` 直接处理显式文件后缀、栏宽、DPI、裁边，以及导出时的重新布局。
- **天然适合整图拼版** — 可以先导出干净的 panel 资产，再在 Figma 里完成多子图大图的拼接、刷新和收尾，而不是手工重画。
- **保留 Matplotlib 原生工作流** — 所有绘图函数都返回标准 Matplotlib `Figure` 对象，能直接接入现有分析脚本。

## 近期更新

- **2026-04-22**: `pubfig 0.3.0` 作为当前 PyPI 版本发布，收口了新的面向 agent 的 JSON CLI（`render`、`validate-spec`、`list-kinds`）、CLI / Python 导出一致性校验，以及更短的 Quick Start。
- **2026-04-10**: `pubfig 0.2.3` 让 `batch_export(...)` 和 `save_figure(...)` 走同一条 publication-size 的 resize / relayout 导出路径，多格式导出时也能保持一致的导出版式。
- **2026-03-31**: `pubfig 0.2.2` 新增 **ECDF、QQ、Bland–Altman、Calibration 和 UpSet**，并已接入首页精选展示和完整图库。
- **2026-03-30**: `pubfig 0.2.1` 已更新到 PyPI，强化了极坐标 / 组成类图型覆盖，并补全了完整图库示例。
- **2026-03-29**: `pubfig 0.2.0` 已发布到 PyPI，支持 `pip install pubfig`、按后缀导出，以及 panel-first Figma 工作流。

<details>
<summary><strong>查看更早更新</strong></summary>

- **2026-03-25**: 面板优先的 Figma 链路继续打磨 — 面板导出现在默认产出不带标题的干净资产，便于在 Figma 里做整图级标题编排；`pubfig-sync` 默认关闭共享标题 / 图例占位；`bridge` / `watch` 也会直接暴露 bundle 来源信息和手动兜底对应的打包文件路径。
- **2026-03-20**: Figma 本地桥接自动化同步 — 增加由桥接驱动的 `pubfig figma bridge|sync|watch` 工作流，升级 `pubfig-sync` 的桥接连接模式，并支持在一次插件连接后由命令行触发矢量导入 / 刷新。
- **2026-03-20**: Figma 插件 v2 工作流打磨 — 增加 `auto` / `hero_top` 重新布局预设，补齐共享标题 / 图例占位，并改进刷新行为，使用户在 Figma 中手调过的位置默认能更稳定地保留下来。
- **2026-03-20**: CLI + Figma 插件工作流 — 新增 `pubfig figma package|validate|inspect`，引入单文件的 Figma bundle JSON 格式，并提供 `figma-plugin/pubfig-sync` 插件脚手架，用于节点级导入与刷新。
- **2026-03-20**: Figma 优先的面板导出工作流 — 新增 `export_panel(...)` 和 `export_panels(...)`，用于稳定导出子图资产；同时增加最小化的 `panel-index.json` 同步索引，并补充 Codex + Figma MCP 的多面板精修路径说明。
- **2026-03-20**: 与 pubtab 风格对齐并刷新首页结构 — 按照 pubtab 的首页组织方式重排 README，补上居中徽章、语言切换、亮点、带日期的近期更新、精选示例和图库头图。
- **2026-03-20**: 默认完整安装与元信息简化 — 将 `pip install pubfig` 调整为默认安装完整绘图栈，移除主安装路径上的用户可见额外依赖选项，并同步统一包元信息、GitHub About 和 README 文案。
- **2026-03-19**: 新增 raincloud 并刷新图库 — 增加 `raincloud(...)`，优化其默认样式，接入图库，并重新导出整套图像产物。
- **2026-03-19**: 更新 PCA biplot 与 radar 默认示例 — 扩展 `pca_biplot(...)` 的载荷面板模式和分组椭圆，刷新 radar 默认示例，统一字体处理，并重新导出图库。

</details>

## 示例

### 精选展示

#### 单图示例

<p align="center">
  <a href="examples/bar_scatter.png"><img src="examples/bar_scatter.png" width="32%" alt="Bar scatter 示例"></a>
  <a href="examples/raincloud.png"><img src="examples/raincloud.png" width="32%" alt="Raincloud 示例"></a>
  <a href="examples/line.png"><img src="examples/line.png" width="32%" alt="Line 示例"></a>
</p>
<p align="center">
  <a href="examples/radar.png"><img src="examples/radar.png" width="32%" alt="Radar 示例"></a>
  <a href="examples/scatter.png"><img src="examples/scatter.png" width="32%" alt="Scatter 示例"></a>
  <a href="examples/heatmap.png"><img src="examples/heatmap.png" width="32%" alt="Heatmap 示例"></a>
</p>

#### 新增图型示例

<p align="center">
  <a href="examples/ecdf.png"><img src="examples/ecdf.png" width="32%" alt="ECDF 示例"></a>
  <a href="examples/qq.png"><img src="examples/qq.png" width="32%" alt="QQ plot 示例"></a>
  <a href="examples/bland_altman.png"><img src="examples/bland_altman.png" width="32%" alt="Bland-Altman 示例"></a>
</p>
<p align="center">
  <a href="examples/calibration.png"><img src="examples/calibration.png" width="48%" alt="Calibration 示例"></a>
  <a href="examples/upset.png"><img src="examples/upset.png" width="48%" alt="UpSet 示例"></a>
</p>
<p align="center">
  <a href="examples/dumbbell.png"><img src="examples/dumbbell.png" width="48%" alt="Dumbbell 示例"></a>
  <a href="examples/forest_plot.png"><img src="examples/forest_plot.png" width="48%" alt="Forest plot 示例"></a>
</p>
<p align="center">
  <a href="examples/hexbin.png"><img src="examples/hexbin.png" width="48%" alt="Hexbin 示例"></a>
  <a href="examples/volcano.png"><img src="examples/volcano.png" width="48%" alt="Volcano 示例"></a>
</p>
<p align="center">
  <a href="examples/grouped_scatter.png"><img src="examples/grouped_scatter.png" width="48%" alt="Grouped scatter 示例"></a>
  <a href="examples/radial_hierarchy.png"><img src="examples/radial_hierarchy.png" width="48%" alt="Radial hierarchy 示例"></a>
</p>
<p align="center">
  <a href="examples/circular_stacked_bar.png"><img src="examples/circular_stacked_bar.png" width="48%" alt="Circular stacked bar 示例"></a>
  <a href="examples/circular_grouped_bar.png"><img src="examples/circular_grouped_bar.png" width="48%" alt="Circular grouped bar 示例"></a>
</p>

#### 在 Figma 中拼接的合成大图示例

<p align="center">
  <a href="examples/composite-showcase-benchmark.png"><img src="examples/composite-showcase-benchmark.png" width="96%" alt="在 Figma 中拼接的 benchmark 大图示例"></a>
</p>
<p align="center">
  <a href="examples/composite-showcase-intervention.png"><img src="examples/composite-showcase-intervention.png" width="96%" alt="在 Figma 中拼接的 intervention 大图示例"></a>
</p>
<p align="center">
  <a href="examples/composite-showcase-stratification.png"><img src="examples/composite-showcase-stratification.png" width="96%" alt="在 Figma 中拼接的 stratification 大图示例"></a>
</p>

<details>
<summary><strong>完整图库</strong></summary>

下面这张完整图库也已经收进本轮新增的诊断、评估和集合关系图，包括 ECDF、QQ、Bland–Altman、Calibration 和 UpSet。

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
pf.save_figure(fig, "figure1.pdf")
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

pf.save_figure(fig, "figure1.pdf", spec="nature", width="single")
```

- `category_names`：x 轴分组名称
- `series_names`：图例名称
- `title`：图标题
- `spec` / `width`：期刊风格导出预设

像 `aspect_ratio`、`trim` 这类参数，只有在你已经明确知道自己为什么要改时再加。

#### 去哪里看详细参数

如果你想看某一类图的详细参数，建议从这里开始：

```python
help(pf.bar_scatter)
help(pf.line)
help(pf.heatmap)
```

也可以直接看 [`examples/`](examples/) 里的可运行示例。

#### 如何保存 PNG / SVG / PDF

`save_figure(...)` 现在要求你显式写出文件后缀：

- `pf.save_figure(fig, "figure1.pdf")` → 存 PDF
- `pf.save_figure(fig, "figure1.svg")` → 存 SVG
- `pf.save_figure(fig, "figure1.png")` → 存 PNG
- `pf.save_figure(fig, "figure1.jpg")` → 存 JPG

如果你想一次导出多个格式，请改用 `batch_export(...)`：

```python
pf.batch_export(fig, "figure1", formats=("pdf", "svg", "png", "jpg"))
```

`batch_export(...)` 现在和 `save_figure(...)` 走同一条 publication-size
导出路径：会先按目标尺寸 resize，再重新执行 layout / post-layout hooks，
然后再分别写出各个格式。

### CLI 快速上手

Python API 仍然最适合 notebook 和交互式分析。
CLI 则是面向 agent / 自动化的主路径：它提供一套稳定的 JSON 接口来做绘图、校验和导出。

先记住这三条命令：

```bash
pubfig render figure.spec.json
pubfig validate-spec figure.spec.json
pubfig list-kinds
```

- `render`：读取 JSON spec，真正写出单图或 panels
- `validate-spec`：读取同一份 spec，实际构造图但不写文件
- `list-kinds`：列出当前 CLI 支持的 plot kind

#### 示例 1：单图导出

如果数据量不大，可以直接把数据内联写进 JSON：

```json
{
  "schema_version": 1,
  "plot": {
    "kind": "line",
    "kwargs": {
      "data": [
        [0.78, 1.03, 1.15, 0.90],
        [0.87, 1.01, 1.04, 0.95]
      ],
      "x": [0.0, 0.8, 1.6, 2.4],
      "series_names": ["Square", "Circle"]
    }
  },
  "export": {
    "mode": "save_figure",
    "path": "outputs/line.pdf",
    "spec": "nature",
    "width": "single"
  }
}
```

```bash
pubfig render figure.spec.json
```

#### 示例 2：panel 导出

如果你要给 Figma 或其他整图装配流程导出 panel 资产，就用 `export_panels` 模式：

```json
{
  "schema_version": 1,
  "panels": [
    {
      "panel_id": "a",
      "kind": "bar_scatter",
      "kwargs": {
        "data": {"$load": "data/a.npy"},
        "random_seed": 0
      }
    },
    {
      "panel_id": "b",
      "kind": "line",
      "kwargs": {
        "data": {"$load": "data/b.npy"}
      }
    }
  ],
  "export": {
    "mode": "export_panels",
    "output_dir": "outputs/panels",
    "overwrite": true
  }
}
```

```bash
pubfig validate-spec panels.spec.json
pubfig render panels.spec.json
```

CLI 本身只是对同一套 Python 绘图 / 导出函数的薄封装。我们已经用 gallery
同源输入做过本地回归，当前 CLI 导出的 PNG 与直接走 Python API 的结果一致。

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
| `dumbbell` | 带连接线的成对比较图 | [示例](#recipe-dumbbell) |
| `forest_plot` | 带置信区间的效应量图 | [示例](#recipe-forest_plot) |

### 组成与极坐标图

| 函数 | 说明 | 示例 |
|------|------|------|
| `grouped_scatter` | 紧凑的分组散点 / benchmark panel | [示例](#recipe-grouped_scatter) |
| `donut` | publication 风格 donut 图 | [示例](#recipe-donut) |
| `stacked_ratio_barh` | 100% 横向比例柱状图 | [示例](#recipe-stacked_ratio_barh) |
| `radial_hierarchy` | 两层径向层级 / sunburst 风格图 | [示例](#recipe-radial_hierarchy) |
| `circular_stacked_bar` | 带内圈分组环的致密环形堆积柱状图 | [示例](#recipe-circular_stacked_bar) |
| `circular_grouped_bar` | 带内圈分组环的致密环形分组柱状图 | [示例](#recipe-circular_grouped_bar) |

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
| `hexbin` | 面向高密度散点的六边形分箱图 | [示例](#recipe-hexbin) |
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
| `volcano` | 展示效应量与显著性的火山图 | [示例](#recipe-volcano) |
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
- `examples/export_composite_showcases_panels.py` —— 导出面板优先的 composite showcases，并推到 Figma 做整图拼接
- `examples/figma_workflow_demo.md` —— 面板优先的 pubfig → Figma 工作流说明
- `examples/generate_palette_gallery.py` —— 重新生成调色板预览图与图库文档
- `examples/README.md` —— 这个目录的保留 / 生成 / 清理清单
- `help(pubfig.circular_stacked_bar)` / `help(pubfig.circular_grouped_bar)` —— 直接在 Python 里查看这两类极坐标图已经固定好的默认参数

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
