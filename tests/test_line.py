"""Tests for line plot functions."""

import numpy as np

from pubfig.plots.line import area, line


def test_line_basic():
    data = np.random.rand(10, 3)
    fig = line(data)
    assert len(fig.axes[0].lines) == 3


def test_line_series_names():
    data = np.random.rand(10, 2)
    fig = line(data, series_names=["Signal A", "Signal B"])
    legend = fig.axes[0].get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["Signal A", "Signal B"]


def test_line_ci_marker_style():
    data = np.random.rand(2, 8, 5)
    fig = line(
        data,
        marker="s",
        marker_size=4.0,
        marker_edge_color="black",
        marker_edge_line_width=0.2,
    )
    ax = fig.axes[0]
    assert len(ax.lines) == 2
    assert ax.lines[0].get_marker() == "s"
    assert ax.lines[0].get_markeredgecolor() == "black"


def test_line_auto_marker_cycle():
    data = np.random.rand(8, 4)
    fig = line(data, marker="auto")
    ax = fig.axes[0]
    assert [artist.get_marker() for artist in ax.lines] == ["s", "o", "D", "^"]


def test_area_basic():
    data = np.random.rand(20, 3)
    fig = area(data)
    assert len(fig.axes[0].collections) >= 3


def test_area_unstacked():
    data = np.random.rand(20, 2)
    fig = area(data, stacked=False)
    assert len(fig.axes[0].lines) == 2


def test_line_axis_controls_apply() -> None:
    data = np.random.rand(10, 2)
    fig = line(data, tick_direction="in", show_full_box=True, show_x_grid=True, show_y_grid=False)
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.xaxis.majorTicks[0]._tickdir == "in"
    assert ax.yaxis.majorTicks[0]._tickdir == "in"
    assert ax.spines["top"].get_visible() is True
    assert ax.spines["right"].get_visible() is True
    assert any(grid.get_visible() for grid in ax.xaxis.get_gridlines())
    assert not any(grid.get_visible() for grid in ax.yaxis.get_gridlines())
