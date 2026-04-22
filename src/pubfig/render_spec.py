"""Agent-first JSON render spec loading, validation, and execution."""

from __future__ import annotations

from dataclasses import dataclass
import inspect
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from ._version import __version__
from .export import batch_export, export_panels, save_figure
from .export.io import _coerce_mpl_figure, _resolve_save_figure_target
from .export.panels import _normalize_format as _normalize_panel_format
from .export.panels import _validate_panel_id
from .plot_registry import get_plot_callable, list_plot_kinds
from .themes import get_theme


_SCHEMA_VERSION = 1
_TOP_LEVEL_KEYS = frozenset({"schema_version", "plot", "panels", "export"})
_PLOT_KEYS = frozenset({"kind", "kwargs"})
_PANEL_KEYS = frozenset({"panel_id", "kind", "kwargs"})
_LOAD_BASE_KEYS = frozenset({"$load"})
_CSV_LOAD_KEYS = frozenset({"$load", "delimiter", "skip_header"})
_NPZ_LOAD_KEYS = frozenset({"$load", "key"})
_SAVE_FIGURE_EXPORT_KEYS = frozenset(
    {"mode", "path", "spec", "width", "height_mm", "aspect_ratio", "raster_dpi", "transparent", "trim", "svg_fonttype"}
)
_BATCH_EXPORT_KEYS = frozenset(
    {
        "mode",
        "base_path",
        "formats",
        "spec",
        "width",
        "height_mm",
        "aspect_ratio",
        "dpi",
        "transparent",
        "trim",
        "svg_fonttype",
    }
)
_EXPORT_PANELS_KEYS = frozenset(
    {
        "mode",
        "output_dir",
        "format",
        "index_file",
        "trim",
        "transparent",
        "spec",
        "width",
        "height_mm",
        "svg_fonttype",
        "include_title",
        "overwrite",
        "labels",
    }
)

_INLINE_ARRAY_PARAM_NAMES_BY_KIND: dict[str, frozenset[str]] = {
    # Public APIs mostly annotate ndarray inputs, but a few older functions keep
    # untyped arguments while still expecting array-like scientific data. These
    # entries let small inline JSON datasets behave like direct Python calls that
    # pass NumPy arrays.
    "upset": frozenset({"memberships"}),
    "ecdf": frozenset({"group"}),
    "qq": frozenset({"values"}),
    "bland_altman": frozenset({"x", "y"}),
    "box": frozenset({"data"}),
    "density": frozenset({"data"}),
    "raincloud": frozenset({"data"}),
    "strip": frozenset({"data"}),
    "violin": frozenset({"data"}),
    "line": frozenset({"data", "x"}),
    "area": frozenset({"data", "x"}),
}
_INLINE_FEATURE_LIST_PARAM_NAMES_BY_KIND: dict[str, frozenset[str]] = {
    # These functions accept either a 1D/2D ndarray or a Python list of 1D
    # arrays. For inline JSON, nested lists map more naturally to list-of-series.
    "ecdf": frozenset({"values"}),
    "ridgeline": frozenset({"data"}),
    "roc": frozenset({"fpr", "tpr"}),
    "pr_curve": frozenset({"precision", "recall"}),
    "calibration": frozenset({"y_true", "y_prob"}),
}


class RenderSpecError(Exception):
    """Base error for CLI JSON render specs."""

    def __init__(
        self,
        message: str,
        *,
        field_path: str | None = None,
        error_type: str = "SpecValidationError",
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = str(message)
        self.field_path = field_path
        self.error_type = error_type
        self.extra = dict(extra or {})

    def to_payload(self, *, command: str) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": False,
            "command": command,
            "error_type": self.error_type,
            "message": self.message,
            "pubfig_version": __version__,
        }
        if self.field_path is not None:
            payload["field_path"] = self.field_path
        payload.update(self.extra)
        return payload


@dataclass(frozen=True)
class RenderSummary:
    """Stable JSON summary for render/validate-spec."""

    command: str
    schema_version: int
    mode: str
    spec_path: str
    plot_kinds: list[str]
    panel_count: int
    output_paths: list[str] | None = None
    would_write_paths: list[str] | None = None

    def to_payload(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "ok": True,
            "command": self.command,
            "schema_version": self.schema_version,
            "pubfig_version": __version__,
            "mode": self.mode,
            "spec_path": self.spec_path,
            "plot_kinds": self.plot_kinds,
            "panel_count": self.panel_count,
        }
        if self.output_paths is not None:
            payload["output_paths"] = self.output_paths
        if self.would_write_paths is not None:
            payload["would_write_paths"] = self.would_write_paths
        return payload


def _ensure_dict(value: Any, *, field_path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise RenderSpecError(f"{field_path} must be an object", field_path=field_path)
    return dict(value)


def _ensure_list(value: Any, *, field_path: str) -> list[Any]:
    if not isinstance(value, list):
        raise RenderSpecError(f"{field_path} must be a list", field_path=field_path)
    return list(value)


def _reject_unknown_keys(payload: dict[str, Any], allowed: frozenset[str], *, field_path: str) -> None:
    unknown = sorted(set(payload) - set(allowed))
    if unknown:
        raise RenderSpecError(
            f"Unknown fields in {field_path}: {unknown}",
            field_path=field_path,
            extra={"unknown_fields": unknown},
        )


def _resolve_path(value: str | Path, *, spec_dir: Path) -> Path:
    path = Path(value).expanduser()
    if not path.is_absolute():
        path = spec_dir / path
    return path.resolve()


def _load_from_reference(reference: dict[str, Any], *, spec_dir: Path, field_path: str) -> Any:
    ref_path = _resolve_path(reference["$load"], spec_dir=spec_dir)
    if not ref_path.exists():
        raise RenderSpecError(
            f"Referenced file does not exist: {ref_path}",
            field_path=field_path,
            error_type="DataLoadError",
        )

    suffix = ref_path.suffix.lower()
    if suffix == ".json":
        _reject_unknown_keys(reference, _LOAD_BASE_KEYS, field_path=field_path)
        with ref_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    if suffix == ".csv":
        _reject_unknown_keys(reference, _CSV_LOAD_KEYS, field_path=field_path)
        delimiter = str(reference.get("delimiter", ","))
        skip_header = int(reference.get("skip_header", 0))
        return np.loadtxt(ref_path, delimiter=delimiter, skiprows=skip_header)
    if suffix == ".npy":
        _reject_unknown_keys(reference, _LOAD_BASE_KEYS, field_path=field_path)
        return np.load(ref_path, allow_pickle=False)
    if suffix == ".npz":
        _reject_unknown_keys(reference, _NPZ_LOAD_KEYS, field_path=field_path)
        if "key" not in reference:
            raise RenderSpecError(
                "NPZ references must include 'key'",
                field_path=field_path,
                error_type="DataLoadError",
            )
        key = str(reference["key"])
        with np.load(ref_path, allow_pickle=False) as payload:
            if key not in payload:
                raise RenderSpecError(
                    f"NPZ key not found: {key}",
                    field_path=field_path,
                    error_type="DataLoadError",
                )
            return payload[key]

    raise RenderSpecError(
        f"Unsupported data reference suffix: {suffix}",
        field_path=field_path,
        error_type="DataLoadError",
    )


def _resolve_value(value: Any, *, spec_dir: Path, field_path: str) -> Any:
    if isinstance(value, dict):
        if "$load" in value:
            return _load_from_reference(value, spec_dir=spec_dir, field_path=field_path)
        return {
            key: _resolve_value(subvalue, spec_dir=spec_dir, field_path=f"{field_path}.{key}")
            for key, subvalue in value.items()
        }
    if isinstance(value, list):
        return [
            _resolve_value(item, spec_dir=spec_dir, field_path=f"{field_path}[{index}]")
            for index, item in enumerate(value)
        ]
    return value


def _is_numeric_inline_sequence(value: Any) -> bool:
    """Return True when a JSON value can safely become a numeric ndarray."""

    if isinstance(value, (bool, int, float)):
        return True
    if isinstance(value, list):
        return all(_is_numeric_inline_sequence(item) for item in value)
    return False


def _annotation_wants_ndarray(annotation: Any) -> bool:
    annotation_text = str(annotation)
    return "np.ndarray" in annotation_text or "numpy.ndarray" in annotation_text


def _coerce_inline_array_value(value: Any) -> Any:
    if isinstance(value, list) and _is_numeric_inline_sequence(value):
        return np.asarray(value)
    return value


def _coerce_inline_feature_list_value(value: Any) -> Any:
    if not isinstance(value, list) or not _is_numeric_inline_sequence(value):
        return value
    if value and all(isinstance(item, list) for item in value):
        return [np.asarray(item) for item in value]
    return np.asarray(value)


def _coerce_plot_inline_arrays(
    kind: str,
    kwargs: dict[str, Any],
    plot_callable: Any,
) -> dict[str, Any]:
    """Convert small inline JSON numeric lists to arrays for array-like plot args."""

    signature = inspect.signature(plot_callable)
    fallback_array_params = _INLINE_ARRAY_PARAM_NAMES_BY_KIND.get(str(kind), frozenset())
    fallback_feature_list_params = _INLINE_FEATURE_LIST_PARAM_NAMES_BY_KIND.get(str(kind), frozenset())
    coerced = dict(kwargs)
    for name, value in list(coerced.items()):
        parameter = signature.parameters.get(name)
        annotation = parameter.annotation if parameter is not None else inspect.Signature.empty
        if name in fallback_feature_list_params:
            coerced[name] = _coerce_inline_feature_list_value(value)
        elif _annotation_wants_ndarray(annotation) or name in fallback_array_params:
            coerced[name] = _coerce_inline_array_value(value)
    return coerced


def _coerce_plot_theme_from_export(
    kwargs: dict[str, Any],
    plot_callable: Any,
    export_payload: dict[str, Any],
) -> dict[str, Any]:
    """Apply the export theme during CLI figure construction when possible."""

    if "theme" in kwargs or "theme" not in inspect.signature(plot_callable).parameters:
        return kwargs
    spec_name = export_payload.get("spec")
    if spec_name is None and export_payload.get("mode") in {"save_figure", "batch_export"}:
        spec_name = "nature"
    if not isinstance(spec_name, str):
        return kwargs
    try:
        theme = get_theme(spec_name)
    except KeyError:
        return kwargs
    coerced = dict(kwargs)
    coerced["theme"] = theme
    return coerced


def _coerce_plot_result_to_figure(result: Any):
    """Coerce a plot return value to a Figure, accepting (Figure, metadata)."""

    if isinstance(result, (tuple, list)) and result:
        result = result[0]
    return _coerce_mpl_figure(result)


def _bind_callable(callable_obj: Any, /, *args: Any, field_path: str, **kwargs: Any) -> None:
    try:
        inspect.signature(callable_obj).bind(*args, **kwargs)
    except TypeError as error:
        raise RenderSpecError(str(error), field_path=field_path) from error


def _resolve_plot_kwargs(kwargs_payload: Any, *, spec_dir: Path, field_path: str) -> dict[str, Any]:
    kwargs_obj = _ensure_dict(kwargs_payload, field_path=field_path)
    return {
        key: _resolve_value(value, spec_dir=spec_dir, field_path=f"{field_path}.{key}")
        for key, value in kwargs_obj.items()
    }


def _load_spec(spec_path: str | Path) -> tuple[dict[str, Any], Path, Path]:
    resolved = Path(spec_path).expanduser().resolve()
    if not resolved.exists():
        raise RenderSpecError(f"Spec file does not exist: {resolved}", field_path="spec_path")
    try:
        with resolved.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as error:
        raise RenderSpecError(
            f"Invalid JSON: {error.msg}",
            field_path="spec",
        ) from error
    if not isinstance(payload, dict):
        raise RenderSpecError("Spec root must be a JSON object", field_path="spec")
    return dict(payload), resolved, resolved.parent


def _validate_top_level(payload: dict[str, Any]) -> None:
    _reject_unknown_keys(payload, _TOP_LEVEL_KEYS, field_path="spec")
    if "schema_version" not in payload:
        raise RenderSpecError("schema_version is required", field_path="schema_version")
    if payload["schema_version"] != _SCHEMA_VERSION:
        raise RenderSpecError(
            f"Unsupported schema_version: {payload['schema_version']}",
            field_path="schema_version",
        )
    has_plot = "plot" in payload
    has_panels = "panels" in payload
    if has_plot == has_panels:
        raise RenderSpecError(
            "Spec must contain exactly one of 'plot' or 'panels'",
            field_path="spec",
        )
    if "export" not in payload:
        raise RenderSpecError("export is required", field_path="export")


def _resolve_output_paths_for_export(
    export_payload: dict[str, Any], *, spec_dir: Path, panel_ids: list[str] | None = None
) -> list[Path]:
    mode = str(export_payload["mode"])
    if mode == "save_figure":
        output_path = _resolve_path(export_payload["path"], spec_dir=spec_dir)
        _resolve_save_figure_target(output_path)
        return [output_path]
    if mode == "batch_export":
        base_path = _resolve_path(export_payload["base_path"], spec_dir=spec_dir)
        formats = export_payload.get("formats")
        if not isinstance(formats, list) or not formats:
            raise RenderSpecError("batch_export.formats must be a non-empty list", field_path="export.formats")
        resolved: list[Path] = []
        for index, fmt in enumerate(formats):
            if not isinstance(fmt, str) or not str(fmt).strip():
                raise RenderSpecError(
                    "Each batch_export format must be a non-empty string",
                    field_path=f"export.formats[{index}]",
                )
            resolved.append(base_path.with_suffix(f".{str(fmt).strip().lower().lstrip('.')}"))
        return resolved
    if mode == "export_panels":
        if panel_ids is None:
            raise RenderSpecError("panel_ids are required for export_panels path resolution", field_path="export.mode")
        output_dir = _resolve_path(export_payload["output_dir"], spec_dir=spec_dir)
        try:
            format_name = _normalize_panel_format(str(export_payload.get("format", "svg")))
        except ValueError as error:
            raise RenderSpecError(str(error), field_path="export.format") from error
        output_paths = [output_dir / f"{panel_id}.{format_name}" for panel_id in panel_ids]
        if bool(export_payload.get("index_file", True)):
            output_paths.append(output_dir / "panel-index.json")
        return output_paths
    raise RenderSpecError(f"Unsupported export mode: {mode}", field_path="export.mode")


def _validate_single_export_contract(export_payload: dict[str, Any], *, spec_dir: Path) -> list[Path]:
    mode = export_payload.get("mode")
    if mode not in {"save_figure", "batch_export"}:
        raise RenderSpecError(
            "Single-plot specs require export.mode to be 'save_figure' or 'batch_export'",
            field_path="export.mode",
        )
    if mode == "save_figure":
        _reject_unknown_keys(export_payload, _SAVE_FIGURE_EXPORT_KEYS, field_path="export")
        if "path" not in export_payload:
            raise RenderSpecError("save_figure export requires 'path'", field_path="export.path")
        kwargs = dict(export_payload)
        kwargs.pop("mode", None)
        resolved_path = _resolve_path(export_payload["path"], spec_dir=spec_dir)
        kwargs.pop("path", None)
        _bind_callable(save_figure, object(), resolved_path, field_path="export", **kwargs)
    else:
        _reject_unknown_keys(export_payload, _BATCH_EXPORT_KEYS, field_path="export")
        if "base_path" not in export_payload:
            raise RenderSpecError("batch_export export requires 'base_path'", field_path="export.base_path")
        kwargs = dict(export_payload)
        kwargs.pop("mode", None)
        resolved_base_path = _resolve_path(export_payload["base_path"], spec_dir=spec_dir)
        kwargs.pop("base_path", None)
        _bind_callable(batch_export, object(), resolved_base_path, field_path="export", **kwargs)
    return _resolve_output_paths_for_export(export_payload, spec_dir=spec_dir)


def _validate_panels_export_contract(
    export_payload: dict[str, Any], *, spec_dir: Path, panel_ids: list[str]
) -> list[Path]:
    if export_payload.get("mode") != "export_panels":
        raise RenderSpecError(
            "Panel specs require export.mode to be 'export_panels'",
            field_path="export.mode",
        )
    _reject_unknown_keys(export_payload, _EXPORT_PANELS_KEYS, field_path="export")
    if "output_dir" not in export_payload:
        raise RenderSpecError("export_panels export requires 'output_dir'", field_path="export.output_dir")
    kwargs = dict(export_payload)
    kwargs.pop("mode", None)
    resolved_output_dir = _resolve_path(export_payload["output_dir"], spec_dir=spec_dir)
    kwargs.pop("output_dir", None)
    _bind_callable(export_panels, [], resolved_output_dir, field_path="export", **kwargs)
    return _resolve_output_paths_for_export(export_payload, spec_dir=spec_dir, panel_ids=panel_ids)


def _validate_and_render_single(
    plot_payload: dict[str, Any],
    export_payload: dict[str, Any],
    *,
    spec_dir: Path,
    perform_export: bool,
) -> tuple[list[str], list[Path]]:
    _reject_unknown_keys(plot_payload, _PLOT_KEYS, field_path="plot")
    if "kind" not in plot_payload:
        raise RenderSpecError("plot.kind is required", field_path="plot.kind")
    if "kwargs" not in plot_payload:
        raise RenderSpecError("plot.kwargs is required", field_path="plot.kwargs")

    kind = str(plot_payload["kind"])
    try:
        plot_callable = get_plot_callable(kind)
    except KeyError as error:
        raise RenderSpecError(
            f"Unknown plot kind: {kind}",
            field_path="plot.kind",
            extra={"available_kinds": list_plot_kinds()},
        ) from error

    kwargs = _resolve_plot_kwargs(plot_payload["kwargs"], spec_dir=spec_dir, field_path="plot.kwargs")
    kwargs = _coerce_plot_inline_arrays(kind, kwargs, plot_callable)
    kwargs = _coerce_plot_theme_from_export(kwargs, plot_callable, export_payload)
    _bind_callable(plot_callable, field_path="plot.kwargs", **kwargs)
    output_paths = _validate_single_export_contract(export_payload, spec_dir=spec_dir)

    fig_obj = plot_callable(**kwargs)
    fig = _coerce_plot_result_to_figure(fig_obj)
    try:
        if perform_export:
            mode = str(export_payload["mode"])
            export_kwargs = dict(export_payload)
            export_kwargs.pop("mode", None)
            if mode == "save_figure":
                export_kwargs.pop("path", None)
                output_paths = list(
                    save_figure(fig, _resolve_path(export_payload["path"], spec_dir=spec_dir), **export_kwargs)
                )
            else:
                export_kwargs.pop("base_path", None)
                output_paths = list(
                    batch_export(fig, _resolve_path(export_payload["base_path"], spec_dir=spec_dir), **export_kwargs)
                )
    finally:
        plt.close(fig)
    return [kind], output_paths


def _validate_and_render_panels(
    panels_payload: list[Any],
    export_payload: dict[str, Any],
    *,
    spec_dir: Path,
    perform_export: bool,
) -> tuple[list[str], list[Path], int]:
    panel_specs = _ensure_list(panels_payload, field_path="panels")
    if not panel_specs:
        raise RenderSpecError("panels must contain at least one panel", field_path="panels")

    panel_entries: list[tuple[str, str, dict[str, Any], str]] = []
    rendered_panels: list[tuple[str, Any]] = []
    plot_kinds: list[str] = []
    panel_ids: list[str] = []
    try:
        for index, raw_panel in enumerate(panel_specs):
            panel = _ensure_dict(raw_panel, field_path=f"panels[{index}]")
            _reject_unknown_keys(panel, _PANEL_KEYS, field_path=f"panels[{index}]")
            if "panel_id" not in panel:
                raise RenderSpecError("panel_id is required", field_path=f"panels[{index}].panel_id")
            if "kind" not in panel:
                raise RenderSpecError("kind is required", field_path=f"panels[{index}].kind")
            if "kwargs" not in panel:
                raise RenderSpecError("kwargs is required", field_path=f"panels[{index}].kwargs")

            panel_id = _validate_panel_id(str(panel["panel_id"]))
            if panel_id in panel_ids:
                raise RenderSpecError(f"Duplicate panel_id: {panel_id}", field_path=f"panels[{index}].panel_id")
            panel_ids.append(panel_id)
            panel_entries.append(
                (
                    panel_id,
                    str(panel["kind"]),
                    _ensure_dict(panel["kwargs"], field_path=f"panels[{index}].kwargs"),
                    f"panels[{index}]",
                )
            )

        output_paths = _validate_panels_export_contract(export_payload, spec_dir=spec_dir, panel_ids=panel_ids)

        for panel_id, kind, raw_kwargs, panel_field_path in panel_entries:
            panel_index_field = f"{panel_field_path}.kind"

            try:
                plot_callable = get_plot_callable(kind)
            except KeyError as error:
                raise RenderSpecError(
                    f"Unknown plot kind: {kind}",
                    field_path=panel_index_field,
                    extra={"available_kinds": list_plot_kinds()},
                ) from error

            kwargs = _resolve_plot_kwargs(raw_kwargs, spec_dir=spec_dir, field_path=f"{panel_field_path}.kwargs")
            kwargs = _coerce_plot_inline_arrays(kind, kwargs, plot_callable)
            kwargs = _coerce_plot_theme_from_export(kwargs, plot_callable, export_payload)
            _bind_callable(plot_callable, field_path=f"{panel_field_path}.kwargs", **kwargs)
            fig_obj = plot_callable(**kwargs)
            fig = _coerce_plot_result_to_figure(fig_obj)
            rendered_panels.append((panel_id, fig))
            plot_kinds.append(kind)
        if perform_export:
            export_kwargs = dict(export_payload)
            export_kwargs.pop("mode", None)
            export_kwargs.pop("output_dir", None)
            records = export_panels(
                rendered_panels,
                _resolve_path(export_payload["output_dir"], spec_dir=spec_dir),
                **export_kwargs,
            )
            output_paths = [Path(record.path).resolve() for record in records]
            if bool(export_payload.get("index_file", True)):
                output_paths.append(_resolve_path(export_payload["output_dir"], spec_dir=spec_dir) / "panel-index.json")
        return plot_kinds, output_paths, len(rendered_panels)
    finally:
        for _, fig in rendered_panels:
            plt.close(fig)


def run_render_spec(spec_path: str | Path, *, validate_only: bool) -> RenderSummary:
    payload, resolved_spec, spec_dir = _load_spec(spec_path)
    _validate_top_level(payload)
    export_payload = _ensure_dict(payload["export"], field_path="export")

    if "plot" in payload:
        plot_payload = _ensure_dict(payload["plot"], field_path="plot")
        plot_kinds, output_paths = _validate_and_render_single(
            plot_payload,
            export_payload,
            spec_dir=spec_dir,
            perform_export=not validate_only,
        )
        return RenderSummary(
            command="validate-spec" if validate_only else "render",
            schema_version=_SCHEMA_VERSION,
            mode=str(export_payload["mode"]),
            spec_path=str(resolved_spec),
            plot_kinds=plot_kinds,
            panel_count=0,
            output_paths=None if validate_only else [str(path.resolve()) for path in output_paths],
            would_write_paths=[str(path.resolve()) for path in output_paths] if validate_only else None,
        )

    plot_kinds, output_paths, panel_count = _validate_and_render_panels(
        payload["panels"],
        export_payload,
        spec_dir=spec_dir,
        perform_export=not validate_only,
    )
    return RenderSummary(
        command="validate-spec" if validate_only else "render",
        schema_version=_SCHEMA_VERSION,
        mode=str(export_payload["mode"]),
        spec_path=str(resolved_spec),
        plot_kinds=plot_kinds,
        panel_count=panel_count,
        output_paths=None if validate_only else [str(path.resolve()) for path in output_paths],
        would_write_paths=[str(path.resolve()) for path in output_paths] if validate_only else None,
    )


__all__ = ["RenderSpecError", "RenderSummary", "run_render_spec"]
