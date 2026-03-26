# pubfig-sync

A Figma plugin for **panel-bundle import / refresh** in the `pubfig` panel-first workflow.

## Primary workflow

1. Build panels in Python with `pubfig`
2. Export them with `export_panel(...)` or `export_panels(...)`
3. Open this plugin in Figma and click **Connect Bridge**
4. Run `pubfig figma push <panel_dir> --figure-id <id>` from the terminal
5. Use the loaded bundle only when you need manual fallback

```bash
pubfig figma push examples/figma_panels_demo_output --figure-id figure-01
```

`push` is the default daily command. It ensures the local bridge is running,
defaults to the latest connected session, auto-enables `--write-bundle`, and
then performs the sync / refresh.

## Manual fallback

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01
```

Or just load the exact `.pubfig-figma.json` bundle already written by
`pubfig figma push`. The plugin UI exposes manual import / refresh controls so
you can recover quickly if bridge sync fails.

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

## Secondary and advanced commands

Secondary:

```bash
pubfig figma package examples/figma_panels_demo_output --figure-id figure-01
```

Advanced:

```bash
pubfig figma sync examples/figma_panels_demo_output/figure-01.pubfig-figma.json --session latest
pubfig figma watch examples/figma_panels_demo_output --session latest --figure-id figure-01 --write-bundle
pubfig figma bridge status
```

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
