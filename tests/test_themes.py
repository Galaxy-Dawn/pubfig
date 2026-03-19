"""Tests for theme system."""

import matplotlib.pyplot as plt
import pytest

from pubfig.themes import AxisStyle, Theme, _apply_theme, get_default_theme, get_theme, register_theme, set_default_theme


def test_theme_is_frozen():
    t = Theme(name="x")
    with pytest.raises(AttributeError):
        t.name = "changed"


def test_axis_style_is_frozen():
    a = AxisStyle()
    with pytest.raises(AttributeError):
        a.line_width = 5


def test_get_theme():
    t = get_theme("nature")
    assert t.name == "nature"


def test_get_theme_unknown():
    with pytest.raises(KeyError):
        get_theme("nonexistent")


def test_set_and_get_default():
    original = get_default_theme()
    set_default_theme("science")
    assert get_default_theme().name == "science"
    set_default_theme(original)


def test_register_theme():
    custom = Theme(name="custom_test")
    register_theme("custom_test", custom)
    assert get_theme("custom_test").name == "custom_test"


def test_apply_theme_to_axes():
    fig, ax = plt.subplots()
    t = get_theme("nature")
    _apply_theme(ax, t)
    for spine in ax.spines.values():
        assert abs(spine.get_linewidth() - t.axis.line_width) < 1e-6


def test_apply_theme_explicitly_sets_axis_and_tick_fontfamilies():
    fig, ax = plt.subplots()
    ax.set_title("Title")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_xticks([0, 1], labels=["A", "B"])
    ax.set_yticks([0, 1], labels=["C", "D"])
    t = get_theme("nature")
    _apply_theme(ax, t)
    expected = list(t.font_family)
    assert ax.title.get_fontfamily() == expected
    assert ax.xaxis.label.get_fontfamily() == expected
    assert ax.yaxis.label.get_fontfamily() == expected
    assert all(label.get_fontfamily() == expected for label in ax.get_xticklabels())
    assert all(label.get_fontfamily() == expected for label in ax.get_yticklabels())


def test_nature_theme_spines_and_legend_defaults():
    t = get_theme("nature")
    rc = t.rc_params()
    assert rc["axes.spines.left"] is True
    assert rc["axes.spines.bottom"] is True
    assert rc["axes.spines.top"] is False
    assert rc["axes.spines.right"] is False
    assert rc["legend.frameon"] is False


def test_nature_theme_uses_arial_helvetica_stack():
    t = get_theme("nature")
    rc = t.rc_params()
    assert rc["font.family"] == ["Helvetica", "Arial", "sans-serif"]
    assert rc["axes.titleweight"] == "semibold"
    assert rc["legend.labelcolor"] == "linecolor"
