"""Tests for color utilities and palettes."""

import matplotlib.figure
import pytest

from pubfig.colors import (
    DEFAULT,
    JAMA,
    LANCET,
    NATURE,
    SCIENCE,
    color_to_rgba,
    darken_color,
    get_palette,
    register_palette,
    show_palette,
)


def test_palettes_are_lists():
    for p in [DEFAULT, NATURE, SCIENCE, LANCET, JAMA]:
        assert isinstance(p, (list, tuple))
        assert len(p) >= 4


def test_get_palette():
    assert get_palette("nature") == NATURE
    assert get_palette("SCIENCE") == SCIENCE


def test_get_palette_unknown():
    with pytest.raises(KeyError):
        get_palette("nonexistent")


def test_register_palette():
    custom = ["#111", "#222", "#333"]
    register_palette("custom_test", custom)
    assert get_palette("custom_test") == custom


def test_color_to_rgba_hex():
    assert color_to_rgba("#FF0000", alpha=0.5) == (1.0, 0.0, 0.0, 0.5)


def test_color_to_rgba_rgb():
    rgba = color_to_rgba("rgb(0,128,255)", alpha=0.3)
    assert rgba[0] == 0.0
    assert rgba[3] == 0.3
    assert abs(rgba[1] - (128 / 255.0)) < 1e-6
    assert abs(rgba[2] - 1.0) < 1e-6


def test_color_to_rgba_invalid():
    with pytest.raises(ValueError):
        color_to_rgba("not_a_color")


def test_darken_color_hex():
    assert darken_color("#FF0000", factor=0.5) == "#800000"


def test_darken_color_rgb():
    assert darken_color("rgb(200,100,50)", factor=0.5) == "#643219"


def test_show_palette():
    fig = show_palette(DEFAULT)
    assert isinstance(fig, matplotlib.figure.Figure)
    assert len(fig.axes) == 1
    assert len(fig.axes[0].patches) == len(DEFAULT)

