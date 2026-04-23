from __future__ import annotations

import json

from conftest import write_json


def test_render_cli_writes_single_figure(tmp_path, run_cli) -> None:
    spec_path = write_json(
        tmp_path / "figure.spec.json",
        {
            "schema_version": 1,
            "plot": {
                "kind": "line",
                "kwargs": {
                    "data": [[0.78, 0.87], [1.03, 1.01], [1.15, 1.04], [0.90, 0.95]],
                    "x": [0.0, 0.8, 1.6, 2.4],
                    "series_names": ["Square", "Circle"],
                },
            },
            "export": {
                "mode": "save_figure",
                "path": "outputs/line.png",
                "spec": "nature",
                "width": "single",
                "raster_dpi": 120,
            },
        },
    )

    result = run_cli("render", str(spec_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["mode"] == "save_figure"
    assert payload["plot_kinds"] == ["line"]
    assert len(payload["output_paths"]) == 1
    assert (tmp_path / "outputs" / "line.png").exists()


def test_validate_spec_cli_dry_run_does_not_write_panel_outputs(tmp_path, run_cli) -> None:
    spec_path = write_json(
        tmp_path / "panels.spec.json",
        {
            "schema_version": 1,
            "panels": [
                {
                    "panel_id": "a",
                    "kind": "line",
                    "kwargs": {
                        "data": [[0.8, 0.9], [0.9, 1.0], [1.0, 1.1]],
                        "x": [0, 1, 2],
                    },
                },
                {
                    "panel_id": "b",
                    "kind": "heatmap",
                    "kwargs": {"data": [[0.9, 0.2], [0.3, 0.8]]},
                },
            ],
            "export": {
                "mode": "export_panels",
                "output_dir": "outputs/panels",
                "overwrite": True,
            },
        },
    )

    result = run_cli("validate-spec", str(spec_path))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["mode"] == "export_panels"
    assert payload["panel_count"] == 2
    assert payload["plot_kinds"] == ["line", "heatmap"]
    assert len(payload["would_write_paths"]) == 3
    assert not (tmp_path / "outputs").exists()
