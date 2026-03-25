"""Tests for the pubfig local Figma bridge workflow."""

from __future__ import annotations

import json
import sys
from threading import Thread
import time
from urllib.request import Request, urlopen

import matplotlib.pyplot as plt

from pubfig.cli import main as cli_main
from pubfig.export import export_panels
from pubfig.figma import (
    BridgeClientError,
    build_figma_bundle_payload,
    list_bridge_sessions,
    submit_bridge_job,
    wait_for_bridge_job,
)
from pubfig.figma.bridge_server import BridgeHttpServer


def _make_simple_fig(title: str):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    ax.set_title(title)
    return fig


def _post_json(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request) as response:  # noqa: S310 - local test server only
        return json.loads(response.read().decode("utf-8"))


def _get_json(url: str) -> dict:
    with urlopen(url) as response:  # noqa: S310 - local test server only
        return json.loads(response.read().decode("utf-8"))


def test_build_figma_bundle_payload_in_memory(tmp_path):
    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)

    payload = build_figma_bundle_payload(panel_dir, figure_id="memory-figure", shared_title=True)

    assert payload["figure_id"] == "memory-figure"
    assert payload["placeholders"]["shared_title"]["enabled"] is True
    assert payload["panels"][0]["panel_id"] == "a"

    plt.close(fig_a)


def test_bridge_server_register_submit_and_complete_job(tmp_path):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle = build_figma_bundle_payload(panel_dir, figure_id="bridge-figure")

    register_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.3.0",
            "bridge_url": base_url,
        },
    )
    session_id = register_payload["session"]["session_id"]

    sessions = list_bridge_sessions(base_url)
    assert sessions[0]["session_id"] == session_id

    job = submit_bridge_job(
        base_url,
        session_id=session_id,
        bundle=bundle,
        bundle_provenance={
            "source_kind": "panel_dir",
            "source_path": str(panel_dir.resolve()),
            "bundle_path": str((panel_dir / "bridge-figure.pubfig-figma.json").resolve()),
            "bundle_written": True,
            "bundle_origin": "written_bundle",
        },
        mode="auto",
        relayout=False,
    )
    next_job = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]
    assert next_job["job_id"] == job["job_id"]
    assert next_job["bundle"]["figure_id"] == "bridge-figure"
    assert next_job["bundle_provenance"]["bundle_origin"] == "written_bundle"
    assert next_job["bundle_provenance"]["source_path"] == str(panel_dir.resolve())

    _post_json(
        f"{base_url}/jobs/{job['job_id']}/result",
        {"result": {"root_name": "figure/bridge-figure"}, "error": None},
    )
    waited = wait_for_bridge_job(base_url, job["job_id"], timeout_seconds=2.0)
    assert waited.job["status"] == "completed"
    assert waited.job["result"]["root_name"] == "figure/bridge-figure"
    assert waited.job["result"]["bundle_provenance"]["bundle_path"].endswith("bridge-figure.pubfig-figma.json")

    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_bridge_server_fills_null_bundle_provenance_in_result(tmp_path):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle = build_figma_bundle_payload(panel_dir, figure_id="bridge-null-provenance")

    register_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.4.1",
            "bridge_url": base_url,
        },
    )
    session_id = register_payload["session"]["session_id"]

    job = submit_bridge_job(
        base_url,
        session_id=session_id,
        bundle=bundle,
        bundle_provenance={
            "source_kind": "panel_dir",
            "source_path": str(panel_dir.resolve()),
            "bundle_path": str((panel_dir / "bridge-null-provenance.pubfig-figma.json").resolve()),
            "bundle_written": True,
            "bundle_origin": "written_bundle",
        },
        mode="refresh",
        relayout=False,
    )
    _ = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]

    _post_json(
        f"{base_url}/jobs/{job['job_id']}/result",
        {
            "result": {
                "figure_id": "bridge-null-provenance",
                "root_name": "figure/bridge-null-provenance",
                "page_name": "Page 1",
                "mode": "refresh",
                "relayout": False,
                "bundle_provenance": None,
            },
            "error": None,
        },
    )
    waited = wait_for_bridge_job(base_url, job["job_id"], timeout_seconds=2.0)
    assert waited.job["status"] == "completed"
    assert waited.job["result"]["bundle_provenance"]["bundle_origin"] == "written_bundle"
    assert waited.job["result"]["bundle_provenance"]["bundle_path"].endswith(
        "bridge-null-provenance.pubfig-figma.json"
    )

    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_cli_figma_sync_end_to_end(tmp_path, capsys):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    session_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.3.0",
            "bridge_url": base_url,
        },
    )
    session_id = session_payload["session"]["session_id"]

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)

    def plugin_worker() -> None:
        deadline = time.time() + 5
        while time.time() < deadline:
            next_job = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]
            if next_job is None:
                time.sleep(0.05)
                continue
            _post_json(
                f"{base_url}/jobs/{next_job['job_id']}/result",
                {
                    "result": {
                        "figure_id": next_job["figure_id"],
                        "root_name": "figure/cli-sync",
                        "page_name": "Page 1",
                        "mode": "import",
                        "relayout": False,
                    },
                    "error": None,
                },
            )
            return
        raise BridgeClientError("Timed out waiting for test bridge job")

    worker = Thread(target=plugin_worker, daemon=True)
    worker.start()

    exit_code = cli_main(
        [
            "figma",
            "sync",
            str(panel_dir),
            "--bridge-url",
            base_url,
            "--session",
            session_id,
            "--figure-id",
            "cli-sync-figure",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["status"] == "completed"
    assert payload["session_id"] == session_id
    assert payload["result"]["root_name"] == "figure/cli-sync"

    worker.join(timeout=2)
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_cli_figma_sync_accepts_bundle_file_end_to_end(tmp_path, capsys):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    session_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.3.0",
            "bridge_url": base_url,
        },
    )
    session_id = session_payload["session"]["session_id"]

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_path = panel_dir / "bundle.pubfig-figma.json"
    cli_main(["figma", "package", str(panel_dir), "--figure-id", "bundle-sync-figure", "-o", str(bundle_path)])
    _ = capsys.readouterr()

    def plugin_worker() -> None:
        deadline = time.time() + 5
        while time.time() < deadline:
            next_job = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]
            if next_job is None:
                time.sleep(0.05)
                continue
            _post_json(
                f"{base_url}/jobs/{next_job['job_id']}/result",
                {
                    "result": {
                        "figure_id": next_job["figure_id"],
                        "root_name": "figure/bundle-sync",
                        "page_name": "Page 1",
                        "mode": "refresh",
                        "relayout": False,
                    },
                    "error": None,
                },
            )
            return
        raise BridgeClientError("Timed out waiting for test bridge job")

    worker = Thread(target=plugin_worker, daemon=True)
    worker.start()

    exit_code = cli_main(
        [
            "figma",
            "sync",
            str(bundle_path),
            "--bridge-url",
            base_url,
            "--session",
            session_id,
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["source_kind"] == "bundle_file"
    assert payload["figure_id"] == "bundle-sync-figure"
    assert payload["result"]["root_name"] == "figure/bundle-sync"

    worker.join(timeout=2)
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_cli_figma_sync_write_bundle_end_to_end(tmp_path, capsys):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    session_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.3.0",
            "bridge_url": base_url,
        },
    )
    session_id = session_payload["session"]["session_id"]

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_output = tmp_path / "sync-write.pubfig-figma.json"

    def plugin_worker() -> None:
        deadline = time.time() + 5
        while time.time() < deadline:
            next_job = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]
            if next_job is None:
                time.sleep(0.05)
                continue
            _post_json(
                f"{base_url}/jobs/{next_job['job_id']}/result",
                {
                    "result": {
                        "figure_id": next_job["figure_id"],
                        "root_name": "figure/sync-write-bundle",
                        "page_name": "Page 1",
                        "mode": "refresh",
                        "relayout": False,
                    },
                    "error": None,
                },
            )
            return
        raise BridgeClientError("Timed out waiting for test bridge job")

    worker = Thread(target=plugin_worker, daemon=True)
    worker.start()

    exit_code = cli_main(
        [
            "figma",
            "sync",
            str(panel_dir),
            "--bridge-url",
            base_url,
            "--session",
            session_id,
            "--figure-id",
            "sync-write-bundle",
            "--write-bundle",
            "--bundle-output",
            str(bundle_output),
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["bundle_written"] is True
    assert payload["bundle_path"] == str(bundle_output.resolve())
    assert payload["bundle_provenance"]["bundle_path"] == str(bundle_output.resolve())
    assert payload["bundle_provenance"]["bundle_origin"] == "written_bundle"
    assert bundle_output.exists()

    written_bundle = json.loads(bundle_output.read_text(encoding="utf-8"))
    assert written_bundle["figure_id"] == "sync-write-bundle"
    assert payload["result"]["root_name"] == "figure/sync-write-bundle"
    assert payload["result"]["bundle_provenance"]["bundle_path"] == str(bundle_output.resolve())

    worker.join(timeout=2)
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_cli_figma_sync_bundle_file_write_bundle_reports_existing_path(tmp_path, capsys):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    session_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.3.0",
            "bridge_url": base_url,
        },
    )
    session_id = session_payload["session"]["session_id"]

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)
    bundle_path = panel_dir / "bundle.pubfig-figma.json"
    cli_main(["figma", "package", str(panel_dir), "--figure-id", "bundle-reuse", "-o", str(bundle_path)])
    _ = capsys.readouterr()

    def plugin_worker() -> None:
        deadline = time.time() + 5
        while time.time() < deadline:
            next_job = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]
            if next_job is None:
                time.sleep(0.05)
                continue
            _post_json(
                f"{base_url}/jobs/{next_job['job_id']}/result",
                {
                    "result": {
                        "figure_id": next_job["figure_id"],
                        "root_name": "figure/bundle-reuse",
                        "page_name": "Page 1",
                        "mode": "refresh",
                        "relayout": False,
                    },
                    "error": None,
                },
            )
            return
        raise BridgeClientError("Timed out waiting for test bridge job")

    worker = Thread(target=plugin_worker, daemon=True)
    worker.start()

    exit_code = cli_main(
        [
            "figma",
            "sync",
            str(bundle_path),
            "--bridge-url",
            base_url,
            "--session",
            session_id,
            "--write-bundle",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["bundle_written"] is False
    assert payload["bundle_path"] == str(bundle_path.resolve())
    assert payload["source_kind"] == "bundle_file"
    assert payload["bundle_provenance"]["bundle_path"] == str(bundle_path.resolve())
    assert payload["bundle_provenance"]["bundle_origin"] == "existing_bundle"
    assert payload["result"]["root_name"] == "figure/bundle-reuse"
    assert payload["result"]["bundle_provenance"]["bundle_path"] == str(bundle_path.resolve())

    worker.join(timeout=2)
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_cli_figma_push_end_to_end_defaults_latest_and_write_bundle(tmp_path, capsys):
    server = BridgeHttpServer(("127.0.0.1", 0), public_url="http://127.0.0.1:0")
    port = int(server.server_address[1])
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{port}"

    session_payload = _post_json(
        f"{base_url}/sessions/register",
        {
            "client_name": "pubfig-sync",
            "file_name": "Acceptance File",
            "page_name": "Page 1",
            "plugin_version": "0.4.8",
            "bridge_url": base_url,
        },
    )
    session_id = session_payload["session"]["session_id"]

    fig_a = _make_simple_fig("A")
    panel_dir = tmp_path / "panels"
    export_panels({"a": fig_a}, panel_dir, overwrite=True)

    def plugin_worker() -> None:
        deadline = time.time() + 5
        while time.time() < deadline:
            next_job = _get_json(f"{base_url}/sessions/{session_id}/next-job")["job"]
            if next_job is None:
                time.sleep(0.05)
                continue
            _post_json(
                f"{base_url}/jobs/{next_job['job_id']}/result",
                {
                    "result": {
                        "figure_id": next_job["figure_id"],
                        "root_name": "figure/push-sync",
                        "page_name": "Page 1",
                        "mode": "refresh",
                        "relayout": False,
                    },
                    "error": None,
                },
            )
            return
        raise BridgeClientError("Timed out waiting for test bridge job")

    worker = Thread(target=plugin_worker, daemon=True)
    worker.start()

    exit_code = cli_main(
        [
            "figma",
            "push",
            str(panel_dir),
            "--bridge-url",
            base_url,
            "--figure-id",
            "push-sync-figure",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["session_id"] == session_id
    assert payload["bundle_written"] is True
    assert payload["push_defaults"]["session"] == "latest"
    assert payload["push_defaults"]["write_bundle"] is True
    assert payload["result"]["root_name"] == "figure/push-sync"
    assert payload["bridge_started"] is False

    worker.join(timeout=2)
    server.shutdown()
    server.server_close()
    thread.join(timeout=2)
    plt.close(fig_a)


def test_cli_figma_push_autostarts_local_bridge(monkeypatch, tmp_path, capsys):
    import pubfig.cli as cli_module

    health_calls: list[str] = []
    popen_calls: list[list[str]] = []

    def fake_healthcheck(url: str) -> dict:
        health_calls.append(url)
        if len(health_calls) == 1:
            raise BridgeClientError("bridge down")
        return {"ok": True, "service": "pubfig-figma-bridge"}

    def fake_popen(cmd: list[str], **kwargs):
        popen_calls.append(list(cmd))

        class _DummyProcess:
            pass

        return _DummyProcess()

    def fake_sync_once(args):
        assert args.write_bundle is True
        assert args.session == "latest"
        return {
            "ok": True,
            "bridge_url": args.bridge_url,
            "session_id": "latest-session",
            "job_id": "job-push",
            "status": "completed",
            "figure_id": args.figure_id,
            "source_kind": "panel_dir",
            "source_path": str(args.source),
            "bundle_written": True,
            "bundle_path": str(tmp_path / "push.pubfig-figma.json"),
            "bundle_provenance": {"bundle_origin": "written_bundle"},
            "waited_seconds": 0.01,
            "result": {"root_name": "figure/push"},
            "error": None,
        }

    monkeypatch.setattr(cli_module, "healthcheck_bridge", fake_healthcheck)
    monkeypatch.setattr(cli_module.subprocess, "Popen", fake_popen)
    monkeypatch.setattr(cli_module, "_sync_once", fake_sync_once)

    exit_code = cli_main(
        [
            "figma",
            "push",
            str(tmp_path / "panels"),
            "--figure-id",
            "push-figure",
        ]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["ok"] is True
    assert payload["bridge_started"] is True
    assert payload["push_defaults"]["session"] == "latest"
    assert payload["push_defaults"]["write_bundle"] is True
    assert len(popen_calls) == 1
    assert popen_calls[0][:4] == [sys.executable, "-m", "pubfig.cli", "figma"]
    assert "bridge" in popen_calls[0]
    assert "start" in popen_calls[0]
