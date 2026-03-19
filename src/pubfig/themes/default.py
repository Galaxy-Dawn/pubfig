"""Default publication theme."""

from .base import AxisStyle, Theme

DEFAULT_THEME = Theme(
    name="default",
    font_family="Arial",
    font_size=7,
    title_font_size=8,
    legend_font_size=6,
    axis=AxisStyle(
        label_font_size=7,
        tick_font_size=6,
        line_width=0.8,
        tick_direction="out",
        tick_length=2.5,
        tick_width=0.8,
    ),
)
