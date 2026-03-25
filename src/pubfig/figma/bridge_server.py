"""HTTP bridge server for pubfig -> Figma plugin automation."""

from __future__ import annotations

from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from typing import Any
from urllib.parse import urlparse

from .bridge_models import BridgeState


class BridgeApiError(RuntimeError):
    """Structured API error for handler responses."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def _read_json_body(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    """Read a JSON body from the handler."""
    content_length = int(handler.headers.get("Content-Length", "0"))
    if content_length <= 0:
        return {}
    payload = handler.rfile.read(content_length).decode("utf-8")
    if not payload.strip():
        return {}
    return json.loads(payload)


def _send_json(handler: BaseHTTPRequestHandler, status_code: int, payload: dict[str, Any]) -> None:
    """Write a JSON response."""
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(encoded)))
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.end_headers()
    handler.wfile.write(encoded)


def _require_str(payload: dict[str, Any], key: str) -> str:
    """Read a required non-empty string field."""
    value = str(payload.get(key, "")).strip()
    if not value:
        raise BridgeApiError(HTTPStatus.BAD_REQUEST, f"Missing required field: {key}")
    return value


class BridgeRequestHandler(BaseHTTPRequestHandler):
    """Request handler for the bridge API."""

    server: "BridgeHttpServer"

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        """Silence default request logging."""
        return

    def do_OPTIONS(self) -> None:  # noqa: N802
        """Handle CORS preflight."""
        _send_json(self, HTTPStatus.OK, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        """Handle GET requests."""
        try:
            payload = self._dispatch_get()
            _send_json(self, HTTPStatus.OK, payload)
        except BridgeApiError as exc:
            _send_json(self, exc.status_code, {"ok": False, "error": exc.message})
        except Exception as exc:  # pragma: no cover - defensive
            _send_json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})

    def do_POST(self) -> None:  # noqa: N802
        """Handle POST requests."""
        try:
            payload = self._dispatch_post()
            _send_json(self, HTTPStatus.OK, payload)
        except BridgeApiError as exc:
            _send_json(self, exc.status_code, {"ok": False, "error": exc.message})
        except Exception as exc:  # pragma: no cover - defensive
            _send_json(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"ok": False, "error": str(exc)})

    def _dispatch_get(self) -> dict[str, Any]:
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]

        if parsed.path == "/health":
            return {"ok": True, "service": "pubfig-figma-bridge"}
        if parsed.path == "/sessions":
            return {"ok": True, "sessions": self.server.state.list_sessions()}
        if len(parts) == 3 and parts[0] == "sessions" and parts[2] == "next-job":
            job = self.server.state.next_job_for_session(parts[1])
            return {"ok": True, "job": job.to_dict(include_bundle=True) if job else None}
        if len(parts) == 2 and parts[0] == "jobs":
            job = self.server.state.get_job(parts[1])
            return {"ok": True, "job": job.to_dict(include_bundle=False)}

        raise BridgeApiError(HTTPStatus.NOT_FOUND, f"Unknown GET endpoint: {parsed.path}")

    def _dispatch_post(self) -> dict[str, Any]:
        parsed = urlparse(self.path)
        parts = [part for part in parsed.path.split("/") if part]
        payload = _read_json_body(self)

        if parsed.path == "/sessions/register":
            session = self.server.state.register_session(
                session_id=str(payload.get("session_id", "")).strip() or None,
                client_name=str(payload.get("client_name", "pubfig-sync")),
                file_name=str(payload.get("file_name", "Untitled")),
                page_name=str(payload.get("page_name", "Page 1")),
                plugin_version=str(payload.get("plugin_version", "")),
                bridge_url=str(payload.get("bridge_url", self.server.public_url)),
                meta=dict(payload.get("meta", {})),
            )
            return {"ok": True, "session": session.to_dict()}

        if len(parts) == 3 and parts[0] == "sessions" and parts[2] == "heartbeat":
            session = self.server.state.heartbeat(parts[1])
            return {"ok": True, "session": session.to_dict()}

        if parsed.path == "/jobs":
            session_id = _require_str(payload, "session_id")
            mode = str(payload.get("mode", "auto")).strip().lower() or "auto"
            bundle = payload.get("bundle")
            bundle_provenance = payload.get("bundle_provenance")
            if not isinstance(bundle, dict):
                raise BridgeApiError(HTTPStatus.BAD_REQUEST, "Field 'bundle' must be an object")
            if bundle_provenance is not None and not isinstance(bundle_provenance, dict):
                raise BridgeApiError(HTTPStatus.BAD_REQUEST, "Field 'bundle_provenance' must be an object when provided")
            job = self.server.state.create_job(
                session_id=session_id,
                bundle=bundle,
                mode=mode,
                relayout=bool(payload.get("relayout", False)),
                bundle_provenance=bundle_provenance,
            )
            return {"ok": True, "job": job.to_dict(include_bundle=False)}

        if len(parts) == 3 and parts[0] == "jobs" and parts[2] == "result":
            result = payload.get("result")
            if result is not None and not isinstance(result, dict):
                raise BridgeApiError(HTTPStatus.BAD_REQUEST, "Field 'result' must be an object when provided")
            raw_error = payload.get("error")
            error = None if raw_error is None else str(raw_error).strip() or None
            job = self.server.state.complete_job(
                parts[1],
                result=result,
                error=error,
            )
            return {"ok": True, "job": job.to_dict(include_bundle=False)}

        raise BridgeApiError(HTTPStatus.NOT_FOUND, f"Unknown POST endpoint: {parsed.path}")


class BridgeHttpServer(ThreadingHTTPServer):
    """HTTP server wrapper carrying shared bridge state."""

    def __init__(self, server_address: tuple[str, int], public_url: str) -> None:
        super().__init__(server_address, BridgeRequestHandler)
        self.state = BridgeState()
        self.public_url = public_url.rstrip("/")


def serve_bridge(host: str = "127.0.0.1", port: int = 47329) -> None:
    """Start the blocking bridge HTTP server."""
    public_url = f"http://{host}:{port}"
    server = BridgeHttpServer((host, port), public_url=public_url)
    print(json.dumps({"ok": True, "bridge_url": public_url}, ensure_ascii=False), flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
