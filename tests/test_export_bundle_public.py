from __future__ import annotations

import json

import numpy as np

import pubfig as pf
from pubfig.figma import package_figma_bundle, validate_figma_bundle


def test_export_panels_writes_svg_assets_and_panel_index(tmp_path) -> None:
    rng = np.random.default_rng(0)
    bar_data = np.clip(
        rng.normal(
            loc=np.array([[0.8, 0.95], [0.9, 1.05]], dtype=float)[..., None],
            scale=0.04,
            size=(2, 2, 10),
        ),
        0.0,
        None,
    )
    line_data = np.array([[0.78, 0.88], [0.92, 0.97], [1.05, 1.02], [1.12, 1.08]], dtype=float)

    panels = {
        "a": pf.bar_scatter(bar_data, category_names=["A", "B"], series_names=["Ctrl", "Tx"]),
        "b": pf.line(line_data, x=[0, 1, 2, 3], series_names=["Square", "Circle"]),
    }

    records = pf.export_panels(panels, tmp_path / "panels", overwrite=True)

    assert len(records) == 2
    assert (tmp_path / "panels" / "a.svg").exists()
    assert (tmp_path / "panels" / "b.svg").exists()
    index_path = tmp_path / "panels" / "panel-index.json"
    assert index_path.exists()
    index_payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert [record["panel_id"] for record in index_payload["records"]] == ["a", "b"]


def test_package_and_validate_figma_bundle_on_trusted_panel_dir(tmp_path) -> None:
    panels = {
        "a": pf.line(np.array([[0.75], [0.88], [1.02], [1.10]], dtype=float), x=[0, 1, 2, 3]),
    }
    panel_dir = tmp_path / "panels"
    pf.export_panels(panels, panel_dir, overwrite=True)

    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-01")
    panel_validation = validate_figma_bundle(panel_dir)
    bundle_validation = validate_figma_bundle(bundle_path)

    assert bundle_path.exists()
    assert panel_validation["valid"] is True
    assert panel_validation["record_count"] == 1
    assert bundle_validation["valid"] is True
    assert bundle_validation["figure_id"] == "figure-01"
