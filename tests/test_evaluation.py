"""Tests for evaluation plot functions."""

import numpy as np

from pubfig.plots.evaluation import pr_curve, roc


def test_roc_single():
    fpr = np.array([0, 0.1, 0.3, 0.6, 1.0])
    tpr = np.array([0, 0.5, 0.7, 0.9, 1.0])
    fig = roc(fpr, tpr)
    assert len(fig.axes[0].lines) == 2  # curve + diagonal


def test_roc_multi():
    fpr = [np.array([0, 0.2, 1.0]), np.array([0, 0.3, 1.0])]
    tpr = [np.array([0, 0.8, 1.0]), np.array([0, 0.6, 1.0])]
    fig = roc(fpr, tpr, series_names=["A", "B"])
    assert len(fig.axes[0].lines) == 3  # 2 curves + diagonal


def test_roc_series_names():
    fpr = [np.array([0, 0.2, 1.0]), np.array([0, 0.3, 1.0])]
    tpr = [np.array([0, 0.8, 1.0]), np.array([0, 0.6, 1.0])]
    fig = roc(fpr, tpr, series_names=["Baseline", "Improved"])
    legend = fig.axes[0].get_legend()
    assert legend is not None
    labels = [text.get_text() for text in legend.get_texts()]
    assert labels[0].startswith("Baseline ")
    assert labels[1].startswith("Improved ")


def test_pr_curve_single():
    precision = np.array([1.0, 0.8, 0.6, 0.4])
    recall = np.array([0.2, 0.5, 0.7, 1.0])
    fig = pr_curve(precision, recall)
    assert len(fig.axes[0].lines) == 1


def test_roc_axis_controls_apply() -> None:
    fpr = np.array([0, 0.1, 0.3, 0.6, 1.0])
    tpr = np.array([0, 0.5, 0.7, 0.9, 1.0])
    fig = roc(fpr, tpr, show_full_box=True, show_x_grid=True, show_y_grid=True, tick_direction="in")
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.xaxis.majorTicks[0]._tickdir == "in"
    assert ax.yaxis.majorTicks[0]._tickdir == "in"
    assert ax.spines["top"].get_visible() is True
    assert ax.spines["right"].get_visible() is True
    assert any(grid.get_visible() for grid in ax.xaxis.get_gridlines())
    assert any(grid.get_visible() for grid in ax.yaxis.get_gridlines())
