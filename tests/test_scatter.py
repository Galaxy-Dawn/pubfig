"""Tests for scatter plot functions."""

import numpy as np
import pytest

from pubfig.plots.scatter import bubble, contour2d, paired, scatter


def test_scatter_basic():
    x = np.random.randn(50)
    y = np.random.randn(50)
    fig = scatter(x, y)
    assert len(fig.axes[0].collections) >= 1


def test_scatter_with_labels():
    x = np.random.randn(20)
    y = np.random.randn(20)
    labels = np.array([0] * 10 + [1] * 10)
    fig = scatter(x, y, labels=labels)
    assert len(fig.axes[0].collections) == 2


def test_scatter_reference_and_regression_linewidth_overrides():
    pytest.importorskip("statsmodels")
    x = np.linspace(0.0, 1.0, 20)
    y = x + 0.1
    fig = scatter(
        x,
        y,
        show_y_equal_x=True,
        y_equal_x_line_width=0.7,
        show_regression=True,
        regression_line_width=0.9,
    )
    ax = fig.axes[0]
    assert len(ax.lines) == 2
    assert ax.lines[0].get_linewidth() == 0.7
    assert ax.lines[1].get_linewidth() == 0.9


def test_contour2d():
    x = np.random.randn(100)
    y = np.random.randn(100)
    fig = contour2d(x, y)
    assert len(fig.axes) == 3


def test_contour2d_uses_figure_level_title():
    x = np.random.randn(100)
    y = np.random.randn(100)
    fig = contour2d(x, y, title="Contour 2D")
    assert fig._suptitle is not None
    assert fig._suptitle.get_text() == "Contour 2D"
    assert fig.axes[2].get_title() == ""


def test_paired():
    before = np.array([1.0, 2.0, 3.0])
    after = np.array([1.5, 2.5, 3.5])
    fig = paired(before, after)
    assert len(fig.axes[0].lines) == 3
    assert len(fig.axes[0].collections) == 3


def test_bubble_basic():
    x = np.random.randn(20)
    y = np.random.randn(20)
    size = np.abs(np.random.randn(20)) * 10 + 1
    fig = bubble(x, y, size)
    assert len(fig.axes[0].collections) == 1


def test_bubble_limits_include_marker_padding():
    x = np.array([0.0, 1.0])
    y = np.array([0.0, 1.0])
    size = np.array([1.0, 400.0])
    fig = bubble(x, y, size, max_marker_size=40)
    ax = fig.axes[0]
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    assert xmin < 0.0 and xmax > 1.0
    assert ymin < 0.0 and ymax > 1.0


def test_bubble_with_labels():
    x = np.random.randn(20)
    y = np.random.randn(20)
    size = np.abs(np.random.randn(20)) * 10 + 1
    labels = np.array([0] * 10 + [1] * 10)
    fig = bubble(x, y, size, labels=labels)
    assert len(fig.axes[0].collections) == 2


def test_scatter_axis_controls_apply() -> None:
    x = np.random.randn(30)
    y = np.random.randn(30)
    fig = scatter(x, y, tick_direction="inout", show_full_box=True, show_x_grid=True, show_y_grid=False)
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.xaxis.majorTicks[0]._tickdir == "inout"
    assert ax.yaxis.majorTicks[0]._tickdir == "inout"
    assert ax.spines["top"].get_visible() is True
    assert ax.spines["right"].get_visible() is True
    assert any(grid.get_visible() for grid in ax.xaxis.get_gridlines())
    assert not any(grid.get_visible() for grid in ax.yaxis.get_gridlines())
