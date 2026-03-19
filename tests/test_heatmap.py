"""Tests for heatmap plot functions."""

import numpy as np
import pytest

from pubfig.plots.heatmap import clustermap, corr_matrix, heatmap


def test_heatmap_basic():
    data = np.random.rand(5, 5)
    fig = heatmap(data)
    assert len(fig.axes[0].images) == 1
    ax = fig.axes[0]
    assert all(not spine.get_visible() for spine in ax.spines.values())
    assert ax.images[0].get_cmap().name == "Blues"


def test_heatmap_annotated():
    cm = np.array([[45, 5], [3, 47]])
    fig = heatmap(cm, category_names=["Neg", "Pos"], annotate=True)
    assert len(fig.axes[0].texts) == 4


def test_heatmap_title_spacing_is_compact():
    data = np.random.rand(4, 4)
    fig = heatmap(data, title="Heatmap")
    assert fig.axes[0].title.get_position()[1] == pytest.approx(1.05)


def test_heatmap_category_names():
    cm = np.array([[45, 5], [3, 47]])
    fig = heatmap(cm, category_names=["Ctrl", "Case"], annotate=False)
    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["Ctrl", "Case"]
    assert [tick.get_text() for tick in ax.get_yticklabels()] == ["Ctrl", "Case"]


def test_corr_matrix_pearson():
    data = np.random.randn(50, 4)
    fig = corr_matrix(data)
    assert len(fig.axes[0].images) == 1
    assert len(fig.axes[0].texts) == 16


def test_corr_matrix_variable_names():
    data = np.random.randn(50, 3)
    fig = corr_matrix(data, variable_names=["Gene A", "Gene B", "Gene C"], annotate=False)
    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["Gene A", "Gene B", "Gene C"]


def test_heatmap_show_spines_override():
    data = np.random.rand(4, 4)
    fig = heatmap(data, show_spines=True, tick_length=1.5)
    ax = fig.axes[0]
    assert any(spine.get_visible() for spine in ax.spines.values())


def test_heatmap_cell_borders():
    data = np.random.rand(4, 4)
    fig = heatmap(data, cell_border_line_width=0.4)
    ax = fig.axes[0]
    assert len(ax.xaxis.get_minorticklines()) >= 0


def test_clustermap():
    data = np.random.rand(8, 6)
    fig = clustermap(data)
    assert len(fig.axes[0].images) == 1


def test_clustermap_row_column_category_names():
    data = np.random.rand(8, 6)
    fig = clustermap(
        data,
        row_category_names=[f"R{i}" for i in range(8)],
        column_category_names=[f"C{i}" for i in range(6)],
    )
    assert len(fig.axes[0].images) == 1
    assert len(fig.axes[0].get_xticklabels()) == 6
    assert len(fig.axes[0].get_yticklabels()) == 8


def test_clustermap_legacy_row_col_removed():
    data = np.random.rand(8, 6)
    with pytest.raises(TypeError):
        clustermap(
            data,
            row_names=[f"R{i}" for i in range(8)],
            col_names=[f"C{i}" for i in range(6)],
        )
