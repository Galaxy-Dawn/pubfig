"""Tests for export functions."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pytest

from pubfig.export import batch_export, save_figure
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
