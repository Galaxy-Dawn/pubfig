from __future__ import annotations

from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from pubfig.colors import (
    DEFAULT,
    JAMA,
    LANCET,
    NATURE,
    ORANGE_RED_4,
    SCIENCE,
    PLOTLY_CARTO_PALETTES,
    PLOTLY_CMOCEAN_PALETTES,
    PLOTLY_COLORBREWER_PALETTES,
)

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "examples" / "palettes"


PaletteMap = dict[str, list[str]]


BUILTIN_PALETTES: PaletteMap = {
    "default": list(DEFAULT),
    "nature": list(NATURE),
    "science": list(SCIENCE),
    "lancet": list(LANCET),
    "jama": list(JAMA),
    "orange_red": list(ORANGE_RED_4),
}

FEATURED_PALETTES: PaletteMap = {
    "nature": list(NATURE),
    "science": list(SCIENCE),
    "lancet": list(LANCET),
    "jama": list(JAMA),
    "carto_blugrn": list(PLOTLY_CARTO_PALETTES["blugrn"]),
    "carto_sunsetdark": list(PLOTLY_CARTO_PALETTES["sunsetdark"]),
    "cmocean_ice": list(PLOTLY_CMOCEAN_PALETTES["ice"]),
    "colorbrewer_blues": list(PLOTLY_COLORBREWER_PALETTES["blues"]),
}


def _figure_size(num_rows: int) -> tuple[float, float]:
    return (12.0, max(2.6, 0.48 * num_rows + 1.1))


def _draw_palette_sheet(title: str, palettes: PaletteMap, output_path: Path) -> None:
    names = list(palettes)
    fig_w, fig_h = _figure_size(len(names))
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=200)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, len(names) + 1)
    ax.axis("off")

    fig.patch.set_facecolor("white")
    ax.text(
        0.02,
        len(names) + 0.55,
        title,
        fontsize=16,
        fontweight="bold",
        ha="left",
        va="center",
        family="DejaVu Sans",
    )

    label_x = 0.02
    swatch_left = 0.34
    swatch_total_width = 0.62

    for idx, name in enumerate(names):
        y = len(names) - idx - 0.15
        colors = palettes[name]
        ax.text(
            label_x,
            y + 0.12,
            name,
            fontsize=10.5,
            ha="left",
            va="center",
            family="DejaVu Sans Mono",
            color="#1B1F23",
        )
        n = len(colors)
        gap = 0.004
        width = (swatch_total_width - gap * (n - 1)) / max(1, n)
        for j, color in enumerate(colors):
            x = swatch_left + j * (width + gap)
            rect = Rectangle(
                (x, y - 0.05),
                width,
                0.36,
                facecolor=color,
                edgecolor="#D0D7DE",
                linewidth=0.35,
            )
            ax.add_patch(rect)

    fig.tight_layout(pad=0.4)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _format_palette_names(names: Iterable[str]) -> str:
    return "、".join(f"`{name}`" for name in names)


DOC_EN = ROOT / "docs" / "palette-gallery.md"
DOC_ZH = ROOT / "docs" / "palette-gallery.zh-CN.md"


def _write_docs() -> None:
    en = f"""# Palette Gallery

This page previews the palettes currently available in `pubfig`.

## Built-in Palettes

Names: {', '.join(f'`{name}`' for name in BUILTIN_PALETTES)}

![Built-in palettes](../examples/palettes/builtin-palettes.png)

## Plotly Carto Palettes

Names: {', '.join(f'`carto_{name}`' for name in PLOTLY_CARTO_PALETTES)}

![Plotly carto palettes](../examples/palettes/plotly-carto-palettes.png)

## Plotly CMOcean Palettes

Names: {', '.join(f'`cmocean_{name}`' for name in PLOTLY_CMOCEAN_PALETTES)}

![Plotly cmocean palettes](../examples/palettes/plotly-cmocean-palettes.png)

## Plotly ColorBrewer Palettes

Names: {', '.join(f'`colorbrewer_{name}`' for name in PLOTLY_COLORBREWER_PALETTES)}

![Plotly colorbrewer palettes](../examples/palettes/plotly-colorbrewer-palettes.png)

## Usage

```python
import pubfig as pf

palette = pf.get_palette("carto_blugrn")
```
"""

    zh = f"""# Palette Gallery

这个页面汇总展示 `pubfig` 当前可用的调色板预览。

## 内置调色板

名称：{_format_palette_names(BUILTIN_PALETTES)}

![内置调色板](../examples/palettes/builtin-palettes.png)

## Plotly Carto 调色板

名称：{_format_palette_names(f'carto_{name}' for name in PLOTLY_CARTO_PALETTES)}

![Plotly carto 调色板](../examples/palettes/plotly-carto-palettes.png)

## Plotly CMOcean 调色板

名称：{_format_palette_names(f'cmocean_{name}' for name in PLOTLY_CMOCEAN_PALETTES)}

![Plotly cmocean 调色板](../examples/palettes/plotly-cmocean-palettes.png)

## Plotly ColorBrewer 调色板

名称：{_format_palette_names(f'colorbrewer_{name}' for name in PLOTLY_COLORBREWER_PALETTES)}

![Plotly colorbrewer 调色板](../examples/palettes/plotly-colorbrewer-palettes.png)

## 用法

```python
import pubfig as pf

palette = pf.get_palette("carto_blugrn")
```
"""

    DOC_EN.write_text(en)
    DOC_ZH.write_text(zh)


if __name__ == "__main__":
    _draw_palette_sheet("pubfig featured palettes", FEATURED_PALETTES, OUT_DIR / "featured-palettes.png")
    _draw_palette_sheet("pubfig built-in palettes", BUILTIN_PALETTES, OUT_DIR / "builtin-palettes.png")
    _draw_palette_sheet("plotly carto palettes", PLOTLY_CARTO_PALETTES, OUT_DIR / "plotly-carto-palettes.png")
    _draw_palette_sheet("plotly cmocean palettes", PLOTLY_CMOCEAN_PALETTES, OUT_DIR / "plotly-cmocean-palettes.png")
    _draw_palette_sheet("plotly colorbrewer palettes", PLOTLY_COLORBREWER_PALETTES, OUT_DIR / "plotly-colorbrewer-palettes.png")
    _write_docs()
