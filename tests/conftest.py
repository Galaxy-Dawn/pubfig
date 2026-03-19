from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

import pytest


# Allow importing the package directly from src/ without requiring an editable install.
_ROOT = Path(__file__).resolve().parents[1]
_SRC = _ROOT / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Ensure a headless backend for CI / non-GUI environments.
matplotlib.use("Agg", force=True)


@pytest.fixture(autouse=True)
def _close_mpl_figures():
    """Avoid leaking Matplotlib figures across tests (reduces memory + warnings)."""
    yield
    import matplotlib.pyplot as plt

    plt.close("all")
