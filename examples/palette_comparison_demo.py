"""Compare multiple palettes on the same pubfig chart."""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pubfig as pf  # noqa: E402

OUT_DIR = ROOT / "examples" / "palettes"
OUT_DIR.mkdir(parents=True, exist_ok=True)

PALETTES = [
    "nature",
    "science",
    "lancet",
    "jama",
    "carto_blugrn",
    "carto_sunsetdark",
]


def make_demo_data(seed: int = 7) -> np.ndarray:
    rng = np.random.default_rng(seed)
    means = np.array(
        [
            [0.82, 1.00, 0.88, 0.78],
            [0.94, 1.10, 0.95, 0.87],
            [0.86, 1.05, 0.90, 0.84],
            [0.90, 1.08, 0.93, 0.86],
        ],
        dtype=float,
    )
    data = rng.normal(loc=means[..., None], scale=0.07, size=(4, 4, 18))
    return np.clip(data, 0.0, None)


def main() -> None:
    pf.set_default_theme("nature")
    data = make_demo_data()

    fig, axes = plt.subplots(2, 3, figsize=(14, 8), dpi=180)
    axes = axes.ravel()

    handles = None
    labels = None
    for ax, palette_name in zip(axes, PALETTES):
        fig_panel = pf.bar(
            data.mean(axis=2),
            ax=ax,
            category_names=["Task A", "Task B", "Task C", "Task D"],
            series_names=["Baseline", "Method 1", "Method 2", "Method 3"],
            title=palette_name,
            x_label="",
            y_label="Score",
            color_palette=pf.get_palette(palette_name),
            legend_show=False,
            category_spacing=0.88,
            grouped_total_span=0.7,
            grouped_bar_width_ratio=0.82,
        )
        assert fig_panel is fig
        ax.set_ylim(0.0, 1.25)
        ax.set_yticks([0.0, 0.4, 0.8, 1.2])
        if handles is None:
            handles, labels = ax.get_legend_handles_labels()

    if handles and labels:
        fig.legend(
            handles,
            labels,
            loc="upper center",
            ncol=4,
            frameon=False,
            bbox_to_anchor=(0.5, 0.985),
            columnspacing=1.4,
            handlelength=1.4,
            prop={"family": "DejaVu Sans", "size": 10},
        )

    fig.suptitle(
        "Same Chart, Different Palettes",
        fontsize=16,
        fontweight="bold",
        y=0.995,
        fontfamily="DejaVu Sans",
    )
    fig.tight_layout(rect=[0.0, 0.0, 1.0, 0.95])

    pf.save_figure(
        fig,
        OUT_DIR / "palette-comparison-demo",
        spec="nature",
        width="double",
        aspect_ratio=0.62,
        raster_dpi=500,
        vector_formats=("pdf", "svg"),
        raster_formats=("png",),
        trim=True,
    )
    plt.close(fig)
    print(OUT_DIR / "palette-comparison-demo.png")


if __name__ == "__main__":
    main()
