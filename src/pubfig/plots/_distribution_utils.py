"""Shared helpers for distribution-style plots."""

from __future__ import annotations

import numpy as np


def normalize_features(data) -> list[np.ndarray]:
    """Normalize supported distribution inputs to a list of 1D float arrays."""
    if isinstance(data, np.ndarray):
        if data.ndim == 1:
            return [np.asarray(data, dtype=float).ravel()]
        if data.ndim == 2:
            return [np.asarray(data[:, i], dtype=float).ravel() for i in range(data.shape[1])]
        raise ValueError("Input data must be a 1D or 2D array.")
    if isinstance(data, list):
        if all(isinstance(feature, np.ndarray) and feature.ndim == 1 for feature in data):
            return [np.asarray(feature, dtype=float).ravel() for feature in data]
    raise ValueError("Input must be a list of 1D ndarrays or a 1D/2D ndarray.")
