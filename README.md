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

> Publication-ready scientific plotting with Matplotlib.

## Highlights

- **Publication-Style Defaults** — Compact titles, cleaner legends, explicit font handling, and line weights that read more like finished paper figures.
- **One Library for Common Figure Types** — Statistical plots, distribution plots, dimensionality-reduction plots, evaluation curves, heatmaps, and flow plots in one API surface.
- **Export Specs Without Boilerplate** — `save_figure(...)` directly handles `single`/`double` column widths, vector formats, raster DPI, and trimming.
- **Matplotlib-Native Workflow** — Plot functions return Matplotlib `Figure` objects, so existing analysis scripts remain easy to integrate.
- **Explicit Layout Controls** — Fine-grained control over tick direction, box/grid visibility, palettes, legends, and plot-specific layout options.

## Recent News

- **2026-03-25**: Panel-first Figma loop polish — panel export now defaults to title-free assets for cleaner Figma assembly, `pubfig-sync` now keeps shared title / legend placeholders off by default, and bridge/watch flows now surface bundle provenance plus the exact manual-fallback bundle path.
- **2026-03-20**: Local bridge automation for Figma sync — added a bridge-backed `pubfig figma bridge|sync|watch` workflow, upgraded `pubfig-sync` with bridge connection mode, and enabled CLI-triggered vector import/refresh after one-time plugin connection.
- **2026-03-20**: Figma plugin v2 workflow polish — added `auto` / `hero_top` relayout presets, upgraded shared title / legend placeholders, and improved refresh behavior so manual Figma positioning is preserved more reliably unless relayout is requested.

<details>
<summary><strong>View older changelog</strong></summary>

- **2026-03-20**: CLI + Figma plugin workflow — added `pubfig figma package|validate|inspect`, introduced a single-file Figma bundle JSON format for exported panels, and scaffolded the `figma-plugin/pubfig-sync` plugin for node-level import and refresh.
- **2026-03-20**: Figma-first panel export workflow — added `export_panel(...)` and `export_panels(...)` for stable subplot asset export, introduced a minimal `panel-index.json` sync index, and documented the Codex + Figma MCP refinement path for multi-panel figures.
- **2026-03-20**: README alignment with pubtab style and homepage refresh — reorganized the README into a pubtab-style homepage with centered badges, language switch, highlights, dated recent news, showcase examples, and an embedded gallery hero.
- **2026-03-20**: Default full install and metadata simplification — changed `pip install pubfig` to install the full plotting stack by default, removed user-facing extras from the main install path, and aligned package metadata, GitHub About, and README wording.
- **2026-03-19**: Raincloud plot support and gallery refresh — added `raincloud(...)`, tuned its default styling, integrated it into the gallery, and regenerated the exported figure set.
- **2026-03-19**: PCA biplot and radar default updates — expanded `pca_biplot(...)` with loading panel modes and group ellipses, refreshed radar defaults, unified font handling, and re-exported the gallery.

</details>

## Examples

### Showcase

<p align="center">
  <a href="examples/bar_scatter.png"><img src="examples/bar_scatter.png" width="48%" alt="Bar scatter example"></a>
  <a href="examples/raincloud.png"><img src="examples/raincloud.png" width="48%" alt="Raincloud example"></a>
</p>
<p align="center">
  <a href="examples/line.png"><img src="examples/line.png" width="48%" alt="Line example"></a>
  <a href="examples/radar.png"><img src="examples/radar.png" width="48%" alt="Radar example"></a>
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

Start with the fewest possible parameters first:

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

This is enough to get your first figure out. You do **not** need to understand
layout, export, or publication-specific parameters before the first run.

#### Most common next parameters

Once the minimal example works, these are usually the first parameters worth adding:

```python
fig = pf.bar_scatter(
    data,
    category_names=["Condition A", "Condition B", "Condition C"],
    series_names=["Ctrl", "Treatment"],
    title="Bar + Scatter",
)

pf.save_figure(fig, "figure1", spec="nature", width="single")
```

- `category_names`: names on the x-axis
- `series_names`: names in the legend
- `title`: figure title
- `spec` / `width`: journal-style export presets

Only add parameters like `aspect_ratio`, `vector_formats`, `raster_formats`, or
`trim` when you already know why you need them.

#### Where to look up detailed parameters

If you want to understand a specific plot in more detail, start here:

```python
help(pf.bar_scatter)
help(pf.line)
help(pf.heatmap)
```

You can also inspect runnable examples under [`examples/`](examples/).

#### Saving PNG / SVG / PDF

`pf.save_figure(fig, "figure1")` takes a base path **without** an extension and,
by default, writes:

- `figure1.pdf`
- `figure1.svg`
- `figure1.png`

If you want to choose formats explicitly:

```python
pf.save_figure(fig, "figure1", vector_formats=("pdf",), raster_formats=())
pf.save_figure(fig, "figure1", vector_formats=("svg",), raster_formats=("png",))
```

#### Plot recipes by family

These rows are the shortest useful plotting calls. When you want to export one,
reuse `pf.save_figure(fig, "name")` from Quick Start.

Each row assumes:

```python
import numpy as np
import pubfig as pf
```

##### Categorical and statistical

| Plot | Minimal call | Common next parameters |
|------|--------------|------------------------|
| <a id="recipe-bar"></a>`bar` | `pf.bar(np.array([3, 5, 4]), category_names=["A", "B", "C"])` | `category_names`, `title`, `color_palette` |
| <a id="recipe-bar-scatter"></a>`bar_scatter` | `pf.bar_scatter(np.random.default_rng(0).normal(size=(3, 2, 20)))` | `category_names`, `series_names`, `show_statistics` |
| <a id="recipe-stacked_bar"></a>`stacked_bar` | `pf.stacked_bar(np.array([[[3, 2], [4, 1]], [[2, 3], [3, 2]]], dtype=float), group_names=["Batch 1", "Batch 2"])` | `group_names`, `normalize`, `title` |
| <a id="recipe-paired"></a>`paired` | `pf.paired(np.array([1.0, 2.0, 2.5, 3.0]), np.array([1.3, 2.1, 2.9, 3.2]))` | `x_labels`, `y_label`, `title` |

##### Distribution

| Plot | Minimal call | Common next parameters |
|------|--------------|------------------------|
| <a id="recipe-box"></a>`box` | `pf.box(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `show_means`, `title` |
| <a id="recipe-violin"></a>`violin` | `pf.violin(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `show_box`, `show_points` |
| <a id="recipe-strip"></a>`strip` | `pf.strip(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `jitter`, `title` |
| <a id="recipe-raincloud"></a>`raincloud` | `pf.raincloud(np.random.default_rng(0).normal(size=(80, 3)), category_names=["A", "B", "C"])` | `category_names`, `orientation`, `title` |
| <a id="recipe-density"></a>`density` | `pf.density(np.random.default_rng(0).normal(size=400))` | `title`, `color_palette`, `bins` |
| <a id="recipe-histogram"></a>`histogram` | `pf.histogram(np.random.default_rng(0).normal(size=400), show_kde=True)` | `bins`, `show_kde`, `title` |
| <a id="recipe-ridgeline"></a>`ridgeline` | `pf.ridgeline([np.random.default_rng(0).normal(loc=i, size=200) for i in range(4)], category_names=["S1", "S2", "S3", "S4"])` | `category_names`, `offset_step`, `title` |

##### Trend and relationship

| Plot | Minimal call | Common next parameters |
|------|--------------|------------------------|
| <a id="recipe-area"></a>`area` | `pf.area(np.random.default_rng(0).random((20, 3)), series_names=["A", "B", "C"])` | `series_names`, `x`, `title` |
| <a id="recipe-line"></a>`line` | `pf.line(np.sin(np.linspace(0, 2 * np.pi, 100)), x=np.linspace(0, 2 * np.pi, 100))` | `x_label`, `y_label`, `series_names`, `title` |
| <a id="recipe-scatter"></a>`scatter` | `pf.scatter(np.random.default_rng(0).normal(size=60), np.random.default_rng(1).normal(size=60))` | `labels`, `x_label`, `y_label` |
| <a id="recipe-bubble"></a>`bubble` | `pf.bubble(np.random.default_rng(0).normal(size=30), np.random.default_rng(1).normal(size=30), np.random.default_rng(2).uniform(1, 10, size=30))` | `labels`, `size_label`, `title` |
| <a id="recipe-contour2d"></a>`contour2d` | `pf.contour2d(np.random.default_rng(0).normal(size=500), np.random.default_rng(1).normal(size=500))` | `bins`, `colorscale`, `title` |
| <a id="recipe-radar"></a>`radar` | `pf.radar([[0.8, 0.7, 0.9, 0.75], [0.65, 0.85, 0.7, 0.8]], categories=["Speed", "Accuracy", "Recall", "Stability"], series_names=["Model A", "Model B"])` | `categories`, `series_names`, `title` |

##### Matrix and multivariate

| Plot | Minimal call | Common next parameters |
|------|--------------|------------------------|
| <a id="recipe-heatmap"></a>`heatmap` | `pf.heatmap(np.random.default_rng(0).uniform(size=(4, 4)))` | `category_names`, `title`, color scale related options |
| <a id="recipe-corr_matrix"></a>`corr_matrix` | `pf.corr_matrix(np.random.default_rng(0).normal(size=(60, 4)), variable_names=["A", "B", "C", "D"])` | `variable_names`, `method`, `title` |
| <a id="recipe-clustermap"></a>`clustermap` | `pf.clustermap(np.random.default_rng(0).uniform(size=(8, 6)))` | `row_category_names`, `column_category_names`, `title` |
| <a id="recipe-dimreduce"></a>`dimreduce` | `fig, _ = pf.dimreduce(np.random.default_rng(0).normal(size=(40, 8)), cluster_id=np.repeat([0, 1], 20))` | `cluster_id`, `labels`, `n_components` |
| <a id="recipe-pca_biplot"></a>`pca_biplot` | `pf.pca_biplot(np.random.default_rng(0).normal(size=(40, 5)), labels=np.repeat(["A", "B"], 20), variable_names=["V1", "V2", "V3", "V4", "V5"])` | `labels`, `variable_names`, `loading_panel` |
| <a id="recipe-parallel_coordinates"></a>`parallel_coordinates` | `pf.parallel_coordinates(np.random.default_rng(0).uniform(size=(20, 4)), variable_names=["W", "X", "Y", "Z"])` | `variable_names`, `color_col`, `title` |

##### Evaluation and flow

| Plot | Minimal call | Common next parameters |
|------|--------------|------------------------|
| <a id="recipe-roc"></a>`roc` | `pf.roc([np.array([0.0, 0.1, 0.3, 1.0])], [np.array([0.0, 0.7, 0.9, 1.0])], series_names=["Model A"])` | `series_names`, `baseline`, `title` |
| <a id="recipe-pr_curve"></a>`pr_curve` | `pf.pr_curve([np.array([1.0, 0.9, 0.8, 0.6])], [np.array([0.1, 0.4, 0.7, 1.0])], series_names=["Model A"])` | `series_names`, `title`, `xlim` / `ylim` |
| <a id="recipe-sankey"></a>`sankey` | `pf.sankey([0, 0, 1], [2, 3, 3], [10, 5, 8], node_names=["Input A", "Input B", "Path 1", "Outcome"])` | `node_names`, `title`, `color_palette` |

For `bar_scatter(...)`, significance spacing parameters now follow explicit orientation-based names:

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

#### What this gives you

`pubfig` exports clean panel artwork, and Figma stays the place where you
assemble and finish the whole publication figure.

For day-to-day use, the main command is `pubfig figma push`.

#### Quick Start

1. Install `pubfig-sync` in Figma Desktop the first time: go to **Plugins → Development → Import plugin from manifest...**, then select `figma-plugin/pubfig-sync/manifest.json` from this repo. After that, reopen it from **Plugins → Development → pubfig-sync**.
2. Click **Connect Bridge** once in the plugin.
3. Export your panels from Python.
4. Run `pubfig figma push <panel_dir> --figure-id <id>` from the terminal.
5. If the bridge path fails, load the written bundle in the plugin and use the manual buttons.

```bash
pubfig figma push panels --figure-id figure-01
```

#### Minimal example

Panel export now defaults to **clean, title-free art** so subplot titles can be
handled at the Figma assembly layer. If you explicitly want embedded panel
headers, pass `include_title=True`.

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)

panels = {
    "a": pf.bar(rng.uniform(0.4, 0.9, size=3), category_names=["A", "B", "C"]),
    "b": pf.scatter(rng.normal(size=40), rng.normal(size=40)),
}

pf.export_panels(panels, "panels", overwrite=True)  # title-free art by default
```

```bash
pubfig figma push panels --figure-id figure-01
```

This writes panel assets such as `a.svg`, `b.svg`, and `panel-index.json`, then
uses `push` as the primary panel-first handoff into Figma.

#### How refresh works

- Keep the same `figure_id` to refresh the existing figure in place.
- Use a new `figure_id` to import a separate figure.

#### FAQ / Troubleshooting

**What does Connect Bridge do?**  
It links the open Figma plugin to your local terminal workflow so later `push`
commands know which live session to refresh.

**What does `pubfig figma push` do automatically?**  
It is the primary agent-first command. It ensures the local bridge is available,
selects the latest connected session, writes the bundle, and then syncs or
refreshes the figure.

**What is the `.pubfig-figma.json` file?**  
It is the exact Figma handoff bundle for one figure. Keep it around for manual
import, refresh, debugging, or recovery.

**How do I do manual fallback?**  
If bridge refresh stalls, load the latest written `.pubfig-figma.json` bundle in
`pubfig-sync`, then use **Import as New**, **Manual Refresh**, or **Refresh + Relayout**.

**When should I use `pubfig figma package`?**  
Use it as the **secondary** path when you only want to write a standalone
bundle without pushing immediately.

```bash
pubfig figma package panels --figure-id figure-01
```

**Where are the advanced commands?**  
Use these only for finer control or debugging after the normal `push` path:

```bash
pubfig figma sync figure-01.pubfig-figma.json --session latest
pubfig figma watch figure-01.pubfig-figma.json --session latest
pubfig figma bridge status
```

If you use Codex locally, the companion skill `pubfig-figma-workflow` can still
orchestrate the panel export → Figma import → MCP review loop.

## Plot Families

### Categorical and Statistical Plots

| Function | Description | Recipe |
|----------|-------------|--------|
| `bar` | Simple bar chart and grouped bar chart | [recipe](#recipe-bar) |
| `bar_scatter` | Grouped bar chart with raw points and significance annotations | [recipe](#recipe-bar-scatter) |
| `stacked_bar` | Horizontal stacked bar chart | [recipe](#recipe-stacked_bar) |
| `paired` | Paired dot plot | [recipe](#recipe-paired) |

### Distribution Plots

| Function | Description | Recipe |
|----------|-------------|--------|
| `box` | Box plot | [recipe](#recipe-box) |
| `violin` | Violin plot | [recipe](#recipe-violin) |
| `strip` | Strip plot | [recipe](#recipe-strip) |
| `raincloud` | Half-violin + box + raw-point raincloud plot | [recipe](#recipe-raincloud) |
| `density` | Density plot with KDE | [recipe](#recipe-density) |
| `histogram` | Histogram with optional KDE | [recipe](#recipe-histogram) |
| `ridgeline` | Ridgeline plot | [recipe](#recipe-ridgeline) |

### Trend and Relationship Plots

| Function | Description | Recipe |
|----------|-------------|--------|
| `line` | Line chart with optional CI | [recipe](#recipe-line) |
| `area` | Stacked area chart | [recipe](#recipe-area) |
| `scatter` | Scatter plot with optional grouped workflow | [recipe](#recipe-scatter) |
| `bubble` | Bubble chart | [recipe](#recipe-bubble) |
| `contour2d` | 2D contour plot with marginals | [recipe](#recipe-contour2d) |
| `radar` | Radar chart | [recipe](#recipe-radar) |

### Matrix, Embedding, and Multivariate Plots

| Function | Description | Recipe |
|----------|-------------|--------|
| `heatmap` | Heatmap | [recipe](#recipe-heatmap) |
| `corr_matrix` | Correlation heatmap | [recipe](#recipe-corr_matrix) |
| `clustermap` | Clustered heatmap | [recipe](#recipe-clustermap) |
| `dimreduce` | Dimensionality-reduction scatter plot | [recipe](#recipe-dimreduce) |
| `pca_biplot` | PCA biplot with optional loadings and group ellipses | [recipe](#recipe-pca_biplot) |
| `parallel_coordinates` | Parallel coordinates plot | [recipe](#recipe-parallel_coordinates) |

### Evaluation and Flow Plots

| Function | Description | Recipe |
|----------|-------------|--------|
| `roc` | ROC curve with AUC | [recipe](#recipe-roc) |
| `pr_curve` | Precision-Recall curve with AP | [recipe](#recipe-pr_curve) |
| `sankey` | Sankey diagram | [recipe](#recipe-sankey) |

## Themes, Specs, and Palettes

### Built-in Themes

`pubfig` currently ships with these themes:

- `default`
- `nature`
- `science`
- `cell`

```python
pf.set_default_theme("science")
```

### Figure Specs

For export, `save_figure(...)` uses named figure specs:

- `nature`
- `science`
- `cell`

Width can be specified as:

- `"single"`
- `"double"`
- numeric millimeters such as `120`
- string millimeters such as `"120mm"`

### Built-in Palettes

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
palette = pf.get_palette("carto_blugrn")
```

These journal-style palettes are **inspired** palettes, not official journal standards. In `pubfig`, the `NATURE`, `SCIENCE`, `LANCET`, and `JAMA` cards are derived from widely used **ggsci-derived community palettes** rather than publisher-mandated color specifications.

Source note: ggsci documents these palettes as inspired by NPG / Nature Publishing Group, AAAS / Science, Lancet journals, and JAMA figures. See [pal_npg](https://nanx.me/ggsci/reference/pal_npg.html), [pal_aaas](https://nanx.me/ggsci/reference/pal_aaas.html), [pal_lancet](https://nanx.me/ggsci/reference/pal_lancet.html), and [pal_jama](https://nanx.me/ggsci/reference/pal_jama.html).

For a visual preview of all currently available palettes, see [`docs/palette-gallery.md`](docs/palette-gallery.md).

[![Featured palettes](examples/palettes/featured-palettes.png)](docs/palette-gallery.md)

## Gallery and Examples

Most files under `examples/` are either:

- runnable example scripts, or
- rendered assets used by this README and the palette docs.

If you only want the main entry points, start here:

- `examples/gallery.py` — quick visual walkthrough of supported plots
- `examples/export_gallery.py` — exports the gallery to `output_figures/`
- `examples/figma_panels_demo.py` — exports multiple pubfig panels for Figma handoff
- `examples/figma_workflow_demo.md` — panel-first pubfig → Figma workflow guide
- `examples/generate_palette_gallery.py` — regenerates the palette preview sheets and gallery docs
- `examples/README.md` — keep/remove inventory for this folder

Advanced / secondary:

- `examples/export_gallery_mpl.py` — focused Matplotlib export examples
- `figma-plugin/pubfig-sync/` — Figma plugin scaffold for panel import and refresh
- [`docs/palette-gallery.md`](docs/palette-gallery.md) — visual palette gallery for built-in and Plotly-derived palettes

## Development

### Editable Install

```bash
pip install -e .[dev]
```

### Run Tests

```bash
pytest
```

### Lint

```bash
ruff check src tests examples
```

### Regenerate Gallery

```bash
python examples/export_gallery.py
```

## License

MIT
