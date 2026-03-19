"""Tests for distribution plot functions."""

import matplotlib.figure
import numpy as np
import pytest

from pubfig.plots.distribution import box, density, histogram, raincloud, ridgeline, strip, violin


def test_box_1d():
    fig = box(np.random.randn(50))
    assert isinstance(fig, matplotlib.figure.Figure)
    assert len(fig.axes[0].get_xticklabels()) == 1


def test_box_2d():
    fig = box(np.random.randn(50, 3), category_names=["A", "B", "C"])
    labels = [t.get_text() for t in fig.axes[0].get_xticklabels()]
    assert labels == ["A", "B", "C"]


def test_box_title_spacing_is_compact():
    fig = box(np.random.randn(50), title="Box")
    assert fig.axes[0].title.get_position()[1] == pytest.approx(1.06)


def test_box_category_names():
    fig = box(np.random.randn(50, 2), category_names=["Ctrl", "Treatment"])
    labels = [t.get_text() for t in fig.axes[0].get_xticklabels()]
    assert labels == ["Ctrl", "Treatment"]


def test_density_scipy():
    fig = density(np.random.randn(100), model="scipy")
    assert len(fig.axes[0].lines) >= 1


def test_ridgeline():
    data = [np.random.randn(100) for _ in range(3)]
    fig = ridgeline(data, category_names=["A", "B", "C"])
    ax = fig.axes[0]
    # One outline per feature.
    assert len(ax.lines) == 3
    # Fill + baseline collections per feature.
    assert len(ax.collections) >= 6


def test_ridgeline_draw_order_places_first_state_on_top():
    data = [np.random.randn(100) for _ in range(3)]
    fig = ridgeline(data, category_names=["A", "B", "C"])
    ax = fig.axes[0]

    line_positions_and_zorders = sorted(
        ((float(np.min(line.get_ydata())), float(line.get_zorder())) for line in ax.lines),
        key=lambda item: item[0],
    )
    zorders = [item[1] for item in line_positions_and_zorders]
    assert zorders[0] > zorders[1] > zorders[2]


def test_violin():
    fig = violin(np.random.randn(50, 2), category_names=["A", "B"])
    labels = [t.get_text() for t in fig.axes[0].get_xticklabels()]
    assert labels == ["A", "B"]


def test_histogram_basic():
    fig = histogram(np.random.randn(200))
    assert len(fig.axes[0].patches) > 0


def test_histogram_with_kde():
    fig = histogram(np.random.randn(200), show_kde=True)
    assert len(fig.axes[0].lines) >= 1


def test_strip_2d():
    fig = strip(np.random.randn(30, 3), category_names=["A", "B", "C"])
    assert len(fig.axes[0].collections) == 3


def test_raincloud_vertical() -> None:
    fig = raincloud(np.random.randn(60, 3), category_names=["A", "B", "C"], title="Raincloud")
    ax = fig.axes[0]
    labels = [tick.get_text() for tick in ax.get_xticklabels()]
    assert labels == ["A", "B", "C"]
    assert len(ax.collections) >= 6
    assert ax.get_ylabel() == "Value"


def test_raincloud_horizontal() -> None:
    fig = raincloud(np.random.randn(60, 2), category_names=["Ctrl", "Treat"], orientation="horizontal")
    ax = fig.axes[0]
    labels = [tick.get_text() for tick in ax.get_yticklabels()]
    assert labels == ["Ctrl", "Treat"]
    assert ax.get_xlabel() == "Value"


def test_violin_category_names():
    fig = violin(np.random.randn(50, 2), category_names=["Group 1", "Group 2"])
    labels = [t.get_text() for t in fig.axes[0].get_xticklabels()]
    assert labels == ["Group 1", "Group 2"]


def test_box_axis_controls_apply() -> None:
    fig = box(np.random.randn(50, 2), show_full_box=True, show_x_grid=False, show_y_grid=True, tick_direction="in")
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.xaxis.majorTicks[0]._tickdir == "in"
    assert ax.yaxis.majorTicks[0]._tickdir == "in"
    assert ax.spines["top"].get_visible() is True
    assert ax.spines["right"].get_visible() is True
    assert not any(grid.get_visible() for grid in ax.xaxis.get_gridlines())
    assert any(grid.get_visible() for grid in ax.yaxis.get_gridlines())
