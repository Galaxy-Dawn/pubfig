"""Export a small pubfig gallery with Matplotlib."""

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pubfig as pf  # noqa: E402 - allow local import after sys.path tweak for examples

OUT = ROOT / "output_figures_mpl"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    rng = np.random.default_rng(0)
    # Use small-variance, strictly-positive synthetic data so bars are always visible
    # when the plot enforces y_min=0 (publication-style bar charts).
    means = np.array(
        [
            [0.80, 1.00, 0.82, 0.78],  # Cond A: Ctrl, Treat, Var1, Var2
            [0.90, 1.12, 0.90, 0.90],  # Cond B (Var1 vs Var2 should be n.s.)
            [0.85, 1.06, 0.86, 0.86],  # Cond C (Var1 vs Var2 should be n.s.)
            [0.88, 1.10, 0.90, 0.87],  # Cond D
        ],
        dtype=float,
    )
    sd = 0.08
    data = rng.normal(loc=means[..., None], scale=sd, size=(4, 4, 20))
    data = np.clip(data, 0.0, None)

    fig = pf.bar_scatter(
        data,
        category_names=["Cond A", "Cond B", "Cond C", "Cond D"],
        series_names=["Ctrl", "Treat", "Var1", "Var2"],
        title="Bar + Scatter (Matplotlib)",
        color_palette=pf.get_palette("orange_red"),
        show_statistics=True,
        random_seed=0,
    )

    pf.save_figure(
        fig,
        OUT / "01_bar_scatter_mpl",
        spec="nature",
        width="single",
        aspect_ratio=0.6,
        raster_dpi=600,
        vector_formats=("pdf", "svg"),
        raster_formats=("png", "tiff"),
        trim=True,
    )
    try:
        import matplotlib.pyplot as plt

        plt.close(fig)
    except Exception:
        pass
    print("Saved:", OUT / "01_bar_scatter_mpl.*")  # noqa: T201 - example script

    fig_h = pf.bar_scatter(
        data,
        category_names=["Cond A", "Cond B", "Cond C", "Cond D"],
        series_names=["Ctrl", "Treat", "Var1", "Var2"],
        title="Bar + Scatter (Horizontal)",
        color_palette=pf.get_palette("orange_red"),
        orientation="horizontal",
        show_statistics=False,
        random_seed=0,
    )

    pf.save_figure(
        fig_h,
        OUT / "02_bar_scatter_horizontal_mpl",
        spec="nature",
        width="single",
        aspect_ratio=0.6,
        raster_dpi=600,
        vector_formats=("pdf", "svg"),
        raster_formats=("png", "tiff"),
        trim=True,
    )
    try:
        import matplotlib.pyplot as plt

        plt.close(fig_h)
    except Exception:
        pass
    print("Saved:", OUT / "02_bar_scatter_horizontal_mpl.*")  # noqa: T201 - example script

    # The default bar_scatter style is now the "gray points + compact brackets" variant.


if __name__ == "__main__":
    main()
