"""Helpers for building the pubfig gallery contact sheet."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from PIL import Image


_GALLERY_ROWS: tuple[tuple[str, ...], ...] = (
    ("01_bar", "02_bar_grouped", "03_bar_scatter", "03_stacked_bar"),
    ("04_box", "05_violin", "06_density", "07_histogram"),
    ("08_strip", "08b_raincloud", "09_ridgeline", "10_line"),
    ("11_line_ci", "12_area", "13_scatter", "14_bubble"),
    ("15_contour2d", "15b_hexbin", "16_paired", "16b_dumbbell"),
    ("16c_forest_plot", "16d_grouped_scatter", "16e_donut", "16f_stacked_ratio_barh"),
    ("16g_radial_hierarchy", "16h_circular_stacked_bar", "16i_circular_grouped_bar", "17_radar"),
    ("18_heatmap", "19_confusion_matrix", "20_corr_matrix", "21_clustermap"),
    ("24_roc", "25_pr_curve", "25b_volcano", "26_sankey"),
    ("27_parallel_coords",),
)

_CELL_WIDTH = 560
_CELL_HEIGHT = 430
_PADDING = 20
_BACKGROUND = (255, 255, 255)


def _render_tile(image_path: Path) -> Image.Image:
    with Image.open(image_path) as source:
        image = source.convert("RGB")

    canvas = Image.new("RGB", (_CELL_WIDTH, _CELL_HEIGHT), _BACKGROUND)
    image.thumbnail((_CELL_WIDTH, _CELL_HEIGHT), Image.Resampling.LANCZOS)
    offset_x = (_CELL_WIDTH - image.width) // 2
    offset_y = (_CELL_HEIGHT - image.height) // 2
    canvas.paste(image, (offset_x, offset_y))
    return canvas


def _load_row_tiles(output_dir: Path, row: Sequence[str]) -> list[Image.Image]:
    return [_render_tile(output_dir / f"{name}.png") for name in row]


def build_gallery_contact_sheet(
    output_dir: Path,
    contact_sheet_path: Path,
    hero_path: Path,
) -> None:
    """Build the README gallery contact sheet from exported figure PNGs."""
    rows = [_load_row_tiles(output_dir, row) for row in _GALLERY_ROWS]
    row_count = len(rows)
    col_count = max(len(row) for row in rows)

    width = (col_count * _CELL_WIDTH) + ((col_count + 1) * _PADDING)
    height = (row_count * _CELL_HEIGHT) + ((row_count + 1) * _PADDING)
    sheet = Image.new("RGB", (width, height), _BACKGROUND)

    for row_index, row_tiles in enumerate(rows):
        y_offset = _PADDING + row_index * (_CELL_HEIGHT + _PADDING)
        for col_index, tile in enumerate(row_tiles):
            x_offset = _PADDING + col_index * (_CELL_WIDTH + _PADDING)
            sheet.paste(tile, (x_offset, y_offset))

    contact_sheet_path.parent.mkdir(parents=True, exist_ok=True)
    hero_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(contact_sheet_path)
    sheet.save(hero_path)


__all__ = ["build_gallery_contact_sheet"]
