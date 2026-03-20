# pubfig

**语言**: [English](README.md) | [中文](README.zh-CN.md)

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB.svg?logo=python&logoColor=white)](https://github.com/Galaxy-Dawn/pubfig)
[![Matplotlib](https://img.shields.io/badge/matplotlib-3.8%2B-11557C.svg)](https://github.com/Galaxy-Dawn/pubfig)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Galaxy-Dawn/pubfig?style=social)](https://github.com/Galaxy-Dawn/pubfig)

面向科研论文的 Matplotlib 高质量绘图库。

`pubfig` 是一个构建在 Matplotlib 之上的科研绘图库。它把期刊风格主题、更干净的绘图默认值、调色板工具和投稿导向的导出辅助封装成一个统一工作流，让你可以更少地做手工排版清理，更快地从原始数组走到投稿级图件。

## 快速导航

| 主题 | 说明 |
|------|------|
| 🚀 [快速开始](#快速开始) | 安装 `pubfig`、生成图像并导出为论文图 |
| ✨ [为什么是 pubfig](#为什么是-pubfig) | 这个库重点优化了什么 |
| 📦 [安装](#安装) | 安装 `pubfig` 并直接开始画图 |
| 📊 [图类型分组](#图类型分组) | 按科研任务组织支持的图表 |
| 🎨 [主题、规格与配色](#主题规格与配色) | 期刊主题、导出规格和调色板工具 |
| 🖼️ [Gallery 与示例](#gallery-与示例) | 示例脚本与导出的 gallery 产物 |
| 🔧 [开发](#开发) | 可编辑安装、测试、lint 与 gallery 重导 |

## 为什么是 pubfig

`pubfig` 面向的是分析代码到论文图件之间的最后一公里。

- **论文导向默认值**：更紧凑的标题、更干净的图例、显式字体处理、以及更接近论文风格的线宽
- **覆盖常见科研图形**：统计图、分布图、降维图、评估曲线、热图和 flow 图都在一个库里
- **面向投稿的导出接口**：`save_figure(...)` 支持 `single`/`double` 栏宽、raster DPI、vector 格式和 trim
- **Matplotlib 原生工作流**：所有绘图函数都返回 Matplotlib `Figure` 对象，便于接入现有分析脚本
- **需要时可精细控制**：刻度朝向、box/grid 显示、palette 覆盖、以及各图专属布局参数

## 安装

### 基础安装

```bash
pip install pubfig
```

### 运行要求

- Python `>=3.10`
- 核心依赖：`matplotlib`、`numpy`、`scipy`、`statsmodels`、`scikit-learn`、`pillow`

## 快速开始

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

## 常见工作流

### 1. 统计比较图

当你需要在 biology、neuroscience、psychology 或 experimental ML 中同时展示 summary statistics 和 raw observations 时，可以使用 `bar`、`bar_scatter`、`box`、`violin`、`strip` 和 `raincloud`。

### 2. 趋势与关系图

当你要展示轨迹、配对比较、组间关系或分布重叠时，可以使用 `line`、`area`、`scatter`、`paired`、`bubble` 和 `contour2d`。

### 3. 结构、嵌入与评估图

当你要做模型解释、embedding 可视化、聚类展示或评估汇报时，可以使用 `heatmap`、`corr_matrix`、`clustermap`、`dimreduce`、`pca_biplot`、`roc`、`pr_curve`、`sankey` 和 `parallel_coordinates`。

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

### 评估与 flow 图

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

### Figure spec

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
```

## Gallery 与示例

示例入口包括：

- `examples/gallery.py` —— 快速浏览支持的图类型
- `examples/export_gallery.py` —— 把 gallery 导出到 `output_figures/`
- `examples/export_gallery_mpl.py` —— 更聚焦的 Matplotlib 导出示例

当前导出的 gallery 产物位于：

- `output_figures/`
- `output_figures/all_plots_contact_sheet.png`

当你修改主题、字体、布局或颜色后，这是回看全库视觉一致性的最快方式。

## 开发

### 可编辑安装

```bash
pip install -e .[all,dev]
```

### 运行测试

```bash
pytest
```

### Lint

```bash
ruff check src tests examples
```

### 重导 gallery

```bash
python examples/export_gallery.py
```

## License

MIT
