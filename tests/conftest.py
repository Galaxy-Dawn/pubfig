from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Callable

import matplotlib
import pytest


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

matplotlib.use("Agg", force=True)


@pytest.fixture(autouse=True)
def _close_mpl_figures():
    yield
    import matplotlib.pyplot as plt

    plt.close("all")


@pytest.fixture
def run_cli() -> Callable[..., subprocess.CompletedProcess[str]]:
    def _run(*args: str) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        existing_pythonpath = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(SRC) if not existing_pythonpath else f"{SRC}{os.pathsep}{existing_pythonpath}"
        env["MPLBACKEND"] = "Agg"
        return subprocess.run(
            [sys.executable, "-m", "pubfig.cli", *args],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    return _run


def write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
