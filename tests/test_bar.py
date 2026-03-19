"""Tests for bar plot functions."""

import matplotlib.collections as mcoll
import matplotlib.figure
import matplotlib.ticker as mticker
import numpy as np
import pytest

from pubfig.plots.bar import bar, bar_scatter, stacked_bar


def test_bar_1d():
    fig = bar(np.array([1.0, 2.0, 3.0]))
    assert isinstance(fig, matplotlib.figure.Figure)
    ax = fig.axes[0]
    assert len(ax.patches) == 3
    left_edge = min(float(p.get_x()) for p in ax.patches)
    x0, _ = ax.get_xlim()
    assert x0 < left_edge


def test_bar_1d_with_names():
    fig = bar(np.array([1, 2]), category_names=["A", "B"], title="Test")
    assert fig.axes[0].get_title() == "Test"


def test_bar_title_spacing_is_compact():
    fig = bar(np.array([1, 2]), title="Test")
    assert fig.axes[0].title.get_position()[1] == pytest.approx(1.06)


def test_bar_legacy_names_removed():
    with pytest.raises(TypeError):
        bar(np.array([1, 2]), names=["A", "B"])


def test_bar_2d_grouped():
    data = np.array([[1.0, 2.0], [3.0, 4.0]])
    fig = bar(data)
    assert len(fig.axes[0].patches) == 4


def test_bar_2d_generic_names():
    data = np.array([[1.0, 2.0], [3.0, 4.0]])
    fig = bar(data, category_names=["Cat A", "Cat B"], series_names=["Ctrl", "Treat"])
    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["Cat A", "Cat B"]
    legend = ax.get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["Ctrl", "Treat"]


def test_bar_horizontal_orientation():
    fig = bar(np.array([1.0, 2.0, 3.0]), orientation="horizontal")
    assert isinstance(fig, matplotlib.figure.Figure)
    ax = fig.axes[0]
    assert len(ax.patches) == 3


def test_bar_tick_direction_override():
    fig = bar(np.array([1.0, 2.0, 3.0]), tick_direction="in")
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.xaxis.majorTicks[0]._tickdir == "in"
    assert ax.yaxis.majorTicks[0]._tickdir == "in"


def test_bar_axis_box_and_split_grid_controls():
    fig = bar(np.array([1.0, 2.0, 3.0]), show_full_box=True, show_x_grid=False, show_y_grid=True)
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.spines["top"].get_visible() is True
    assert ax.spines["right"].get_visible() is True
    assert not any(grid.get_visible() for grid in ax.xaxis.get_gridlines())
    assert any(grid.get_visible() for grid in ax.yaxis.get_gridlines())


def test_bar_value_dtick_sets_locator():
    fig = bar(np.array([1.0, 2.0, 3.0]), value_dtick=0.5)
    ax = fig.axes[0]
    loc = ax.yaxis.get_major_locator()
    assert isinstance(loc, mticker.MultipleLocator)
    vals = loc.tick_values(0.0, 2.0)
    diffs = {round(float(vals[i + 1] - vals[i]), 6) for i in range(min(5, len(vals) - 1))}
    assert 0.5 in diffs


def test_bar_invalid():
    with pytest.raises(ValueError):
        bar(np.ones((2, 3, 4)))


def test_stacked_bar_uses_figure_level_title():
    data = np.abs(np.random.rand(2, 3, 4))
    fig = stacked_bar(data, title="Stacked")
    assert fig._suptitle is not None
    assert fig._suptitle.get_text() == "Stacked"


def test_bar_scatter_2d():
    data = np.array([[1.0, 2.0], [3.0, 4.0]])
    fig = bar_scatter(data, show_statistics=False)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert len(fig.axes[0].patches) == 4


def test_bar_scatter_generic_names():
    data = np.random.rand(2, 2, 6)
    fig = bar_scatter(
        data,
        category_names=["Cond A", "Cond B"],
        series_names=["Ctrl", "Treatment"],
        show_statistics=False,
    )
    ax = fig.axes[0]
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["Cond A", "Cond B"]
    legend = ax.get_legend()
    assert legend is not None
    assert [text.get_text() for text in legend.get_texts()] == ["Ctrl", "Treatment"]


def test_bar_scatter_3d():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, show_statistics=False)
    assert len(fig.axes[0].patches) == 6


def test_bar_scatter_significance_bar_pairs_multi_group():
    data = np.random.rand(2, 4, 8)
    fig = bar_scatter(
        data,
        show_statistics=True,
        significance_bar_pairs=[(0, 1)],
    )
    assert isinstance(fig, matplotlib.figure.Figure)


def test_bar_scatter_horizontal_orientation():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, orientation="horizontal", show_statistics=False)
    assert isinstance(fig, matplotlib.figure.Figure)
    # Same number of bars (patches), but rendered as horizontal bars.
    assert len(fig.axes[0].patches) == 6


def test_bar_scatter_horizontal_orientation_with_statistics():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, orientation="horizontal", show_statistics=True, random_seed=0)
    assert isinstance(fig, matplotlib.figure.Figure)
    ax = fig.axes[0]
    assert len(ax.texts) == 0
    assert len(ax.lines) == 0


def test_bar_scatter_tick_direction_override():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, show_statistics=False, tick_direction="in")
    ax = fig.axes[0]
    fig.canvas.draw()
    assert ax.xaxis.majorTicks[0]._tickdir == "in"
    assert ax.yaxis.majorTicks[0]._tickdir == "in"


def test_bar_scatter_value_dtick_vertical_sets_locator():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, show_statistics=False, value_dtick=0.2)
    ax = fig.axes[0]
    loc = ax.yaxis.get_major_locator()
    assert isinstance(loc, mticker.MultipleLocator)
    vals = loc.tick_values(0.0, 1.0)
    diffs = {round(float(vals[i + 1] - vals[i]), 6) for i in range(min(5, len(vals) - 1))}
    assert 0.2 in diffs


def test_bar_scatter_value_nticks_vertical_sets_locator():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, show_statistics=False, value_nticks=3)
    ax = fig.axes[0]
    loc = ax.yaxis.get_major_locator()
    assert isinstance(loc, mticker.MaxNLocator)


def test_bar_scatter_value_dtick_horizontal_sets_locator():
    data = np.random.rand(2, 3, 10)
    fig = bar_scatter(data, orientation="horizontal", show_statistics=False, value_dtick=0.25)
    ax = fig.axes[0]
    loc = ax.xaxis.get_major_locator()
    assert isinstance(loc, mticker.MultipleLocator)


def test_bar_scatter_scatter_size_scales_with_bar_width():
    # With more groups, bars are narrower (auto bar_width = grouped_total_span/num_groups),
    # so scatter marker sizes should scale down when enabled.
    data2 = np.random.rand(1, 2, 5)
    fig2 = bar_scatter(data2, show_statistics=False, random_seed=0)
    ax2 = fig2.axes[0]
    scat2 = [c for c in ax2.collections if isinstance(c, mcoll.PathCollection)]
    assert len(scat2) >= 1
    s2 = float(scat2[0].get_sizes()[0])

    data4 = np.random.rand(1, 4, 5)
    fig4 = bar_scatter(data4, show_statistics=False, random_seed=0)
    ax4 = fig4.axes[0]
    scat4 = [c for c in ax4.collections if isinstance(c, mcoll.PathCollection)]
    assert len(scat4) >= 1
    s4 = float(scat4[0].get_sizes()[0])

    # For 4 groups, bw is about half of 2 groups => area should be smaller.
    assert s4 < s2


def test_bar_scatter_statistics_clear_larger_scatter_markers():
    rng = np.random.default_rng(0)
    data = rng.normal(loc=[[[0.8], [1.0]]], scale=0.03, size=(1, 2, 12))

    fig_small = bar_scatter(
        data,
        show_statistics=True,
        significance_bar_pairs=[(0, 1)],
        significance_category_indices=[0],
        scatter_size=1.0,
        random_seed=0,
    )
    fig_large = bar_scatter(
        data,
        show_statistics=True,
        significance_bar_pairs=[(0, 1)],
        significance_category_indices=[0],
        scatter_size=12.0,
        random_seed=0,
    )

    ax_small = fig_small.axes[0]
    ax_large = fig_large.axes[0]
    y_small = float(np.max(ax_small.lines[0].get_ydata()))
    y_large = float(np.max(ax_large.lines[0].get_ydata()))

    assert y_large > y_small


def test_stacked_bar():
    data = np.random.rand(2, 3, 4)
    fig = stacked_bar(data)
    # n_rows = subjects * models = 6, n_samples = 4 => 24 patches
    assert len(fig.axes[0].patches) == 24

    # Ensure subject groups do not overlap by default.
    # We infer row centers from rectangle positions (barh uses align="center").
    centers = sorted({p.get_y() + p.get_height() / 2 for p in fig.axes[0].patches})
    assert len(centers) == 6
    # Boundary between the last model of subject 0 and first model of subject 1.
    assert (centers[3] - centers[2]) > 0.20

    # Default normalize=True => each row should sum to ~1.0 total width.
    totals = {}
    for p in fig.axes[0].patches:
        cy = float(p.get_y() + p.get_height() / 2)
        totals[cy] = totals.get(cy, 0.0) + float(p.get_width())
    assert len(totals) == 6
    for total in totals.values():
        assert total == pytest.approx(1.0, abs=1e-6)


def test_stacked_bar_group_names():
    data = np.random.rand(2, 3, 4)
    fig = stacked_bar(data, group_names=["G1", "G2"], group_gap=0.15)
    labels = [t.get_text() for t in fig.axes[0].get_yticklabels()]
    assert labels == ["G1", "G2"]


def test_stacked_bar_legacy_aliases_removed():
    data = np.random.rand(2, 3, 4)
    with pytest.raises(TypeError):
        stacked_bar(data, subject_names=["G1", "G2"], subject_gap=0.15)
