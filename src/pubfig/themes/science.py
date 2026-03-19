"""Science-style theme (Matplotlib)."""

from .base import AxisStyle, Theme

SCIENCE_THEME = Theme(
    name="science",
    font_family="Helvetica",
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
