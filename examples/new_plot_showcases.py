"""Shared showcase datasets for newer publication-oriented plot families."""

from __future__ import annotations

from typing import Optional

import numpy as np


DEFAULT_SEED = 23


def _rng(seed: Optional[int] = None) -> np.random.Generator:
    return np.random.default_rng(DEFAULT_SEED if seed is None else int(seed))


def make_dumbbell_demo(seed: Optional[int] = None) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return a compact benchmark-style before/after comparison."""
    rng = _rng(seed)
    labels = [
        "AUROC",
        "AUPRC",
        "F1 score",
        "Sensitivity",
        "Specificity",
        "Calibration",
    ]
    baseline = np.array([0.84, 0.72, 0.68, 0.74, 0.88, 0.79], dtype=float)
    gains = np.array([0.038, 0.061, 0.052, 0.044, 0.019, 0.047], dtype=float)
    updated = baseline + gains + rng.normal(0.0, 0.0045, size=baseline.size)
    updated = np.clip(updated, 0.0, 0.99)
    return baseline, updated, labels


def make_ecdf_demo(seed: Optional[int] = None) -> tuple[list[np.ndarray], list[str]]:
    """Return three shifted distributions for ECDF comparison."""
    rng = _rng(seed)
    labels = ["Baseline", "Fine-tuned", "Ensemble"]
    series = [
        rng.normal(loc=0.78, scale=0.11, size=160),
        rng.normal(loc=0.85, scale=0.09, size=160),
        np.concatenate(
            [
                rng.normal(loc=0.90, scale=0.06, size=110),
                rng.normal(loc=0.78, scale=0.05, size=50),
            ]
        ),
    ]
    return [np.clip(values, 0.35, 1.15) for values in series], labels


def make_qq_demo(seed: Optional[int] = None) -> np.ndarray:
    """Return a mildly heavy-tailed sample for QQ diagnostics."""
    rng = _rng(seed)
    core = rng.normal(loc=0.0, scale=1.0, size=220)
    tails = rng.normal(loc=0.0, scale=2.2, size=28)
    return np.concatenate([core, tails])


def make_bland_altman_demo(seed: Optional[int] = None) -> tuple[np.ndarray, np.ndarray]:
    """Return paired measurements with a small positive bias."""
    rng = _rng(seed)
    reference = rng.normal(loc=72.0, scale=8.0, size=56)
    candidate = reference + 1.6 + rng.normal(loc=0.0, scale=3.4, size=reference.size)
    return reference, candidate


def make_calibration_demo(seed: Optional[int] = None) -> tuple[np.ndarray, list[np.ndarray], list[str]]:
    """Return three probability models with distinct calibration patterns."""
    rng = _rng(seed)
    latent = rng.normal(loc=0.0, scale=1.1, size=420)
    true_prob = 1.0 / (1.0 + np.exp(-latent))
    y_true = rng.binomial(1, true_prob, size=true_prob.size).astype(int)

    calibrated = np.clip(true_prob + rng.normal(0.0, 0.035, size=true_prob.size), 0.001, 0.999)
    overconfident = np.clip(true_prob ** 0.72 + rng.normal(0.0, 0.03, size=true_prob.size), 0.001, 0.999)
    underconfident = np.clip(0.58 * true_prob + 0.20 + rng.normal(0.0, 0.03, size=true_prob.size), 0.001, 0.999)

    names = ["Calibrated", "Over-confident", "Under-confident"]
    return y_true, [calibrated, overconfident, underconfident], names


def make_upset_demo() -> tuple[list[list[str]], list[str]]:
    """Return a compact, publication-style set-overlap example."""
    set_names = ["Imaging", "Clinical", "Genomics", "Pathology"]
    pattern_counts = {
        ("Imaging", "Clinical"): 18,
        ("Imaging", "Genomics"): 12,
        ("Clinical", "Genomics"): 10,
        ("Clinical", "Pathology"): 8,
        ("Imaging", "Clinical", "Genomics"): 9,
        ("Imaging", "Pathology"): 7,
        ("Genomics", "Pathology"): 6,
        ("Imaging",): 11,
        ("Clinical",): 13,
        ("Genomics",): 9,
        ("Pathology",): 5,
    }
    memberships: list[list[str]] = []
    for pattern, count in pattern_counts.items():
        memberships.extend([list(pattern)] * int(count))
    return memberships, set_names


def make_forest_demo(
    seed: Optional[int] = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str], list[str], list[bool], list[str]]:
    """Return subgroup odds ratios with one summary row per section."""
    rng = _rng(seed)
    labels = [
        "Age > 65",
        "Male sex",
        "Hypertension",
        "Prior stroke",
        "Current smoker",
        "Overall cohort",
    ]
    groups = [
        "Demographics",
        "Demographics",
        "Clinical history",
        "Clinical history",
        "Lifestyle",
        "Summary",
    ]
    effect = np.array([1.24, 0.93, 1.41, 1.58, 1.19, 1.27], dtype=float)
    half_width = np.array([0.16, 0.11, 0.19, 0.24, 0.15, 0.10], dtype=float)
    jitter = rng.normal(0.0, 0.01, size=effect.size)
    effect = np.clip(effect + jitter, 0.2, None)
    ci_low = effect - half_width
    ci_high = effect + half_width
    ci_low[-1] = effect[-1] - 0.08
    ci_high[-1] = effect[-1] + 0.08
    is_summary = [False, False, False, False, False, True]
    right_labels = [
        "1.24 [1.08, 1.40]",
        "0.93 [0.82, 1.04]",
        "1.41 [1.22, 1.60]",
        "1.58 [1.34, 1.82]",
        "1.19 [1.04, 1.34]",
        "1.27 [1.19, 1.35]",
    ]
    return effect, ci_low, ci_high, labels, groups, is_summary, right_labels


def make_hexbin_demo(seed: Optional[int] = None) -> tuple[np.ndarray, np.ndarray]:
    """Return a dense two-population correlated cloud for hexbin showcases."""
    rng = _rng(seed)
    n1, n2 = 3400, 2200
    x1 = rng.normal(loc=5.2, scale=1.2, size=n1)
    y1 = 0.82 * x1 + rng.normal(loc=0.8, scale=0.9, size=n1)
    x2 = rng.normal(loc=8.3, scale=0.95, size=n2)
    y2 = 0.92 * x2 + rng.normal(loc=-0.1, scale=0.65, size=n2)
    x = np.concatenate([x1, x2])
    y = np.concatenate([y1, y2])
    return x, y


def make_volcano_demo(seed: Optional[int] = None) -> tuple[np.ndarray, np.ndarray, list[str]]:
    """Return a structured volcano dataset with realistic top-hit labels."""
    rng = _rng(seed)
    n = 420
    log2_fc = rng.normal(loc=0.0, scale=0.78, size=n)
    signal = np.abs(log2_fc) * 2.5 + rng.gamma(shape=1.8, scale=0.7, size=n)
    neglog10_p = np.clip(signal, 0.02, 8.5)
    pvals = np.clip(10 ** (-neglog10_p), 1e-9, 1.0)

    top_up = {
        8: (2.45, 7.9, "CXCL10"),
        27: (2.10, 7.4, "IL6"),
        66: (1.86, 6.8, "STAT1"),
        94: (2.62, 7.1, "ISG15"),
    }
    top_down = {
        131: (-2.15, 7.6, "PPARG"),
        184: (-1.92, 6.9, "GATA3"),
        245: (-2.38, 7.3, "KLF4"),
        311: (-1.74, 6.4, "FOXA1"),
    }
    labels = [f"Gene {i + 1}" for i in range(n)]
    for idx, (fc, nl10p, name) in {**top_up, **top_down}.items():
        log2_fc[idx] = fc
        pvals[idx] = 10 ** (-nl10p)
        labels[idx] = name

    return log2_fc, pvals, labels


def make_donut_demo() -> tuple[np.ndarray, list[str], str]:
    """Return a task-split donut chart demo."""
    values = np.array([48, 27, 14, 8], dtype=float)
    labels = ["Held-out", "External", "Independent", "Zero-shot"]
    center_text = "97\ntasks"
    return values, labels, center_text


def make_grouped_scatter_demo(seed: Optional[int] = None) -> tuple[np.ndarray, list[str], list[str], list[list[str]]]:
    """Return a benchmark-style grouped scatter demo with top metrics."""
    rng = _rng(seed)
    category_names = ["Overall", "Independent", "External"]
    group_names = ["R50", "PLIP", "CONCH", "mSTAR"]
    means = np.array(
        [
            [0.727, 0.790, 0.823, 0.845],
            [0.831, 0.866, 0.902, 0.911],
            [0.599, 0.692, 0.735, 0.756],
        ],
        dtype=float,
    )
    spreads = np.array(
        [
            [0.030, 0.028, 0.024, 0.020],
            [0.050, 0.045, 0.035, 0.030],
            [0.065, 0.060, 0.050, 0.045],
        ],
        dtype=float,
    )
    data = rng.normal(loc=means[..., None], scale=spreads[..., None], size=(3, 4, 14))
    data = np.clip(data, 0.35, 0.99)
    top_annotations = [[f"{value:.2f}" for value in row] for row in means]
    return data, category_names, group_names, top_annotations


def make_stacked_ratio_demo() -> tuple[np.ndarray, list[str], list[str]]:
    """Return a mutation-ratio style horizontal stacked bar demo."""
    positive = np.array([30, 33, 30, 33, 36, 40, 65, 43, 52, 53, 22, 51], dtype=float)
    labels = [
        "CPTAC_LUAD_EGFR",
        "CPTAC_LUAD_KRAS",
        "CPTAC_BRCA_TTN",
        "CPTAC_BRCA_TP53",
        "CPTAC_BRCA_PIK3CA",
        "UCEC_TTN",
        "UCEC_PTEN",
        "UCEC_ARID1A",
        "SKCM_DNAH5",
        "SKCM_BRAF",
        "NSCLC_TMB",
        "LUSC_TP53",
    ]
    groups = [
        "CPTAC LUAD",
        "CPTAC LUAD",
        "CPTAC BRCA",
        "CPTAC BRCA",
        "CPTAC BRCA",
        "UCEC",
        "UCEC",
        "UCEC",
        "SKCM",
        "SKCM",
        "NSCLC",
        "NSCLC",
    ]
    return positive, labels, groups


def make_radial_hierarchy_demo() -> tuple[np.ndarray, list[str], list[str], list[str], str]:
    """Return a cancer-burden style radial hierarchy demo."""
    group_labels = [
        "Digestive",
        "Thoracic",
        "Hormone / gyn",
        "Urogenital",
        "Hematologic",
        "CNS / skin",
    ]
    subgroup_labels = [
        "LIHC",
        "CRC",
        "GAST",
        "PAAD",
        "LUAD",
        "ESCA",
        "BRCA",
        "OV",
        "UCEC",
        "PRAD",
        "BLCA",
        "KIRC",
        "LYM",
        "LEUK",
        "MM",
        "GLI",
        "MEL",
    ]
    subgroup_groups = [
        "Digestive",
        "Digestive",
        "Digestive",
        "Digestive",
        "Thoracic",
        "Thoracic",
        "Hormone / gyn",
        "Hormone / gyn",
        "Hormone / gyn",
        "Urogenital",
        "Urogenital",
        "Urogenital",
        "Hematologic",
        "Hematologic",
        "Hematologic",
        "CNS / skin",
        "CNS / skin",
    ]
    values = np.array([24, 18, 15, 11, 28, 10, 26, 12, 9, 19, 13, 10, 16, 14, 8, 9, 12], dtype=float)
    center_text = "6 systems\n17 tumor classes\n254 cohorts"
    return values, subgroup_labels, subgroup_groups, group_labels, center_text


def make_circular_stacked_bar_demo() -> tuple[np.ndarray, list[str], list[str], list[str]]:
    """Return a dense proteomics-style circular stacked bar demo."""
    item_groups = (
        ["Thor"] * 6
        + ["GI"] * 6
        + ["Br-gyn"] * 6
        + ["GU-skin"] * 6
    )
    item_labels = [
        "LUAD",
        "LUSC",
        "SCLC",
        "MESO",
        "THYM",
        "ESCA",
        "COAD",
        "READ",
        "PAAD",
        "LIHC",
        "STAD",
        "CHOL",
        "BRCA",
        "OV",
        "UCEC",
        "CESC",
        "UCS",
        "CERV",
        "PRAD",
        "BLCA",
        "KIRC",
        "KIRP",
        "SKCM",
        "HNSC",
    ]
    values = np.array(
        [
            [9, 11, 7, 4],
            [8, 10, 8, 4],
            [7, 9, 7, 3],
            [6, 8, 6, 3],
            [7, 8, 6, 2],
            [8, 9, 7, 3],
            [10, 12, 8, 4],
            [9, 11, 7, 4],
            [8, 10, 8, 5],
            [9, 10, 6, 3],
            [8, 9, 7, 3],
            [6, 7, 5, 2],
            [11, 12, 8, 4],
            [9, 11, 8, 4],
            [8, 10, 7, 3],
            [7, 9, 7, 3],
            [6, 8, 6, 2],
            [7, 8, 6, 2],
            [8, 9, 8, 4],
            [7, 8, 7, 3],
            [8, 10, 7, 3],
            [7, 9, 6, 3],
            [9, 10, 8, 4],
            [8, 9, 7, 3],
        ],
        dtype=float,
    )
    stack_labels = ["1 peptide", "2–3", "4–6", "7+"]
    return values, item_labels, item_groups, stack_labels


def make_circular_grouped_bar_demo() -> tuple[np.ndarray, list[str], list[str], list[str]]:
    """Return a true grouped circular bar demo."""
    item_groups = (
        ["Thor"] * 6
        + ["GI"] * 6
        + ["Br-gyn"] * 6
        + ["GU-skin"] * 6
    )
    item_labels = [
        "LUAD",
        "LUSC",
        "SCLC",
        "MESO",
        "THYM",
        "ESCA",
        "COAD",
        "READ",
        "PAAD",
        "LIHC",
        "STAD",
        "CHOL",
        "BRCA",
        "OV",
        "UCEC",
        "CESC",
        "UCS",
        "CERV",
        "PRAD",
        "BLCA",
        "KIRC",
        "KIRP",
        "SKCM",
        "HNSC",
    ]
    values = np.array(
        [
            [11, 14, 13],
            [10, 13, 12],
            [9, 11, 10],
            [8, 10, 9],
            [7, 9, 8],
            [8, 11, 10],
            [12, 15, 14],
            [11, 14, 13],
            [10, 12, 11],
            [10, 13, 12],
            [9, 11, 10],
            [7, 9, 8],
            [13, 16, 15],
            [12, 15, 14],
            [10, 13, 12],
            [9, 11, 10],
            [8, 10, 9],
            [8, 9, 8],
            [9, 12, 11],
            [8, 10, 9],
            [10, 13, 12],
            [9, 11, 10],
            [11, 14, 13],
            [9, 12, 11],
        ],
        dtype=float,
    )
    series_labels = ["Cohort A", "Cohort B", "Cohort C"]
    return values, item_labels, item_groups, series_labels


__all__ = [
    "make_circular_grouped_bar_demo",
    "make_circular_stacked_bar_demo",
    "make_donut_demo",
    "make_dumbbell_demo",
    "make_forest_demo",
    "make_grouped_scatter_demo",
    "make_hexbin_demo",
    "make_radial_hierarchy_demo",
    "make_stacked_ratio_demo",
    "make_volcano_demo",
]
