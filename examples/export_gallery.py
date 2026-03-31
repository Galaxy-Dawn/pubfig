"""Export a gallery of pubfig plot types to output_figures/."""

import shutil
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pubfig as pf  # noqa: E402 - allow local import after sys.path tweak for examples
from gallery_contact_sheet import build_gallery_contact_sheet  # noqa: E402
from new_plot_showcases import (  # noqa: E402
    make_bland_altman_demo as make_bland_altman_showcase,
    make_calibration_demo as make_calibration_showcase,
    make_circular_grouped_bar_demo as make_circular_grouped_bar_showcase,
    make_circular_stacked_bar_demo as make_circular_stacked_bar_showcase,
    make_donut_demo as make_donut_showcase,
    make_dumbbell_demo as make_dumbbell_showcase,
    make_ecdf_demo as make_ecdf_showcase,
    make_forest_demo as make_forest_showcase,
    make_grouped_scatter_demo as make_grouped_scatter_showcase,
    make_hexbin_demo as make_hexbin_showcase,
    make_qq_demo as make_qq_showcase,
    make_radial_hierarchy_demo as make_radial_hierarchy_showcase,
    make_stacked_ratio_demo as make_stacked_ratio_showcase,
    make_upset_demo as make_upset_showcase,
    make_volcano_demo as make_volcano_showcase,
)

pf.set_default_theme("nature")
OUT = ROOT / "output_figures"
GALLERY_HERO = ROOT / "examples" / "gallery-hero.png"
CONTACT_SHEET = OUT / "all_plots_contact_sheet.png"
FEATURED_EXPORTS = {
    "03_bar_scatter.png": ROOT / "examples" / "bar_scatter.png",
    "08b_raincloud.png": ROOT / "examples" / "raincloud.png",
    "10_line.png": ROOT / "examples" / "line.png",
    "13_scatter.png": ROOT / "examples" / "scatter.png",
    "17_radar.png": ROOT / "examples" / "radar.png",
    "18_heatmap.png": ROOT / "examples" / "heatmap.png",
    "16b_dumbbell.png": ROOT / "examples" / "dumbbell.png",
    "16c_forest_plot.png": ROOT / "examples" / "forest_plot.png",
    "16d_grouped_scatter.png": ROOT / "examples" / "grouped_scatter.png",
    "16e_donut.png": ROOT / "examples" / "donut.png",
    "16f_stacked_ratio_barh.png": ROOT / "examples" / "stacked_ratio_barh.png",
    "16g_radial_hierarchy.png": ROOT / "examples" / "radial_hierarchy.png",
    "16h_circular_stacked_bar.png": ROOT / "examples" / "circular_stacked_bar.png",
    "16i_circular_grouped_bar.png": ROOT / "examples" / "circular_grouped_bar.png",
    "16j_upset.png": ROOT / "examples" / "upset.png",
    "07b_ecdf.png": ROOT / "examples" / "ecdf.png",
    "07c_qq.png": ROOT / "examples" / "qq.png",
    "15c_bland_altman.png": ROOT / "examples" / "bland_altman.png",
    "24b_calibration.png": ROOT / "examples" / "calibration.png",
    "15b_hexbin.png": ROOT / "examples" / "hexbin.png",
    "25b_volcano.png": ROOT / "examples" / "volcano.png",
}
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(7)

VECTOR_FORMATS = ("pdf", "svg")
RASTER_FORMATS = ("png",)


def make_line_demo() -> tuple[np.ndarray, np.ndarray, list[str]]:
    x_vals = np.linspace(0.0, 12.0, 16)
    series = np.column_stack(
        [
            0.78 + 0.035 * x_vals + 0.08 * np.sin(x_vals / 3.0),
            0.98 + 0.025 * x_vals + 0.06 * np.cos(x_vals / 4.2 + 0.3),
            1.12 + 0.018 * x_vals + 0.05 * np.sin(x_vals / 2.7 + 0.6),
            0.88 + 0.03 * x_vals + 0.045 * np.cos(x_vals / 3.1 + 1.1),
        ]
    )
    return x_vals, series, ["Square", "Circle", "Diamond", "Triangle"]


BAR_DEMO_PALETTE = ["#C7DCEF", "#92B9D9", "#5E95C0", "#2F5F8A"]
GROUPED_BAR_DEMO_PALETTE = ["#D7E8E2", "#A9CFC1", "#73B49B", "#3F8E74"]
STACKED_BAR_DEMO_PALETTE = ["#4E79A7", "#A0CBE8", "#59A14F", "#F28E2B", "#E15759"]


def make_line_ci_demo() -> tuple[np.ndarray, np.ndarray, list[str]]:
    x_vals = np.linspace(0.0, 12.0, 18)
    base = np.stack(
        [
            0.92 + 0.028 * x_vals + 0.05 * np.sin(x_vals / 2.8),
            1.06 + 0.02 * x_vals + 0.04 * np.cos(x_vals / 3.5 + 0.4),
        ],
        axis=0,
    )
    repeats = base[..., None] + rng.normal(loc=0.0, scale=0.025, size=(2, x_vals.size, 10))
    return x_vals, repeats, ["Cohort 1", "Cohort 2"]


def make_scatter_demo() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n_per_group = 28
    x_groups = [
        rng.normal(loc=-0.9, scale=0.28, size=n_per_group),
        rng.normal(loc=0.0, scale=0.24, size=n_per_group),
        rng.normal(loc=0.95, scale=0.26, size=n_per_group),
    ]
    y_groups = [
        0.45 * x_groups[0] + rng.normal(loc=0.35, scale=0.20, size=n_per_group),
        0.55 * x_groups[1] + rng.normal(loc=0.55, scale=0.18, size=n_per_group),
        0.50 * x_groups[2] + rng.normal(loc=0.72, scale=0.18, size=n_per_group),
    ]
    x_vals = np.concatenate(x_groups)
    y_vals = np.concatenate(y_groups)
    labels = np.array(["Group A"] * n_per_group + ["Group B"] * n_per_group + ["Group C"] * n_per_group)
    return x_vals, y_vals, labels


def make_heatmap_demo() -> tuple[np.ndarray, list[str]]:
    labels = [f"S{i}" for i in range(1, 7)]
    matrix = np.array(
        [
            [0.92, 0.88, 0.82, 0.28, 0.22, 0.18],
            [0.87, 0.94, 0.79, 0.30, 0.24, 0.20],
            [0.81, 0.78, 0.90, 0.34, 0.29, 0.26],
            [0.26, 0.30, 0.35, 0.86, 0.80, 0.74],
            [0.21, 0.25, 0.28, 0.79, 0.91, 0.85],
            [0.18, 0.20, 0.25, 0.73, 0.84, 0.93],
        ],
        dtype=float,
    )
    return matrix, labels


def make_evaluation_demo() -> tuple[list[np.ndarray], list[np.ndarray], list[str]]:
    fpr = [
        np.array([0.0, 0.03, 0.08, 0.16, 0.28, 0.45, 1.0]),
        np.array([0.0, 0.05, 0.11, 0.22, 0.36, 0.55, 1.0]),
    ]
    tpr = [
        np.array([0.0, 0.42, 0.67, 0.81, 0.90, 0.95, 1.0]),
        np.array([0.0, 0.31, 0.55, 0.73, 0.84, 0.91, 1.0]),
    ]
    return fpr, tpr, ["Model A", "Model B"]


def make_pr_demo() -> tuple[list[np.ndarray], list[np.ndarray], list[str]]:
    precision = [
        np.array([1.0, 0.96, 0.90, 0.84, 0.77, 0.69, 0.58]),
        np.array([1.0, 0.92, 0.86, 0.77, 0.68, 0.57, 0.45]),
    ]
    recall = [
        np.array([0.05, 0.18, 0.34, 0.52, 0.68, 0.84, 1.0]),
        np.array([0.05, 0.18, 0.34, 0.52, 0.68, 0.84, 1.0]),
    ]
    return precision, recall, ["Model A", "Model B"]


def make_parallel_demo() -> np.ndarray:
    cluster_a = np.column_stack(
        [
            rng.normal(0.82, 0.08, 10),
            rng.normal(0.32, 0.10, 10),
            rng.normal(0.76, 0.09, 10),
            rng.normal(0.42, 0.10, 10),
        ]
    )
    cluster_b = np.column_stack(
        [
            rng.normal(0.36, 0.10, 10),
            rng.normal(0.78, 0.08, 10),
            rng.normal(0.30, 0.10, 10),
            rng.normal(0.70, 0.09, 10),
        ]
    )
    data = np.vstack([cluster_a, cluster_b])
    return np.clip(data, 0.0, 1.0)


def make_distribution_demo() -> tuple[np.ndarray, list[str]]:
    labels = ["Ctrl", "Treatment A", "Treatment B"]
    data = np.column_stack(
        [
            rng.normal(loc=0.00, scale=0.75, size=180),
            rng.normal(loc=0.28, scale=0.62, size=180),
            np.concatenate(
                [
                    rng.normal(loc=-0.35, scale=0.40, size=90),
                    rng.normal(loc=0.55, scale=0.35, size=90),
                ]
            ),
        ]
    )
    return data, labels


def make_grouped_bar_demo() -> tuple[np.ndarray, list[str], list[str]]:
    data = np.array(
        [
            [0.82, 0.91, 0.87, 0.79],
            [0.95, 1.08, 1.01, 0.90],
            [0.88, 1.02, 0.97, 0.86],
            [0.92, 1.05, 0.99, 0.89],
        ],
        dtype=float,
    )
    return data, ["Task A", "Task B", "Task C", "Task D"], ["Baseline", "Method 1", "Method 2", "Method 3"]


def make_bar_scatter_demo() -> np.ndarray:
    means = np.array(
        [
            [0.80, 1.00, 0.82, 0.78],
            [0.90, 1.12, 0.90, 0.90],
            [0.85, 1.06, 0.86, 0.86],
            [0.88, 1.10, 0.90, 0.87],
        ],
        dtype=float,
    )
    data = rng.normal(loc=means[..., None], scale=0.08, size=(4, 4, 20))
    return np.clip(data, 0.0, None)


def make_stacked_bar_demo() -> tuple[np.ndarray, list[str]]:
    data = np.array(
        [
            [
                [22, 18, 26, 20, 14],
                [20, 22, 24, 18, 16],
                [18, 25, 23, 19, 15],
                [16, 27, 22, 21, 14],
            ],
            [
                [15, 20, 28, 23, 14],
                [14, 18, 30, 24, 14],
                [16, 19, 27, 23, 15],
                [15, 17, 29, 24, 15],
            ],
            [
                [12, 16, 25, 29, 18],
                [11, 18, 24, 30, 17],
                [13, 17, 23, 29, 18],
                [12, 16, 22, 31, 19],
            ],
        ],
        dtype=float,
    )
    return data, ["Batch 1", "Batch 2", "Batch 3"]


def make_density_demo() -> np.ndarray:
    return rng.normal(loc=0.2, scale=0.72, size=500)


def make_ridgeline_demo() -> tuple[list[np.ndarray], list[str]]:
    labels = ["State 1", "State 2", "State 3", "State 4"]
    series = [
        rng.normal(loc=-0.2, scale=0.55, size=220),
        np.concatenate([rng.normal(loc=0.6, scale=0.45, size=150), rng.normal(loc=1.6, scale=0.30, size=70)]),
        rng.normal(loc=1.7, scale=0.58, size=220),
        np.concatenate([rng.normal(loc=2.4, scale=0.40, size=110), rng.normal(loc=3.2, scale=0.46, size=110)]),
    ]
    return series, labels


def save(fig, name: str) -> None:
    for suffix in (*VECTOR_FORMATS, *RASTER_FORMATS):
        pf.save_figure(
            fig,
            (OUT / name).with_suffix(f".{suffix}"),
            spec="nature",
            width="single",
            aspect_ratio=0.75,
            raster_dpi=600,
            trim=True,
        )
    try:
        import matplotlib.pyplot as plt

        plt.close(fig)
    except Exception:
        pass
    print(f"  ✓ {name}")  # noqa: T201 - example script


def save_square(fig, name: str) -> None:
    for suffix in (*VECTOR_FORMATS, *RASTER_FORMATS):
        pf.save_figure(
            fig,
            (OUT / name).with_suffix(f".{suffix}"),
            spec="nature",
            width="single",
            aspect_ratio=1.0,
            raster_dpi=600,
            trim=True,
        )
    try:
        import matplotlib.pyplot as plt

        plt.close(fig)
    except Exception:
        pass
    print(f"  ✓ {name}")  # noqa: T201 - example script

print("=== Bar plots ===")
grouped_bar_data, grouped_bar_categories, grouped_bar_series = make_grouped_bar_demo()
stacked_bar_data, stacked_bar_groups = make_stacked_bar_demo()
save(
    pf.bar(
        np.array([3, 7, 5, 9]),
        category_names=["A", "B", "C", "D"],
        title="Bar",
        color_palette=BAR_DEMO_PALETTE,
    ),
    "01_bar",
)
save(
    pf.bar(
        grouped_bar_data,
        category_names=grouped_bar_categories,
        series_names=grouped_bar_series,
        title="Grouped Bar",
        color_palette=GROUPED_BAR_DEMO_PALETTE,
    ),
    "02_bar_grouped",
)
save(
    pf.bar_scatter(
        make_bar_scatter_demo(),
        category_names=["Cond A", "Cond B", "Cond C", "Cond D"],
        series_names=["Ctrl", "Treat", "Var1", "Var2"],
        title="Bar + Scatter",
        color_palette=pf.get_palette("orange_red"),
        show_statistics=True,
        random_seed=0,
    ),
    "03_bar_scatter",
)
save(
    pf.stacked_bar(
        stacked_bar_data,
        group_names=stacked_bar_groups,
        title="Stacked Bar",
        color_palette=STACKED_BAR_DEMO_PALETTE,
    ),
    "03_stacked_bar",
)

print("=== Distribution plots ===")
dist_data, dist_labels = make_distribution_demo()
ridgeline_data, ridgeline_labels = make_ridgeline_demo()
save(pf.box(dist_data, category_names=dist_labels, title="Box"), "04_box")
save(pf.violin(dist_data, category_names=dist_labels, title="Violin"), "05_violin")
save(pf.density(make_density_demo(), title="Density"), "06_density")
save(pf.histogram(make_density_demo(), show_kde=True, title="Histogram"), "07_histogram")
ecdf_values, ecdf_names = make_ecdf_showcase()
save(pf.ecdf(ecdf_values, series_names=ecdf_names, x_label="Held-out AUROC", title="ECDF"), "07b_ecdf")
save(pf.qq(make_qq_showcase(), title="QQ Plot"), "07c_qq")
save(pf.strip(dist_data, category_names=dist_labels, title="Strip"), "08_strip")
save(
    pf.raincloud(
        dist_data,
        category_names=dist_labels,
        title="Raincloud",
        color_palette=["#9AB7A5", "#8FAFD2", "#C49AA0"],
        show_full_box=False,
        show_x_grid=False,
        show_y_grid=False,
    ),
    "08b_raincloud",
)
save(pf.ridgeline(ridgeline_data, category_names=ridgeline_labels, title="Ridgeline"), "09_ridgeline")

print("=== Line plots ===")
x_line, y_line, line_names = make_line_demo()
x_ci, y_ci, ci_names = make_line_ci_demo()
save(pf.line(y_line, x=x_line, series_names=line_names, title="Line"), "10_line")
save(pf.line(y_ci, x=x_ci, ci=0.95, series_names=ci_names, title="Line with CI"), "11_line_ci")
save(pf.area(rng.random((20, 3)), series_names=["A", "B", "C"], title="Stacked Area"), "12_area")

print("=== Scatter plots ===")
x_scatter, y_scatter, scatter_labels = make_scatter_demo()
save(pf.scatter(x_scatter, y_scatter, labels=scatter_labels, title="Scatter"), "13_scatter")
save(pf.bubble(rng.normal(size=30), rng.normal(size=30),
               np.abs(rng.normal(size=30)) * 20 + 5, title="Bubble"), "14_bubble")
save(pf.contour2d(rng.normal(size=500), rng.normal(size=500), title="Contour 2D"), "15_contour2d")
hexbin_x, hexbin_y = make_hexbin_showcase()
save(
    pf.hexbin(
        hexbin_x,
        hexbin_y,
        gridsize=32,
        log_color_scale=True,
        show_y_equal_x=True,
        x_label="Baseline biomarker score",
        y_label="Follow-up biomarker score",
        title="Hexbin",
    ),
    "15b_hexbin",
)
ba_reference, ba_candidate = make_bland_altman_showcase()
save(
    pf.bland_altman(
        ba_reference,
        ba_candidate,
        x_label="Mean resting heart rate",
        y_label="Candidate - reference",
        title="Bland–Altman",
    ),
    "15c_bland_altman",
)
save(pf.paired(np.array([1, 2, 3, 4]), np.array([1.5, 2.8, 2.9, 4.5]), title="Paired"), "16_paired")
grouped_scatter_data, grouped_scatter_categories, grouped_scatter_groups, grouped_scatter_top = make_grouped_scatter_showcase()
save(
    pf.grouped_scatter(
        grouped_scatter_data,
        category_names=grouped_scatter_categories,
        group_names=grouped_scatter_groups,
        y_label="Macro-AUC",
        point_size=2.3,
        jitter=0.0,
        summary_line_width=0.9,
        top_annotations=None,
        category_spacing=2.4,
        grouped_total_span=1.6,
        show_statistics=False,
        statistics_pairs=[(0, 3)],
        width=1500,
        height=420,
        title=None,
    ),
    "16d_grouped_scatter",
)
donut_values, donut_labels, donut_center = make_donut_showcase()
save(
    pf.donut(
        donut_values,
        labels=donut_labels,
        center_text=donut_center,
        colors=["#D7E1DB", "#F6D7C6", "#F6BFCF", "#F1A8B7"],
        title="Donut",
    ),
    "16e_donut",
)
radial_values, radial_subgroups, radial_group_map, radial_groups, radial_center = make_radial_hierarchy_showcase()
save_square(
    pf.radial_hierarchy(
        radial_values,
        subgroup_labels=radial_subgroups,
        subgroup_groups=radial_group_map,
        group_labels=radial_groups,
        center_text=radial_center,
        group_colors=["#C97F70", "#D79B78", "#E7C28A", "#94AEBF", "#6F8FA6", "#617A8C"],
        center_text_font_size=9,
        group_label_font_size=4,
        subgroup_label_font_size=4,
        value_label_font_size=5,
        group_gap_degrees=3.4,
        outer_label_radius_offset=0.08,
        outer_value_radius_offset=0.03,
        show_group_labels=True,
        show_outer_values=True,
        legend_show=False,
        title=None,
        width=900,
        height=900,
    ),
    "16g_radial_hierarchy",
)
positive_ratio, ratio_labels, ratio_groups = make_stacked_ratio_showcase()
save(
    pf.stacked_ratio_barh(
        positive_ratio,
        labels=ratio_labels,
        group_labels=ratio_groups,
        title="Stacked Ratio",
    ),
    "16f_stacked_ratio_barh",
)
upset_memberships, upset_sets = make_upset_showcase()
save(
    pf.upset(
        upset_memberships,
        set_names=upset_sets,
        title="UpSet",
    ),
    "16j_upset",
)
circular_values, circular_items, circular_groups, circular_stack_labels = make_circular_stacked_bar_showcase()
save_square(
    pf.circular_stacked_bar(
        circular_values,
        item_labels=circular_items,
        item_groups=circular_groups,
        stack_labels=circular_stack_labels,
            title=None,
        width=900,
        height=900,
    ),
    "16h_circular_stacked_bar",
)
circular_grouped_values, circular_grouped_items, circular_grouped_groups, circular_grouped_series = make_circular_grouped_bar_showcase()
save_square(
    pf.circular_grouped_bar(
        circular_grouped_values,
        item_labels=circular_grouped_items,
        item_groups=circular_grouped_groups,
        series_labels=circular_grouped_series,
        title=None,
        width=1000,
        height=1000,
    ),
    "16i_circular_grouped_bar",
)
dumbbell_start, dumbbell_end, dumbbell_labels = make_dumbbell_showcase()
save(
    pf.dumbbell(
        dumbbell_start,
        dumbbell_end,
        category_names=dumbbell_labels,
        left_label="Baseline model",
        right_label="Fine-tuned model",
        sort_by="delta",
        sort_desc=True,
        show_delta_labels=True,
        x_label="Held-out performance",
        title="Dumbbell",
    ),
    "16b_dumbbell",
)
forest_effect, forest_ci_low, forest_ci_high, forest_labels, forest_groups, forest_summary, forest_right = make_forest_showcase()
save(
    pf.forest_plot(
        forest_effect,
        forest_ci_low,
        forest_ci_high,
        labels=forest_labels,
        group_labels=forest_groups,
        right_labels=forest_right,
        is_summary=forest_summary,
        reference=1.0,
        x_scale="log",
        x_label="Odds ratio",
        title="Forest Plot",
    ),
    "16c_forest_plot",
)

print("=== Radar ===")
save(pf.radar(
    [
        [0.82, 0.74, 0.88, 0.79, 0.84, 0.68, 0.77, 0.71, 0.73, 0.86],
        [0.66, 0.89, 0.72, 0.83, 0.69, 0.76, 0.81, 0.63, 0.78, 0.74],
        [0.74, 0.68, 0.79, 0.71, 0.90, 0.72, 0.84, 0.80, 0.69, 0.77],
        [0.58, 0.72, 0.67, 0.64, 0.73, 0.88, 0.70, 0.76, 0.85, 0.69],
    ],
    categories=[
        "Speed",
        "Power",
        "Accuracy",
        "Recall",
        "Stability",
        "Latency",
        "Robustness",
        "Interpretability",
        "Scalability",
        "Efficiency",
    ],
    series_names=["Model A", "Model B", "Model C", "Model D"],
    category_label_pad=1.8,
    legend_ncol=4,
    title="Radar (10 axes, 4 series)",
), "17_radar")

print("=== Heatmap plots ===")
heatmap_data, heatmap_labels = make_heatmap_demo()
save(
    pf.heatmap(
        heatmap_data,
        category_names=heatmap_labels,
        title="Heatmap",
        cell_border_line_width=0.4,
    ),
    "18_heatmap",
)
cm = np.array([[45, 5], [3, 47]])
save(pf.heatmap(cm, category_names=["Neg", "Pos"], annotate=True, colorscale="Blues", tick_rotation=0.0,
                cell_border_line_width=0.6,
                title="Confusion Matrix"), "19_confusion_matrix")
save(pf.corr_matrix(rng.normal(size=(50, 5)), title="Correlation Matrix"), "20_corr_matrix")
save(pf.clustermap(rng.random((10, 8)), title="Clustermap"), "21_clustermap")

print("=== Evaluation plots ===")
fpr, tpr, eval_names = make_evaluation_demo()
save(pf.roc(fpr, tpr, series_names=eval_names, title="ROC Curve"), "24_roc")
cal_y_true, cal_y_prob, cal_names = make_calibration_showcase()
save(
    pf.calibration(
        cal_y_true,
        cal_y_prob,
        series_names=cal_names,
        title="Calibration",
    ),
    "24b_calibration",
)
prec, rec, pr_names = make_pr_demo()
save(pf.pr_curve(prec, rec, series_names=pr_names, title="PR Curve"), "25_pr_curve")
volcano_fc, volcano_p, volcano_labels = make_volcano_showcase()
save(
    pf.volcano(
        volcano_fc,
        volcano_p,
        labels=volcano_labels,
        fc_threshold=1.0,
        p_threshold=0.05,
        label_top_n=8,
        label_fc_min=1.4,
        title="Volcano",
    ),
    "25b_volcano",
)

print("=== Flow plots ===")
save(
    pf.sankey(
        [0, 0, 1, 1, 2, 3],
        [2, 3, 2, 3, 4, 5],
        [10, 5, 8, 3, 12, 11],
        node_names=["Input A", "Input B", "Path 1", "Path 2", "Outcome +", "Outcome -"],
        title="Sankey",
    ),
    "26_sankey",
)
save(pf.parallel_coordinates(make_parallel_demo(),
                             variable_names=["W", "X", "Y", "Z"], color_col=0,
                             title="Parallel Coordinates"), "27_parallel_coords")
build_gallery_contact_sheet(
    output_dir=OUT,
    contact_sheet_path=CONTACT_SHEET,
    hero_path=GALLERY_HERO,
)
for exported_name, target_path in FEATURED_EXPORTS.items():
    shutil.copy2(OUT / exported_name, target_path)
    print(f"  ✓ {target_path.relative_to(ROOT)}")  # noqa: T201 - example script
print(f"  ✓ {CONTACT_SHEET.relative_to(ROOT)}")  # noqa: T201 - example script
print(f"  ✓ {GALLERY_HERO.relative_to(ROOT)}")  # noqa: T201 - example script

print("\n=== All done! ===")
