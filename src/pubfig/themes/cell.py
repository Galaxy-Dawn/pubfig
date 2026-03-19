"""Cell-style theme (Matplotlib).

Note:
    Cell Press journals vary by section/template. We default to a Nature-like
    minimal style and keep the theme name distinct so users can override it.
"""

from .base import AxisStyle, Theme

CELL_THEME = Theme(
    name="cell",
    font_family="Arial",
    font_size=7,
    title_font_size=8,
    legend_font_size=6,
    background_color="#FFFFFF",
    axis=AxisStyle(
        label_font_size=7,
        tick_font_size=6,
        line_width=0.8,
        show_grid=False,
        tick_direction="out",
        tick_length=2.5,
        tick_width=0.8,
    ),
)
