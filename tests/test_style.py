"""Tests for shared style helpers."""

from __future__ import annotations

import matplotlib.pyplot as plt
import pytest

from pubfig._style import title_above


def test_title_above_uses_compact_default_offset():
    fig, ax = plt.subplots()

    title = title_above(ax, "Example")

    assert title.get_position()[1] == pytest.approx(1.16)
    assert title.get_fontweight() == "semibold"
    plt.close(fig)
