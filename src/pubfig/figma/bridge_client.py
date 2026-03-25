"""Client helpers for talking to the local pubfig Figma bridge."""

from __future__ import annotations

from dataclasses import dataclass
import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import ProxyHandler, Request, build_opener, urlopen


class BridgeClientError(RuntimeError):
    """Raised when the local bridge returns an error or is unreachable."""


_LOCAL_BRIDGE_HOSTS = {"127.0.0.1", "localhost", "::1"}


def _should_bypass_proxy(url: str) -> bool:
    parsed = urlparse(url)
    return (parsed.hostname or "").lower() in _LOCAL_BRIDGE_HOSTS


def _json_request(
    method: str,
    url: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    body = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=body, headers=headers, method=method)
    try:
        opener = build_opener(ProxyHandler({})) if _should_bypass_proxy(url) else None
        open_fn = opener.open if opener is not None else urlopen
        with open_fn(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:  # pragma: no cover - exercised through caller handling
        detail = exc.read().decode("utf-8")
        raise BridgeClientError(f"Bridge request failed: {exc.code} {detail}") from exc
    except URLError as exc:
        raise BridgeClientError(f"Could not reach bridge at {url}: {exc.reason}") from exc


def _endpoint(base_url: str, path: str) -> str:
    base = base_url.rstrip("/") + "/"
    return urljoin(base, path.lstrip("/"))


@dataclass(frozen=True)
class BridgeJobWaitResult:
    """Completed job result returned to CLI callers."""

    job: dict[str, Any]
    waited_seconds: float


def healthcheck_bridge(base_url: str) -> dict[str, Any]:
    """Check whether the bridge is reachable."""
    return _json_request("GET", _endpoint(base_url, "/health"))


def list_bridge_sessions(base_url: str) -> list[dict[str, Any]]:
    """List known bridge sessions."""
    payload = _json_request("GET", _endpoint(base_url, "/sessions"))
    return list(payload.get("sessions", []))


def submit_bridge_job(
    base_url: str,
    *,
    session_id: str,
    bundle: dict[str, Any],
    bundle_provenance: dict[str, Any] | None = None,
    mode: str,
    relayout: bool,
) -> dict[str, Any]:
    """Submit a sync job to the bridge."""
    payload = _json_request(
        "POST",
        _endpoint(base_url, "/jobs"),
        payload={
            "session_id": session_id,
            "bundle": bundle,
            "bundle_provenance": bundle_provenance or {},
            "mode": mode,
            "relayout": relayout,
        },
    )
    return dict(payload["job"])


def get_bridge_job(base_url: str, job_id: str) -> dict[str, Any]:
    """Fetch a bridge job by id."""
    payload = _json_request("GET", _endpoint(base_url, f"/jobs/{job_id}"))
    return dict(payload["job"])


def wait_for_bridge_job(
    base_url: str,
    job_id: str,
    *,
    timeout_seconds: float = 120.0,
    poll_interval_seconds: float = 1.0,
) -> BridgeJobWaitResult:
    """Wait until a bridge job reaches completed or failed."""
    started = time.monotonic()
    while True:
        job = get_bridge_job(base_url, job_id)
        if job.get("status") in {"completed", "failed"}:
            return BridgeJobWaitResult(job=job, waited_seconds=time.monotonic() - started)
        if time.monotonic() - started > timeout_seconds:
            raise BridgeClientError(f"Timed out waiting for bridge job {job_id}")
        time.sleep(poll_interval_seconds)
