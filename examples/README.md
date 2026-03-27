# Examples Inventory

This directory is intentionally split into two kinds of files:

## 1. Runnable example entry points

- `gallery.py` — quick visual walkthrough of supported plot families
- `export_gallery.py` — regenerates the featured gallery images used in the root README
- `export_gallery_mpl.py` — focused Matplotlib export examples
- `figma_panels_demo.py` — exports a small deterministic panel set for `pubfig figma push`
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
python examples/figma_panels_demo.py
```

## Notes

- Files under ignored output folders such as `figma_panels_demo_output/` are local generated artifacts, not canonical examples.
- `gallery_contact_sheet.py` is an internal helper used by `export_gallery.py`.
