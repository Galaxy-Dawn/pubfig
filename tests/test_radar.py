"""Tests for radar plot functions."""

from pubfig.themes import get_default_theme
from pubfig.plots.radar import radar


def test_radar_uses_figure_level_title() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    title_text = getattr(fig.axes[0], "_pubfig_title_text", None)
    assert title_text is not None
    assert title_text.get_text() == "Radar"


def test_radar_title_is_above_highest_category_label() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    fig.canvas.draw()
    title_text = fig.axes[0]._pubfig_title_text
    renderer = fig.canvas.get_renderer()
    title_box = fig.transFigure.inverted().transform_bbox(title_text.get_window_extent(renderer=renderer))
    highest_label_top = max(
        fig.transFigure.inverted().transform_bbox(text.get_window_extent(renderer=renderer)).y1
        for text in fig.axes[0]._pubfig_category_texts
    )
    assert title_box.y0 >= highest_label_top


def test_radar_fills_each_series() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    assert len(fig.axes[0].patches) >= 2


def test_radar_has_markers_by_default() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    assert all(line.get_marker() == "o" for line in fig.axes[0].lines)


def test_radar_shows_spoke_grid_by_default() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    fig.canvas.draw()
    assert any(line.get_visible() and line.get_linestyle() == "--" for line in fig.axes[0].xaxis.get_gridlines())


def test_radar_uses_three_internal_radial_ticks_by_default() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    assert len(fig.axes[0].get_yticks()) == 3


def test_radar_legend_is_figure_level_and_bottom_aligned() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    assert len(fig.legends) == 1
    anchor = fig.legends[0].get_bbox_to_anchor()._bbox
    assert anchor.y0 < 0.1


def test_radar_outer_ring_is_black() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    edge = fig.axes[0].spines["polar"].get_edgecolor()
    assert tuple(round(v, 3) for v in edge[:3]) == (0.0, 0.0, 0.0)


def test_radar_uses_tangent_labels_by_default() -> None:
    fig = radar(
        [[0.7, 0.6, 0.8, 0.5], [0.5, 0.9, 0.4, 0.7]],
        categories=["Top", "Right", "Bottom", "Left"],
        title="Radar",
    )
    fig.canvas.draw()
    rotations = [float(tick.get_rotation()) for tick in fig.axes[0]._pubfig_category_texts]
    assert rotations[0] == 0.0
    assert rotations[2] == 0.0
    assert set(rotations[1:]) == {0.0, 90.0, 270.0}


def test_radar_supports_tangent_category_labels() -> None:
    fig = radar(
        [[0.7, 0.6, 0.8, 0.5], [0.5, 0.9, 0.4, 0.7]],
        categories=["Top", "Right", "Bottom", "Left"],
        category_label_mode="tangent",
        title="Radar",
    )
    fig.canvas.draw()
    rotations = [float(tick.get_rotation()) for tick in fig.axes[0]._pubfig_category_texts]
    assert rotations[0] == 0.0
    assert rotations[2] == 0.0
    assert set(rotations[1:]) == {0.0, 90.0, 270.0}


def test_radar_category_labels_are_center_aligned() -> None:
    fig = radar(
        [[0.7, 0.6, 0.8, 0.5], [0.5, 0.9, 0.4, 0.7]],
        categories=["Top", "Right", "Bottom", "Left"],
        category_label_mode="tangent",
        title="Radar",
    )
    assert all(text.get_ha() == "center" and text.get_va() == "center" for text in fig.axes[0]._pubfig_category_texts)


def test_radar_horizontal_labels_stay_unrotated() -> None:
    fig = radar(
        [[0.7, 0.6, 0.8, 0.5], [0.5, 0.9, 0.4, 0.7]],
        categories=["Top", "Right", "Bottom", "Left"],
        category_label_mode="horizontal",
        title="Radar",
    )
    fig.canvas.draw()
    assert all(float(text.get_rotation()) == 0.0 for text in fig.axes[0]._pubfig_category_texts)


def test_radar_horizontal_labels_align_outward() -> None:
    fig = radar(
        [[0.7, 0.6, 0.8, 0.5], [0.5, 0.9, 0.4, 0.7]],
        categories=["Top", "Right", "Bottom", "Left"],
        category_label_mode="horizontal",
        title="Radar",
    )
    fig.canvas.draw()
    top, right, bottom, left = fig.axes[0]._pubfig_category_texts
    assert top.get_ha() == "center" and top.get_va() == "bottom"
    assert right.get_ha() == "left" and right.get_va() == "center"
    assert bottom.get_ha() == "center" and bottom.get_va() == "top"
    assert left.get_ha() == "right" and left.get_va() == "center"


def test_radar_wraps_category_labels_when_requested() -> None:
    fig = radar(
        [[0.7, 0.6, 0.8]],
        categories=["Cross-subject Robustness", "Speed", "Interpretability"],
        category_label_wrap_width=8,
        title="Radar",
    )
    fig.canvas.draw()
    assert "\n" in fig.axes[0]._pubfig_category_texts[0].get_text()


def test_radar_figure_texts_use_theme_fontfamily() -> None:
    fig = radar([[0.7, 0.6, 0.8]], categories=["A", "B", "C"], title="Radar")
    expected = list(get_default_theme().font_family)
    assert fig.axes[0]._pubfig_title_text.get_fontfamily() == expected
    assert all(text.get_fontfamily() == expected for text in fig.axes[0]._pubfig_category_texts)


def test_radar_legend_uses_theme_fontfamily() -> None:
    fig = radar([[0.7, 0.6, 0.8], [0.5, 0.9, 0.4]], categories=["A", "B", "C"], title="Radar")
    expected = list(get_default_theme().font_family)
    assert len(fig.legends) == 1
    assert all(text.get_fontfamily() == expected for text in fig.legends[0].get_texts())
