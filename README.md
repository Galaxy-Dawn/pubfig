# pubfig

<div align="center">

  <img src="examples/gallery-hero.png" alt="pubfig gallery" width="100%"/>

  <p>
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python 3.10+"/>
    <img src="https://img.shields.io/badge/Matplotlib-3.8%2B-11557C?style=flat-square" alt="Matplotlib 3.8+"/>
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
    <a href="https://github.com/Galaxy-Dawn/pubfig"><img src="https://img.shields.io/github/stars/Galaxy-Dawn/pubfig?style=flat-square" alt="GitHub Stars"/></a>
  </p>

  <strong>Language</strong>: <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.md">English</a> | <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.zh-CN.md">中文</a>

</div>

> Generate publication-quality scientific figures with Matplotlib, journal-style themes, and paper-ready export workflows.

## Highlights

- **Paper-Oriented Defaults** — Compact titles, cleaner legends, explicit font handling, and lighter publication-style line weights.
- **One Library for Common Figure Types** — Statistical plots, distribution plots, dimensionality-reduction plots, evaluation curves, heatmaps, and flow plots in one API surface.
- **Journal-Aware Export** — `save_figure(...)` supports `single`/`double` column widths, vector formats, raster DPI, and trimming for submission workflows.
- **Matplotlib-Native Workflow** — Plot functions return Matplotlib `Figure` objects, so existing analysis scripts remain easy to integrate.
- **Explicit Layout Controls** — Fine-grained control over tick direction, box/grid visibility, palettes, legends, and plot-specific layout options.

## Recent News

2026-03-20: README alignment with pubtab style and homepage refresh — reorganized the README into a pubtab-style homepage with centered badges, language switch, highlights, dated recent news, showcase examples, and an embedded gallery hero.
2026-03-20: Default full install and metadata simplification — changed `pip install pubfig` to install the full plotting stack by default, removed user-facing extras from the main install path, and aligned package metadata, GitHub About, and README wording.
2026-03-19: Raincloud plot support and gallery refresh — added `raincloud(...)`, tuned its default styling, integrated it into the gallery, and regenerated the exported figure set.
2026-03-19: PCA biplot and radar default updates — expanded `pca_biplot(...)` with loading panel modes and group ellipses, refreshed radar defaults, unified font handling, and re-exported the gallery.

## Examples

### Showcase

<p align="center">
  <a href="examples/bar_scatter.png"><img src="examples/bar_scatter.png" width="48%" alt="Bar scatter example"></a>
  <a href="examples/raincloud.png"><img src="examples/raincloud.png" width="48%" alt="Raincloud example"></a>
</p>
<p align="center">
  <a href="examples/radar.png"><img src="examples/radar.png" width="72%" alt="Radar example"></a>
</p>

<details>
<summary><strong>Full Gallery</strong></summary>

<p align="center">
  <img src="examples/gallery-hero.png" width="100%" alt="Full gallery contact sheet">
</p>

</details>

## Quick Start

```bash
pip install pubfig
```

### Python Quick Start

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

If you want explicit suffix-based export instead of the journal-oriented wrapper, use:

```python
pf.batch_export(fig, "figure1", formats=("pdf", "png"), dpi=300)
```

## Plot Families

### Categorical and statistical plots

| Function | Description |
|----------|-------------|
| `bar` | Simple bar chart and grouped bar chart |
| `bar_scatter` | Grouped bar chart with raw points and significance annotations |
| `stacked_bar` | Horizontal stacked bar chart |
| `paired` | Paired dot plot |

### Distribution plots

| Function | Description |
|----------|-------------|
| `box` | Box plot |
| `violin` | Violin plot |
| `strip` | Strip plot |
| `raincloud` | Half-violin + box + raw-point raincloud plot |
| `density` | Density plot with KDE |
| `histogram` | Histogram with optional KDE |
| `ridgeline` | Ridgeline plot |

### Trend and relationship plots

| Function | Description |
|----------|-------------|
| `line` | Line chart with optional CI |
| `area` | Stacked area chart |
| `scatter` | Scatter plot with optional grouped workflow |
| `bubble` | Bubble chart |
| `contour2d` | 2D contour plot with marginals |
| `radar` | Radar chart |

### Matrix, embedding, and multivariate plots

| Function | Description |
|----------|-------------|
| `heatmap` | Heatmap |
| `corr_matrix` | Correlation heatmap |
| `clustermap` | Clustered heatmap |
| `dimreduce` | Dimensionality-reduction scatter plot |
| `pca_biplot` | PCA biplot with optional loadings and group ellipses |
| `parallel_coordinates` | Parallel coordinates plot |

### Evaluation and flow plots

| Function | Description |
|----------|-------------|
| `roc` | ROC curve with AUC |
| `pr_curve` | Precision-Recall curve with AP |
| `sankey` | Sankey diagram |

## Themes, Specs, and Palettes

### Built-in themes

`pubfig` currently ships with these themes:

- `default`
- `nature`
- `science`
- `cell`

```python
pf.set_default_theme("science")
```

### Figure specs

For export, `save_figure(...)` uses named figure specs:

- `nature`
- `science`
- `cell`

Width can be specified as:

- `"single"`
- `"double"`
- numeric millimeters such as `120`
- string millimeters such as `"120mm"`

### Built-in palettes

Built-in palettes include:

- `DEFAULT`
- `NATURE`
- `SCIENCE`
- `LANCET`
- `JAMA`

```python
from pubfig import NATURE, show_palette

show_palette(NATURE).show()
```

You can also fetch palettes by name:

```python
palette = pf.get_palette("science")
```

## Gallery and Examples

Example entry points:

- `examples/gallery.py` — quick visual walkthrough of supported plots
- `examples/export_gallery.py` — exports the gallery to `output_figures/`
- `examples/export_gallery_mpl.py` — focused Matplotlib export examples

## Development

### Editable install

```bash
pip install -e .[dev]
```

### Run tests

```bash
pytest
```

### Lint

```bash
ruff check src tests examples
```

### Regenerate gallery

```bash
python examples/export_gallery.py
```

## License

MIT
