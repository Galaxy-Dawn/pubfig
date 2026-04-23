from __future__ import annotations

import matplotlib.figure
import numpy as np
import pytest

import pubfig as pf


@pytest.mark.parametrize(
    ("kind", "kwargs"),
    [
        (
            "bar_scatter",
            {
                "data": np.clip(
                    np.random.default_rng(1).normal(
                        loc=np.array([[0.8, 0.95], [0.9, 1.05]], dtype=float)[..., None],
                        scale=0.04,
                        size=(2, 2, 8),
                    ),
                    0.0,
                    None,
                ),
                "category_names": ["A", "B"],
                "series_names": ["Ctrl", "Tx"],
            },
        ),
        (
            "line",
            {
                "data": np.array([[0.78, 0.88], [0.92, 0.97], [1.05, 1.02], [1.12, 1.08]], dtype=float),
                "x": [0, 1, 2, 3],
                "series_names": ["Square", "Circle"],
            },
        ),
        (
            "heatmap",
            {
                "data": np.array([[0.92, 0.18], [0.25, 0.87]], dtype=float),
                "category_names": ["Ctrl", "Case"],
            },
        ),
    ],
)
def test_public_plot_smoke(kind: str, kwargs: dict) -> None:
    figure = getattr(pf, kind)(**kwargs)
    assert isinstance(figure, matplotlib.figure.Figure)
    assert len(figure.axes) >= 1
