"""Tests for pubfig Figma bundle packaging and CLI."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pytest

from pubfig.cli import _diff_watch_snapshot, main as cli_main
from pubfig.export import export_panels
from pubfig.figma import (
    inspect_figma_bundle,
    materialize_figma_sync_bundle,
    package_figma_bundle,
    resolve_figma_bundle_output_path,
    resolve_figma_sync_source,
    validate_figma_bundle,
)


def _make_simple_fig(title: str):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    ax.set_title(title)
    return fig


def test_package_figma_bundle_from_panel_dir(tmp_path):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a, "b": fig_b}, panel_dir, overwrite=True)

    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-01")
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert payload["bundle_type"] == "pubfig_figma_bundle"
    assert payload["figure_id"] == "figure-01"
    assert payload["workflow"]["path"] == "panel-first"
    assert payload["layout"] == {}
    assert payload["panel_labels"]["offset_x"] == 12.0
    assert payload["panel_labels"]["offset_y"] == 12.0
    assert payload["panel_labels"]["align_x"] == "column"
    assert payload["panel_labels"]["align_y"] == "row"
    assert [panel["panel_id"] for panel in payload["panels"]] == ["a", "b"]
    assert [panel["label"] for panel in payload["panels"]] == ["a", "b"]
    assert payload["panels"][0]["title"] == "A"
    assert "<svg" in payload["panels"][0]["svg"]

    plt.close(fig_a)
    plt.close(fig_b)


def test_package_figma_bundle_preserves_duplicate_group_labels(tmp_path):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    fig_c = _make_simple_fig("C")
    panel_dir = tmp_path / "panels"
    export_panels(
        {"p1": fig_a, "p2": fig_b, "p3": fig_c},
        panel_dir,
        overwrite=True,
        labels=["a", "a", "a"],
    )

    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-grouped-labels")
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert [panel["label"] for panel in payload["panels"]] == ["a", "a", "a"]

    plt.close(fig_a)
    plt.close(fig_b)
    plt.close(fig_c)


def test_validate_and_inspect_figma_bundle(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-a")

    panel_validation = validate_figma_bundle(panel_dir)
    bundle_validation = validate_figma_bundle(bundle_path)
    inspection = inspect_figma_bundle(bundle_path)

    assert panel_validation["kind"] == "panel_dir"
    assert bundle_validation["kind"] == "bundle_file"
    assert bundle_validation["figure_id"] == "figure-a"
    assert inspection["panel_ids"] == ["a"]

    plt.close(fig_a)


def test_resolve_figma_sync_source_accepts_bundle_file(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-a")

    resolved = resolve_figma_sync_source(bundle_path)

    assert resolved["source_kind"] == "bundle_file"
    assert resolved["source_path"] == str(bundle_path.resolve())
    assert resolved["bundle"]["figure_id"] == "figure-a"

    plt.close(fig_a)


def test_resolve_figma_sync_source_rejects_bundle_file_overrides(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-a")

    with pytest.raises(ValueError):
        resolve_figma_sync_source(bundle_path, figure_id="different-figure")

    plt.close(fig_a)


def test_materialize_figma_sync_bundle_writes_exact_bundle_for_panel_dir(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)

    bundle_output = tmp_path / "manual-fallback.pubfig-figma.json"
    resolved = materialize_figma_sync_bundle(
        panel_dir,
        write_bundle=True,
        bundle_output=bundle_output,
        figure_id="bundle-written-figure",
        panel_gap=6,
    )

    assert resolved["source_kind"] == "panel_dir"
    assert resolved["bundle_written"] is True
    assert resolved["bundle_path"] == str(bundle_output.resolve())
    assert bundle_output.exists()

    payload = json.loads(bundle_output.read_text(encoding="utf-8"))
    assert payload["figure_id"] == "bundle-written-figure"
    assert payload["layout"]["panel_gap"] == 6.0
    assert resolved["bundle"] == payload

    plt.close(fig_a)


def test_materialize_figma_sync_bundle_reuses_existing_bundle_file(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_path = package_figma_bundle(panel_dir, figure_id="figure-a")

    resolved = materialize_figma_sync_bundle(bundle_path, write_bundle=True)

    assert resolved["source_kind"] == "bundle_file"
    assert resolved["bundle_written"] is False
    assert resolved["bundle_path"] == str(bundle_path.resolve())
    assert resolved["bundle"]["figure_id"] == "figure-a"

    plt.close(fig_a)


def test_resolve_figma_bundle_output_path_defaults_to_figure_id(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)

    resolved = resolve_figma_bundle_output_path(panel_dir, figure_id="figure-a")

    assert resolved == panel_dir / "figure-a.pubfig-figma.json"

    plt.close(fig_a)


def test_diff_watch_snapshot_reports_added_modified_and_removed_paths():
    previous = {
        "/tmp/a.svg": 1.0,
        "/tmp/b.svg": 2.0,
    }
    current = {
        "/tmp/b.svg": 3.0,
        "/tmp/c.svg": 4.0,
    }

    diff = _diff_watch_snapshot(previous, current)

    assert diff["added_paths"] == ["/tmp/c.svg"]
    assert diff["removed_paths"] == ["/tmp/a.svg"]
    assert diff["modified_paths"] == ["/tmp/b.svg"]
    assert diff["changed_paths"] == ["/tmp/c.svg", "/tmp/b.svg", "/tmp/a.svg"]


def test_package_figma_bundle_with_placeholders_and_custom_preset(tmp_path):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    fig_c = _make_simple_fig("C")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a, "b": fig_b, "c": fig_c}, panel_dir, overwrite=True)

    bundle_path = package_figma_bundle(
        panel_dir,
        figure_id="figure-placeholders",
        title="Shared Figure",
        preset="hero_top",
        columns=3,
        panel_gap=8,
        shared_title=True,
        shared_legend=True,
        legend_position="bottom",
        preserve_positions_on_refresh=False,
        label_offset_x=9,
        label_offset_y=7,
        label_align_x="panel",
        label_align_y="panel",
    )
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert payload["layout"]["preset"] == "hero_top"
    assert payload["layout"]["columns"] == 3
    assert payload["layout"]["panel_gap"] == 8.0
    assert payload["layout"]["preserve_positions_on_refresh"] is False
    assert payload["panel_labels"]["offset_x"] == 9.0
    assert payload["panel_labels"]["offset_y"] == 7.0
    assert payload["panel_labels"]["align_x"] == "panel"
    assert payload["panel_labels"]["align_y"] == "panel"
    assert payload["placeholders"]["shared_title"]["enabled"] is True
    assert payload["placeholders"]["shared_title"]["text"] == "Shared Figure"
    assert payload["placeholders"]["shared_legend"]["enabled"] is True
    assert payload["placeholders"]["shared_legend"]["position"] == "bottom"

    plt.close(fig_a)
    plt.close(fig_b)
    plt.close(fig_c)


def test_package_figma_bundle_accepts_row_panel_counts(tmp_path):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    fig_c = _make_simple_fig("C")
    fig_d = _make_simple_fig("D")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a, "b": fig_b, "c": fig_c, "d": fig_d}, panel_dir, overwrite=True)

    bundle_path = package_figma_bundle(
        panel_dir,
        figure_id="figure-row-counts",
        row_panel_counts=(3, 1),
    )
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert payload["layout"]["row_panel_counts"] == [3, 1]
    assert "columns" not in payload["layout"]

    plt.close(fig_a)
    plt.close(fig_b)
    plt.close(fig_c)
    plt.close(fig_d)


def test_cli_figma_package_validate_and_inspect(tmp_path, capsys):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a, "b": fig_b}, panel_dir, overwrite=True)

    output_path = tmp_path / "bundle.json"
    exit_code = cli_main(
        [
            "figma",
            "package",
            str(panel_dir),
            "--figure-id",
            "cli-figure",
            "--preset",
            "hero_left",
            "--columns",
            "3",
            "--panel-gap",
            "0",
            "--shared-title",
            "--shared-legend",
            "--legend-position",
            "bottom",
            "--no-preserve-positions-on-refresh",
            "--label-offset-x",
            "10",
            "--label-offset-y",
            "8",
            "--label-align-x",
            "panel",
            "--label-align-y",
            "panel",
            "-o",
            str(output_path),
        ]
    )
    assert exit_code == 0
    package_payload = json.loads(capsys.readouterr().out)
    assert package_payload["ok"] is True
    assert package_payload["bundle_path"] == str(output_path.resolve())

    packaged_bundle = json.loads(output_path.read_text(encoding="utf-8"))
    assert packaged_bundle["layout"]["preset"] == "hero_left"
    assert packaged_bundle["layout"]["columns"] == 3
    assert packaged_bundle["layout"]["panel_gap"] == 0.0
    assert packaged_bundle["layout"]["preserve_positions_on_refresh"] is False
    assert packaged_bundle["panel_labels"]["offset_x"] == 10.0
    assert packaged_bundle["panel_labels"]["offset_y"] == 8.0
    assert packaged_bundle["panel_labels"]["align_x"] == "panel"
    assert packaged_bundle["panel_labels"]["align_y"] == "panel"
    assert packaged_bundle["placeholders"]["shared_title"]["enabled"] is True
    assert packaged_bundle["placeholders"]["shared_legend"]["position"] == "bottom"

    exit_code = cli_main(["figma", "validate", str(output_path)])
    assert exit_code == 0
    validate_payload = json.loads(capsys.readouterr().out)
    assert validate_payload["kind"] == "bundle_file"
    assert validate_payload["figure_id"] == "cli-figure"

    exit_code = cli_main(["figma", "inspect", str(output_path)])
    assert exit_code == 0
    inspect_payload = json.loads(capsys.readouterr().out)
    assert inspect_payload["panel_count"] == 2
    assert inspect_payload["figure_id"] == "cli-figure"

    plt.close(fig_a)
    plt.close(fig_b)


def test_cli_figma_package_accepts_row_panel_counts(tmp_path, capsys):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    fig_c = _make_simple_fig("C")
    fig_d = _make_simple_fig("D")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a, "b": fig_b, "c": fig_c, "d": fig_d}, panel_dir, overwrite=True)

    output_path = tmp_path / "bundle-row-counts.json"
    exit_code = cli_main(
        [
            "figma",
            "package",
            str(panel_dir),
            "--figure-id",
            "cli-row-counts",
            "--row-panel-counts",
            "3,1",
            "-o",
            str(output_path),
        ]
    )
    assert exit_code == 0
    package_payload = json.loads(capsys.readouterr().out)
    assert package_payload["ok"] is True

    packaged_bundle = json.loads(output_path.read_text(encoding="utf-8"))
    assert packaged_bundle["layout"]["row_panel_counts"] == [3, 1]
    assert "columns" not in packaged_bundle["layout"]

    plt.close(fig_a)
    plt.close(fig_b)
    plt.close(fig_c)
    plt.close(fig_d)


def test_build_figma_bundle_payload_uses_plugin_defaults_when_layout_overrides_omitted(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)

    bundle_path = package_figma_bundle(panel_dir, figure_id="defaults-figure")
    payload = json.loads(bundle_path.read_text(encoding="utf-8"))

    assert payload["layout"] == {}

    plt.close(fig_a)


def test_package_figma_bundle_rejects_columns_with_row_panel_counts(tmp_path):
    fig_a = _make_simple_fig("A")
    fig_b = _make_simple_fig("B")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a, "b": fig_b}, panel_dir, overwrite=True)

    try:
        package_figma_bundle(panel_dir, figure_id="bad-layout", columns=2, row_panel_counts=(1, 1))
    except ValueError as error:
        assert "columns cannot be combined with row_panel_counts" in str(error)
    else:
        raise AssertionError("Expected ValueError when columns and row_panel_counts are both provided")

    plt.close(fig_a)
    plt.close(fig_b)
