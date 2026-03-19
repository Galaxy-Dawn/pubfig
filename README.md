# pubfig

**Language**: [English](README.md) | [中文](README.zh-CN.md)

Publication-quality plotting with Matplotlib for academic papers.

`pubfig` is an academic-first plotting library built on top of Matplotlib. It brings together journal-style themes, paper-oriented plot defaults, palette utilities, and export helpers so you can move from raw arrays to submission-ready figures with less manual cleanup.

## Quick Navigation

| Topic | Description |
|-------|-------------|
| 🚀 [Quick Start](#quick-start) | Install `pubfig`, create a figure, and export it for a paper |
| ✨ [Why pubfig](#why-pubfig) | What the library is optimized for |
| 📦 [Installation](#installation) | Base install and optional extras |
| 📊 [Plot Families](#plot-families) | Supported plots grouped by scientific task |
| 🎨 [Themes, Specs, and Palettes](#themes-specs-and-palettes) | Journal themes, export specs, and palette helpers |
| 🖼️ [Gallery and Examples](#gallery-and-examples) | Example scripts and exported gallery assets |
| 🔧 [Development](#development) | Editable install, tests, lint, and gallery regeneration |

## Why pubfig

`pubfig` is built for the last mile between analysis code and publication figures.

- **Academic-first defaults**: compact titles, cleaner legends, explicit font handling, and lighter paper-style line weights
- **One library for common scientific figures**: statistical plots, distribution plots, embedding plots, evaluation curves, heatmaps, and flow plots
- **Journal-aware export**: `save_figure(...)` supports `single`/`double` column widths, raster DPI, vector formats, and trimming
- **Matplotlib-native workflow**: plot functions return Matplotlib `Figure` objects, so existing analysis pipelines remain easy to integrate
- **Explicit control when needed**: axis tick direction, box/grid visibility, palette overrides, and plot-specific layout parameters

## Installation

### Base installation

```bash
pip install pubfig
```

### Optional extras

```bash
pip install pubfig[stats]         # OLS-style regression support in scatter workflows
pip install pubfig[dimreduction]  # scikit-learn-backed dimensionality reduction helpers
pip install pubfig[raster]        # TIFF export via Pillow
pip install pubfig[all]           # Everything above
```

### Requirements

- Python `>=3.10`
- Core dependencies: `matplotlib`, `numpy`, `scipy`

## Quick Start

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

## Common Workflows

### 1. Statistical comparison figures

Use `bar`, `bar_scatter`, `box`, `violin`, `strip`, and `raincloud` when you need summary statistics together with raw observations for biology, neuroscience, psychology, or experimental ML.

### 2. Trend and relationship figures

Use `line`, `area`, `scatter`, `paired`, `bubble`, and `contour2d` for trajectories, pairwise comparisons, grouped relationships, and compact distribution-overlap views.

### 3. Structure, embedding, and evaluation figures

Use `heatmap`, `corr_matrix`, `clustermap`, `dimreduce`, `pca_biplot`, `roc`, `pr_curve`, `sankey`, and `parallel_coordinates` for model interpretation, embedding visualization, clustering, and evaluation reporting.

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

Current exported gallery assets live in:

- `output_figures/`
- `output_figures/all_plots_contact_sheet.png`

This is the easiest way to review theme, font, layout, and color changes across the full library after an update.

## Development

### Editable install

```bash
pip install -e .[all,dev]
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
