# pubfig → Figma Workflow Demo

This repo uses a **panel-first workflow** for Figma finishing.

## Recommended path

1. build each panel in Python with `pubfig`
2. export them with `export_panel(...)` or `export_panels(...)`
3. package the panel directory with `pubfig figma package`
4. import / refresh those assets through `pubfig-sync`
5. finish multi-panel alignment, labels, arrows, and annotations in Figma

## Step 1 — Export panels

Run:

```bash
python examples/figma_panels_demo.py
```

This creates a directory containing:

- SVG panel assets
- `panel-index.json`

## Step 2 — Package for the plugin

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01
```

For a tighter 2×2 arrangement or other explicit row layouts:

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01 --panel-gap 6 --row-panel-counts 2,2
```

For panel label tuning:

```bash
pubfig figma package examples/figma_panels_demo_output \
  --figure-id figure-01 \
  --panel-gap 6 \
  --row-panel-counts 2,2 \
  --label-offset-x 12 \
  --label-offset-y 10 \
  --label-align-x column \
  --label-align-y row
```

## Step 3 — Import into Figma

In Figma:

1. load the plugin from `figma-plugin/pubfig-sync/manifest.json`
2. choose the generated `.pubfig-figma.json`
3. click **Import New Figure**

## Step 4 — Refresh from the terminal

```bash
pubfig figma sync examples/figma_panels_demo_output --session latest --figure-id figure-01 --write-bundle
pubfig figma sync examples/figma_panels_demo_output/figure-01.pubfig-figma.json --session latest
```

The first form keeps the panel directory as the source of truth but also writes
the exact `.pubfig-figma.json` payload used by the bridge, so manual import in
Figma stays available as an immediate fallback.

In the plugin, loading that bundle now shows a manual-fallback summary card
before import, making it easier to confirm figure id, panel count, source dir,
and layout settings before you click import / refresh.

If you prefer to keep the panel directory as the source, that still works:

```bash
pubfig figma sync examples/figma_panels_demo_output --session latest --panel-gap 6 --row-panel-counts 2,2
```

## Optional — Use bridge automation

```bash
pubfig figma bridge start
pubfig figma bridge status
```
