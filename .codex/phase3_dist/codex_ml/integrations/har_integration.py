"""
HAR (HTTP Archive) Integration Module

Implements HAR file capture, storage, and replay for:
- Caching audit dashboard data for offline viewing
- Storing API responses for reproducible testing
- Recording web function executions for debugging
- Creating portable audit snapshots

Based on HAR 1.2 specification: http://www.softwareishard.com/blog/har-12-spec/
"""

from __future__ import annotations

import gzip
import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

__all__ = [
    "HARCache",
    "HAREntry",
    "HARLog",
    "HARRecorder",
    "HARReplayer",
    "create_audit_snapshot",
    "record_api_call",
]


@dataclass
class HARTimings:
    """Timing information for a request/response cycle."""

    blocked: float = -1
    dns: float = -1
    connect: float = -1
    send: float = 0
    wait: float = 0
    receive: float = 0
    ssl: float = -1

    def to_dict(self) -> dict[str, float]:
        return {
            "blocked": self.blocked,
            "dns": self.dns,
            "connect": self.connect,
            "send": self.send,
            "wait": self.wait,
            "receive": self.receive,
            "ssl": self.ssl,
        }

    @property
    def total(self) -> float:
        return sum(
            v
            for v in [
                self.blocked,
                self.dns,
                self.connect,
                self.send,
                self.wait,
                self.receive,
                self.ssl,
            ]
            if v >= 0
        )


@dataclass
class HARRequest:
    """HTTP request information."""

    method: str
    url: str
    http_version: str = "HTTP/1.1"
    headers: list[dict[str, str]] = field(default_factory=list)
    query_string: list[dict[str, str]] = field(default_factory=list)
    cookies: list[dict[str, str]] = field(default_factory=list)
    post_data: Optional[dict[str, Any]] = None
    headers_size: int = -1
    body_size: int = -1

    def to_dict(self) -> dict[str, Any]:
        result = {
            "method": self.method,
            "url": self.url,
            "httpVersion": self.http_version,
            "headers": self.headers,
            "queryString": self.query_string,
            "cookies": self.cookies,
            "headersSize": self.headers_size,
            "bodySize": self.body_size,
        }
        if self.post_data:
            result["postData"] = self.post_data
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HARRequest:
        return cls(
            method=data["method"],
            url=data["url"],
            http_version=data.get("httpVersion", "HTTP/1.1"),
            headers=data.get("headers", []),
            query_string=data.get("queryString", []),
            cookies=data.get("cookies", []),
            post_data=data.get("postData"),
            headers_size=data.get("headersSize", -1),
            body_size=data.get("bodySize", -1),
        )


@dataclass
class HARResponse:
    """HTTP response information."""

    status: int
    status_text: str
    http_version: str = "HTTP/1.1"
    headers: list[dict[str, str]] = field(default_factory=list)
    cookies: list[dict[str, str]] = field(default_factory=list)
    content: dict[str, Any] = field(default_factory=dict)
    redirect_url: str = ""
    headers_size: int = -1
    body_size: int = -1

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "statusText": self.status_text,
            "httpVersion": self.http_version,
            "headers": self.headers,
            "cookies": self.cookies,
            "content": self.content,
            "redirectURL": self.redirect_url,
            "headersSize": self.headers_size,
            "bodySize": self.body_size,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HARResponse:
        return cls(
            status=data["status"],
            status_text=data["statusText"],
            http_version=data.get("httpVersion", "HTTP/1.1"),
            headers=data.get("headers", []),
            cookies=data.get("cookies", []),
            content=data.get("content", {}),
            redirect_url=data.get("redirectURL", ""),
            headers_size=data.get("headersSize", -1),
            body_size=data.get("bodySize", -1),
        )


@dataclass
class HAREntry:
    """A single HTTP transaction in the HAR log."""

    request: HARRequest
    response: HARResponse
    started_datetime: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    time: float = 0
    timings: HARTimings = field(default_factory=HARTimings)
    cache: dict[str, Any] = field(default_factory=dict)
    server_ip_address: str = ""
    connection: str = ""
    comment: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "startedDateTime": self.started_datetime,
            "time": self.time,
            "request": self.request.to_dict(),
            "response": self.response.to_dict(),
            "cache": self.cache,
            "timings": self.timings.to_dict(),
            "serverIPAddress": self.server_ip_address,
            "connection": self.connection,
            "comment": self.comment,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HAREntry:
        return cls(
            started_datetime=data["startedDateTime"],
            time=data.get("time", 0),
            request=HARRequest.from_dict(data["request"]),
            response=HARResponse.from_dict(data["response"]),
            cache=data.get("cache", {}),
            timings=HARTimings(
                **{
                    k: v
                    for k, v in data.get("timings", {}).items()
                    if k in HARTimings.__dataclass_fields__
                }
            ),
            server_ip_address=data.get("serverIPAddress", ""),
            connection=data.get("connection", ""),
            comment=data.get("comment", ""),
        )


@dataclass
class HARLog:
    """Complete HAR log containing all entries."""

    version: str = "1.2"
    creator: dict[str, str] = field(
        default_factory=lambda: {
            "name": "Codex HAR Recorder",
            "version": "1.0.0",
        }
    )
    browser: Optional[dict[str, str]] = None
    pages: list[dict[str, Any]] = field(default_factory=list)
    entries: list[HAREntry] = field(default_factory=list)
    comment: str = ""

    def to_dict(self) -> dict[str, Any]:
        result = {
            "log": {
                "version": self.version,
                "creator": self.creator,
                "entries": [e.to_dict() for e in self.entries],
            }
        }
        if self.browser:
            result["log"]["browser"] = self.browser
        if self.pages:
            result["log"]["pages"] = self.pages
        if self.comment:
            result["log"]["comment"] = self.comment
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> HARLog:
        log_data = data.get("log", data)
        return cls(
            version=log_data.get("version", "1.2"),
            creator=log_data.get("creator", {"name": "Unknown", "version": "0.0.0"}),
            browser=log_data.get("browser"),
            pages=log_data.get("pages", []),
            entries=[HAREntry.from_dict(e) for e in log_data.get("entries", [])],
            comment=log_data.get("comment", ""),
        )

    def add_entry(self, entry: HAREntry) -> None:
        self.entries.append(entry)

    def save(self, path: Path, compress: bool = False) -> None:
        data = json.dumps(self.to_dict(), indent=2)
        if compress:
            path = path.with_suffix(".har.gz")
            with gzip.open(path, "wt", encoding="utf-8") as f:
                f.write(data)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(data)
        logger.info(f"Saved HAR log to {path} ({len(self.entries)} entries)")

    @classmethod
    def load(cls, path: Path) -> HARLog:
        if str(path).endswith(".gz"):
            with gzip.open(path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        return cls.from_dict(data)


class HARRecorder:
    """Records HTTP transactions into HAR format."""

    def __init__(
        self,
        name: str = "Codex Recording",
        auto_save: bool = False,
        save_path: Optional[Path] = None,
    ):
        self.har_log = HARLog()
        self.name = name
        self.auto_save = auto_save
        self.save_path = save_path
        self._recording = False

    def __enter__(self) -> HARRecorder:
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stop()
        if self.auto_save and self.save_path:
            self.save(self.save_path)

    def start(self) -> None:
        self._recording = True
        logger.info(f"Started HAR recording: {self.name}")

    def stop(self) -> None:
        self._recording = False
        logger.info(f"Stopped HAR recording: {self.name} ({len(self.har_log.entries)} entries)")

    def record_complete_transaction(
        self,
        method: str,
        url: str,
        request_headers: Optional[dict[str, str]] = None,
        request_body: Optional[str] = None,
        status: int = 200,
        status_text: str = "OK",
        response_headers: Optional[dict[str, str]] = None,
        response_body: Optional[str] = None,
        elapsed_ms: float = 0,
    ) -> HAREntry:
        req_header_list = [{"name": k, "value": v} for k, v in (request_headers or {}).items()]
        resp_header_list = [{"name": k, "value": v} for k, v in (response_headers or {}).items()]

        request = HARRequest(
            method=method,
            url=url,
            headers=req_header_list,
            body_size=len(request_body) if request_body else 0,
        )
        if request_body:
            request.post_data = {"mimeType": "application/json", "text": request_body}

        response = HARResponse(
            status=status,
            status_text=status_text,
            headers=resp_header_list,
            body_size=len(response_body) if response_body else 0,
            content={
                "size": len(response_body) if response_body else 0,
                "mimeType": "application/json",
                "text": response_body or "",
            },
        )

        entry = HAREntry(request=request, response=response, time=elapsed_ms)
        entry.timings.wait = elapsed_ms
        self.har_log.add_entry(entry)
        return entry

    def save(self, path: Path, compress: bool = False) -> None:
        self.har_log.save(path, compress)

    def get_entries(self) -> list[HAREntry]:
        return self.har_log.entries


class HARCache:
    """Cache layer using HAR files for API response caching."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._index: dict[str, Path] = {}
        self._load_index()

    def _load_index(self) -> None:
        for har_file in self.cache_dir.glob("*.har*"):
            try:
                har_log = HARLog.load(har_file)
                for entry in har_log.entries:
                    key = self._make_key(entry.request.method, entry.request.url)
                    self._index[key] = har_file
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning(f"Failed to index {har_file}: <ERROR_TYPE>")

    def _make_key(self, method: str, url: str) -> str:
        return hashlib.sha256(f"{method}:{url}".encode()).hexdigest()

    def get(self, method: str, url: str) -> Optional[HAREntry]:
        key = self._make_key(method, url)
        if key in self._index:
            har_file = self._index[key]
            try:
                har_log = HARLog.load(har_file)
                for entry in har_log.entries:
                    if entry.request.method == method and entry.request.url == url:
                        return entry
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning("Failed to load cached entry: <ERROR_TYPE>")
        return None

    def put(self, entry: HAREntry) -> None:
        key = self._make_key(entry.request.method, entry.request.url)
        har_log = HARLog(entries=[entry])
        cache_file = self.cache_dir / f"{key}.har"
        har_log.save(cache_file)
        self._index[key] = cache_file

    def clear(self) -> int:
        count = len(self._index)
        for cache_file in self._index.values():
            try:
                cache_file.unlink()
            except (IOError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.warning(
                    f"Exception: {e}", exc_info=True
                )  # Ignore file deletion errors during cleanup
        self._index.clear()
        return count


class HARReplayer:
    """Replays HAR files for testing and offline operation."""

    def __init__(self, har_log: HARLog):
        self.har_log = har_log
        self._index: dict[str, HAREntry] = {}
        self._build_index()

    def _build_index(self) -> None:
        for entry in self.har_log.entries:
            key = f"{entry.request.method}:{entry.request.url}"
            self._index[key] = entry

    @classmethod
    def from_file(cls, path: Path) -> HARReplayer:
        har_log = HARLog.load(path)
        return cls(har_log)

    def get_response(self, method: str, url: str) -> Optional[HARResponse]:
        key = f"{method}:{url}"
        entry = self._index.get(key)
        return entry.response if entry else None

    def get_response_body(self, method: str, url: str) -> Optional[str]:
        response = self.get_response(method, url)
        if response and response.content:
            return response.content.get("text")
        return None

    def has_entry(self, method: str, url: str) -> bool:
        return f"{method}:{url}" in self._index


def record_api_call(
    method: str,
    url: str,
    response_status: int,
    response_body: str,
    request_body: Optional[str] = None,
    elapsed_ms: float = 0,
) -> HAREntry:
    recorder = HARRecorder()
    return recorder.record_complete_transaction(
        method=method,
        url=url,
        request_body=request_body,
        status=response_status,
        status_text="OK" if response_status < 400 else "Error",
        response_body=response_body,
        elapsed_ms=elapsed_ms,
    )


def create_audit_snapshot(audit_id: str, entries: list[HAREntry], output_dir: Path) -> Path:
    har_log = HARLog(
        creator={"name": "Codex Audit Snapshot", "version": "1.0.0"},
        comment=f"Audit snapshot: {audit_id}",
        entries=entries,
    )
    output_path = output_dir / f"audit-{audit_id}.har.gz"
    har_log.save(output_path, compress=True)
    return output_path
