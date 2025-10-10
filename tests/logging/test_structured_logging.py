#!/usr/bin/env python
# Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5
# Purpose: Validate structured (NDJSON) logging write/read locally.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.mark.smoke
def test_logging_write_and_read_ndjson(tmp_path: Path):
    log = tmp_path / "events.ndjson"
    events = [
        {"ts": datetime.now(timezone.utc).isoformat(), "level": "INFO", "msg": "start"},
        {"ts": datetime.now(timezone.utc).isoformat(), "level": "INFO", "msg": "done"},
    ]
    with log.open("w", encoding="utf-8") as fh:
        for e in events:
            fh.write(json.dumps(e, sort_keys=True) + "\n")
    lines = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) == 2
    assert all({"ts", "level", "msg"} <= set(e) for e in lines)
