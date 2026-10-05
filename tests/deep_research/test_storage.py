"""Tests for topic-keyed research output persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from codex.deep_research.cli import main
from codex.deep_research.storage import TopicResearchStore, safe_topic_slug


def _bundle(status: str = "incomplete") -> dict[str, Any]:
    return {
        "research_id": "research-123",
        "status": status,
        "checkpoint": {"checkpoint_id": "checkpoint-123"},
    }


def _artifacts(bundle: dict[str, Any]) -> dict[str, bytes]:
    return {
        "bundle.json": json.dumps(bundle, sort_keys=True).encode(),
        "report.md": f"# {bundle['status']}\n".encode(),
    }


def test_safe_topic_slug_is_readable_safe_and_collision_resistant() -> None:
    title, slug = safe_topic_slug("../../EV Ownership: TCO?")
    assert title == "../../EV Ownership: TCO?"
    assert slug.startswith("ev-ownership-tco-")
    assert "/" not in slug
    assert ".." not in slug
    assert len(slug) <= 81
    assert safe_topic_slug("EV Ownership")[1] != safe_topic_slug("ev ownership")[1]
    assert safe_topic_slug("電気自動車")[1].startswith("research-")


@pytest.mark.parametrize("topic", ["", "   ", "research api_key=private"])
def test_safe_topic_slug_rejects_empty_and_credential_like_labels(topic: str) -> None:
    with pytest.raises(ValueError):
        safe_topic_slug(topic)


def test_topic_store_is_idempotent_and_indexes_distinct_content(tmp_path: Path) -> None:
    store = TopicResearchStore(tmp_path)
    topic = "EV ownership costs"
    bundle = _bundle()

    first = store.publish(topic, bundle, _artifacts(bundle))
    repeated = store.publish(topic, bundle, _artifacts(bundle))
    assert first == repeated
    assert (first / "manifest.json").is_file()

    updated = _bundle(status="complete")
    second = store.publish(topic, updated, _artifacts(updated))
    assert first != second

    title, slug = safe_topic_slug(topic)
    topic_index = json.loads((tmp_path / slug / "index.json").read_text())
    root_index = json.loads((tmp_path / "index.json").read_text())
    assert topic_index["topic"] == title
    assert len(topic_index["runs"]) == 2
    assert topic_index["latest_run_id"] == second.name
    assert root_index["topics"][0]["topic_slug"] == slug
    assert root_index["topics"][0]["run_count"] == 2


def test_topic_store_rejects_path_escape_and_invalid_bundle_ids(tmp_path: Path) -> None:
    topic = "safe topic"
    _, slug = safe_topic_slug(topic)
    (tmp_path / slug).symlink_to(tmp_path.parent, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes"):
        TopicResearchStore(tmp_path).publish(topic, _bundle(), _artifacts(_bundle()))

    clean_root = tmp_path / "clean"
    invalid = _bundle()
    invalid["research_id"] = "../outside"
    with pytest.raises(ValueError, match="research_id"):
        TopicResearchStore(clean_root).publish(topic, invalid, _artifacts(invalid))


def test_cli_defaults_to_topic_store_and_uses_explicit_topic(tmp_path: Path) -> None:
    brief_path = Path("examples/deep_research/ev_ownership_cost/brief.json")
    topic = "US Electric Vehicle Efficiency and Ownership Cost Comparison"
    root = tmp_path / "research"
    exit_code = main(
        [
            "--brief",
            str(brief_path),
            "--topic",
            topic,
            "--research-root",
            str(root),
        ]
    )
    assert exit_code == 2
    _, slug = safe_topic_slug(topic)
    topic_index = json.loads((root / slug / "index.json").read_text())
    assert topic_index["topic"] == topic
    run_id = topic_index["latest_run_id"]
    bundle = json.loads((root / slug / "runs" / run_id / "bundle.json").read_text())
    assert bundle["status"] == "incomplete"
    assert bundle["capability"]["fresh_web_research"] is False
    assert len(bundle["objective_matrix"]) == 7
