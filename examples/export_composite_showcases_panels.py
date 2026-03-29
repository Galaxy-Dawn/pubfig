"""Export composite showcase figures as panel-first SVG directories and push them to Figma."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pubfig as pf  # noqa: E402
from export_composite_showcases import (  # noqa: E402
    ACCENT,
    MODEL_COLORS,
    bar_scatter_panel,
    heatmap_panel,
    intervention_heatmap,
    plot_embedding,
    polish_axis,
    raincloud_panel,
    rng,
    stratification_heatmap,
)

OUT = ROOT / 'temp' / 'composite_showcases_panels'
OUT.mkdir(parents=True, exist_ok=True)
pf.set_default_theme('nature')

INTERVENTION_COLORS = ['#DDEFE3', '#90C3A8', '#2F7D5C']
STRATIFICATION_COLORS = ['#EFE4FB', '#B392E0', '#6D4AA5']
BENCHMARK_COLORS = MODEL_COLORS


def _new_polar_fig(*, width: float = 3.1, height: float = 2.35) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(width, height), subplot_kw={'projection': 'polar'}, facecolor='white')
    return fig, ax


def radar_panel(
    ax: plt.Axes,
    data: list[list[float]],
    *,
    categories: list[str],
    series_names: list[str],
    palette: list[str],
) -> None:
    pf.radar(
        data,
        categories=categories,
        series_names=series_names,
        title=None,
        color_palette=palette,
        legend_show=False,
        fill_alpha=0.09,
        marker='o',
        marker_size=1.8,
        marker_edge_line_width=0.45,
        category_label_mode='horizontal',
        category_label_pad=1.8,
        radial_tick_values=[0.2, 0.4, 0.6, 0.8],
        ax=ax,
    )
    ax.tick_params(labelsize=6.2)
    ax.set_facecolor('white')


def violin_panel(
    ax: plt.Axes,
    data: list[np.ndarray],
    *,
    categories: list[str],
    xlabel: str,
    ylabel: str,
    palette: list[str],
) -> None:
    pf.violin(
        data,
        category_names=categories,
        title=None,
        color_palette=palette,
        show_box=True,
        show_points=True,
        violin_width=0.52,
        box_width=0.10,
        points_jitter=0.05,
        points_size=1.7,
        points_alpha=0.38,
        ax=ax,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    polish_axis(ax)


def histogram_panel(
    ax: plt.Axes,
    data: np.ndarray,
    *,
    xlabel: str,
    palette: list[str],
) -> None:
    pf.histogram(
        data,
        bins=18,
        show_kde=True,
        normalize=False,
        title=None,
        color_palette=palette,
        legend_show=False,
        ax=ax,
    )
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Count')
    polish_axis(ax)


def _new_panel_fig(*, width: float = 3.1, height: float = 2.35) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(width, height), facecolor='white')
    return fig, ax


def _new_wide_panel_fig(*, width: float = 6.4, height: float = 2.45) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(width, height), facecolor='white')
    return fig, ax


def build_intervention_panels() -> dict[str, plt.Figure]:
    panels: dict[str, plt.Figure] = {}
    top_weeks = [
        np.array([[0.38, 0.45, 0.52], [0.34, 0.41, 0.49], [0.36, 0.43, 0.51], [0.33, 0.40, 0.47]]),
        np.array([[0.47, 0.56, 0.67], [0.42, 0.52, 0.63], [0.45, 0.55, 0.68], [0.39, 0.50, 0.60]]),
        np.array([[0.56, 0.68, 0.82], [0.49, 0.62, 0.77], [0.54, 0.68, 0.84], [0.44, 0.58, 0.73]]),
    ]
    for key, means, label in zip(['a', 'b', 'c'], top_weeks, ['Week 2', 'Week 4', 'Week 8'], strict=True):
        fig, ax = _new_panel_fig()
        bar_scatter_panel(
            ax,
            means,
            categories=['Motor', 'Sensory', 'Language', 'Social'],
            series=['Placebo', 'Low dose', 'High dose'],
            palette=INTERVENTION_COLORS,
            xlabel=label,
            ylabel='Score' if key == 'a' else None,
            ylim=(0.26, 0.92),
            seed=10 + ord(key.upper()),
            show_stats=True,
        )
        panels[key] = fig

    fig, ax = _new_panel_fig()
    weeks = np.arange(1, 9)
    placebo = 0.32 + 0.018 * weeks + 0.012 * np.sin(weeks / 1.5)
    low = 0.34 + 0.030 * weeks + 0.014 * np.sin(weeks / 1.7 + 0.25)
    high = 0.36 + 0.047 * weeks + 0.016 * np.sin(weeks / 1.9 + 0.45)
    repeated = np.stack([placebo, low, high], axis=0)[..., None] + rng.normal(0.0, 0.024, size=(3, weeks.size, 16))
    repeated = np.clip(repeated, 0.16, 0.90)
    pf.line(
        repeated,
        x=weeks,
        series_names=['Placebo', 'Low dose', 'High dose'],
        x_label='Week',
        y_label='Network gain',
        ci=0.95,
        ci_band_alpha=0.11,
        color_palette=INTERVENTION_COLORS,
        legend_show=False,
        title=None,
        ax=ax,
    )
    polish_axis(ax)
    panels['d'] = fig

    fig, ax = _new_polar_fig()
    radar_panel(
        ax,
        [
            [0.34, 0.38, 0.42, 0.30, 0.37, 0.35],
            [0.49, 0.54, 0.57, 0.46, 0.52, 0.50],
            [0.66, 0.70, 0.76, 0.64, 0.72, 0.69],
        ],
        categories=['Motor', 'Sensory', 'Language', 'Sleep', 'Mood', 'QoL'],
        series_names=['Placebo', 'Low dose', 'High dose'],
        palette=INTERVENTION_COLORS,
    )
    panels['e'] = fig

    fig, ax = _new_panel_fig()
    violin_panel(
        ax,
        [
            rng.normal(0.18, 0.05, size=32),
            rng.normal(0.29, 0.06, size=32),
            rng.normal(0.43, 0.07, size=32),
        ],
        categories=['Placebo', 'Low', 'High'],
        xlabel='Arm',
        ylabel='Symptom drop',
        palette=INTERVENTION_COLORS,
    )
    panels['f'] = fig

    fig, ax = _new_panel_fig()
    raincloud_panel(
        ax,
        [rng.normal(0.34, 0.05, size=28), rng.normal(0.48, 0.06, size=28), rng.normal(0.64, 0.06, size=28)],
        categories=['Placebo', 'Low', 'High'],
        xlabel='Responder index',
        ylabel='Index',
        palette=INTERVENTION_COLORS,
    )
    ax.set_ylabel('Index')
    panels['g'] = fig

    fig, ax = _new_panel_fig()
    inter_a = rng.normal([1.4, 0.5, 0.8, 0.3, 0.7], 0.18, size=(22, 5))
    inter_b = rng.normal([0.8, 1.2, 0.6, 0.7, 0.5], 0.18, size=(22, 5))
    inter_c = rng.normal([0.4, 0.8, 1.3, 0.9, 1.1], 0.18, size=(22, 5))
    inter_x = np.vstack([inter_a, inter_b, inter_c])
    inter_labels = np.array(['Placebo'] * 22 + ['Low dose'] * 22 + ['High dose'] * 22)
    pf.pca_biplot(
        inter_x,
        variable_names=['IL-6', 'BDNF', 'Motor', 'Sleep', 'QoL'],
        labels=inter_labels,
        title=None,
        color_palette=INTERVENTION_COLORS,
        loading_panel='none',
        legend_show=False,
        score_marker_size=16,
        show_group_ellipse=True,
        ellipse_fill=False,
        ax=ax,
    )
    polish_axis(ax)
    panels['h'] = fig

    fig, ax = _new_wide_panel_fig(width=6.6, height=2.35)
    corr_data = np.column_stack([
        rng.normal(0.0, 1.0, size=180),
        rng.normal(0.2, 1.0, size=180),
        rng.normal(0.4, 0.9, size=180),
        rng.normal(0.1, 0.8, size=180),
        rng.normal(-0.2, 0.9, size=180),
        rng.normal(0.5, 0.7, size=180),
        rng.normal(0.0, 1.1, size=180),
        rng.normal(0.3, 0.85, size=180),
    ])
    corr_data[:, 2] = 0.62 * corr_data[:, 0] + 0.38 * corr_data[:, 1] + rng.normal(0, 0.45, size=180)
    corr_data[:, 3] = -0.58 * corr_data[:, 0] + rng.normal(0, 0.55, size=180)
    corr_data[:, 4] = 0.66 * corr_data[:, 2] + rng.normal(0, 0.40, size=180)
    corr_data[:, 5] = 0.54 * corr_data[:, 4] + 0.30 * corr_data[:, 1] + rng.normal(0, 0.35, size=180)
    corr_data[:, 6] = -0.45 * corr_data[:, 3] + 0.35 * corr_data[:, 5] + rng.normal(0, 0.45, size=180)
    corr_data[:, 7] = 0.60 * corr_data[:, 5] + rng.normal(0, 0.42, size=180)
    pf.corr_matrix(
        corr_data,
        variable_names=['IL-6', 'BDNF', 'Motor', 'Sleep', 'Mood', 'QoL', 'Fatigue', 'Adherence'],
        title=None,
        colorscale='YlGn',
        annotate=False,
        cbar=True,
        tick_rotation=40,
        ax=ax,
    )
    polish_axis(ax)
    panels['i'] = fig

    fig, ax = _new_panel_fig()
    heatmap_panel(
        ax,
        intervention_heatmap(),
        xlabels=[str(i) for i in range(1, 9)],
        ytick_positions=[3.5, 11.5, 19.5],
        ytick_labels=['High', 'Mid', 'Low'],
        xlabel='Week',
        ylabel='Participants',
        cmap='YlGn',
        separators=[7.5, 15.5],
    )
    panels['j'] = fig

    fig, ax = _new_panel_fig()
    histogram_panel(
        ax,
        rng.normal(0.54, 0.12, size=120),
        xlabel='Recovery index',
        palette=INTERVENTION_COLORS,
    )
    panels['k'] = fig

    fig, ax = _new_panel_fig()
    baseline = np.linspace(0.2, 0.9, 54)
    delta = np.clip(0.08 + 0.62 * baseline + rng.normal(0.0, 0.08, baseline.size), 0.02, 0.95)
    arm_labels = np.array(['Placebo'] * 18 + ['Low dose'] * 18 + ['High dose'] * 18)
    pf.scatter(
        baseline,
        delta,
        labels=arm_labels,
        x_label='Baseline severity',
        y_label='Week-8 gain',
        title=None,
        color_palette=INTERVENTION_COLORS,
        show_regression=True,
        legend_ncol=1,
        ax=ax,
    )
    polish_axis(ax)
    panels['l'] = fig
    return panels


def build_stratification_panels() -> dict[str, plt.Figure]:
    panels: dict[str, plt.Figure] = {}
    top = [
        np.array([[0.80, 0.58, 0.43], [0.72, 0.66, 0.54], [0.60, 0.78, 0.86], [0.76, 0.61, 0.70]]),
        np.array([[0.22, 0.36, 0.44], [0.18, 0.29, 0.38], [0.26, 0.33, 0.41], [0.20, 0.31, 0.40]]),
        np.array([[0.48, 0.36, 0.24], [0.29, 0.40, 0.32], [0.18, 0.31, 0.53], [0.26, 0.38, 0.48]]),
    ]
    for key, means, label in zip(['a', 'b', 'c'], top, ['Phenotype axis', 'Clinical burden', 'Response mix'], strict=True):
        fig, ax = _new_panel_fig()
        bar_scatter_panel(
            ax, means,
            categories=['Plastic.', 'Specific.', 'Adaptive', 'Clinical'],
            series=['State A', 'State B', 'State C'],
            palette=STRATIFICATION_COLORS,
            xlabel=label,
            ylabel='Score' if key == 'a' else None,
            ylim=(0.0, 0.94 if key == 'a' else 0.64),
            seed=40 + ord(key.upper()),
            show_stats=(key == 'a'),
        )
        panels[key] = fig

    fig, ax = _new_polar_fig()
    radar_panel(
        ax,
        [
            [0.78, 0.74, 0.66, 0.42, 0.34, 0.29],
            [0.56, 0.59, 0.61, 0.54, 0.50, 0.46],
            [0.32, 0.37, 0.44, 0.81, 0.84, 0.76],
        ],
        categories=['Inflamm.', 'Plastic.', 'Motor', 'Sleep', 'Mood', 'Social'],
        series_names=['State A', 'State B', 'State C'],
        palette=STRATIFICATION_COLORS,
    )
    panels['d'] = fig

    fig, ax = _new_panel_fig()
    visits = np.arange(1, 7)
    state_a = 0.72 - 0.035 * visits + 0.02 * np.sin(visits / 1.6)
    state_b = 0.56 - 0.012 * visits + 0.015 * np.sin(visits / 1.8 + 0.2)
    state_c = 0.42 + 0.028 * visits + 0.014 * np.sin(visits / 1.7 + 0.4)
    burden = np.stack([state_a, state_b, state_c], axis=0)[..., None] + rng.normal(0.0, 0.024, size=(3, visits.size, 18))
    burden = np.clip(burden, 0.18, 0.92)
    pf.line(
        burden,
        x=visits,
        series_names=['State A', 'State B', 'State C'],
        x_label='Visit',
        y_label='Burden',
        ci=0.95,
        ci_band_alpha=0.10,
        color_palette=STRATIFICATION_COLORS,
        legend_show=False,
        title=None,
        ax=ax,
    )
    polish_axis(ax)
    panels['e'] = fig

    fig, ax = _new_panel_fig()
    violin_panel(
        ax,
        [
            rng.normal(0.69, 0.08, size=28),
            rng.normal(0.53, 0.07, size=28),
            rng.normal(0.40, 0.06, size=28),
        ],
        categories=['State A', 'State B', 'State C'],
        xlabel='State',
        ylabel='Confidence',
        palette=STRATIFICATION_COLORS,
    )
    panels['f'] = fig

    fig, ax = _new_panel_fig()
    raincloud_panel(
        ax,
        [rng.normal(0.68, 0.08, size=24), rng.normal(0.54, 0.07, size=24), rng.normal(0.42, 0.06, size=24)],
        categories=['State A', 'State B', 'State C'],
        xlabel='Inflammation load',
        ylabel='Load',
        palette=STRATIFICATION_COLORS,
    )
    panels['g'] = fig

    fig, ax = _new_panel_fig()
    state_a_embed = rng.normal([1.2, 0.4, 0.6, 0.2, 0.5], 0.17, size=(24, 5))
    state_b_embed = rng.normal([0.6, 1.1, 0.4, 0.8, 0.4], 0.17, size=(24, 5))
    state_c_embed = rng.normal([0.2, 0.5, 1.1, 0.6, 0.9], 0.17, size=(24, 5))
    latent = np.vstack([state_a_embed, state_b_embed, state_c_embed])
    labels = np.array(['State A'] * 24 + ['State B'] * 24 + ['State C'] * 24)
    plot_embedding(ax, latent, labels, STRATIFICATION_COLORS)
    panels['h'] = fig

    fig, ax = _new_wide_panel_fig(width=6.6, height=2.35)
    strat_corr = np.column_stack([
        rng.normal(0.0, 1.0, size=180),
        rng.normal(0.2, 0.9, size=180),
        rng.normal(-0.1, 0.95, size=180),
        rng.normal(0.4, 0.8, size=180),
        rng.normal(0.3, 0.9, size=180),
        rng.normal(-0.3, 1.0, size=180),
        rng.normal(0.5, 0.75, size=180),
        rng.normal(0.1, 0.85, size=180),
    ])
    strat_corr[:, 1] = 0.68 * strat_corr[:, 0] + rng.normal(0, 0.42, size=180)
    strat_corr[:, 2] = 0.56 * strat_corr[:, 0] + 0.25 * strat_corr[:, 4] + rng.normal(0, 0.40, size=180)
    strat_corr[:, 3] = -0.62 * strat_corr[:, 5] + rng.normal(0, 0.38, size=180)
    strat_corr[:, 4] = 0.70 * strat_corr[:, 3] + rng.normal(0, 0.36, size=180)
    strat_corr[:, 6] = 0.52 * strat_corr[:, 2] + 0.33 * strat_corr[:, 4] + rng.normal(0, 0.34, size=180)
    strat_corr[:, 7] = -0.48 * strat_corr[:, 5] + 0.41 * strat_corr[:, 6] + rng.normal(0, 0.36, size=180)
    pf.corr_matrix(
        strat_corr,
        variable_names=['Inflamm.', 'Plastic.', 'Motor', 'Sleep', 'Mood', 'Social', 'Cognition', 'Anxiety'],
        title=None,
        colorscale='Purples',
        annotate=False,
        cbar=True,
        tick_rotation=40,
        ax=ax,
    )
    polish_axis(ax)
    panels['i'] = fig

    fig, ax = _new_panel_fig()
    heatmap_panel(
        ax,
        stratification_heatmap(),
        xlabels=['Inflamm.', 'Plastic.', 'Motor', 'Sleep', 'Mood', 'Social'],
        ytick_positions=[3.5, 11.5, 19.5],
        ytick_labels=['State A', 'State B', 'State C'],
        xlabel='Marker',
        ylabel='Representative subjects',
        cmap='Purples',
        separators=[7.5, 15.5],
    )
    panels['j'] = fig

    fig, ax = _new_panel_fig()
    histogram_panel(
        ax,
        rng.normal(0.0, 0.85, size=140),
        xlabel='Subtype score',
        palette=STRATIFICATION_COLORS,
    )
    panels['k'] = fig

    fig, ax = _new_panel_fig()
    pca_a = rng.normal([1.1, 0.4, 0.7, 0.3, 0.5], 0.17, size=(20, 5))
    pca_b = rng.normal([0.6, 1.0, 0.5, 0.8, 0.4], 0.17, size=(20, 5))
    pca_c = rng.normal([0.3, 0.5, 1.1, 0.6, 0.9], 0.17, size=(20, 5))
    pca_x = np.vstack([pca_a, pca_b, pca_c])
    pca_labels = np.array(['State A'] * 20 + ['State B'] * 20 + ['State C'] * 20)
    pf.pca_biplot(
        pca_x,
        variable_names=['Inflamm.', 'Plastic.', 'Motor', 'Sleep', 'Mood'],
        labels=pca_labels,
        title=None,
        color_palette=STRATIFICATION_COLORS,
        loading_panel='none',
        legend_show=False,
        score_marker_size=16,
        show_group_ellipse=True,
        ellipse_fill=False,
        ax=ax,
    )
    polish_axis(ax)
    panels['l'] = fig
    return panels


def build_benchmark_panels() -> dict[str, plt.Figure]:
    panels: dict[str, plt.Figure] = {}
    top = [
        np.array([[0.74, 0.80, 0.85], [0.69, 0.78, 0.84], [0.66, 0.75, 0.81], [0.61, 0.70, 0.78]]),
        np.array([[0.72, 0.79, 0.83], [0.67, 0.76, 0.82], [0.63, 0.72, 0.79], [0.58, 0.67, 0.74]]),
        np.array([[0.70, 0.77, 0.81], [0.64, 0.73, 0.78], [0.60, 0.69, 0.75], [0.56, 0.65, 0.72]]),
    ]
    for key, means, label in zip(['a', 'b', 'c'], top, ['Overall', 'Held-out', 'External'], strict=True):
        fig, ax = _new_panel_fig()
        bar_scatter_panel(
            ax, means,
            categories=['Accuracy', 'AUROC', 'AUPRC', 'F1'],
            series=['Baseline', 'Ablated', 'Full model'],
            palette=BENCHMARK_COLORS,
            xlabel=label,
            ylabel='Score' if key == 'a' else None,
            ylim=(0.50, 0.90),
            seed=70 + ord(key.upper()),
            show_stats=True,
        )
        panels[key] = fig

    fig, ax = _new_polar_fig()
    radar_panel(
        ax,
        [
            [0.58, 0.60, 0.43, 0.66, 0.52, 0.48],
            [0.68, 0.71, 0.55, 0.76, 0.64, 0.60],
            [0.81, 0.83, 0.72, 0.86, 0.78, 0.74],
        ],
        categories=['AUROC', 'AUPRC', 'Latency', 'Robust.', 'Transfer', 'Calib.'],
        series_names=['Baseline', 'Ablated', 'Full model'],
        palette=BENCHMARK_COLORS,
    )
    panels['d'] = fig

    fig, ax = _new_panel_fig()
    sites = np.arange(1, 6)
    baseline = 0.58 + 0.020 * sites + 0.012 * np.sin(sites / 1.6)
    ablated = 0.64 + 0.019 * sites + 0.013 * np.sin(sites / 1.7 + 0.2)
    full = 0.70 + 0.022 * sites + 0.015 * np.sin(sites / 1.8 + 0.4)
    transfer = np.stack([baseline, ablated, full], axis=0)[..., None] + rng.normal(0.0, 0.022, size=(3, sites.size, 14))
    transfer = np.clip(transfer, 0.45, 0.90)
    pf.line(
        transfer,
        x=sites,
        series_names=['Baseline', 'Ablated', 'Full model'],
        x_label='External site',
        y_label='Transfer score',
        ci=0.95,
        ci_band_alpha=0.10,
        color_palette=BENCHMARK_COLORS,
        legend_show=False,
        title=None,
        ax=ax,
    )
    polish_axis(ax)
    panels['e'] = fig

    fig, ax = _new_panel_fig()
    pf.bar(
        np.array([[22, 30, 41], [16, 24, 34], [2.6, 3.9, 5.4]]),
        category_names=['Latency', 'Memory', 'Params'],
        series_names=['Baseline', 'Ablated', 'Full model'],
        x_label='Deployment cost',
        y_label='Cost',
        title=None,
        color_palette=BENCHMARK_COLORS,
        legend_show=False,
        ax=ax,
    )
    ax.set_ylim(0.0, 46.0)
    polish_axis(ax)
    panels['f'] = fig

    fig, ax = _new_panel_fig()
    roc_x = np.linspace(0.0, 1.0, 120)
    roc_curves = [np.clip(roc_x ** 0.55, 0, 1), np.clip(roc_x ** 0.38, 0, 1), np.clip(roc_x ** 0.24, 0, 1)]
    pf.roc(roc_x, roc_curves, series_names=['Baseline', 'Ablated', 'Full model'], title=None, color_palette=BENCHMARK_COLORS, legend_show=False, ax=ax)
    polish_axis(ax)
    panels['g'] = fig

    fig, ax = _new_panel_fig()
    recall = np.linspace(0.0, 1.0, 120)
    precision = [
        0.32 + 0.68 * (1 - recall**0.62) * 0.62,
        0.40 + 0.60 * (1 - recall**0.75) * 0.74,
        0.52 + 0.48 * (1 - recall**0.88) * 0.82,
    ]
    pf.pr_curve(precision, [recall, recall, recall], series_names=['Baseline', 'Ablated', 'Full model'], title=None, color_palette=BENCHMARK_COLORS, legend_show=False, ax=ax)
    polish_axis(ax)
    panels['h'] = fig

    fig, ax = _new_panel_fig()
    base = rng.normal([1.3, 0.4, 0.6, 0.2, 0.5, 0.1], 0.16, size=(26, 6))
    ablated = rng.normal([0.9, 1.1, 0.5, 0.7, 0.6, 0.4], 0.16, size=(26, 6))
    full = rng.normal([0.4, 0.8, 1.2, 0.9, 1.0, 0.8], 0.16, size=(26, 6))
    pca_data = np.vstack([base, ablated, full])
    pca_labels = np.array(['Baseline'] * 26 + ['Ablated'] * 26 + ['Full model'] * 26)
    pf.pca_biplot(
        pca_data,
        variable_names=['AUROC', 'AUPRC', 'Latency', 'Robust.', 'Transfer', 'Calib.'],
        labels=pca_labels,
        title=None,
        color_palette=BENCHMARK_COLORS,
        loading_panel='none',
        legend_show=False,
        score_marker_size=16,
        show_group_ellipse=True,
        ellipse_fill=False,
        ax=ax,
    )
    polish_axis(ax)
    panels['i'] = fig

    fig, ax = _new_panel_fig()
    predicted = np.linspace(0.18, 0.94, 60)
    observed = np.clip(predicted + rng.normal(0.0, 0.045, 60), 0.05, 0.98)
    bins = np.array(['Fold 1'] * 20 + ['Fold 2'] * 20 + ['Fold 3'] * 20)
    pf.scatter(
        predicted,
        observed,
        labels=bins,
        x_label='Predicted probability',
        y_label='Observed frequency',
        title=None,
        color_palette=['#B4C9E4', '#92B7D8', '#648DB1'],
        show_regression=True,
        show_y_equal_x=True,
        legend_ncol=1,
        ax=ax,
    )
    polish_axis(ax)
    panels['j'] = fig

    fig, ax = _new_panel_fig()
    thresholds = np.linspace(0.15, 0.85, 11)
    operating = np.column_stack([
        0.92 - 0.22 * thresholds + 0.01 * np.sin(thresholds * 10),
        0.54 + 0.35 * thresholds - 0.02 * np.cos(thresholds * 8),
    ])
    pf.line(
        operating,
        x=thresholds,
        series_names=['Precision', 'Recall'],
        x_label='Decision threshold',
        y_label='Score',
        title=None,
        color_palette=[BENCHMARK_COLORS[2], ACCENT],
        legend_show=False,
        ax=ax,
    )
    idx = 6
    ax.axvline(thresholds[idx], color='0.72', linestyle='--', linewidth=0.8)
    ax.scatter([thresholds[idx]], [operating[idx, 0]], s=18, color=MODEL_COLORS[2], zorder=5)
    ax.scatter([thresholds[idx]], [operating[idx, 1]], s=18, color=ACCENT, zorder=5)
    polish_axis(ax)
    panels['k'] = fig

    fig, ax = _new_panel_fig()
    bench_corr = np.column_stack([
        rng.normal(0.0, 1.0, size=150),
        rng.normal(0.3, 0.8, size=150),
        rng.normal(0.1, 0.9, size=150),
        rng.normal(0.5, 0.7, size=150),
        rng.normal(-0.2, 0.9, size=150),
        rng.normal(0.2, 0.8, size=150),
    ])
    bench_corr[:, 1] = 0.62 * bench_corr[:, 0] + rng.normal(0, 0.38, size=150)
    bench_corr[:, 2] = 0.48 * bench_corr[:, 0] + 0.28 * bench_corr[:, 3] + rng.normal(0, 0.36, size=150)
    bench_corr[:, 4] = -0.56 * bench_corr[:, 2] + rng.normal(0, 0.35, size=150)
    bench_corr[:, 5] = 0.59 * bench_corr[:, 3] + 0.21 * bench_corr[:, 1] + rng.normal(0, 0.32, size=150)
    pf.corr_matrix(
        bench_corr,
        variable_names=['AUROC', 'AUPRC', 'Latency', 'Robust.', 'Transfer', 'Calib.'],
        title=None,
        colorscale='Blues',
        annotate=False,
        cbar=True,
        tick_rotation=38,
        ax=ax,
    )
    polish_axis(ax)
    panels['l'] = fig
    return panels


def export_panel_sets() -> dict[str, Path]:
    builders = {
        'intervention': build_intervention_panels,
        'stratification': build_stratification_panels,
        'benchmark': build_benchmark_panels,
    }
    labels_by_name = {
        'benchmark': list('aaabcdefghij'),
        'intervention': list('aaabcddefghi'),
        'stratification': list('aaabcddefghi'),
    }
    out_dirs: dict[str, Path] = {}
    for name, builder in builders.items():
        out_dir = OUT / name
        panels = builder()
        pf.export_panels(
            panels,
            out_dir,
            format='svg',
            index_file=True,
            overwrite=True,
            include_title=False,
            svg_fonttype='path',
            labels=labels_by_name.get(name),
        )
        for fig in panels.values():
            plt.close(fig)
        out_dirs[name] = out_dir
    return out_dirs


def push_panel_sets(panel_dirs: dict[str, Path]) -> None:
    rows = '4,4,4'
    for name, panel_dir in panel_dirs.items():
        figure_id = f'composite-showcase-{name}'
        cmd = [
            str(ROOT / '.venv' / 'bin' / 'python'),
            '-m',
            'pubfig.cli',
            'figma',
            'push',
            str(panel_dir),
            '--figure-id',
            figure_id,
            '--title',
            name,
            '--row-panel-counts',
            rows,
            '--panel-gap',
            '14',
            '--mode',
            'auto',
            '--relayout',
        ]
        print('PUSH', ' '.join(cmd))
        subprocess.run(cmd, check=True, cwd=ROOT)


def main() -> None:
    panel_dirs = export_panel_sets()
    for name, path in panel_dirs.items():
        print(f'EXPORTED {name}: {path}')
    push_panel_sets(panel_dirs)


if __name__ == '__main__':
    main()
