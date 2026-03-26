# pubfig → Figma Workflow Demo

This repo uses a **panel-first workflow** for Figma finishing, with
`pubfig figma push` as the default terminal entry point.

## Recommended path

1. build each panel in Python with `pubfig`
2. export them with `export_panel(...)` or `export_panels(...)`
3. open `pubfig-sync` in Figma Desktop and click **Connect Bridge**
4. run `pubfig figma push <panel_dir> --figure-id <id>`
5. use manual bundle import only as fallback
6. finish multi-panel alignment, labels, arrows, and annotations in Figma

## Step 1 — Export panels

Run:

```bash
python examples/figma_panels_demo.py
```

This creates a directory containing:

- SVG panel assets
- `panel-index.json`

## Step 2 — Push from the terminal

```bash
pubfig figma push examples/figma_panels_demo_output --figure-id figure-01
```

For a tighter 2×2 arrangement or other explicit row layouts:

```bash
pubfig figma push examples/figma_panels_demo_output --figure-id figure-01 --panel-gap 6 --row-panel-counts 2,2
```

For panel label tuning:

```bash
pubfig figma push examples/figma_panels_demo_output \
  --figure-id figure-01 \
  --panel-gap 6 \
  --row-panel-counts 2,2 \
  --label-offset-x 12 \
  --label-offset-y 10 \
  --label-align-x column \
  --label-align-y row
```

`push` auto-starts the local bridge when needed, targets the latest connected
plugin session, and writes the exact `.pubfig-figma.json` bundle for fallback.

## Step 3 — Connect the plugin once

In Figma:

1. load the plugin from `figma-plugin/pubfig-sync/manifest.json`
2. click **Connect Bridge**
3. keep the plugin open while future terminal `push` commands refresh the figure

## Step 4 — Manual fallback when bridge sync stalls

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01
```

Then in the plugin:

1. choose the generated `.pubfig-figma.json`
2. use **Import as New**, **Manual Refresh**, or **Refresh + Relayout**

When `push` succeeds, it already writes the same `.pubfig-figma.json` payload
for you, so the manual path normally starts from that written bundle.

## Optional — Secondary and advanced commands

Secondary:

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01
```

Advanced:

```bash
pubfig figma sync examples/figma_panels_demo_output/figure-01.pubfig-figma.json --session latest
pubfig figma watch examples/figma_panels_demo_output/figure-01.pubfig-figma.json --session latest
pubfig figma bridge status
```
