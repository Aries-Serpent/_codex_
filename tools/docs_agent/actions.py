from __future__ import annotations

from .utils import CANONICAL_JSONL_FILES, read_jsonl, utc_now, write_jsonl


def update_action_status(action_id: str, status: str, evidence: str, changed_by: str) -> dict:
    path = CANONICAL_JSONL_FILES["actions"]
    rows = read_jsonl(path)
    updated = None
    for row in rows:
        if row.get("id") == action_id:
            row["status"] = status
            row["updated_at"] = utc_now()
            row.setdefault("evidence", []).append(
                {"evidence": evidence, "changed_by": changed_by, "at": utc_now()}
            )
            updated = row
            break
    write_jsonl(path, rows)
    return {"updated": bool(updated), "action": updated}
