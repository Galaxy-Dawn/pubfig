"""Export a 3/3/4/4 panel set for a Figma-first multi-panel workflow demo."""

from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import numpy as np

import pubfig as pf
from pubfig.themes.base import AxisStyle, Theme


OUTPUT_DIR = Path(__file__).resolve().parent / "figma_panels_3344_demo_output"
ROW_PANEL_COUNTS = (3, 3, 4, 4)
EXPORT_WIDTH_MM = 132
BAR_SCATTER_PALETTE = ["#6FA8DC", "#93C47D", "#F6B26B"]
LINE_PALETTE = ["#5B8FF9", "#5AD8A6", "#9270CA"]
RADAR_PALETTE = ["#5B8FF9", "#61DDAA", "#F6BD16"]


FIGMA_PANEL_THEME = Theme(
    name="nature-figma-demo",
    font_family=["Helvetica", "Arial", "sans-serif"],
    font_size=9,
    title_font_size=10,
    legend_font_size=8,
    background_color="#FFFFFF",
    axis=AxisStyle(
        label_font_size=9,
        tick_font_size=8,
        line_width=0.6,
        show_grid=False,
        tick_direction="out",
        tick_length=2.5,
        tick_width=0.6,
    ),
    rc_overrides={
        "axes.titleweight": "semibold",
        "legend.labelcolor": "linecolor",
    },
)


def _make_bar_scatter_from_means(
    rng: np.random.Generator,
    means: np.ndarray,
    *,
    repeats: int = 18,
    noise: float = 0.042,
) -> np.ndarray:
    values = rng.normal(loc=means[..., None], scale=float(noise), size=(*means.shape, repeats))
    return np.clip(values, 0.05, None)


def _make_line_panel(x: np.ndarray, mode: str) -> np.ndarray:
    if mode == "gradual_rise":
        y1 = 0.46 + 0.040 * x + 0.018 * np.sin(x / 1.8)
        y2 = 0.58 + 0.032 * x + 0.015 * np.sin(x / 2.1 + 0.3)
        y3 = 0.72 + 0.025 * x + 0.012 * np.sin(x / 2.4 + 0.8)
    elif mode == "plateau":
        logistic = 1.0 / (1.0 + np.exp(-(x - 3.2) / 0.95))
        y1 = 0.40 + 0.32 * logistic + 0.010 * np.sin(x / 2.5)
        y2 = 0.52 + 0.26 * logistic + 0.010 * np.sin(x / 2.6 + 0.5)
        y3 = 0.64 + 0.22 * logistic + 0.009 * np.sin(x / 2.7 + 1.0)
    elif mode == "late_gain":
        ramp = np.clip((x - 2.5) / 5.5, 0.0, 1.0)
        y1 = 0.50 + 0.08 * ramp + 0.17 * ramp**1.6 + 0.012 * np.sin(x / 2.2)
        y2 = 0.60 + 0.06 * ramp + 0.14 * ramp**1.5 + 0.010 * np.sin(x / 2.3 + 0.5)
        y3 = 0.72 + 0.05 * ramp + 0.11 * ramp**1.45 + 0.009 * np.sin(x / 2.4 + 0.9)
    else:
        raise ValueError(f"Unknown line mode: {mode}")
    return np.column_stack([y1, y2, y3])


def _make_radar_panel(levels: list[list[float]]) -> list[list[float]]:
    return [[float(v) for v in row] for row in levels]


def build_demo_panels() -> OrderedDict[str, object]:
    rng = np.random.default_rng(20260323)
    pf.set_default_theme(FIGMA_PANEL_THEME)

    panels: OrderedDict[str, object] = OrderedDict()
    x = np.linspace(0.0, 8.0, 18)
    categories = ["Ctrl", "Low", "Mid", "High"]
    radar_categories = ["Accuracy", "Recall", "Precision", "Robustness", "Speed", "Stability"]

    # Row 1: 3 bar_scatter panels with clearly different profiles.
    row1_specs = {
        "a": (
            np.array(
                [
                    [0.58, 0.67, 0.76],
                    [0.61, 0.72, 0.82],
                    [0.65, 0.78, 0.88],
                    [0.70, 0.83, 0.93],
                ]
            ),
            ["Vehicle", "Dose 1", "Dose 2"],
            "Relative signal",
        ),
        "b": (
            np.array(
                [
                    [0.86, 0.78, 0.69],
                    [0.82, 0.76, 0.66],
                    [0.75, 0.70, 0.60],
                    [0.69, 0.64, 0.56],
                ]
            ),
            ["Reference", "Regimen A", "Regimen B"],
            "Viability",
        ),
        "c": (
            np.array(
                [
                    [0.56, 0.63, 0.60],
                    [0.64, 0.76, 0.72],
                    [0.71, 0.86, 0.80],
                    [0.63, 0.74, 0.69],
                ]
            ),
            ["Baseline", "Responsive", "Recovered"],
            "Activation score",
        ),
    }
    for panel_id, (means, series_names, y_label) in row1_specs.items():
        panels[panel_id] = pf.bar_scatter(
            _make_bar_scatter_from_means(rng, means, noise=0.040),
            category_names=categories,
            series_names=series_names,
            color_palette=BAR_SCATTER_PALETTE,
            x_label="Condition",
            y_label=y_label,
            legend_show=True,
            show_statistics=True,
            random_seed=0,
        )

    # Row 2: 3 line panels with different but smooth trends.
    row2_specs = {
        "d": ("gradual_rise", ["Cohort 1", "Cohort 2", "Cohort 3"], "Response"),
        "e": ("plateau", ["Arm A", "Arm B", "Arm C"], "Normalized output"),
        "f": ("late_gain", ["Week 1", "Week 2", "Week 3"], "Signal ratio"),
    }
    for panel_id, (mode, series_names, y_label) in row2_specs.items():
        panels[panel_id] = pf.line(
            _make_line_panel(x, mode),
            x=x,
            series_names=series_names,
            color_palette=LINE_PALETTE,
            x_label="Time (weeks)",
            y_label=y_label,
            legend_show=True,
            marker="auto",
        )

    # Row 3: 4 radar panels with distinct shapes rather than shifted copies.
    row3_specs = {
        "g": [
            [0.70, 0.78, 0.74, 0.66, 0.80, 0.76],
            [0.76, 0.84, 0.80, 0.74, 0.86, 0.82],
            [0.81, 0.87, 0.84, 0.79, 0.88, 0.86],
        ],
        "h": [
            [0.82, 0.73, 0.69, 0.77, 0.65, 0.71],
            [0.86, 0.79, 0.74, 0.82, 0.72, 0.77],
            [0.90, 0.84, 0.79, 0.86, 0.78, 0.83],
        ],
        "i": [
            [0.62, 0.72, 0.81, 0.76, 0.69, 0.64],
            [0.68, 0.78, 0.87, 0.81, 0.75, 0.70],
            [0.73, 0.83, 0.90, 0.86, 0.80, 0.76],
        ],
        "j": [
            [0.75, 0.86, 0.72, 0.83, 0.78, 0.69],
            [0.80, 0.89, 0.78, 0.87, 0.83, 0.74],
            [0.84, 0.92, 0.83, 0.90, 0.88, 0.80],
        ],
    }
    for panel_id, levels in row3_specs.items():
        panels[panel_id] = pf.radar(
            _make_radar_panel(levels),
            categories=radar_categories,
            series_names=["Baseline", "Method A", "Method B"],
            color_palette=RADAR_PALETTE,
            category_label_mode="tangent",
            legend_show=True,
        )

    # Row 4: 4 more bar_scatter panels, also distinct from each other and from row 1.
    row4_specs = {
        "k": (
            np.array(
                [
                    [0.48, 0.54, 0.61],
                    [0.59, 0.68, 0.77],
                    [0.66, 0.75, 0.86],
                    [0.72, 0.80, 0.91],
                ]
            ),
            ["Ctrl", "Treatment A", "Treatment B"],
            "Normalized intensity",
        ),
        "l": (
            np.array(
                [
                    [0.79, 0.70, 0.60],
                    [0.74, 0.67, 0.58],
                    [0.70, 0.63, 0.55],
                    [0.66, 0.59, 0.51],
                ]
            ),
            ["Wildtype", "Mutant 1", "Mutant 2"],
            "Survival fraction",
        ),
        "m": (
            np.array(
                [
                    [0.54, 0.59, 0.64],
                    [0.68, 0.77, 0.85],
                    [0.62, 0.70, 0.79],
                    [0.58, 0.64, 0.71],
                ]
            ),
            ["Untreated", "Combo A", "Combo B"],
            "Enrichment score",
        ),
        "n": (
            np.array(
                [
                    [0.64, 0.73, 0.81],
                    [0.61, 0.70, 0.79],
                    [0.58, 0.67, 0.76],
                    [0.55, 0.64, 0.73],
                ]
            ),
            ["Start", "Midpoint", "Endpoint"],
            "Recovery index",
        ),
    }
    for panel_id, (means, series_names, y_label) in row4_specs.items():
        panels[panel_id] = pf.bar_scatter(
            _make_bar_scatter_from_means(rng, means, noise=0.044),
            category_names=categories,
            series_names=series_names,
            color_palette=["#77AADD", "#A3C585", "#E7B46A"],
            x_label="Condition",
            y_label=y_label,
            legend_show=True,
            show_statistics=True,
            random_seed=0,
        )

    return panels


def main() -> None:
    panels = build_demo_panels()
    records = pf.export_panels(
        panels,
        OUTPUT_DIR,
        format="svg",
        index_file=True,
        overwrite=True,
        spec="nature",
        width=EXPORT_WIDTH_MM,
    )
    print(f"Exported {len(records)} panel assets to {OUTPUT_DIR}")
    print(f"Sync index: {OUTPUT_DIR / 'panel-index.json'}")
    print("Suggested Figma sync:")
    print(
        "  pubfig figma sync "
        f"{OUTPUT_DIR} --row-panel-counts {','.join(str(v) for v in ROW_PANEL_COUNTS)} "
        "--panel-gap 6 --label-offset-x 12 --label-offset-y 10"
    )


if __name__ == "__main__":
    main()
