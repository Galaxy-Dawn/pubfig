"""Tests for export functions."""

from __future__ import annotations

import json

import matplotlib.pyplot as plt
import pytest

from pubfig.export import batch_export, export_panel, export_panels, save_figure
from pubfig.specs import NATURE_FIGURE_SPEC, mm_to_inches


def _make_simple_fig():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    return fig


def test_save_figure_png_size_and_restore(tmp_path):
    fig = _make_simple_fig()
    orig_size = fig.get_size_inches().copy()

    base = tmp_path / "test"
    paths = save_figure(
        fig,
        base,
        spec="nature",
        width="single",
        aspect_ratio=0.5,
        raster_dpi=200,
        vector_formats=(),
        raster_formats=("png",),
    )

    out_png = tmp_path / "test.png"
    assert out_png in paths
    assert out_png.exists()
    assert out_png.stat().st_size > 0
    assert fig.get_size_inches()[0] == orig_size[0]
    assert fig.get_size_inches()[1] == orig_size[1]
    plt.close(fig)


def test_save_figure_svg_keeps_text_as_text(tmp_path):
    fig = _make_simple_fig()
    ax = fig.axes[0]
    ax.set_title("Title")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    base = tmp_path / "fig_svg"
    paths = save_figure(
        fig,
        base,
        spec="nature",
        width="single",
        aspect_ratio=0.5,
        vector_formats=("svg",),
        raster_formats=(),
    )

    out_svg = tmp_path / "fig_svg.svg"
    assert out_svg in paths
    svg = out_svg.read_text(encoding="utf-8")
    assert "<text" in svg
    plt.close(fig)


def test_save_figure_svg_can_outline_text_for_figma(tmp_path):
    fig = _make_simple_fig()
    ax = fig.axes[0]
    ax.set_title("Title")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    base = tmp_path / "fig_svg_path"
    paths = save_figure(
        fig,
        base,
        spec="nature",
        width="single",
        aspect_ratio=0.5,
        vector_formats=("svg",),
        raster_formats=(),
        svg_fonttype="path",
    )

    out_svg = tmp_path / "fig_svg_path.svg"
    assert out_svg in paths
    svg = out_svg.read_text(encoding="utf-8")
    assert "<text" not in svg
    plt.close(fig)


def test_save_figure_png_transparent(tmp_path):
    fig = _make_simple_fig()
    base = tmp_path / "fig_transparent"

    save_figure(
        fig,
        base,
        spec="nature",
        width="single",
        aspect_ratio=0.5,
        raster_dpi=200,
        vector_formats=(),
        raster_formats=("png",),
        transparent=True,
    )

    out_png = tmp_path / "fig_transparent.png"
    assert out_png.exists()
    plt.close(fig)


def test_batch_export_preserves_explicit_suffix_api(tmp_path):
    fig = _make_simple_fig()

    paths = batch_export(fig, tmp_path / "batch_fig", formats=("png",), dpi=180)

    out_png = tmp_path / "batch_fig.png"
    assert paths == [out_png]
    assert out_png.exists()
    plt.close(fig)


def test_save_figure_tiff_requires_pillow(tmp_path, monkeypatch):
    fig = _make_simple_fig()
    base = tmp_path / "fig_tiff"

    import pubfig.export.io as export_io

    real_require = export_io._require

    def _fake_require(name: str, extra: str) -> None:
        if name == "PIL":
            raise ImportError(
                "PIL is required for this feature. "
                "Reinstall pubfig or install the missing dependency directly: pip install pillow"
            )
        real_require(name, extra)

    monkeypatch.setattr(export_io, "_require", _fake_require, raising=True)

    with pytest.raises(ImportError) as exc:
        save_figure(
            fig,
            base,
            spec="nature",
            width="single",
            aspect_ratio=0.5,
            raster_dpi=300,
            vector_formats=(),
            raster_formats=("tiff",),
        )
    assert "pip install pillow" in str(exc.value)
    plt.close(fig)


def test_save_figure_resolves_expected_publication_dimensions():
    expected_w = mm_to_inches(NATURE_FIGURE_SPEC.single_column_mm)
    expected_h = mm_to_inches(NATURE_FIGURE_SPEC.single_column_mm * 0.5)
    assert expected_w > 0
    assert expected_h > 0


def test_export_panel_writes_svg_and_metadata(tmp_path):
    fig = _make_simple_fig()
    fig.axes[0].set_title("Panel A")

    record = export_panel(fig, "panel_a", tmp_path)

    out_svg = tmp_path / "panel_a.svg"
    svg_text = out_svg.read_text(encoding="utf-8")
    assert out_svg.exists()
    assert record.panel_id == "panel_a"
    assert record.path == str(out_svg.resolve())
    assert record.format == "svg"
    assert record.figma_node_name == "panel/panel_a"
    assert record.title == "Panel A"
    assert "Panel A" not in svg_text
    plt.close(fig)


def test_export_panel_can_keep_title_when_requested(tmp_path):
    fig = _make_simple_fig()
    fig.axes[0].set_title("Panel A")

    record = export_panel(fig, "panel_a_with_title", tmp_path, include_title=True)

    out_svg = tmp_path / "panel_a_with_title.svg"
    svg_text = out_svg.read_text(encoding="utf-8")
    assert out_svg.exists()
    assert record.title == "Panel A"
    assert "Panel A" in svg_text
    plt.close(fig)


def test_export_panel_rejects_existing_file_without_overwrite(tmp_path):
    fig = _make_simple_fig()
    export_panel(fig, "panel_a", tmp_path)

    with pytest.raises(FileExistsError):
        export_panel(fig, "panel_a", tmp_path)
    plt.close(fig)


def test_export_panel_allows_publication_sizing(tmp_path):
    fig = _make_simple_fig()

    record = export_panel(fig, "panel_pub", tmp_path, spec="nature", width="single")

    assert (tmp_path / "panel_pub.svg").exists()
    assert record.panel_id == "panel_pub"
    plt.close(fig)


def test_export_panel_can_outline_svg_text(tmp_path):
    fig = _make_simple_fig()
    fig.axes[0].set_xlabel("Axis")

    record = export_panel(fig, "panel_path", tmp_path, spec="nature", width="single", svg_fonttype="path")

    svg = (tmp_path / "panel_path.svg").read_text(encoding="utf-8")
    assert record.panel_id == "panel_path"
    assert "<text" not in svg
    plt.close(fig)


def test_export_panels_writes_index_file(tmp_path):
    fig_a = _make_simple_fig()
    fig_b = _make_simple_fig()

    records = export_panels(
        {
            "a": fig_a,
            "b": fig_b,
        },
        tmp_path,
        index_file=True,
    )

    index_path = tmp_path / "panel-index.json"
    payload = json.loads(index_path.read_text(encoding="utf-8"))
    assert [record.panel_id for record in records] == ["a", "b"]
    assert payload["schema_version"] == 1
    assert [item["panel_id"] for item in payload["records"]] == ["a", "b"]
    assert payload["records"][0]["figma_node_name"] == "panel/a"
    assert payload["records"][0]["title"] in ("", None)
    plt.close(fig_a)
    plt.close(fig_b)


def test_export_panels_rejects_duplicate_ids(tmp_path):
    fig_a = _make_simple_fig()
    fig_b = _make_simple_fig()

    with pytest.raises(ValueError, match="Duplicate panel_id"):
        export_panels([("dup", fig_a), ("dup", fig_b)], tmp_path)
    plt.close(fig_a)
    plt.close(fig_b)
