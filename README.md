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

  <strong>Language</strong>: <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.md">English</a> | <a href="https://github.com/Galaxy-Dawn/pubfig/blob/main/README.zh-CN.md">中文</a>

</div>

> Publication-style figures for papers, from single plots to panel-first Figma assembly.

`pubfig` is a Matplotlib-native plotting library for researchers who want figures that already look close to the final paper figure. It combines common scientific plot families, journal-aware export, and a panel-first Figma workflow for assembling large multi-panel figures without rebuilding artwork by hand.

**Project links**: [PyPI](https://pypi.org/project/pubfig/) · [GitHub](https://github.com/Galaxy-Dawn/pubfig) · [Examples](examples/)

## Highlights

- **Paper-Ready Defaults, Not a Blank Canvas** — Titles, legends, fonts, line widths, and spacing start from a more publication-like baseline.
- **Common Scientific Plot Families in One API** — Statistical plots, distributions, trends, dimensionality reduction, evaluation curves, heatmaps, and flow plots live in one consistent surface.
- **Journal-Aware Export Without Boilerplate** — `save_figure(...)` and `batch_export(...)` handle explicit output suffixes, column widths, DPI, trimming, and export-time relayout directly.
- **Panel-First Workflow for Composite Figures** — Export clean subplot assets, then assemble and refresh full figures in Figma instead of re-drawing panels manually.
- **Matplotlib-Native and Script-Friendly** — Plot functions return standard Matplotlib `Figure` objects, so they drop into existing analysis code easily.

## Recent News

- **2026-04-22**: `pubfig 0.3.0` is now the PyPI release for the current automation path, with the new agent-first JSON CLI (`render`, `validate-spec`, `list-kinds`), CLI/Python export parity checks, and a shorter Quick Start.
- **2026-04-10**: `pubfig 0.2.3` makes `batch_export(...)` follow the same publication-size resize / relayout path as `save_figure(...)`, so multi-format export now keeps export-time layout consistent.
- **2026-03-31**: `pubfig 0.2.2` adds **ECDF, QQ, Bland–Altman, Calibration, and UpSet**, and brings them into the homepage showcase and full gallery.
- **2026-03-30**: `pubfig 0.2.1` refreshed the PyPI release with stronger polar/composition coverage and fuller gallery examples.
- **2026-03-29**: `pubfig 0.2.0` landed on PyPI with `pip install pubfig`, suffix-based export, and the documented panel-first Figma workflow.

<details>
<summary><strong>View older changelog</strong></summary>

- **2026-03-25**: Panel-first Figma loop polish — panel export now defaults to title-free assets for cleaner Figma assembly, `pubfig-sync` now keeps shared title / legend placeholders off by default, and bridge/watch flows now surface bundle provenance plus the exact manual-fallback bundle path.
- **2026-03-20**: Local bridge automation for Figma sync — added a bridge-backed `pubfig figma bridge|sync|watch` workflow, upgraded `pubfig-sync` with bridge connection mode, and enabled CLI-triggered vector import/refresh after one-time plugin connection.
- **2026-03-20**: Figma plugin v2 workflow polish — added `auto` / `hero_top` relayout presets, upgraded shared title / legend placeholders, and improved refresh behavior so manual Figma positioning is preserved more reliably unless relayout is requested.
- **2026-03-20**: CLI + Figma plugin workflow — added `pubfig figma package|validate|inspect`, introduced a single-file Figma bundle JSON format for exported panels, and scaffolded the `figma-plugin/pubfig-sync` plugin for node-level import and refresh.
- **2026-03-20**: Figma-first panel export workflow — added `export_panel(...)` and `export_panels(...)` for stable subplot asset export, introduced a minimal `panel-index.json` sync index, and documented the Codex + Figma MCP refinement path for multi-panel figures.
- **2026-03-20**: README alignment with pubtab style and homepage refresh — reorganized the README into a pubtab-style homepage with centered badges, language switch, highlights, dated recent news, showcase examples, and an embedded gallery hero.
- **2026-03-20**: Default full install and metadata simplification — changed `pip install pubfig` to install the full plotting stack by default, removed user-facing extras from the main install path, and aligned package metadata, GitHub About, and README wording.
- **2026-03-19**: Raincloud plot support and gallery refresh — added `raincloud(...)`, tuned its default styling, integrated it into the gallery, and regenerated the exported figure set.
- **2026-03-19**: PCA biplot and radar default updates — expanded `pca_biplot(...)` with loading panel modes and group ellipses, refreshed radar defaults, unified font handling, and re-exported the gallery.

</details>

## Examples

### Showcase

#### Single-plot examples

<p align="center">
  <a href="examples/bar_scatter.png"><img src="examples/bar_scatter.png" width="32%" alt="Bar scatter example"></a>
  <a href="examples/raincloud.png"><img src="examples/raincloud.png" width="32%" alt="Raincloud example"></a>
  <a href="examples/line.png"><img src="examples/line.png" width="32%" alt="Line example"></a>
</p>
<p align="center">
  <a href="examples/radar.png"><img src="examples/radar.png" width="32%" alt="Radar example"></a>
  <a href="examples/scatter.png"><img src="examples/scatter.png" width="32%" alt="Scatter example"></a>
  <a href="examples/heatmap.png"><img src="examples/heatmap.png" width="32%" alt="Heatmap example"></a>
</p>

#### New plot families

<p align="center">
  <a href="examples/ecdf.png"><img src="examples/ecdf.png" width="32%" alt="ECDF example"></a>
  <a href="examples/qq.png"><img src="examples/qq.png" width="32%" alt="QQ plot example"></a>
  <a href="examples/bland_altman.png"><img src="examples/bland_altman.png" width="32%" alt="Bland-Altman example"></a>
</p>
<p align="center">
  <a href="examples/calibration.png"><img src="examples/calibration.png" width="48%" alt="Calibration example"></a>
  <a href="examples/upset.png"><img src="examples/upset.png" width="48%" alt="UpSet example"></a>
</p>
<p align="center">
  <a href="examples/dumbbell.png"><img src="examples/dumbbell.png" width="48%" alt="Dumbbell example"></a>
  <a href="examples/forest_plot.png"><img src="examples/forest_plot.png" width="48%" alt="Forest plot example"></a>
</p>
<p align="center">
  <a href="examples/hexbin.png"><img src="examples/hexbin.png" width="48%" alt="Hexbin example"></a>
  <a href="examples/volcano.png"><img src="examples/volcano.png" width="48%" alt="Volcano example"></a>
</p>
<p align="center">
  <a href="examples/grouped_scatter.png"><img src="examples/grouped_scatter.png" width="48%" alt="Grouped scatter example"></a>
  <a href="examples/radial_hierarchy.png"><img src="examples/radial_hierarchy.png" width="48%" alt="Radial hierarchy example"></a>
</p>
<p align="center">
  <a href="examples/circular_stacked_bar.png"><img src="examples/circular_stacked_bar.png" width="48%" alt="Circular stacked bar example"></a>
  <a href="examples/circular_grouped_bar.png"><img src="examples/circular_grouped_bar.png" width="48%" alt="Circular grouped bar example"></a>
</p>

#### Composite figure examples assembled in Figma

<p align="center">
  <a href="examples/composite-showcase-benchmark.png"><img src="examples/composite-showcase-benchmark.png" width="96%" alt="Benchmark composite figure assembled in Figma"></a>
</p>
<p align="center">
  <a href="examples/composite-showcase-intervention.png"><img src="examples/composite-showcase-intervention.png" width="96%" alt="Intervention composite figure assembled in Figma"></a>
</p>
<p align="center">
  <a href="examples/composite-showcase-stratification.png"><img src="examples/composite-showcase-stratification.png" width="96%" alt="Stratification composite figure assembled in Figma"></a>
</p>

<details>
<summary><strong>Full Gallery</strong></summary>

The full gallery below also includes the newest diagnostics, evaluation, and set/composition families such as ECDF, QQ, Bland–Altman, Calibration, and UpSet.

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
pf.save_figure(fig, "figure1.pdf")
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

pf.save_figure(fig, "figure1.pdf", spec="nature", width="single")
```

- `category_names`: names on the x-axis
- `series_names`: names in the legend
- `title`: figure title
- `spec` / `width`: journal-style export presets

Only add parameters like `aspect_ratio` or `trim` when you already know why you
need them.

#### Where to look up detailed parameters

If you want to understand a specific plot in more detail, start here:

```python
help(pf.bar_scatter)
help(pf.line)
help(pf.heatmap)
```

You can also inspect runnable examples under [`examples/`](examples/).

#### Saving PNG / SVG / PDF

`save_figure(...)` now expects an explicit filename suffix:

- `pf.save_figure(fig, "figure1.pdf")` → write PDF
- `pf.save_figure(fig, "figure1.svg")` → write SVG
- `pf.save_figure(fig, "figure1.png")` → write PNG
- `pf.save_figure(fig, "figure1.jpg")` → write JPG

If you want multiple outputs, use `batch_export(...)` instead:

```python
pf.batch_export(fig, "figure1", formats=("pdf", "svg", "png", "jpg"))
```

`batch_export(...)` now follows the same publication-size export path as
`save_figure(...)`: it resizes to the requested output size first, reruns
layout/post-layout hooks, and then writes each format.

### CLI Quick Start

The Python API is still the best path for notebooks and interactive analysis.
The CLI is the agent-first path: it gives automation a stable JSON interface for
rendering, validation, and export.

Use these three commands:

```bash
pubfig render figure.spec.json
pubfig validate-spec figure.spec.json
pubfig list-kinds
```

- `render`: read one JSON spec and write the figure or panels
- `validate-spec`: parse the same spec, build the figure, and check it without writing files
- `list-kinds`: print the supported plot kinds for CLI automation

#### Example 1: single figure

Small datasets can be written inline directly in JSON:

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

#### Example 2: panel export

Use `export_panels` mode when you want panel assets for Figma or another figure
assembly workflow:

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

The CLI is a thin wrapper over the same plotting and export functions used by
Python. We have locally checked it against gallery-sourced inputs, and the
current CLI PNG outputs match the direct Python outputs exactly.

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
| `dumbbell` | Connected paired comparison plot | [recipe](#recipe-dumbbell) |
| `forest_plot` | Effect-size plot with confidence intervals | [recipe](#recipe-forest_plot) |

### Composition and Polar Plots

| Function | Description | Recipe |
|----------|-------------|--------|
| `grouped_scatter` | Dense grouped scatter / strip benchmark panel | [recipe](#recipe-grouped_scatter) |
| `donut` | Publication-style donut chart | [recipe](#recipe-donut) |
| `stacked_ratio_barh` | 100 percent horizontal ratio bar chart | [recipe](#recipe-stacked_ratio_barh) |
| `radial_hierarchy` | Two-level radial hierarchy / sunburst-style chart | [recipe](#recipe-radial_hierarchy) |
| `circular_stacked_bar` | Dense circular stacked bar chart with inner group ring | [recipe](#recipe-circular_stacked_bar) |
| `circular_grouped_bar` | Dense circular grouped bar chart with inner group ring | [recipe](#recipe-circular_grouped_bar) |

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
| `hexbin` | Dense-scatter hexbin plot | [recipe](#recipe-hexbin) |
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
| `volcano` | Volcano plot for effect size vs significance | [recipe](#recipe-volcano) |
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
- `examples/export_composite_showcases_panels.py` — exports the panel-first composite showcases that are assembled in Figma
- `examples/figma_workflow_demo.md` — panel-first pubfig → Figma workflow guide
- `examples/generate_palette_gallery.py` — regenerates the palette preview sheets and gallery docs
- `examples/README.md` — keep/remove inventory for this folder
- `help(pubfig.circular_stacked_bar)` / `help(pubfig.circular_grouped_bar)` — inspect the fixed dense polar defaults directly from Python

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
