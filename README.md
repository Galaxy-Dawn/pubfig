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

- **Paper-Oriented Defaults** — Compact titles, cleaner legends, explicit font handling, and lighter publication-style line weights.
- **One Library for Common Figure Types** — Statistical plots, distribution plots, dimensionality-reduction plots, evaluation curves, heatmaps, and flow plots in one API surface.
- **Journal-Aware Export** — `save_figure(...)` supports `single`/`double` column widths, vector formats, raster DPI, and trimming for submission workflows.
- **Matplotlib-Native Workflow** — Plot functions return Matplotlib `Figure` objects, so existing analysis scripts remain easy to integrate.
- **Explicit Layout Controls** — Fine-grained control over tick direction, box/grid visibility, palettes, legends, and plot-specific layout options.

## Recent News

- **2026-03-20**: Local bridge automation for Figma sync — added a bridge-backed `pubfig figma bridge|sync|watch` workflow, upgraded `pubfig-sync` with bridge connection mode, and enabled CLI-triggered vector import/refresh after one-time plugin connection.
- **2026-03-20**: Figma plugin v2 workflow polish — added `auto` / `hero_top` relayout presets, upgraded shared title / legend placeholders, and improved refresh behavior so manual Figma positioning is preserved more reliably unless relayout is requested.
- **2026-03-20**: CLI + Figma plugin workflow — added `pubfig figma package|validate|inspect`, introduced a single-file Figma bundle JSON format for exported panels, and scaffolded the `figma-plugin/pubfig-sync` plugin for node-level import and refresh.
- **2026-03-20**: Figma-first panel export workflow — added `export_panel(...)` and `export_panels(...)` for stable subplot asset export, introduced a minimal `panel-index.json` sync index, and documented the Codex + Figma MCP refinement path for multi-panel figures.
- **2026-03-20**: README alignment with pubtab style and homepage refresh — reorganized the README into a pubtab-style homepage with centered badges, language switch, highlights, dated recent news, showcase examples, and an embedded gallery hero.
- **2026-03-20**: Default full install and metadata simplification — changed `pip install pubfig` to install the full plotting stack by default, removed user-facing extras from the main install path, and aligned package metadata, GitHub About, and README wording.
- **2026-03-19**: Raincloud plot support and gallery refresh — added `raincloud(...)`, tuned its default styling, integrated it into the gallery, and regenerated the exported figure set.
- **2026-03-19**: PCA biplot and radar default updates — expanded `pca_biplot(...)` with loading panel modes and group ellipses, refreshed radar defaults, unified font handling, and re-exported the gallery.

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

### Figma Workflow

For multi-panel figures, `pubfig` now keeps the responsibility boundary simple:

1. export each panel from Python with `export_panel(...)` or `export_panels(...)`
2. package the exported panel directory with `pubfig figma package`
3. import or refresh those panel assets in Figma with `pubfig-sync`
4. finish alignment, annotations, arrows, and final figure assembly in Figma

```python
import numpy as np
import pubfig as pf

rng = np.random.default_rng(0)

panels = {
    "a": pf.bar(rng.uniform(0.4, 0.9, size=3), category_names=["A", "B", "C"], title="Panel A"),
    "b": pf.scatter(rng.normal(size=40), rng.normal(size=40), title="Panel B"),
}

pf.export_panels(panels, "panels", overwrite=True)
```

Then package / validate / inspect from the CLI:

```bash
pubfig figma package panels --figure-id figure-01
pubfig figma validate panels
pubfig figma inspect figure-01.pubfig-figma.json
```

`sync` / `watch` now accept **either** the panel directory **or** the packaged
`.pubfig-figma.json` bundle. That means the packaged artifact can be reused as the
single source of truth for bridge-driven refreshes:

```bash
pubfig figma sync figure-01.pubfig-figma.json --session latest
pubfig figma watch figure-01.pubfig-figma.json --session latest
```

The supported Figma-facing entry points are now:

- `export_panel(...)`
- `export_panels(...)`
- `pubfig figma package`
- `pubfig figma sync`
- `pubfig figma watch`
- `pubfig figma bridge start|status`

Plugin scaffold:

- `figma-plugin/pubfig-sync/manifest.json`
- `figma-plugin/pubfig-sync/code.js`
- `figma-plugin/pubfig-sync/ui.html`
- `figma-plugin/pubfig-sync/README.md`

If you use Codex locally, the companion skill `pubfig-figma-workflow` can still orchestrate the panel export → Figma import → MCP review loop.

### Figma Bridge Automation

For a more reliable **once-connected, terminal-driven** workflow:

1. Start the local bridge:

```bash
pubfig figma bridge start
```

2. In Figma, open `pubfig-sync`, set the bridge URL to `http://localhost:47329`, and click **Connect Bridge**
3. Trigger future panel refreshes from the terminal:

```bash
pubfig figma sync panels --session latest --figure-id figure-01 --write-bundle
pubfig figma sync panels/figure-01.pubfig-figma.json --session latest
pubfig figma bridge status
```

`--write-bundle` writes the exact bridge payload to disk first. If the bridge or
plugin refresh path breaks, you can immediately import that same
`.pubfig-figma.json` file manually in Figma as a fallback.

`pubfig figma watch` now also reports richer per-refresh events, including the
changed source files, resolved source kind, and the manual fallback
`bundle_path`.

Bridge jobs now also carry `bundle_provenance`, so the plugin can show which
bundle file or source path a pushed refresh came from.

## Plot Families

### Categorical and Statistical Plots

| Function | Description |
|----------|-------------|
| `bar` | Simple bar chart and grouped bar chart |
| `bar_scatter` | Grouped bar chart with raw points and significance annotations |
| `stacked_bar` | Horizontal stacked bar chart |
| `paired` | Paired dot plot |

### Distribution Plots

| Function | Description |
|----------|-------------|
| `box` | Box plot |
| `violin` | Violin plot |
| `strip` | Strip plot |
| `raincloud` | Half-violin + box + raw-point raincloud plot |
| `density` | Density plot with KDE |
| `histogram` | Histogram with optional KDE |
| `ridgeline` | Ridgeline plot |

### Trend and Relationship Plots

| Function | Description |
|----------|-------------|
| `line` | Line chart with optional CI |
| `area` | Stacked area chart |
| `scatter` | Scatter plot with optional grouped workflow |
| `bubble` | Bubble chart |
| `contour2d` | 2D contour plot with marginals |
| `radar` | Radar chart |

### Matrix, Embedding, and Multivariate Plots

| Function | Description |
|----------|-------------|
| `heatmap` | Heatmap |
| `corr_matrix` | Correlation heatmap |
| `clustermap` | Clustered heatmap |
| `dimreduce` | Dimensionality-reduction scatter plot |
| `pca_biplot` | PCA biplot with optional loadings and group ellipses |
| `parallel_coordinates` | Parallel coordinates plot |

### Evaluation and Flow Plots

| Function | Description |
|----------|-------------|
| `roc` | ROC curve with AUC |
| `pr_curve` | Precision-Recall curve with AP |
| `sankey` | Sankey diagram |

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

Example entry points:

- `examples/gallery.py` — quick visual walkthrough of supported plots
- `examples/export_gallery.py` — exports the gallery to `output_figures/`
- `examples/export_gallery_mpl.py` — focused Matplotlib export examples
- `examples/figma_panels_demo.py` — exports multiple pubfig panels plus a `panel-index.json` sync file
- `examples/figma_workflow_demo.md` — panel-first pubfig → Figma workflow guide
- `figma-plugin/pubfig-sync/` — Figma plugin scaffold for panel import and refresh
- `examples/generate_palette_gallery.py` — regenerates the palette preview sheets and gallery docs
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
