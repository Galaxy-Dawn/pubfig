"""Panel export utilities for Figma-first multi-panel workflows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Mapping, Sequence

from matplotlib.figure import Figure

from .._version import __version__
from ..specs import FigureSpec
from .io import _save_basic_figure, _coerce_mpl_figure, save_figure


_PANEL_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_INDEX_FILENAME = "panel-index.json"
_DEFAULT_NODE_PREFIX = "panel/"


@dataclass(frozen=True)
class PanelExportRecord:
    """Metadata for one exported panel asset."""

    panel_id: str
    path: str
    format: str
    exported_at: str
    figma_node_name: str
    pubfig_version: str
    title: str | None = None


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_format(fmt: str) -> str:
    format_name = str(fmt).strip().lower().lstrip(".")
    if not format_name:
        raise ValueError("format must be a non-empty file suffix such as 'svg' or 'png'")
    return format_name


def _validate_panel_id(panel_id: str) -> str:
    value = str(panel_id).strip()
    if not value:
        raise ValueError("panel_id must be a non-empty string")
    if not _PANEL_ID_PATTERN.fullmatch(value):
        raise ValueError(
            "panel_id must use only letters, numbers, dots, underscores, or hyphens, "
            "and must start with a letter or number"
        )
    return value


def _resolve_panel_path(out_dir: str | Path, panel_id: str, format_name: str) -> Path:
    return Path(out_dir).expanduser().resolve() / f"{panel_id}.{format_name}"


def _default_figma_node_name(panel_id: str) -> str:
    return f"{_DEFAULT_NODE_PREFIX}{panel_id}"


def _extract_panel_title(fig: Figure) -> str | None:
    suptitle = getattr(fig, "_suptitle", None)
    if suptitle is not None:
        text = str(getattr(suptitle, "get_text", lambda: "")()).strip()
        if text:
            return text

    for ax in fig.axes:
        if getattr(ax, "name", "") == "legend":
            continue
        text = str(ax.get_title(loc="center")).strip()
        if text:
            return text
    return None


def _ensure_writable_target(path: Path, *, overwrite: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"Panel asset already exists: {path}. Pass overwrite=True to refresh this panel in place."
        )


def _use_publication_export(
    *,
    spec: str | FigureSpec | None,
    width: str | float | int | None,
    height_mm: float | int | None,
) -> bool:
    return spec is not None or width is not None or height_mm is not None


def _coerce_panels(
    panels: Mapping[str, object] | Sequence[tuple[str, object]],
) -> list[tuple[str, Figure]]:
    if isinstance(panels, Mapping):
        items = list(panels.items())
    else:
        items = list(panels)

    normalized: list[tuple[str, Figure]] = []
    seen: set[str] = set()
    for panel_id, fig in items:
        panel_name = _validate_panel_id(panel_id)
        if panel_name in seen:
            raise ValueError(f"Duplicate panel_id detected: {panel_name}")
        seen.add(panel_name)
        normalized.append((panel_name, _coerce_mpl_figure(fig)))
    return normalized


def _write_panel_index(records: Sequence[PanelExportRecord], out_dir: str | Path) -> Path:
    output_dir = Path(out_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    index_path = output_dir / _INDEX_FILENAME
    payload = {
        "schema_version": 1,
        "created_at": _utc_now_iso(),
        "pubfig_version": __version__,
        "records": [asdict(record) for record in records],
    }
    index_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return index_path


def export_panel(
    fig: object,
    panel_id: str,
    out_dir: str | Path,
    *,
    format: str = "svg",
    trim: bool = True,
    transparent: bool = False,
    spec: str | FigureSpec | None = None,
    width: str | float | int | None = None,
    height_mm: float | int | None = None,
    svg_fonttype: str = "none",
    overwrite: bool = False,
) -> PanelExportRecord:
    """Export a single panel asset plus minimal Figma sync metadata.

    When `spec`, `width`, or `height_mm` is provided, pubfig will use the publication-aware
    export path and defaults to `spec="nature"` if no explicit spec is given.
    Otherwise, the current interactive figure size is preserved.
    """

    panel_name = _validate_panel_id(panel_id)
    format_name = _normalize_format(format)
    target_path = _resolve_panel_path(out_dir, panel_name, format_name)
    _ensure_writable_target(target_path, overwrite=overwrite)

    mpl_fig = _coerce_mpl_figure(fig)
    if _use_publication_export(spec=spec, width=width, height_mm=height_mm):
        export_spec = spec if spec is not None else "nature"
        export_width = width if width is not None else "single"
        save_figure(
            mpl_fig,
            target_path.with_suffix(""),
            spec=export_spec,
            width=export_width,
            height_mm=height_mm,
            vector_formats=(format_name,) if format_name in {"svg", "pdf", "eps", "ps"} else (),
            raster_formats=(format_name,) if format_name not in {"svg", "pdf", "eps", "ps"} else (),
            transparent=transparent,
            trim=trim,
            svg_fonttype=svg_fonttype,
        )
    else:
        _save_basic_figure(
            mpl_fig,
            target_path,
            transparent=transparent,
            trim=trim,
            svg_fonttype=svg_fonttype,
        )

    return PanelExportRecord(
        panel_id=panel_name,
        path=str(target_path),
        format=format_name,
        exported_at=_utc_now_iso(),
        figma_node_name=_default_figma_node_name(panel_name),
        pubfig_version=__version__,
        title=_extract_panel_title(mpl_fig),
    )


def export_panels(
    panels: Mapping[str, object] | Sequence[tuple[str, object]],
    out_dir: str | Path,
    *,
    format: str = "svg",
    index_file: bool = True,
    trim: bool = True,
    transparent: bool = False,
    spec: str | FigureSpec | None = None,
    width: str | float | int | None = None,
    height_mm: float | int | None = None,
    svg_fonttype: str = "none",
    overwrite: bool = False,
) -> list[PanelExportRecord]:
    """Export multiple panel assets and optionally write a minimal sync index."""

    normalized = _coerce_panels(panels)
    records = [
        export_panel(
            fig,
            panel_id,
            out_dir,
            format=format,
            trim=trim,
            transparent=transparent,
            spec=spec,
            width=width,
            height_mm=height_mm,
            svg_fonttype=svg_fonttype,
            overwrite=overwrite,
        )
        for panel_id, fig in normalized
    ]
    if index_file:
        _write_panel_index(records, out_dir)
    return records


__all__ = ["PanelExportRecord", "export_panel", "export_panels"]
