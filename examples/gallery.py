"""Gallery demo of all pubfig plot types."""

import numpy as np
import pubfig as pf

pf.set_default_theme("nature")
rng = np.random.default_rng(7)


def make_line_demo() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_vals = np.linspace(0.0, 12.0, 16)
    series = np.column_stack(
        [
            0.78 + 0.035 * x_vals + 0.08 * np.sin(x_vals / 3.0),
            0.98 + 0.025 * x_vals + 0.06 * np.cos(x_vals / 4.2 + 0.3),
            1.12 + 0.018 * x_vals + 0.05 * np.sin(x_vals / 2.7 + 0.6),
            0.88 + 0.03 * x_vals + 0.045 * np.cos(x_vals / 3.1 + 1.1),
        ]
    )
    return x_vals, series, np.array(["Square", "Circle", "Diamond", "Triangle"])


BAR_DEMO_PALETTE = ["#C7DCEF", "#92B9D9", "#5E95C0", "#2F5F8A"]
GROUPED_BAR_DEMO_PALETTE = ["#D7E8E2", "#A9CFC1", "#73B49B", "#3F8E74"]
STACKED_BAR_DEMO_PALETTE = ["#4E79A7", "#A0CBE8", "#59A14F", "#F28E2B", "#E15759"]


def make_line_ci_demo() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    x_vals = np.linspace(0.0, 12.0, 18)
    base = np.stack(
        [
            0.92 + 0.028 * x_vals + 0.05 * np.sin(x_vals / 2.8),
            1.06 + 0.02 * x_vals + 0.04 * np.cos(x_vals / 3.5 + 0.4),
        ],
        axis=0,
    )
    repeats = base[..., None] + rng.normal(loc=0.0, scale=0.025, size=(2, x_vals.size, 10))
    return x_vals, repeats, np.array(["Cohort 1", "Cohort 2"])


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

# Bar charts
grouped_bar_data, grouped_bar_categories, grouped_bar_series = make_grouped_bar_demo()
stacked_bar_data, stacked_bar_groups = make_stacked_bar_demo()

fig = pf.bar(
    np.array([3, 7, 5, 9]),
    category_names=["A", "B", "C", "D"],
    title="Bar",
    color_palette=BAR_DEMO_PALETTE,
)
fig.show()

fig = pf.bar(
    grouped_bar_data,
    category_names=grouped_bar_categories,
    series_names=grouped_bar_series,
    title="Grouped Bar",
    color_palette=GROUPED_BAR_DEMO_PALETTE,
)
fig.show()

fig = pf.bar_scatter(
    make_bar_scatter_demo(),
    category_names=["Cond A", "Cond B", "Cond C", "Cond D"],
    series_names=["Ctrl", "Treat", "Var1", "Var2"],
    title="Bar + Scatter",
    color_palette=pf.get_palette("orange_red"),
    show_statistics=True,
    random_seed=0,
)
fig.show()

fig = pf.stacked_bar(
    stacked_bar_data,
    group_names=stacked_bar_groups,
    title="Stacked Bar",
    color_palette=STACKED_BAR_DEMO_PALETTE,
)
fig.show()

# Distribution
dist_data, dist_labels = make_distribution_demo()
ridgeline_data, ridgeline_labels = make_ridgeline_demo()
fig = pf.box(dist_data, category_names=dist_labels, title="Box")
fig.show()

fig = pf.violin(dist_data, category_names=dist_labels, title="Violin")
fig.show()

fig = pf.density(make_density_demo(), title="Density")
fig.show()

fig = pf.histogram(make_density_demo(), show_kde=True, title="Histogram")
fig.show()

fig = pf.strip(dist_data, category_names=dist_labels, title="Strip")
fig.show()

fig = pf.raincloud(
    dist_data,
    category_names=dist_labels,
    title="Raincloud",
    color_palette=["#9AB7A5", "#8FAFD2", "#C49AA0"],
    show_full_box=False,
    show_x_grid=False,
    show_y_grid=False,
)
fig.show()

fig = pf.ridgeline(ridgeline_data, category_names=ridgeline_labels, title="Ridgeline")
fig.show()

# Line
x_line, y_line, line_names = make_line_demo()
fig = pf.line(x=x_line, data=y_line, series_names=line_names.tolist(), title="Line")
fig.show()

# Line with CI bands (3D data)
x_ci, y_ci, ci_names = make_line_ci_demo()
fig = pf.line(x=x_ci, data=y_ci, ci=0.95, series_names=ci_names.tolist(), title="Line with CI")
fig.show()

# Scatter
x_scatter, y_scatter, scatter_labels = make_scatter_demo()
fig = pf.scatter(x_scatter, y_scatter, labels=scatter_labels, title="Scatter")
fig.show()

fig = pf.paired(np.array([1, 2, 3, 4]), np.array([1.5, 2.8, 2.9, 4.5]), title="Paired")
fig.show()

# Heatmap
heatmap_data, heatmap_labels = make_heatmap_demo()
fig = pf.heatmap(heatmap_data, category_names=heatmap_labels, title="Heatmap", cell_border_line_width=0.4)
fig.show()

# Confusion matrix via heatmap
cm = np.array([[45, 5], [3, 47]])
fig = pf.heatmap(cm, category_names=["Neg", "Pos"], annotate=True, colorscale="Blues", tick_rotation=0.0,
                 cell_border_line_width=0.6,
                 title="Confusion Matrix")
fig.show()

# Radar
fig = pf.radar(
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
    title="Radar (10 axes, 4 series)",
)
fig.show()

# Area chart
fig = pf.area(rng.random((20, 3)), series_names=["A", "B", "C"], title="Stacked Area")
fig.show()

# Bubble chart
fig = pf.bubble(rng.normal(size=30), rng.normal(size=30),
                np.abs(rng.normal(size=30)) * 20 + 5, title="Bubble")
fig.show()

# Correlation matrix
fig = pf.corr_matrix(rng.normal(size=(50, 5)), title="Correlation Matrix")
fig.show()

# Clustermap
fig = pf.clustermap(rng.random((10, 8)), title="Clustermap")
fig.show()

# ROC curve
fpr, tpr, eval_names = make_evaluation_demo()
fig = pf.roc(fpr, tpr, series_names=eval_names, title="ROC Curve")
fig.show()

# Precision-Recall curve
prec, rec, pr_names = make_pr_demo()
fig = pf.pr_curve(prec, rec, series_names=pr_names, title="PR Curve")
fig.show()

# Sankey diagram
fig = pf.sankey(
    [0, 0, 1, 1, 2, 3],
    [2, 3, 2, 3, 4, 5],
    [10, 5, 8, 3, 12, 11],
    node_names=["Input A", "Input B", "Path 1", "Path 2", "Outcome +", "Outcome -"],
    title="Sankey",
)
fig.show()

# Parallel coordinates
fig = pf.parallel_coordinates(make_parallel_demo(),
                              variable_names=["W", "X", "Y", "Z"], color_col=0,
                              title="Parallel Coordinates")
fig.show()

print("Gallery complete!")
