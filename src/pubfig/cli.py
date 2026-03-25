"""Command-line interface for pubfig."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Sequence
from urllib.parse import urlparse

from ._version import __version__
from .figma import (
    BridgeClientError,
    healthcheck_bridge,
    inspect_figma_bundle,
    list_bridge_sessions,
    materialize_figma_sync_bundle,
    package_figma_bundle,
    resolve_figma_bundle_output_path,
    serve_bridge,
    submit_bridge_job,
    validate_figma_bundle,
    wait_for_bridge_job,
)


_DEFAULT_BRIDGE_URL = "http://localhost:47329"
_DEFAULT_WATCH_INTERVAL_SECONDS = 1.0
_DEFAULT_PUSH_BRIDGE_START_TIMEOUT_SECONDS = 5.0
_LOCAL_BRIDGE_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _parse_row_panel_counts(value: str) -> tuple[int, ...]:
    parts = [item.strip() for item in str(value).split(",") if item.strip()]
    if not parts:
        raise argparse.ArgumentTypeError("row panel counts must be a comma-separated list like 2,2 or 3,1")
    try:
        counts = tuple(int(item) for item in parts)
    except ValueError as error:
        raise argparse.ArgumentTypeError("row panel counts must contain integers only") from error
    if any(count <= 0 for count in counts):
        raise argparse.ArgumentTypeError("row panel counts must contain positive integers only")
    return counts


def _figma_bundle_kwargs(args: argparse.Namespace) -> dict:
    bundle_kwargs = {
        "figure_id": args.figure_id,
        "title": args.title,
        "preset": args.preset,
        "columns": args.columns,
        "row_panel_counts": getattr(args, "row_panel_counts", None),
        "panel_gap": args.panel_gap,
        "shared_title": args.shared_title,
        "shared_legend": args.shared_legend,
        "legend_position": args.legend_position,
        "preserve_positions_on_refresh": args.preserve_positions_on_refresh,
        "label_offset_x": args.label_offset_x,
        "label_offset_y": args.label_offset_y,
        "label_align_x": args.label_align_x,
        "label_align_y": args.label_align_y,
    }
    filtered: dict[str, object] = {}
    for key, value in bundle_kwargs.items():
        if value is None:
            continue
        if key in {"shared_title", "shared_legend"} and value is False:
            continue
        if key == "legend_position" and str(value) == "right":
            continue
        filtered[key] = value
    return filtered


def _add_panel_label_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--label-offset-x",
        type=float,
        default=None,
        help="Horizontal offset for panel labels outside the panel frame.",
    )
    parser.add_argument(
        "--label-offset-y",
        type=float,
        default=None,
        help="Vertical offset for panel labels outside the panel frame.",
    )
    parser.add_argument(
        "--label-align-x",
        choices=("panel", "column"),
        default=None,
        help="Align label x positions to each panel or to the column baseline.",
    )
    parser.add_argument(
        "--label-align-y",
        choices=("panel", "row"),
        default=None,
        help="Align label y positions to each panel or to the row baseline.",
    )


def _resolve_session_id(bridge_url: str, requested_session: str | None) -> str:
    sessions = list_bridge_sessions(bridge_url)
    if not sessions:
        raise BridgeClientError(
            "No connected pubfig-sync bridge session found. Open the Figma plugin and click Connect Bridge first."
        )
    if requested_session:
        if requested_session == "latest":
            return str(sessions[0]["session_id"])
        for session in sessions:
            if str(session["session_id"]) == requested_session:
                return str(session["session_id"])
        raise BridgeClientError(f"Requested session_id not found: {requested_session}")
    if len(sessions) == 1:
        return str(sessions[0]["session_id"])
    raise BridgeClientError(
        "Multiple connected bridge sessions found. Pass --session <session_id> or --session latest explicitly."
    )


def _sync_once(args: argparse.Namespace) -> dict:
    if args.bundle_output and not args.write_bundle:
        raise ValueError("--bundle-output requires --write-bundle")
    resolved = materialize_figma_sync_bundle(
        args.source,
        write_bundle=bool(args.write_bundle),
        bundle_output=args.bundle_output,
        **_figma_bundle_kwargs(args),
    )
    bundle = resolved["bundle"]
    bundle_provenance = {
        "source_kind": resolved["source_kind"],
        "source_path": resolved["source_path"],
        "bundle_path": resolved.get("bundle_path"),
        "bundle_written": bool(resolved.get("bundle_written", False)),
        "bundle_origin": (
            "written_bundle"
            if resolved.get("bundle_written")
            else "existing_bundle"
            if resolved["source_kind"] == "bundle_file"
            else "in_memory_panel_dir"
        ),
    }
    session_id = _resolve_session_id(args.bridge_url, args.session)
    job = submit_bridge_job(
        args.bridge_url,
        session_id=session_id,
        bundle=bundle,
        bundle_provenance=bundle_provenance,
        mode=args.mode,
        relayout=args.relayout,
    )
    wait_result = wait_for_bridge_job(
        args.bridge_url,
        str(job["job_id"]),
        timeout_seconds=float(args.timeout),
    )
    final_job = wait_result.job
    return {
        "ok": final_job.get("status") == "completed",
        "bridge_url": args.bridge_url,
        "session_id": session_id,
        "job_id": final_job.get("job_id"),
        "status": final_job.get("status"),
        "figure_id": bundle.get("figure_id"),
        "source_kind": resolved["source_kind"],
        "source_path": resolved["source_path"],
        "bundle_written": resolved.get("bundle_written", False),
        "bundle_path": resolved.get("bundle_path"),
        "bundle_provenance": final_job.get("bundle_provenance", bundle_provenance),
        "waited_seconds": round(wait_result.waited_seconds, 3),
        "result": final_job.get("result"),
        "error": final_job.get("error"),
    }


def _can_autostart_bridge(bridge_url: str) -> bool:
    parsed = urlparse(str(bridge_url).strip())
    host = (parsed.hostname or "").lower()
    return host in _LOCAL_BRIDGE_HOSTS


def _bridge_host_port(bridge_url: str) -> tuple[str, int]:
    parsed = urlparse(str(bridge_url).strip())
    host = parsed.hostname or "127.0.0.1"
    port = int(parsed.port) if parsed.port is not None else 47329
    return host, port


def _ensure_bridge_running(
    bridge_url: str,
    *,
    startup_timeout_seconds: float = _DEFAULT_PUSH_BRIDGE_START_TIMEOUT_SECONDS,
    poll_interval_seconds: float = 0.2,
) -> dict[str, object]:
    """Ensure the local bridge is reachable, auto-starting it for localhost URLs."""

    try:
        return {
            "bridge_url": bridge_url,
            "bridge_started": False,
            "bridge": healthcheck_bridge(bridge_url),
        }
    except BridgeClientError as error:
        if not _can_autostart_bridge(bridge_url):
            raise BridgeClientError(
                f"Bridge is not reachable at {bridge_url}. Auto-start is only supported for localhost bridge URLs."
            ) from error

        host, port = _bridge_host_port(bridge_url)
        try:
            subprocess.Popen(  # noqa: S603 - trusted local command assembled from fixed args
                [
                    sys.executable,
                    "-m",
                    "pubfig.cli",
                    "figma",
                    "bridge",
                    "start",
                    "--host",
                    host,
                    "--port",
                    str(port),
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
        except OSError as start_error:
            raise BridgeClientError(
                f"Failed to auto-start local bridge at {bridge_url}: {start_error}"
            ) from start_error

        deadline = time.monotonic() + max(float(startup_timeout_seconds), 0.5)
        last_error = str(error)
        while time.monotonic() < deadline:
            time.sleep(max(float(poll_interval_seconds), 0.05))
            try:
                return {
                    "bridge_url": bridge_url,
                    "bridge_started": True,
                    "bridge": healthcheck_bridge(bridge_url),
                }
            except BridgeClientError as retry_error:
                last_error = str(retry_error)

        raise BridgeClientError(
            f"Auto-started local bridge at {bridge_url}, but it did not become ready within "
            f"{float(startup_timeout_seconds):.1f}s. Last error: {last_error}"
        )


def _handle_push(args: argparse.Namespace) -> dict:
    """Agent-first wrapper around sync with auto bridge/session defaults."""

    bridge_state = _ensure_bridge_running(
        args.bridge_url,
        startup_timeout_seconds=float(args.bridge_start_timeout),
    )
    args.write_bundle = True
    if not getattr(args, "session", None):
        args.session = "latest"
    result = _sync_once(args)
    result["bridge_started"] = bool(bridge_state["bridge_started"])
    result["push_defaults"] = {
        "session": args.session,
        "write_bundle": bool(args.write_bundle),
        "mode": args.mode,
        "relayout": bool(args.relayout),
    }
    return result


def _watch_event_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _detect_source_kind(source: str | Path) -> str:
    candidate = Path(source).expanduser().resolve()
    if candidate.is_dir():
        return "panel_dir"
    if candidate.is_file():
        return "bundle_file"
    return "unknown"


def _iter_watch_paths(source: str | Path) -> list[Path]:
    candidate = Path(source).expanduser().resolve()
    if candidate.is_file():
        return [candidate]
    if candidate.is_dir():
        return [candidate / "panel-index.json", *sorted(candidate.glob("*.svg"))]
    return [candidate]


def _snapshot_mtimes(source: str | Path) -> dict[str, float]:
    snapshot: dict[str, float] = {}
    for path in _iter_watch_paths(source):
        if path.exists():
            snapshot[str(path)] = path.stat().st_mtime
    return snapshot


def _diff_watch_snapshot(previous: dict[str, float], current: dict[str, float]) -> dict[str, list[str]]:
    previous_paths = set(previous)
    current_paths = set(current)
    added = sorted(current_paths - previous_paths)
    removed = sorted(previous_paths - current_paths)
    modified = sorted(
        path for path in (previous_paths & current_paths) if previous[path] != current[path]
    )
    return {
        "added_paths": added,
        "removed_paths": removed,
        "modified_paths": modified,
        "changed_paths": [*added, *modified, *removed],
    }


def _expected_watch_bundle_path(args: argparse.Namespace) -> str | None:
    if not args.write_bundle:
        return None
    source_kind = _detect_source_kind(args.source)
    if source_kind == "bundle_file":
        return str(Path(args.source).expanduser().resolve())
    if source_kind == "panel_dir":
        return str(
            resolve_figma_bundle_output_path(
                args.source,
                output_path=args.bundle_output,
                figure_id=args.figure_id,
            )
        )
    return None


def _handle_watch(args: argparse.Namespace) -> int:
    interval_seconds = max(float(args.interval), _DEFAULT_WATCH_INTERVAL_SECONDS)
    last_snapshot = _snapshot_mtimes(args.source)
    source_kind = _detect_source_kind(args.source)
    _print_json(
        {
            "ok": True,
            "watch_event": "started",
            "event_at": _watch_event_timestamp(),
            "watching": str(Path(args.source).expanduser().resolve()),
            "source_kind": source_kind,
            "interval_seconds": interval_seconds,
            "bridge_url": args.bridge_url,
            "session": args.session or "auto",
            "write_bundle": bool(args.write_bundle),
            "expected_bundle_path": _expected_watch_bundle_path(args),
            "manual_fallback": {
                "ready": bool(_expected_watch_bundle_path(args)),
                "bundle_path": _expected_watch_bundle_path(args),
                "strategy": (
                    "reuse-existing-bundle"
                    if source_kind == "bundle_file"
                    else "write-exact-bundle-per-sync"
                    if args.write_bundle
                    else "none"
                ),
            },
        }
    )
    event_index = 0
    try:
        while True:
            time.sleep(interval_seconds)
            current_snapshot = _snapshot_mtimes(args.source)
            if current_snapshot != last_snapshot:
                changes = _diff_watch_snapshot(last_snapshot, current_snapshot)
                last_snapshot = current_snapshot
                result = _sync_once(args)
                event_index += 1
                manual_fallback_source = None
                if result.get("bundle_path"):
                    manual_fallback_source = (
                        "written_bundle" if result.get("bundle_written") else "existing_bundle"
                    )
                _print_json(
                    {
                        "watch_event": "synced",
                        "event_at": _watch_event_timestamp(),
                        "watch_sequence": event_index,
                        "watch_trigger": changes,
                        "manual_fallback": {
                            "ready": bool(result.get("bundle_path")),
                            "bundle_path": result.get("bundle_path"),
                            "source": manual_fallback_source,
                        },
                        **result,
                    }
                )
    except KeyboardInterrupt:
        return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pubfig", description="Publication-ready plotting with Matplotlib.")
    parser.add_argument("--version", action="version", version=f"pubfig {__version__}")

    subparsers = parser.add_subparsers(dest="command", required=True)

    figma_parser = subparsers.add_parser("figma", help="Figma-oriented bundle workflows.")
    figma_subparsers = figma_parser.add_subparsers(dest="figma_command", required=True)

    package_parser = figma_subparsers.add_parser(
        "package",
        help="Package an exported panel directory into a single plugin-friendly Figma bundle JSON file.",
    )
    package_parser.add_argument("panel_dir", help="Directory containing panel-index.json and SVG panel assets.")
    package_parser.add_argument("-o", "--output", dest="output_path", help="Output bundle JSON path.")
    package_parser.add_argument("--figure-id", help="Stable figure identifier for Figma plugin refresh.")
    package_parser.add_argument("--title", help="Optional figure title stored in the bundle metadata.")
    package_parser.add_argument(
        "--preset",
        choices=("auto", "grid", "row", "column", "two_by_two", "hero_left", "hero_top"),
        default=None,
        help="Override the plugin default relayout preset for this bundle.",
    )
    package_parser.add_argument("--columns", type=int, default=None, help="Override the plugin default grid column count.")
    package_parser.add_argument(
        "--row-panel-counts",
        type=_parse_row_panel_counts,
        default=None,
        help="Explicit per-row panel counts, e.g. 2,2 or 3,1. Cannot be combined with --columns.",
    )
    package_parser.add_argument("--panel-gap", type=float, default=None, help="Override the plugin default panel gap.")
    package_parser.add_argument(
        "--shared-title",
        action="store_true",
        help="Add a shared title placeholder to the bundle.",
    )
    package_parser.add_argument(
        "--shared-legend",
        action="store_true",
        help="Add a shared legend placeholder to the bundle.",
    )
    package_parser.add_argument(
        "--legend-position",
        choices=("right", "bottom"),
        default="right",
        help="Placement hint for the shared legend placeholder.",
    )
    package_parser.add_argument(
        "--preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_true",
        default=None,
        help="Override the plugin default and preserve manual panel positions during refresh.",
    )
    package_parser.add_argument(
        "--no-preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_false",
        help="Override the plugin default and allow refresh to reapply layout instead of preserving user-adjusted positions.",
    )
    _add_panel_label_args(package_parser)

    validate_parser = figma_subparsers.add_parser(
        "validate",
        help="Validate either an exported panel directory or a packaged Figma bundle JSON file.",
    )
    validate_parser.add_argument("path", help="Panel directory or bundle JSON path.")

    inspect_parser = figma_subparsers.add_parser(
        "inspect",
        help="Inspect a packaged Figma bundle JSON file and print a compact summary.",
    )
    inspect_parser.add_argument("path", help="Bundle JSON path.")

    bridge_parser = figma_subparsers.add_parser("bridge", help="Run or inspect the local pubfig Figma bridge.")
    bridge_subparsers = bridge_parser.add_subparsers(dest="bridge_command", required=True)

    bridge_start_parser = bridge_subparsers.add_parser("start", help="Start the local pubfig Figma bridge server.")
    bridge_start_parser.add_argument("--host", default="127.0.0.1", help="Bridge host to bind.")
    bridge_start_parser.add_argument("--port", type=int, default=47329, help="Bridge port to bind.")

    bridge_status_parser = bridge_subparsers.add_parser("status", help="Check bridge health and list sessions.")
    bridge_status_parser.add_argument("--bridge-url", default=_DEFAULT_BRIDGE_URL, help="Bridge base URL.")

    sync_parser = figma_subparsers.add_parser(
        "sync",
        help="Send either a panel directory or a packaged Figma bundle JSON file to a connected pubfig-sync session.",
    )
    sync_parser.add_argument(
        "source",
        help="Panel directory (with panel-index.json) or packaged .pubfig-figma.json bundle file.",
    )
    sync_parser.add_argument("--bridge-url", default=_DEFAULT_BRIDGE_URL, help="Bridge base URL.")
    sync_parser.add_argument(
        "--session",
        help="Target bridge session id. Use 'latest' to target the most recent connected session.",
    )
    sync_parser.add_argument(
        "--mode",
        choices=("auto", "import", "refresh"),
        default="auto",
        help="Import mode for the Figma plugin job.",
    )
    sync_parser.add_argument("--relayout", action="store_true", help="Request relayout during the sync job.")
    sync_parser.add_argument("--timeout", type=float, default=120.0, help="Seconds to wait for job completion.")
    sync_parser.add_argument(
        "--write-bundle",
        action="store_true",
        help="Write the exact bridge payload to disk first so the same bundle can be imported manually in Figma.",
    )
    sync_parser.add_argument(
        "--bundle-output",
        help="Optional bundle JSON output path used together with --write-bundle.",
    )
    sync_parser.add_argument("--figure-id", help="Stable figure identifier for Figma plugin refresh.")
    sync_parser.add_argument("--title", help="Optional figure title stored in the bundle metadata.")
    sync_parser.add_argument(
        "--preset",
        choices=("auto", "grid", "row", "column", "two_by_two", "hero_left", "hero_top"),
        default=None,
        help="Override the plugin default relayout preset for this sync job.",
    )
    sync_parser.add_argument("--columns", type=int, default=None, help="Override the plugin default grid column count.")
    sync_parser.add_argument(
        "--row-panel-counts",
        type=_parse_row_panel_counts,
        default=None,
        help="Explicit per-row panel counts, e.g. 2,2 or 3,1. Cannot be combined with --columns.",
    )
    sync_parser.add_argument("--panel-gap", type=float, default=None, help="Override the plugin default panel gap.")
    sync_parser.add_argument("--shared-title", action="store_true", help="Add a shared title placeholder.")
    sync_parser.add_argument("--shared-legend", action="store_true", help="Add a shared legend placeholder.")
    sync_parser.add_argument(
        "--legend-position",
        choices=("right", "bottom"),
        default="right",
        help="Placement hint for the shared legend placeholder.",
    )
    sync_parser.add_argument(
        "--preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_true",
        default=None,
        help="Override the plugin default and preserve manual panel positions during refresh.",
    )
    sync_parser.add_argument(
        "--no-preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_false",
        help="Override the plugin default and allow refresh to reapply layout instead of preserving user-adjusted positions.",
    )
    _add_panel_label_args(sync_parser)

    push_parser = figma_subparsers.add_parser(
        "push",
        help="Agent-first sync wrapper: ensure local bridge, default to latest session, write bundle, then sync.",
    )
    push_parser.add_argument(
        "source",
        help="Panel directory (with panel-index.json) or packaged .pubfig-figma.json bundle file.",
    )
    push_parser.add_argument("--bridge-url", default=_DEFAULT_BRIDGE_URL, help="Bridge base URL.")
    push_parser.add_argument(
        "--session",
        default=None,
        help="Optional bridge session override. Defaults to latest.",
    )
    push_parser.add_argument(
        "--mode",
        choices=("auto", "import", "refresh"),
        default="auto",
        help="Import mode for the Figma plugin job.",
    )
    push_parser.add_argument("--relayout", action="store_true", help="Request relayout during the sync job.")
    push_parser.add_argument("--timeout", type=float, default=120.0, help="Seconds to wait for job completion.")
    push_parser.add_argument(
        "--bridge-start-timeout",
        type=float,
        default=_DEFAULT_PUSH_BRIDGE_START_TIMEOUT_SECONDS,
        help="Seconds to wait for an auto-started local bridge to become ready.",
    )
    push_parser.add_argument(
        "--bundle-output",
        help="Optional bundle JSON output path used for the auto-enabled --write-bundle behavior.",
    )
    push_parser.add_argument("--figure-id", help="Stable figure identifier for Figma plugin refresh.")
    push_parser.add_argument("--title", help="Optional figure title stored in the bundle metadata.")
    push_parser.add_argument(
        "--preset",
        choices=("auto", "grid", "row", "column", "two_by_two", "hero_left", "hero_top"),
        default=None,
        help="Override the plugin default relayout preset for this push job.",
    )
    push_parser.add_argument("--columns", type=int, default=None, help="Override the plugin default grid column count.")
    push_parser.add_argument(
        "--row-panel-counts",
        type=_parse_row_panel_counts,
        default=None,
        help="Explicit per-row panel counts, e.g. 2,2 or 3,1. Cannot be combined with --columns.",
    )
    push_parser.add_argument("--panel-gap", type=float, default=None, help="Override the plugin default panel gap.")
    push_parser.add_argument("--shared-title", action="store_true", help="Add a shared title placeholder.")
    push_parser.add_argument("--shared-legend", action="store_true", help="Add a shared legend placeholder.")
    push_parser.add_argument(
        "--legend-position",
        choices=("right", "bottom"),
        default="right",
        help="Placement hint for the shared legend placeholder.",
    )
    push_parser.add_argument(
        "--preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_true",
        default=None,
        help="Override the plugin default and preserve manual panel positions during refresh.",
    )
    push_parser.add_argument(
        "--no-preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_false",
        help="Override the plugin default and allow refresh to reapply layout instead of preserving user-adjusted positions.",
    )
    _add_panel_label_args(push_parser)

    watch_parser = figma_subparsers.add_parser(
        "watch",
        help="Watch a panel directory or packaged bundle file and auto-sync changes to a connected bridge session.",
    )
    watch_parser.add_argument(
        "source",
        help="Panel directory (with panel-index.json) or packaged .pubfig-figma.json bundle file.",
    )
    watch_parser.add_argument("--bridge-url", default=_DEFAULT_BRIDGE_URL, help="Bridge base URL.")
    watch_parser.add_argument(
        "--session",
        help="Target bridge session id. Use 'latest' to target the most recent connected session.",
    )
    watch_parser.add_argument(
        "--mode",
        choices=("auto", "import", "refresh"),
        default="auto",
        help="Import mode for the Figma plugin job.",
    )
    watch_parser.add_argument("--relayout", action="store_true", help="Request relayout during sync jobs.")
    watch_parser.add_argument("--timeout", type=float, default=120.0, help="Seconds to wait for each job.")
    watch_parser.add_argument("--interval", type=float, default=1.0, help="Polling interval in seconds.")
    watch_parser.add_argument(
        "--write-bundle",
        action="store_true",
        help="Write the exact bridge payload to disk first on every sync so the same bundle stays usable for manual import.",
    )
    watch_parser.add_argument(
        "--bundle-output",
        help="Optional bundle JSON output path used together with --write-bundle.",
    )
    watch_parser.add_argument("--figure-id", help="Stable figure identifier for Figma plugin refresh.")
    watch_parser.add_argument("--title", help="Optional figure title stored in the bundle metadata.")
    watch_parser.add_argument(
        "--preset",
        choices=("auto", "grid", "row", "column", "two_by_two", "hero_left", "hero_top"),
        default=None,
        help="Override the plugin default relayout preset for watched sync jobs.",
    )
    watch_parser.add_argument("--columns", type=int, default=None, help="Override the plugin default grid column count.")
    watch_parser.add_argument(
        "--row-panel-counts",
        type=_parse_row_panel_counts,
        default=None,
        help="Explicit per-row panel counts, e.g. 2,2 or 3,1. Cannot be combined with --columns.",
    )
    watch_parser.add_argument("--panel-gap", type=float, default=None, help="Override the plugin default panel gap.")
    watch_parser.add_argument("--shared-title", action="store_true", help="Add a shared title placeholder.")
    watch_parser.add_argument("--shared-legend", action="store_true", help="Add a shared legend placeholder.")
    watch_parser.add_argument(
        "--legend-position",
        choices=("right", "bottom"),
        default="right",
        help="Placement hint for the shared legend placeholder.",
    )
    watch_parser.add_argument(
        "--preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_true",
        default=None,
        help="Override the plugin default and preserve manual panel positions during refresh.",
    )
    watch_parser.add_argument(
        "--no-preserve-positions-on-refresh",
        dest="preserve_positions_on_refresh",
        action="store_false",
        help="Override the plugin default and allow refresh to reapply layout instead of preserving user-adjusted positions.",
    )
    _add_panel_label_args(watch_parser)

    return parser


def _print_json(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command != "figma":
        parser.error("Unsupported command")

    if args.figma_command == "package":
        bundle_path = package_figma_bundle(
            args.panel_dir,
            output_path=args.output_path,
            **_figma_bundle_kwargs(args),
        )
        _print_json(
            {
                "ok": True,
                "bundle_path": str(Path(bundle_path).resolve()),
            }
        )
        return 0

    if args.figma_command == "validate":
        _print_json(validate_figma_bundle(args.path))
        return 0

    if args.figma_command == "inspect":
        _print_json(inspect_figma_bundle(args.path))
        return 0

    if args.figma_command == "bridge":
        if args.bridge_command == "start":
            serve_bridge(host=args.host, port=args.port)
            return 0
        if args.bridge_command == "status":
            _print_json(
                {
                    "ok": True,
                    "bridge": healthcheck_bridge(args.bridge_url),
                    "sessions": list_bridge_sessions(args.bridge_url),
                }
            )
            return 0

    if args.figma_command == "sync":
        _print_json(_sync_once(args))
        return 0

    if args.figma_command == "push":
        _print_json(_handle_push(args))
        return 0

    if args.figma_command == "watch":
        return _handle_watch(args)

    parser.error("Unsupported figma subcommand")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
