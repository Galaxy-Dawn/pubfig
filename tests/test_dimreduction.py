"""Tests for dimensionality reduction plot functions."""

import numpy as np
import pytest
from matplotlib.patches import Ellipse
from matplotlib.text import Annotation

from pubfig.plots.dimreduction import dimreduce, pca_biplot
from pubfig.themes import get_default_theme


def test_dimreduce_tsne_basic():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(0)
    data = rng.normal(size=(40, 4))
    fig, reducer = dimreduce(data, perplexity=10)
    assert len(fig.axes[0].collections) >= 1
    assert reducer.embedding_.shape == (40, 2)


def test_dimreduce_rejects_unsupported_model():
    data = np.random.randn(20, 4)
    with pytest.raises(ValueError, match="Only model='tsne' is supported"):
        dimreduce(data, model="unsupported")


def test_pca_biplot_variable_names():
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    fig = pca_biplot(
        data,
        variable_names=["Feat A", "Feat B", "Feat C"],
        loading_panel="overlay",
        legend_show=False,
    )
    texts = {text.get_text() for text in fig.axes[0].texts}
    assert {"Feat A", "Feat B", "Feat C"}.issubset(texts)


def test_pca_biplot_defaults_to_no_loadings():
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    fig = pca_biplot(
        data,
        variable_names=["Feat A", "Feat B", "Feat C"],
        legend_show=False,
    )
    assert len(fig.axes) == 1
    assert len(fig.axes[0].texts) == 0


def test_pca_biplot_loading_panel_none_hides_loadings():
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    fig = pca_biplot(
        data,
        variable_names=["Feat A", "Feat B", "Feat C"],
        loading_panel="none",
        legend_show=False,
    )
    assert len(fig.axes) == 1
    assert len(fig.axes[0].texts) == 0


def test_pca_biplot_loading_panel_separate_creates_second_panel():
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    fig = pca_biplot(
        data,
        variable_names=["Feat A", "Feat B", "Feat C"],
        loading_panel="separate",
        legend_show=False,
    )
    assert len(fig.axes) == 2
    assert fig.axes[1].get_title() == "Loadings"
    texts = {text.get_text() for text in fig.axes[1].texts}
    assert {"Feat A", "Feat B", "Feat C"}.issubset(texts)


def test_pca_biplot_rejects_unknown_loading_panel():
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    with pytest.raises(ValueError, match="loading_panel must be 'overlay', 'separate', or 'none'"):
        pca_biplot(data, loading_panel="bad-mode")


def test_pca_biplot_overlay_loadings_do_not_overlap_legend():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(0)
    base = rng.normal(size=(80, 5))
    transform = np.array(
        [
            [1.0, 0.2, 0.8, 0.0, 0.3],
            [0.3, 1.1, -0.2, 0.6, 0.1],
            [0.8, -0.3, 1.2, 0.4, -0.2],
            [0.0, 0.5, 0.3, 1.1, 0.7],
            [0.2, 0.1, -0.4, 0.8, 1.0],
        ]
    )
    data = base @ transform
    labels = np.array(["Group A"] * 30 + ["Group B"] * 25 + ["Group C"] * 25)
    fig = pca_biplot(
        data,
        variable_names=["Feature 1", "Feature 2", "Feature 3", "Feature 4", "Feature 5"],
        labels=labels,
        loading_panel="overlay",
    )
    fig.canvas.draw()
    ax = fig.axes[0]
    legend = ax.get_legend()
    assert legend is not None
    renderer = fig.canvas.get_renderer()
    legend_bbox = legend.get_window_extent(renderer=renderer)
    title_bbox = ax.title.get_window_extent(renderer=renderer)
    assert not title_bbox.overlaps(legend_bbox)
    for text in ax.texts:
        assert not text.get_window_extent(renderer=renderer).overlaps(legend_bbox)


def test_pca_biplot_overlay_loadings_use_annotation_arrows():
    pytest.importorskip("sklearn")
    data = np.random.randn(50, 4)
    fig = pca_biplot(
        data,
        variable_names=["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
        loading_panel="overlay",
        legend_show=False,
    )
    arrow_annotations = [
        text
        for text in fig.axes[0].texts
        if isinstance(text, Annotation) and text.get_text() == "" and text.arrow_patch is not None
    ]
    assert len(arrow_annotations) == 4
    first_arrow = arrow_annotations[0].arrow_patch
    assert first_arrow is not None
    assert np.allclose(first_arrow.get_edgecolor()[:3], (0.0, 0.0, 0.0))
    assert np.isclose(first_arrow.get_edgecolor()[3], 1.0)


def test_pca_biplot_loading_labels_are_offset_from_arrow_heads():
    pytest.importorskip("sklearn")
    data = np.random.randn(50, 4)
    fig = pca_biplot(
        data,
        variable_names=["Feature 1", "Feature 2", "Feature 3", "Feature 4"],
        loading_panel="overlay",
        legend_show=False,
    )
    label_annotations = [
        text
        for text in fig.axes[0].texts
        if isinstance(text, Annotation) and text.get_text().startswith("Feature ")
    ]
    assert len(label_annotations) == 4
    assert all(tuple(ann.get_position()) != (0, 0) for ann in label_annotations)


def test_pca_biplot_group_ellipse_outline_added_for_each_label_group():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(0)
    group_a = rng.normal(loc=(-1.5, 0.0, 0.5, 1.0), scale=0.4, size=(25, 4))
    group_b = rng.normal(loc=(1.5, 1.0, -0.5, -1.0), scale=0.45, size=(25, 4))
    data = np.vstack([group_a, group_b])
    labels = np.array(["Group A"] * len(group_a) + ["Group B"] * len(group_b))

    fig = pca_biplot(data, labels=labels, legend_show=False, show_group_ellipse=True)

    ellipse_patches = [patch for patch in fig.axes[0].patches if isinstance(patch, Ellipse)]
    assert len(ellipse_patches) == 2
    assert all(patch.get_linestyle() == "--" for patch in ellipse_patches)


def test_pca_biplot_group_ellipse_fill_uses_translucent_group_color():
    pytest.importorskip("sklearn")
    rng = np.random.default_rng(1)
    group_a = rng.normal(loc=(-1.0, 0.0, 0.5, 1.2), scale=0.35, size=(20, 4))
    group_b = rng.normal(loc=(1.0, 1.2, -0.3, -0.8), scale=0.35, size=(20, 4))
    data = np.vstack([group_a, group_b])
    labels = np.array(["Group A"] * len(group_a) + ["Group B"] * len(group_b))

    fig = pca_biplot(
        data,
        labels=labels,
        legend_show=False,
        show_group_ellipse=True,
        ellipse_fill=True,
        ellipse_fill_alpha=0.5,
    )

    ellipse_patches = [patch for patch in fig.axes[0].patches if isinstance(patch, Ellipse)]
    filled_patches = [patch for patch in ellipse_patches if patch.get_facecolor()[3] > 0.0]
    outline_patches = [patch for patch in ellipse_patches if patch.get_facecolor()[3] == 0.0]
    assert len(filled_patches) == 2
    assert len(outline_patches) == 2
    assert all(np.isclose(patch.get_facecolor()[3], 0.5) for patch in filled_patches)


def test_pca_biplot_rejects_invalid_ellipse_confidence():
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    with pytest.raises(ValueError, match="ellipse_confidence must be in \\(0, 1\\)"):
        pca_biplot(data, ellipse_confidence=1.0)


def test_pca_biplot_title_uses_theme_fontfamily() -> None:
    pytest.importorskip("sklearn")
    data = np.random.randn(40, 3)
    fig = pca_biplot(data, title="Demo", legend_show=False)
    expected = list(get_default_theme().font_family)
    assert fig.axes[0].title.get_fontfamily() == expected
