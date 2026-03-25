"""In-memory models for the pubfig local Figma bridge."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any
from uuid import uuid4


def utc_now_iso() -> str:
    """Return a compact UTC ISO timestamp."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class BridgeSession:
    """A connected Figma plugin bridge session."""

    session_id: str
    client_name: str
    file_name: str
    page_name: str
    plugin_version: str
    bridge_url: str
    connected_at: str
    last_seen: str
    meta: dict[str, Any] = field(default_factory=dict)

    def touch(self) -> None:
        """Update heartbeat timestamp."""
        self.last_seen = utc_now_iso()

    def to_dict(self) -> dict[str, Any]:
        """Serialize the session for API responses."""
        return {
            "session_id": self.session_id,
            "client_name": self.client_name,
            "file_name": self.file_name,
            "page_name": self.page_name,
            "plugin_version": self.plugin_version,
            "bridge_url": self.bridge_url,
            "connected_at": self.connected_at,
            "last_seen": self.last_seen,
            "meta": dict(self.meta),
        }


@dataclass
class BridgeJob:
    """A queued import/refresh job for a connected Figma plugin session."""

    job_id: str
    session_id: str
    bundle: dict[str, Any]
    mode: str
    relayout: bool
    status: str
    submitted_at: str
    bundle_provenance: dict[str, Any] = field(default_factory=dict)
    started_at: str | None = None
    finished_at: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self, *, include_bundle: bool = False) -> dict[str, Any]:
        """Serialize the job for API responses."""
        payload = {
            "job_id": self.job_id,
            "session_id": self.session_id,
            "mode": self.mode,
            "relayout": self.relayout,
            "status": self.status,
            "submitted_at": self.submitted_at,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "result": self.result,
            "error": self.error,
            "figure_id": str(self.bundle.get("figure_id", "")),
            "bundle_provenance": dict(self.bundle_provenance),
        }
        if include_bundle:
            payload["bundle"] = self.bundle
        return payload


class BridgeState:
    """Thread-safe state store for bridge sessions and jobs."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._sessions: dict[str, BridgeSession] = {}
        self._jobs: dict[str, BridgeJob] = {}

    def register_session(
        self,
        *,
        session_id: str | None,
        client_name: str,
        file_name: str,
        page_name: str,
        plugin_version: str,
        bridge_url: str,
        meta: dict[str, Any] | None = None,
    ) -> BridgeSession:
        """Create or update a bridge session."""
        with self._lock:
            final_session_id = session_id or str(uuid4())
            now = utc_now_iso()
            session = self._sessions.get(final_session_id)
            if session is None:
                session = BridgeSession(
                    session_id=final_session_id,
                    client_name=client_name,
                    file_name=file_name,
                    page_name=page_name,
                    plugin_version=plugin_version,
                    bridge_url=bridge_url,
                    connected_at=now,
                    last_seen=now,
                    meta=dict(meta or {}),
                )
                self._sessions[final_session_id] = session
            else:
                session.client_name = client_name
                session.file_name = file_name
                session.page_name = page_name
                session.plugin_version = plugin_version
                session.bridge_url = bridge_url
                session.meta = dict(meta or session.meta)
                session.touch()
            return session

    def heartbeat(self, session_id: str) -> BridgeSession:
        """Refresh last_seen for an existing session."""
        with self._lock:
            session = self._sessions[session_id]
            session.touch()
            return session

    def list_sessions(self) -> list[dict[str, Any]]:
        """Return all sessions sorted by recency."""
        with self._lock:
            sessions = sorted(self._sessions.values(), key=lambda item: item.last_seen, reverse=True)
            return [session.to_dict() for session in sessions]

    def create_job(
        self,
        *,
        session_id: str,
        bundle: dict[str, Any],
        mode: str,
        relayout: bool,
        bundle_provenance: dict[str, Any] | None = None,
    ) -> BridgeJob:
        """Queue a new bridge job."""
        with self._lock:
            if session_id not in self._sessions:
                raise KeyError(f"Unknown session_id: {session_id}")
            job = BridgeJob(
                job_id=str(uuid4()),
                session_id=session_id,
                bundle=bundle,
                mode=mode,
                relayout=relayout,
                status="queued",
                submitted_at=utc_now_iso(),
                bundle_provenance=dict(bundle_provenance or {}),
            )
            self._jobs[job.job_id] = job
            return job

    def next_job_for_session(self, session_id: str) -> BridgeJob | None:
        """Return the next queued job for a session and mark it in progress."""
        with self._lock:
            session = self._sessions[session_id]
            session.touch()
            queued_jobs = [
                job for job in self._jobs.values() if job.session_id == session_id and job.status == "queued"
            ]
            if not queued_jobs:
                return None
            next_job = sorted(queued_jobs, key=lambda item: item.submitted_at)[0]
            next_job.status = "in_progress"
            next_job.started_at = utc_now_iso()
            return next_job

    def get_job(self, job_id: str) -> BridgeJob:
        """Return a job by id."""
        with self._lock:
            return self._jobs[job_id]

    def complete_job(self, job_id: str, *, result: dict[str, Any] | None, error: str | None) -> BridgeJob:
        """Mark a job completed or failed."""
        with self._lock:
            job = self._jobs[job_id]
            job.finished_at = utc_now_iso()
            final_result = dict(result) if result is not None else None
            if final_result is not None:
                existing_provenance = final_result.get("bundle_provenance")
                if not isinstance(existing_provenance, dict) or not existing_provenance:
                    final_result["bundle_provenance"] = dict(job.bundle_provenance)
            job.result = final_result
            job.error = error
            job.status = "failed" if error else "completed"
            return job
