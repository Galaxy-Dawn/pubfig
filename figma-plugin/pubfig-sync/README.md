# pubfig-sync

A Figma plugin for **panel-bundle import / refresh** in the `pubfig` panel-first workflow.

## Recommended workflow

1. Build panels in Python with `pubfig`
2. Export them with `export_panel(...)` or `export_panels(...)`
3. Package the panel directory with `pubfig figma package`
4. Import or refresh it in Figma with this plugin
5. Use plugin relayout presets only for panel placement refinement in Figma

## CLI pairing

Agent-first default:

```bash
pubfig figma push examples/figma_panels_demo_output --figure-id figure-01
```

`push` ensures the local bridge is running, defaults to the latest connected
session, auto-enables `--write-bundle`, and then performs the sync / refresh.

Create a bundle from an exported panel directory:

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01
```

Sync that bundle through the local bridge:

```bash
pubfig figma sync examples/figma_panels_demo_output/figure-01.pubfig-figma.json
```

`sync` and `watch` also still accept the original panel directory when you want
to rebuild the bundle in memory on every refresh:

```bash
pubfig figma sync examples/figma_panels_demo_output --figure-id figure-01 --write-bundle
pubfig figma watch examples/figma_panels_demo_output --session latest --figure-id figure-01 --write-bundle
```

With `--write-bundle`, the CLI writes the exact bridge payload to disk first, so
the same bundle can be imported manually in the plugin if bridge sync fails.

The plugin UI now surfaces a bundle summary card for manual fallback, so after
you choose the written `.pubfig-figma.json` you can see the figure id, panel
count, source panel directory, layout settings, and then trigger manual import /
refresh directly.

When a refresh arrives through the bridge, the same summary card now shows the
bridge job `bundle_provenance` too, including the originating bundle path when
available.

## Bridge automation mode

1. Open the plugin in Figma, set the bridge URL to `http://localhost:47329`, and click **Connect Bridge**
2. Optionally enable **Auto-connect bridge when plugin opens**
3. Trigger future refreshes from the terminal with `pubfig figma push ...`

## Supported relayout presets

Panel bundles support relayout presets such as:

- `auto`
- `grid`
- `row`
- `column`
- `two_by_two`
- `hero_left`
- `hero_top`

You can also override layout more explicitly with:

- `--panel-gap <n>`
- `--row-panel-counts 2,2`

The plugin UI exposes the same controls for manual import / refresh.

Panel labels can also be tuned directly in the bundle or plugin UI:

- `--label-offset-x <n>`
- `--label-offset-y <n>`
- `--label-align-x column|panel`
- `--label-align-y row|panel`
