"""Bundle pubfig panel assets into Figma-friendly JSON packages."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Sequence

from .._version import __version__


_PANEL_BUNDLE_TYPE = "pubfig_figma_bundle"
_BUNDLE_SCHEMA_VERSION = 1
_PANEL_INDEX_NAME = "panel-index.json"
_VALID_LAYOUT_PRESETS = {"auto", "grid", "row", "column", "two_by_two", "hero_left", "hero_top"}
_VALID_LEGEND_POSITIONS = {"right", "bottom"}
_VALID_LABEL_ALIGN_X = {"panel", "column"}
_VALID_LABEL_ALIGN_Y = {"panel", "row"}
_SVG_OPEN_TAG = "<svg"
_FIGURE_ID_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _normalize_figure_id(raw: str) -> str:
    value = _FIGURE_ID_PATTERN.sub("-", str(raw).strip()).strip("-").lower()
    return value or "pubfig-figure"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_panel_dir(path: str | Path) -> Path:
    panel_dir = Path(path).expanduser().resolve()
    if not panel_dir.is_dir():
        raise FileNotFoundError(f"Panel directory not found: {panel_dir}")
    index_path = panel_dir / _PANEL_INDEX_NAME
    if not index_path.exists():
        raise FileNotFoundError(f"Expected panel index at: {index_path}")
    return panel_dir


def _validate_svg_text(svg_text: str, *, source: Path | None = None) -> None:
    if _SVG_OPEN_TAG not in svg_text:
        detail = f": {source}" if source is not None else ""
        raise ValueError(f"Expected inline SVG content{detail}")


def _validate_panel_index_payload(payload: dict[str, Any], panel_dir: Path) -> list[dict[str, Any]]:
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise ValueError("panel-index.json must contain a non-empty 'records' list")

    validated: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Each panel-index record must be an object")
        panel_id = str(record.get("panel_id", "")).strip()
        if not panel_id:
            raise ValueError("Each panel-index record must contain a non-empty panel_id")
        if panel_id in seen_ids:
            raise ValueError(f"Duplicate panel_id in panel-index.json: {panel_id}")
        seen_ids.add(panel_id)

        path_str = str(record.get("path", "")).strip()
        if not path_str:
            raise ValueError(f"Record {panel_id} is missing path")
        panel_path = Path(path_str).expanduser()
        if not panel_path.is_absolute():
            panel_path = (panel_dir / path_str).resolve()
        if not panel_path.exists():
            raise FileNotFoundError(f"Panel asset not found for {panel_id}: {panel_path}")
        if panel_path.suffix.lower() != ".svg":
            raise ValueError(
                f"Figma bundle packaging currently supports SVG panel assets only; got {panel_path.name}"
            )

        svg_text = panel_path.read_text(encoding="utf-8")
        _validate_svg_text(svg_text, source=panel_path)

        validated.append(
            {
                "panel_id": panel_id,
                "figma_node_name": str(record.get("figma_node_name", f"panel/{panel_id}")),
                "format": "svg",
                "source_path": str(panel_path),
                "exported_at": str(record.get("exported_at", "")),
                "pubfig_version": str(record.get("pubfig_version", __version__)),
                "label": panel_id,
                "title": str(record.get("title", "")).strip(),
                "svg": svg_text,
            }
        )
    return validated


def _load_panel_dir(panel_dir: str | Path) -> tuple[Path, dict[str, Any], list[dict[str, Any]]]:
    resolved_dir = _resolve_panel_dir(panel_dir)
    index_payload = _read_json(resolved_dir / _PANEL_INDEX_NAME)
    records = _validate_panel_index_payload(index_payload, resolved_dir)
    return resolved_dir, index_payload, records


def _default_bundle_path(panel_dir: Path, figure_id: str) -> Path:
    return panel_dir / f"{figure_id}.pubfig-figma.json"


def _load_panel_bundle_payload(payload: dict[str, Any], *, source_path: Path) -> dict[str, Any]:
    if int(payload.get("schema_version", -1)) != _BUNDLE_SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema_version in {source_path}")
    panels = payload.get("panels")
    if not isinstance(panels, list) or not panels:
        raise ValueError(f"Bundle file must contain a non-empty 'panels' list: {source_path}")
    for panel in panels:
        if not isinstance(panel, dict):
            raise ValueError("Each bundle panel entry must be an object")
        if not str(panel.get("panel_id", "")).strip():
            raise ValueError("Each bundle panel must include panel_id")
        _validate_svg_text(str(panel.get("svg", "")))
    return payload
def _load_bundle_payload(bundle_path: str | Path) -> dict[str, Any]:
    path = Path(bundle_path).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"Bundle file not found: {path}")
    payload = _read_json(path)
    bundle_type = str(payload.get("bundle_type", "")).strip()
    if bundle_type == _PANEL_BUNDLE_TYPE:
        return _load_panel_bundle_payload(payload, source_path=path)
    raise ValueError(f"Unsupported bundle_type in {path}")


def load_figma_bundle_payload(bundle_path: str | Path) -> dict[str, Any]:
    """Load and validate a packaged Figma bundle JSON file."""
    return _load_bundle_payload(bundle_path)


def resolve_figma_bundle_output_path(
    panel_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    figure_id: str | None = None,
) -> Path:
    """Resolve the bundle path that package/sync/watch would write for a panel directory."""

    resolved_dir = _resolve_panel_dir(panel_dir)
    if output_path is not None:
        return Path(output_path).expanduser().resolve()
    final_figure_id = _normalize_figure_id(figure_id or resolved_dir.name)
    return _default_bundle_path(resolved_dir, final_figure_id)


def materialize_figma_sync_bundle(
    source: str | Path,
    *,
    write_bundle: bool = False,
    bundle_output: str | Path | None = None,
    figure_id: str | None = None,
    title: str | None = None,
    preset: str | None = None,
    columns: int | None = None,
    row_panel_counts: Sequence[int] | None = None,
    panel_gap: float | None = None,
    shared_title: bool = False,
    shared_legend: bool = False,
    legend_position: str = "right",
    preserve_positions_on_refresh: bool | None = None,
    label_offset_x: float | None = None,
    label_offset_y: float | None = None,
    label_align_x: str | None = None,
    label_align_y: str | None = None,
) -> dict[str, Any]:
    """Resolve a sync/watch source and optionally write the exact bridge bundle to disk first."""

    candidate = Path(source).expanduser().resolve()
    override_kwargs = {
        "figure_id": figure_id,
        "title": title,
        "preset": preset,
        "columns": columns,
        "row_panel_counts": row_panel_counts,
        "panel_gap": panel_gap,
        "shared_title": shared_title,
        "shared_legend": shared_legend,
        "legend_position": legend_position,
        "preserve_positions_on_refresh": preserve_positions_on_refresh,
        "label_offset_x": label_offset_x,
        "label_offset_y": label_offset_y,
        "label_align_x": label_align_x,
        "label_align_y": label_align_y,
    }
    non_default_overrides = {
        key: value
        for key, value in override_kwargs.items()
        if value is not None
        and not (key in {"shared_title", "shared_legend"} and value is False)
        and not (key == "legend_position" and str(value) == "right")
    }

    if candidate.is_dir():
        if write_bundle:
            bundle_path = package_figma_bundle(
                candidate,
                output_path=bundle_output,
                figure_id=figure_id,
                title=title,
                preset=preset,
                columns=columns,
                row_panel_counts=row_panel_counts,
                panel_gap=panel_gap,
                shared_title=shared_title,
                shared_legend=shared_legend,
                legend_position=legend_position,
                preserve_positions_on_refresh=preserve_positions_on_refresh,
                label_offset_x=label_offset_x,
                label_offset_y=label_offset_y,
                label_align_x=label_align_x,
                label_align_y=label_align_y,
            )
            return {
                "source_kind": "panel_dir",
                "source_path": str(candidate),
                "bundle": load_figma_bundle_payload(bundle_path),
                "bundle_path": str(bundle_path.resolve()),
                "bundle_written": True,
            }
        return {
            "source_kind": "panel_dir",
            "source_path": str(candidate),
            "bundle": build_figma_bundle_payload(
                candidate,
                figure_id=figure_id,
                title=title,
                preset=preset,
                columns=columns,
                row_panel_counts=row_panel_counts,
                panel_gap=panel_gap,
                shared_title=shared_title,
                shared_legend=shared_legend,
                legend_position=legend_position,
                preserve_positions_on_refresh=preserve_positions_on_refresh,
                label_offset_x=label_offset_x,
                label_offset_y=label_offset_y,
                label_align_x=label_align_x,
                label_align_y=label_align_y,
            ),
            "bundle_path": None,
            "bundle_written": False,
        }

    if candidate.is_file():
        if non_default_overrides:
            keys = ", ".join(sorted(non_default_overrides))
            raise ValueError(
                "Bundle file sources already contain figure/layout metadata. "
                f"Remove these overrides or sync the panel directory instead: {keys}"
            )
        if bundle_output is not None:
            raise ValueError(
                "bundle_output can only be used when the sync source is a panel directory"
            )
        return {
            "source_kind": "bundle_file",
            "source_path": str(candidate),
            "bundle": load_figma_bundle_payload(candidate),
            "bundle_path": str(candidate),
            "bundle_written": False,
        }

    raise FileNotFoundError(f"Figma sync source not found: {candidate}")


def _normalize_row_panel_counts(
    row_panel_counts: Sequence[int] | None,
    *,
    panel_count: int,
) -> list[int] | None:
    if row_panel_counts is None:
        return None
    normalized = [int(value) for value in row_panel_counts]
    if not normalized:
        raise ValueError("row_panel_counts must not be empty")
    if any(value <= 0 for value in normalized):
        raise ValueError("row_panel_counts must contain only positive integers")
    if sum(normalized) != int(panel_count):
        raise ValueError(f"row_panel_counts must sum to panel_count ({panel_count}), got {sum(normalized)}")
    return normalized


def build_figma_bundle_payload(
    panel_dir: str | Path,
    *,
    figure_id: str | None = None,
    title: str | None = None,
    preset: str | None = None,
    columns: int | None = None,
    row_panel_counts: Sequence[int] | None = None,
    panel_gap: float | None = None,
    shared_title: bool = False,
    shared_legend: bool = False,
    legend_position: str = "right",
    preserve_positions_on_refresh: bool | None = None,
    label_offset_x: float | None = None,
    label_offset_y: float | None = None,
    label_align_x: str | None = None,
    label_align_y: str | None = None,
) -> dict[str, Any]:
    """Build a panel-level Figma bundle payload for the panel-first Figma workflow."""

    if columns is not None and int(columns) <= 0:
        raise ValueError("columns must be > 0")
    if panel_gap is not None and float(panel_gap) < 0:
        raise ValueError("panel_gap must be >= 0")
    if label_offset_x is not None and float(label_offset_x) < 0:
        raise ValueError("label_offset_x must be >= 0")
    if label_offset_y is not None and float(label_offset_y) < 0:
        raise ValueError("label_offset_y must be >= 0")
    preset_name = str(preset).strip().lower() if preset is not None else None
    if preset_name is not None and preset_name not in _VALID_LAYOUT_PRESETS:
        raise ValueError(f"preset must be one of {sorted(_VALID_LAYOUT_PRESETS)}")
    legend_position_name = str(legend_position).strip().lower()
    if legend_position_name not in _VALID_LEGEND_POSITIONS:
        raise ValueError(f"legend_position must be one of {sorted(_VALID_LEGEND_POSITIONS)}")
    label_align_x_name = str(label_align_x).strip().lower() if label_align_x is not None else None
    label_align_y_name = str(label_align_y).strip().lower() if label_align_y is not None else None
    if label_align_x_name is not None and label_align_x_name not in _VALID_LABEL_ALIGN_X:
        raise ValueError(f"label_align_x must be one of {sorted(_VALID_LABEL_ALIGN_X)}")
    if label_align_y_name is not None and label_align_y_name not in _VALID_LABEL_ALIGN_Y:
        raise ValueError(f"label_align_y must be one of {sorted(_VALID_LABEL_ALIGN_Y)}")

    resolved_dir, index_payload, records = _load_panel_dir(panel_dir)
    final_figure_id = _normalize_figure_id(figure_id or resolved_dir.name)
    normalized_row_panel_counts = _normalize_row_panel_counts(row_panel_counts, panel_count=len(records))
    if normalized_row_panel_counts is not None and columns is not None:
        raise ValueError("columns cannot be combined with row_panel_counts")
    layout: dict[str, Any] = {}
    if preset_name is not None:
        layout["preset"] = preset_name
    if normalized_row_panel_counts is not None:
        layout["row_panel_counts"] = normalized_row_panel_counts
    elif columns is not None:
        layout["columns"] = int(columns)
    if panel_gap is not None:
        layout["panel_gap"] = float(panel_gap)
    if preserve_positions_on_refresh is not None:
        layout["preserve_positions_on_refresh"] = bool(preserve_positions_on_refresh)

    return {
        "bundle_type": _PANEL_BUNDLE_TYPE,
        "schema_version": _BUNDLE_SCHEMA_VERSION,
        "figure_id": final_figure_id,
        "title": title,
        "created_at": _utc_now_iso(),
        "pubfig_version": __version__,
        "source_panel_dir": str(resolved_dir),
        "source_panel_index": str(resolved_dir / _PANEL_INDEX_NAME),
        "workflow": {
            "path": "panel-first",
            "refresh_strategy": "panel-in-place",
        },
        "layout": layout,
        "placeholders": {
            "shared_title": {
                "enabled": bool(shared_title),
                "text": title or "Shared Figure Title",
                "position": "top",
            },
            "shared_legend": {
                "enabled": bool(shared_legend),
                "text": "Shared Legend",
                "position": legend_position_name,
            },
        },
        "panel_labels": {
            "enabled": True,
            "offset_x": float(label_offset_x) if label_offset_x is not None else 12.0,
            "offset_y": float(label_offset_y) if label_offset_y is not None else 12.0,
            "align_x": label_align_x_name or "column",
            "align_y": label_align_y_name or "row",
        },
        "panels": records,
        "source_index_summary": {
            "created_at": str(index_payload.get("created_at", "")),
            "record_count": len(records),
        },
    }


def package_figma_bundle(
    panel_dir: str | Path,
    *,
    output_path: str | Path | None = None,
    figure_id: str | None = None,
    title: str | None = None,
    preset: str | None = None,
    columns: int | None = None,
    row_panel_counts: Sequence[int] | None = None,
    panel_gap: float | None = None,
    shared_title: bool = False,
    shared_legend: bool = False,
    legend_position: str = "right",
    preserve_positions_on_refresh: bool | None = None,
    label_offset_x: float | None = None,
    label_offset_y: float | None = None,
    label_align_x: str | None = None,
    label_align_y: str | None = None,
) -> Path:
    """Package an exported panel directory into a single JSON bundle."""

    payload = build_figma_bundle_payload(
        panel_dir,
        figure_id=figure_id,
        title=title,
        preset=preset,
        columns=columns,
        row_panel_counts=row_panel_counts,
        panel_gap=panel_gap,
        shared_title=shared_title,
        shared_legend=shared_legend,
        legend_position=legend_position,
        preserve_positions_on_refresh=preserve_positions_on_refresh,
        label_offset_x=label_offset_x,
        label_offset_y=label_offset_y,
        label_align_x=label_align_x,
        label_align_y=label_align_y,
    )
    resolved_dir = _resolve_panel_dir(panel_dir)
    bundle_path = resolve_figma_bundle_output_path(
        resolved_dir,
        output_path=output_path,
        figure_id=str(payload["figure_id"]),
    )
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return bundle_path


def resolve_figma_sync_source(
    source: str | Path,
    *,
    figure_id: str | None = None,
    title: str | None = None,
    preset: str | None = None,
    columns: int | None = None,
    row_panel_counts: Sequence[int] | None = None,
    panel_gap: float | None = None,
    shared_title: bool = False,
    shared_legend: bool = False,
    legend_position: str = "right",
    preserve_positions_on_refresh: bool | None = None,
    label_offset_x: float | None = None,
    label_offset_y: float | None = None,
    label_align_x: str | None = None,
    label_align_y: str | None = None,
) -> dict[str, Any]:
    """Resolve a sync/watch source into a ready-to-send bundle payload.

    Supported sources:
    - exported panel directory containing ``panel-index.json``
    - packaged ``.pubfig-figma.json`` bundle file
    """

    resolved = materialize_figma_sync_bundle(
        source,
        write_bundle=False,
        bundle_output=None,
        figure_id=figure_id,
        title=title,
        preset=preset,
        columns=columns,
        row_panel_counts=row_panel_counts,
        panel_gap=panel_gap,
        shared_title=shared_title,
        shared_legend=shared_legend,
        legend_position=legend_position,
        preserve_positions_on_refresh=preserve_positions_on_refresh,
        label_offset_x=label_offset_x,
        label_offset_y=label_offset_y,
        label_align_x=label_align_x,
        label_align_y=label_align_y,
    )
    return {
        "source_kind": resolved["source_kind"],
        "source_path": resolved["source_path"],
        "bundle": resolved["bundle"],
    }
def validate_figma_bundle(path: str | Path) -> dict[str, Any]:
    """Validate a panel directory or packaged panel Figma bundle JSON file."""

    candidate = Path(path).expanduser().resolve()
    if candidate.is_dir():
        resolved_dir, index_payload, records = _load_panel_dir(candidate)
        return {
            "kind": "panel_dir",
            "path": str(resolved_dir),
            "panel_index": str(resolved_dir / _PANEL_INDEX_NAME),
            "record_count": len(records),
            "panel_ids": [record["panel_id"] for record in records],
            "created_at": str(index_payload.get("created_at", "")),
            "valid": True,
        }

    payload = _load_bundle_payload(candidate)
    bundle_type = str(payload["bundle_type"])
    return {
        "kind": "bundle_file",
        "bundle_type": bundle_type,
        "path": str(candidate),
        "figure_id": str(payload.get("figure_id", "")),
        "record_count": len(payload["panels"]),
        "panel_ids": [str(panel["panel_id"]) for panel in payload["panels"]],
        "layout": payload.get("layout", {}),
        "panel_labels": payload.get("panel_labels", {}),
        "valid": True,
    }


def inspect_figma_bundle(path: str | Path) -> dict[str, Any]:
    """Return a compact summary for a packaged Figma bundle JSON file."""

    payload = _load_bundle_payload(path)
    bundle_type = str(payload["bundle_type"])
    panels = payload["panels"]
    return {
        "bundle_type": bundle_type,
        "schema_version": payload["schema_version"],
        "figure_id": payload["figure_id"],
        "title": payload.get("title"),
        "created_at": payload.get("created_at"),
        "pubfig_version": payload.get("pubfig_version"),
        "panel_count": len(panels),
        "panel_ids": [str(panel["panel_id"]) for panel in panels],
        "layout": payload.get("layout", {}),
        "panel_labels": payload.get("panel_labels", {}),
        "workflow": payload.get("workflow", {}),
    }


__all__ = [
    "build_figma_bundle_payload",
    "inspect_figma_bundle",
    "load_figma_bundle_payload",
    "materialize_figma_sync_bundle",
    "package_figma_bundle",
    "resolve_figma_bundle_output_path",
    "resolve_figma_sync_source",
    "validate_figma_bundle",
]
