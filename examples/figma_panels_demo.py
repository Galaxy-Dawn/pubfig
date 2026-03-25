"""Export multiple pubfig panels for a Figma-first assembly workflow."""

from __future__ import annotations

from pathlib import Path

import numpy as np

import pubfig as pf


OUTPUT_DIR = Path(__file__).resolve().parent / "figma_panels_demo_output"


def build_demo_panels() -> dict[str, object]:
    """Create a small deterministic panel set for Figma assembly demos."""
    rng = np.random.default_rng(42)
    pf.set_default_theme("nature")

    panels = {
        "a": pf.bar(
            rng.uniform(0.35, 0.85, size=4),
            category_names=["Ctrl", "Drug A", "Drug B", "Drug C"],
        ),
        "b": pf.scatter(
            rng.normal(size=60),
            rng.normal(loc=0.3, scale=0.9, size=60),
        ),
        "c": pf.line(
            rng.uniform(0.2, 0.9, size=(30, 2)),
            series_names=["Condition 1", "Condition 2"],
        ),
        "d": pf.heatmap(
            rng.uniform(0.0, 1.0, size=(4, 4)),
            category_names=["A", "B", "C", "D"],
        ),
    }
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
        width="single",
    )
    print(f"Exported {len(records)} panel assets to {OUTPUT_DIR}")
    print(f"Sync index: {OUTPUT_DIR / 'panel-index.json'}")


if __name__ == "__main__":
    main()
