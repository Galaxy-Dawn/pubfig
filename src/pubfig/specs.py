"""Figure specifications and unit conversions for publication export."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, MutableMapping


@dataclass(frozen=True)
class FigureSpec:
    """Publication figure export specification.

    Notes:
        - Plot functions in pubfig accept optional `width`/`height` in *design pixels*.
          We interpret those pixels at `design_dpi` to create a Matplotlib figure size.
        - For submission export, physical sizing is defined in millimeters (mm), then
          converted to inches for Matplotlib.
    """

    name: str
    font_family: str = "Arial"
    # Design pixels per inch (used to interpret `width`/`height` arguments in plot functions).
    design_dpi: int = 96
    # Common journal column widths (approx).
    single_column_mm: float = 89.0
    double_column_mm: float = 183.0
    # Default raster export DPI for submission.
    default_raster_dpi: int = 600
    # Default export background. Transparent backgrounds are opt-in per export call.
    background_color: str = "#FFFFFF"


def mm_to_inches(mm: float) -> float:
    return float(mm) / 25.4


def inches_to_px(inches: float, dpi: float) -> int:
    return int(round(float(inches) * float(dpi)))


def mm_to_px(mm: float, dpi: float) -> int:
    return inches_to_px(mm_to_inches(mm), dpi=dpi)


def px_to_inches(px: float, dpi: float) -> float:
    """Convert pixels to inches at a given DPI."""
    if dpi <= 0:
        raise ValueError("dpi must be > 0")
    return float(px) / float(dpi)


def resolve_width_mm(width: str | float | int, *, spec: FigureSpec) -> float:
    """Resolve width in mm from preset names or numeric values."""
    if isinstance(width, (int, float)):
        return float(width)

    key = width.strip().lower()
    if key in {"single", "single-col", "single_column", "single-column"}:
        return float(spec.single_column_mm)
    if key in {"double", "double-col", "double_column", "double-column", "full"}:
        return float(spec.double_column_mm)
    if key.endswith("mm"):
        return float(key[:-2].strip())

    raise ValueError(
        f"Unsupported width '{width}'. Use 'single', 'double', or a numeric mm value (e.g. 120 or '120mm')."
    )


def resolve_height_mm(
    height_mm: float | int | None,
    *,
    width_mm: float,
    aspect_ratio: float | None,
    default_aspect_ratio: float = 0.75,
) -> float:
    """Resolve height in mm from an explicit value or aspect ratio (height / width)."""
    if height_mm is not None:
        return float(height_mm)
    ar = float(aspect_ratio) if aspect_ratio is not None else float(default_aspect_ratio)
    if ar <= 0:
        raise ValueError("aspect_ratio must be > 0")
    return float(width_mm) * ar


NATURE_FIGURE_SPEC = FigureSpec(name="nature", font_family="Arial")
SCIENCE_FIGURE_SPEC = FigureSpec(name="science", font_family="Helvetica")
CELL_FIGURE_SPEC = FigureSpec(name="cell", font_family="Arial")

_SPEC_REGISTRY: MutableMapping[str, FigureSpec] = {
    "nature": NATURE_FIGURE_SPEC,
    "science": SCIENCE_FIGURE_SPEC,
    # Cell Press journals vary by template; we default to Nature-like sizing.
    "cell": CELL_FIGURE_SPEC,
}


def get_figure_spec(name_or_spec: str | FigureSpec) -> FigureSpec:
    """Get a named figure specification."""
    if isinstance(name_or_spec, FigureSpec):
        return name_or_spec

    key = name_or_spec.strip().lower()
    if key not in _SPEC_REGISTRY:
        raise KeyError(f"Unknown figure spec '{name_or_spec}'. Available: {list(_SPEC_REGISTRY)}")
    return _SPEC_REGISTRY[key]


def register_figure_spec(name: str, spec: FigureSpec) -> None:
    """Register a custom figure specification."""
    _SPEC_REGISTRY[name.strip().lower()] = spec


def list_figure_specs() -> Mapping[str, FigureSpec]:
    """List available built-in and registered figure specs."""
    return dict(_SPEC_REGISTRY)
