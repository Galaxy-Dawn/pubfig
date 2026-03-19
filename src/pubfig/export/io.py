"""Figure export utilities (Matplotlib)."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence
import warnings

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .._compat import _require
from ..specs import FigureSpec, get_figure_spec, mm_to_inches, resolve_height_mm, resolve_width_mm


_VECTOR_TEXT_RCPARAMS: dict[str, object] = {
    # Keep text as text (editable/selectable) in vector outputs.
    # This also avoids "shadow/outline" artifacts in some SVG importers that mis-handle
    # glyph paths.
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "svg.fonttype": "none",
}


def _layout_pubfig_legend_pairs(mpl_fig: Figure) -> None:
    """Center any (left,right) legend pairs marked by plot functions.

    Some figures (notably bar+scatter) need two separate legend blocks:
    a significance key and a group legend. If they are created separately,
    their padding/metrics often makes them look misaligned or not centered.
    Plot functions can attach a private `_pubfig_legend_pair` hint to Axes,
    and we finalize positioning here after layout is settled.
    """
    try:
        canvas = mpl_fig.canvas
        if canvas is None:
            return
        canvas.draw()
        renderer = canvas.get_renderer()
    except Exception:
        return

    fig_w_px = float(mpl_fig.bbox.width) if mpl_fig.bbox is not None else 0.0
    if fig_w_px <= 0:
        return

    for ax in mpl_fig.axes:
        info = getattr(ax, "_pubfig_legend_pair", None)
        if not isinstance(info, dict):
            continue

        leg_left = info.get("left")
        leg_right = info.get("right")
        y_anchor_axes = float(info.get("y_anchor_axes", 1.18))
        gap_px = float(info.get("gap_px", 12.0))
        if leg_left is None or leg_right is None:
            continue

        try:
            bbox_left = leg_left.get_window_extent(renderer=renderer)
            bbox_right = leg_right.get_window_extent(renderer=renderer)
        except Exception:
            continue

        group_w = float(bbox_left.width) + float(gap_px) + float(bbox_right.width)
        # Center within the axes box (not the whole figure canvas). This keeps alignment
        # visually centered even when the tight bounding box is left-heavy (e.g., y-labels).
        try:
            ax_bbox = ax.get_window_extent(renderer=renderer)
            left_px = float(ax_bbox.x0) + (float(ax_bbox.width) - group_w) / 2.0
        except Exception:
            left_px = (fig_w_px - group_w) / 2.0

        # Convert y position from axes coords to figure coords.
        # Align the *centers* of both legend blocks to the same y, so different legend
        # heights (e.g. sig key vs. color legend) still look like one row.
        try:
            _, y_disp_top = ax.transAxes.transform((0.5, float(y_anchor_axes)))
            max_h = max(float(bbox_left.height), float(bbox_right.height))
            y_disp = float(y_disp_top) - max_h / 2.0
            _, y_fig = mpl_fig.transFigure.inverted().transform((0.0, float(y_disp)))
            y_fig = float(y_fig)
        except Exception:
            y_fig = 0.95

        x_left_fig = float(left_px / fig_w_px)
        x_right_fig = float((left_px + float(bbox_left.width) + float(gap_px)) / fig_w_px)

        try:
            leg_left.set_bbox_to_anchor((x_left_fig, y_fig), transform=mpl_fig.transFigure)
            leg_left._loc = 6  # 'center left'
        except Exception:
            pass
        try:
            leg_right.set_bbox_to_anchor((x_right_fig, y_fig), transform=mpl_fig.transFigure)
            leg_right._loc = 6  # 'center left'
        except Exception:
            pass


def _run_pubfig_post_layout_hooks(mpl_fig: Figure) -> None:
    """Run any plot-specific post-layout callbacks attached to Axes."""
    for ax in mpl_fig.axes:
        callback = getattr(ax, "_pubfig_post_layout", None)
        if not callable(callback):
            continue
        try:
            callback()
        except Exception:
            continue


def _coerce_mpl_figure(fig: object) -> Figure:
    """Accept a Matplotlib Figure, Axes, or an object with a `.figure` attribute."""
    if isinstance(fig, Figure):
        return fig
    if isinstance(fig, Axes):
        return fig.figure
    maybe = getattr(fig, "figure", None)
    if isinstance(maybe, Figure):
        return maybe
    raise TypeError("fig must be a matplotlib.figure.Figure (or an Axes with a .figure)")


def _save_basic_figure(
    fig: object,
    path: str | Path,
    *,
    dpi: int = 300,
    transparent: bool = False,
    trim: bool = False,
) -> None:
    """Save a Matplotlib figure to a single explicit file path."""
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)

    mpl_fig = _coerce_mpl_figure(fig)
    kwargs: dict[str, object] = {"dpi": int(dpi), "transparent": bool(transparent)}
    if trim:
        kwargs.update({"bbox_inches": "tight", "pad_inches": 0.01})
    with mpl.rc_context(_VECTOR_TEXT_RCPARAMS):
        _layout_pubfig_legend_pairs(mpl_fig)
        _run_pubfig_post_layout_hooks(mpl_fig)
        mpl_fig.savefig(out, **kwargs)


def batch_export(
    fig: object,
    base_path: str | Path,
    *,
    formats: Sequence[str] = ("pdf", "svg", "png"),
    dpi: int = 300,
    transparent: bool = False,
    trim: bool = False,
) -> list[Path]:
    """Export a figure in multiple formats using explicit file suffixes."""
    base = Path(base_path)
    saved: list[Path] = []
    for fmt in formats:
        p = base.with_suffix(f'.{fmt.lstrip(".").lower()}')
        _save_basic_figure(fig, p, dpi=dpi, transparent=transparent, trim=trim)
        saved.append(p)
    return saved


def save_figure(
    fig: object,
    base_path: str | Path,
    *,
    spec: str | FigureSpec = "nature",
    width: str | float | int = "single",
    height_mm: float | int | None = None,
    aspect_ratio: float | None = None,
    raster_dpi: int | None = None,
    vector_formats: Sequence[str] = ("pdf", "svg"),
    raster_formats: Sequence[str] = ("png",),
    transparent: bool | None = None,
    trim: bool = True,
) -> list[Path]:
    """Export a figure using publication defaults (vector + high-DPI raster)."""
    mpl_fig = _coerce_mpl_figure(fig)

    s = get_figure_spec(spec)
    width_mm = resolve_width_mm(width, spec=s)
    height_mm_resolved = resolve_height_mm(height_mm, width_mm=width_mm, aspect_ratio=aspect_ratio)

    base = Path(base_path)
    base.parent.mkdir(parents=True, exist_ok=True)

    raster_dpi_final = int(raster_dpi) if raster_dpi is not None else int(s.default_raster_dpi)
    if raster_dpi_final <= 0:
        raise ValueError("raster_dpi must be > 0")

    vfmts = [f.strip().lower().lstrip(".") for f in vector_formats]
    rfmts = [f.strip().lower().lstrip(".") for f in raster_formats]

    use_transparent = bool(transparent) if transparent is not None else False

    # Save and restore caller state.
    orig_size = mpl_fig.get_size_inches().copy()
    orig_fig_face = mpl_fig.get_facecolor()
    orig_axes_faces = [ax.get_facecolor() for ax in mpl_fig.axes]

    saved: list[Path] = []

    try:
        mpl_fig.set_size_inches(mm_to_inches(width_mm), mm_to_inches(height_mm_resolved), forward=True)

        if use_transparent:
            mpl_fig.patch.set_facecolor("none")
            mpl_fig.patch.set_alpha(0)
            for ax in mpl_fig.axes:
                ax.set_facecolor("none")
        else:
            mpl_fig.patch.set_facecolor(s.background_color)
            mpl_fig.patch.set_alpha(1)
            for ax in mpl_fig.axes:
                ax.set_facecolor(s.background_color)

        # Re-layout after resizing to the physical submission dimensions.
        # (Export width/height can differ substantially from the interactive design size.)
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="This figure includes Axes that are not compatible with tight_layout*",
                    category=UserWarning,
                )
                mpl_fig.tight_layout()
        except Exception:
            pass
        _layout_pubfig_legend_pairs(mpl_fig)
        _run_pubfig_post_layout_hooks(mpl_fig)

        common_kwargs: dict[str, object] = {"transparent": use_transparent}
        if trim:
            common_kwargs.update({"bbox_inches": "tight", "pad_inches": 0.01})

        for fmt in vfmts:
            out = base.with_suffix(f'.{fmt}')
            with mpl.rc_context(_VECTOR_TEXT_RCPARAMS):
                mpl_fig.savefig(out, format=fmt, dpi=int(s.design_dpi), **common_kwargs)
            saved.append(out)

        png_path: Path | None = None
        if "png" in rfmts:
            png_path = base.with_suffix('.png')
            mpl_fig.savefig(png_path, format='png', dpi=raster_dpi_final, **common_kwargs)
            saved.append(png_path)

        if any(fmt in rfmts for fmt in ("tif", "tiff")):
            _require("PIL", "raster")
            from PIL import Image

            tmp_png: Path | None = None
            src_png: Path
            if png_path is not None:
                src_png = png_path
            else:
                tmp_png = base.with_suffix('.tmp_pubfig.png')
                mpl_fig.savefig(tmp_png, format='png', dpi=raster_dpi_final, **common_kwargs)
                src_png = tmp_png

            tiff_ext = "tif" if ("tif" in rfmts and "tiff" not in rfmts) else "tiff"
            out_tiff = base.with_suffix(f'.{tiff_ext}')
            img = Image.open(src_png)
            img.save(out_tiff, dpi=(raster_dpi_final, raster_dpi_final), compression='tiff_lzw')
            saved.append(out_tiff)

            if tmp_png is not None:
                tmp_png.unlink(missing_ok=True)

    finally:
        mpl_fig.set_size_inches(orig_size[0], orig_size[1], forward=True)
        mpl_fig.patch.set_facecolor(orig_fig_face)
        for ax, face in zip(mpl_fig.axes, orig_axes_faces):
            ax.set_facecolor(face)

    return saved
