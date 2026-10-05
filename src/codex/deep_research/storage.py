"""Topic-keyed, content-addressed persistence for research bundles."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from codex.deep_research.providers import contains_sensitive_material, redact_sensitive_text


class TopicResearchStore:
    """Persist immutable research runs under a shared topic index."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def publish(self, topic: str, bundle: dict[str, Any], artifacts: dict[str, bytes]) -> Path:
        """Write a bundle under a safe topic folder and update topic/global indexes."""
        safe_title, topic_slug = safe_topic_slug(topic)
        bundle_content = artifacts.get("bundle.json")
        if bundle_content is None:
            raise ValueError("Topic research output must include bundle.json")
        run_id = hashlib.sha256(bundle_content).hexdigest()[:24]
        research_id = _required_identifier(bundle.get("research_id"), "research_id")
        checkpoint_id = _required_identifier(
            bundle.get("checkpoint", {}).get("checkpoint_id"), "checkpoint_id"
        )

        root = self.root.resolve()
        root.mkdir(parents=True, exist_ok=True)
        topic_dir = root / topic_slug
        _assert_contained(topic_dir, root)
        topic_dir.mkdir(parents=True, exist_ok=True)
        _assert_contained(topic_dir, root)
        runs_dir = topic_dir / "runs"
        runs_dir.mkdir(exist_ok=True)
        run_dir = runs_dir / run_id
        _assert_contained(run_dir, root)

        artifact_hashes = {
            name: hashlib.sha256(content).hexdigest()
            for name, content in sorted(artifacts.items())
        }
        manifest_path = run_dir / "manifest.json"
        if run_dir.exists():
            if not manifest_path.is_file():
                raise ValueError("Existing topic run has no manifest; refusing to overwrite it")
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
            if existing.get("artifact_sha256") != artifact_hashes:
                raise ValueError("Topic run identifier collision; refusing to overwrite content")
            manifest = existing
        else:
            run_dir.mkdir()
            for name, content in artifacts.items():
                if Path(name).name != name:
                    raise ValueError(f"Invalid research artifact name: {name}")
                _atomic_write(run_dir / name, content)
            manifest = {
                "schema_version": "1.0",
                "topic": safe_title,
                "topic_slug": topic_slug,
                "research_id": research_id,
                "checkpoint_id": checkpoint_id,
                "run_id": run_id,
                "status": bundle.get("status", "incomplete"),
                "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "relative_path": f"{topic_slug}/runs/{run_id}",
                "artifact_sha256": artifact_hashes,
            }
            _atomic_write(manifest_path, _json_bytes(manifest))

        topic_index = _build_topic_index(topic_dir, safe_title, topic_slug)
        _atomic_write(topic_dir / "index.json", _json_bytes(topic_index))
        root_index = _build_root_index(root)
        _atomic_write(root / "index.json", _json_bytes(root_index))
        return run_dir


def safe_topic_slug(topic: str) -> tuple[str, str]:
    """Return a redacted display title and path-safe, collision-resistant topic slug."""
    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Research topic must be a non-empty string")
    if contains_sensitive_material(topic):
        raise ValueError("Research topic contains secret-like credential syntax")
    title = redact_sensitive_text(topic.strip())
    if any(unicodedata.category(character).startswith("C") for character in title):
        raise ValueError("Research topic must not contain control characters")
    normalized = unicodedata.normalize("NFKD", title)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").casefold()
    readable = "-".join(re.findall(r"[a-z0-9]+", ascii_text))[:72].strip("-")
    if not readable:
        readable = "research"
    suffix = hashlib.sha256(title.encode("utf-8")).hexdigest()[:8]
    return title, f"{readable}-{suffix}"


def _build_topic_index(topic_dir: Path, title: str, slug: str) -> dict[str, Any]:
    runs = []
    for manifest_path in sorted((topic_dir / "runs").glob("*/manifest.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("topic_slug") == slug and manifest.get("run_id") == manifest_path.parent.name:
            runs.append(manifest)
    runs.sort(key=lambda item: (item.get("created_at", ""), item["run_id"]))
    return {
        "schema_version": "1.0",
        "topic": title,
        "topic_slug": slug,
        "latest_run_id": runs[-1]["run_id"] if runs else None,
        "runs": [
            {
                "run_id": item["run_id"],
                "research_id": item["research_id"],
                "checkpoint_id": item["checkpoint_id"],
                "status": item["status"],
                "relative_path": item["relative_path"],
                "created_at": item["created_at"],
            }
            for item in runs
        ],
    }


def _build_root_index(root: Path) -> dict[str, Any]:
    topics = []
    for topic_index_path in sorted(root.glob("*/index.json")):
        if topic_index_path.parent.name == "runs":
            continue
        data = json.loads(topic_index_path.read_text(encoding="utf-8"))
        topics.append(
            {
                "topic": data["topic"],
                "topic_slug": data["topic_slug"],
                "index_path": f"{data['topic_slug']}/index.json",
                "latest_run_id": data["latest_run_id"],
                "run_count": len(data["runs"]),
            }
        )
    return {"schema_version": "1.0", "topics": topics}


def _required_identifier(value: Any, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,160}", value):
        raise ValueError(f"Research bundle has an invalid {name}")
    return value


def _assert_contained(path: Path, root: Path) -> None:
    if not path.resolve().is_relative_to(root):
        raise ValueError("Research output path escapes the configured research root")


def _json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def _atomic_write(path: Path, content: bytes) -> None:
    descriptor, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except OSError:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise
