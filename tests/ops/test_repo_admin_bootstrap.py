from __future__ import annotations

from scripts.ops.codex_repo_admin_bootstrap import plan_labels


def test_plan_labels_upserts() -> None:
    labels = [{"name": "type: bug", "color": "#ff0000", "description": "Bug"}]
    ops = plan_labels("o", "r", labels)
    assert ops and ops[0][0] == "upsert"
    payload = ops[0][1]
    assert payload["name"] == "type: bug"
    assert payload["color"] == "ff0000"
