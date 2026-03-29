# Examples Inventory

This directory is intentionally split into two kinds of files:

## 1. Runnable example entry points

- `gallery.py` — quick visual walkthrough of supported plot families
- `export_gallery.py` — regenerates the featured gallery images used in the root README
- `export_gallery_mpl.py` — focused Matplotlib export examples
- `export_composite_showcases_panels.py` — exports the panel-first composite showcases that are pushed into Figma and shown in the root README
- `figma_workflow_demo.md` — panel-first pubfig → Figma walkthrough
- `generate_palette_gallery.py` — regenerates the palette preview sheets and palette docs

## 2. Rendered assets tracked for documentation

These files are generated outputs, but they are kept in Git because the root README
and palette docs link to them directly.

### Gallery assets

- `bar_scatter.png`
- `raincloud.png`
- `line.png`
- `radar.png`
- `gallery-hero.png`

### Composite figure assets

These are the latest Figma-assembled screenshots tracked for the root README.

- `composite-showcase-benchmark.png`
- `composite-showcase-intervention.png`
- `composite-showcase-stratification.png`

### Palette assets

- `palettes/featured-palettes.png`
- `palettes/builtin-palettes.png`
- `palettes/plotly-carto-palettes.png`
- `palettes/plotly-cmocean-palettes.png`
- `palettes/plotly-colorbrewer-palettes.png`

## Regeneration commands

```bash
python examples/export_gallery.py
python examples/generate_palette_gallery.py
python examples/export_composite_showcases_panels.py
```

## Notes

- Cached folders such as `__pycache__/` are local artifacts and are not part of the canonical examples set.
- `gallery_contact_sheet.py` is an internal helper used by `export_gallery.py`.
