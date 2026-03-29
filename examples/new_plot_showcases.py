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


__all__ = [
    "make_dumbbell_demo",
    "make_forest_demo",
    "make_hexbin_demo",
    "make_volcano_demo",
]
