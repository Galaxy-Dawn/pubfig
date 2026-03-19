"""Tests for flow plot functions."""

import numpy as np
import pytest

from pubfig.plots.flow import parallel_coordinates, sankey


def test_sankey():
    fig = sankey([0, 0, 1], [1, 2, 2], [10, 5, 8])
    assert len(fig.axes) == 1
    # nodes + links
    assert len(fig.axes[0].patches) >= 6


def test_sankey_node_names():
    fig = sankey([0, 0, 1], [1, 2, 2], [10, 5, 8], node_names=["Input", "A", "B"])
    texts = {text.get_text() for text in fig.axes[0].texts}
    assert {"Input", "A", "B"}.issubset(texts)


def test_sankey_legacy_node_labels_removed():
    with pytest.raises(TypeError):
        sankey([0, 0, 1], [1, 2, 2], [10, 5, 8], node_labels=["Input", "A", "B"])


def test_parallel_coordinates():
    data = np.random.rand(30, 4)
    fig = parallel_coordinates(data)
    assert len(fig.axes) == 1
    assert len(fig.axes[0].collections) >= 1


def test_parallel_coordinates_variable_names():
    data = np.random.rand(30, 3)
    fig = parallel_coordinates(data, variable_names=["Speed", "Accuracy", "Latency"])
    labels = [tick.get_text() for tick in fig.axes[0].get_xticklabels()]
    assert labels == ["Speed", "Accuracy", "Latency"]


def test_parallel_coordinates_tick_labels_stay_horizontal_and_upright():
    data = np.random.rand(30, 4)
    fig = parallel_coordinates(data, variable_names=["w", "x", "y", "z"])
    tick_labels = fig.axes[0].get_xticklabels()

    assert [tick.get_text() for tick in tick_labels] == ["w", "x", "y", "z"]
    assert all(tick.get_rotation() == 0.0 for tick in tick_labels)
    assert all(tick.get_fontstyle() == "normal" for tick in tick_labels)


def test_parallel_coordinates_colored():
    data = np.random.rand(30, 4)
    fig = parallel_coordinates(data, color_col=0)
    # colorbar adds an extra Axes
    assert len(fig.axes) >= 2
