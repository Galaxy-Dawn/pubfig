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
- **2026-03-20**: CLI + Figma plugin 工作流 — 新增 `pubfig figma package|validate|inspect`，引入单文件的 Figma bundle JSON 格式，并提供 `figma-plugin/pubfig-sync` 插件脚手架，用于节点级导入与刷新。
- **2026-03-20**: Figma-first panel 导出工作流 — 新增 `export_panel(...)` 和 `export_panels(...)`，用于稳定导出 subplot 资产；同时增加最小化的 `panel-index.json` 同步索引，并补充 Codex + Figma MCP 的多 panel 精修路径说明。
- **2026-03-20**: 与 pubtab 风格对齐并刷新首页结构 — 按照 pubtab 的首页组织方式重排 README，补上居中 badges、语言切换、highlights、带日期的 recent news、精选示例和 gallery hero 图。
- **2026-03-20**: 默认完整安装与元信息简化 — 将 `pip install pubfig` 调整为默认安装完整绘图栈，移除主安装路径上的用户可见 extras，并同步统一包元信息、GitHub About 和 README 文案。
- **2026-03-19**: 新增 raincloud 并刷新 gallery — 增加 `raincloud(...)`，优化其默认样式，接入 gallery，并重新导出整套图像产物。
- **2026-03-19**: 更新 PCA biplot 与 radar 默认示例 — 扩展 `pca_biplot(...)` 的 loading panel 模式和 group ellipses，刷新 radar 默认示例，统一字体处理，并重新导出 gallery。

## 示例

### 精选展示

<p align="center">
  <a href="examples/bar_scatter.png"><img src="examples/bar_scatter.png" width="48%" alt="Bar scatter 示例"></a>
  <a href="examples/raincloud.png"><img src="examples/raincloud.png" width="48%" alt="Raincloud 示例"></a>
</p>
<p align="center">
  <a href="examples/radar.png"><img src="examples/radar.png" width="72%" alt="Radar 示例"></a>
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

```python
import numpy as np
import pubfig as pf

pf.set_default_theme("nature")

rng = np.random.default_rng(0)
data = rng.normal(loc=0.0, scale=1.0, size=(3, 2, 20))

fig = pf.bar_scatter(
    data,
    category_names=["Condition A", "Condition B", "Condition C"],
    series_names=["Ctrl", "Treatment"],
    title="Bar + Scatter",
)

pf.save_figure(
    fig,
    "figure1",
    spec="nature",
    width="single",
    aspect_ratio=0.65,
    raster_dpi=600,
    vector_formats=("pdf", "svg"),
    raster_formats=("png", "tiff"),
    trim=True,
)
```

如果你想使用显式后缀驱动的导出，而不是期刊导向的包装接口，可以用：

```python
pf.batch_export(fig, "figure1", formats=("pdf", "png"), dpi=300)
```

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

`pubfig` 和 Figma 现在走的是一条 **panel-first 的整图装配工作流**：

- **Python / pubfig** 负责生成干净、稳定的 panel 图形资产
- **Figma** 负责整张 publication figure 的最终拼版与精修
- 两者之间的交接物是一个 panel 目录，再加一个 `.pubfig-figma.json` bundle

换句话说，`pubfig` 不是要替代 Figma 做整图排版；它负责把 panel 资产稳定导出，
而 Figma 继续负责整图级标题、shared legend、箭头、注释和最终视觉收尾。

现在 panel 导出默认会产出**不带 subplot title 的干净图形资产**，这样标题可以在
Figma 的整图编排阶段统一处理。如果你确实想保留 panel 内嵌 title，可以显式传
`include_title=True`。

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)

panels = {
    "a": pf.bar(rng.uniform(0.4, 0.9, size=3), category_names=["A", "B", "C"]),
    "b": pf.scatter(rng.normal(size=40), rng.normal(size=40)),
}

pf.export_panels(panels, "panels", overwrite=True)
```

这一步会生成：

- `a.svg`、`b.svg` ...
- `panel-index.json`

如果你想得到一个单文件的 Figma 交接包，再对这个目录执行：

```bash
pubfig figma package panels --figure-id figure-01
```

它会写出：

- `figure-01.pubfig-figma.json`

### 推荐的日常主路径

当前更推荐的实际工作流是：

1. 先从 Python 导出 panels
2. 在 Figma 里把 plugin 和本地 bridge 连上一次
3. 之后从终端直接运行 `pubfig figma push`
4. 让 Figma 原地 refresh 当前 figure
5. 如果 bridge refresh 临时卡住，就把刚刚写出的 bundle 直接载入 plugin 做 manual fallback

```bash
pubfig figma push panels --figure-id figure-01
```

`pubfig figma push` 是对旧 bridge 工作流做的 agent-first 封装：它会自动确保本地
bridge 可用、默认选择 latest session、自动开启 `--write-bundle`，然后再执行
sync / refresh。

`--write-bundle` 很关键：它会先把这次 bridge 实际发送的 payload 落成一个
bundle，这样 bridge refresh 和 manual fallback 用的是**同一份交接物**，而不是
两条不同导出链路。

### plugin 负责什么

`figma-plugin/pubfig-sync` 负责：

- 从 panel bundle 导入一张新 figure
- 在 `figure_id` 不变时原地 refresh 现有 figure
- 显示 bridge 状态和 session 状态
- 显示 bundle provenance，包括实际写出的 `bundle_path`
- 当 bridge sync 卡住时，直接从同一个 bundle 做 manual import / refresh

### CLI 入口

现在 `sync` / `watch` 同时接受 **panel 目录** 和已经打好的
`.pubfig-figma.json` bundle：

```bash
pubfig figma sync figure-01.pubfig-figma.json --session latest
pubfig figma watch figure-01.pubfig-figma.json --session latest
```

其他相关入口包括：

- `export_panel(...)`
- `export_panels(...)`
- `pubfig figma push`
- `pubfig figma package`
- `pubfig figma validate`
- `pubfig figma inspect`
- `pubfig figma sync`
- `pubfig figma watch`
- `pubfig figma bridge start|status`

插件脚手架位于：

- `figma-plugin/pubfig-sync/manifest.json`
- `figma-plugin/pubfig-sync/code.js`
- `figma-plugin/pubfig-sync/ui.html`
- `figma-plugin/pubfig-sync/README.md`

如果你在本地用 Codex，也可以继续让配套 skill `pubfig-figma-workflow` 协调 panel 导出 → Figma 导入 → MCP 检查流程。

### Figma Bridge Automation

如果你想要更稳定的 **一次连接、终端触发** 工作流：

1. 在 Figma 中打开 `pubfig-sync`，将 bridge URL 填为 `http://localhost:47329` 并点击 **Connect Bridge**
2. 之后从终端触发刷新：

```bash
pubfig figma push panels --figure-id figure-01
pubfig figma sync panels/figure-01.pubfig-figma.json --session latest
pubfig figma bridge status
```

对 localhost bridge URL，`push` 会在需要时自动拉起本地 bridge。如果 bridge 或
plugin refresh 临时失效，你仍然可以立刻把写出的 `.pubfig-figma.json` 手动导入
到 Figma，形成完整 fallback 闭环。

`pubfig figma watch` 现在也会在每次刷新时输出更完整的事件信息，包括触发变更
的源文件、解析后的 source kind，以及 manual fallback 对应的 `bundle_path`。

bridge job 现在还会携带 `bundle_provenance`，因此 plugin 在收到 bridge 推送时，
也能直接显示这次刷新来自哪个 bundle 文件或 source 路径。换句话说，现在
bridge sync 和 manual fallback 已经围绕同一个落盘 bundle 形成闭环。

## 图类型分组

### 类别与统计图

| 函数 | 说明 |
|------|------|
| `bar` | 简单柱状图与分组柱状图 |
| `bar_scatter` | 带原始点和显著性标注的分组柱状图 |
| `stacked_bar` | 横向 stacked bar |
| `paired` | 配对点图 |

### 分布图

| 函数 | 说明 |
|------|------|
| `box` | 箱线图 |
| `violin` | 小提琴图 |
| `strip` | 条带散点图 |
| `raincloud` | half-violin + box + raw-point 的云雨图 |
| `density` | 带 KDE 的密度图 |
| `histogram` | 可选 KDE 的直方图 |
| `ridgeline` | Ridgeline 图 |

### 趋势与关系图

| 函数 | 说明 |
|------|------|
| `line` | 可带 CI 的折线图 |
| `area` | 堆叠面积图 |
| `scatter` | 支持分组工作流的散点图 |
| `bubble` | 气泡图 |
| `contour2d` | 带边缘分布的 2D contour 图 |
| `radar` | 雷达图 |

### 矩阵、嵌入与多变量图

| 函数 | 说明 |
|------|------|
| `heatmap` | 热图 |
| `corr_matrix` | 相关性热图 |
| `clustermap` | 聚类热图 |
| `dimreduce` | 降维散点图 |
| `pca_biplot` | 支持 loadings 与 group ellipses 的 PCA biplot |
| `parallel_coordinates` | 平行坐标图 |

### 评估与 Flow 图

| 函数 | 说明 |
|------|------|
| `roc` | 带 AUC 的 ROC 曲线 |
| `pr_curve` | 带 AP 的 Precision-Recall 曲线 |
| `sankey` | Sankey 图 |

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
