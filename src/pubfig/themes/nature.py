"""Nature-style theme (Matplotlib)."""

from .base import AxisStyle, Theme

NATURE_THEME = Theme(
    name="nature",
    font_family=["Helvetica", "Arial", "sans-serif"],
    # Tuned for single-column export (~89 mm wide) with a compact Nature-like hierarchy.
    font_size=7,
    title_font_size=8,
    legend_font_size=6,
    background_color="#FFFFFF",
    axis=AxisStyle(
        label_font_size=7,
        tick_font_size=6,
        line_width=0.6,
        show_grid=False,
        tick_direction="out",
        tick_length=2.5,
        tick_width=0.6,
    ),
    rc_overrides={
        "axes.titleweight": "semibold",
        "legend.labelcolor": "linecolor",
    },
)
