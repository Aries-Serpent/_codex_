import json
from pathlib import Path

import pytest

from tools import ledger


def test_append_and_verify(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger.append_event({"event": "start", "status": "ok", "run_id": "r1"}, path)
    ledger.append_event({"event": "end", "status": "ok", "run_id": "r1"}, path)
    assert ledger.verify_chain(path)


def test_tamper_detect(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    ledger.append_event({"event": "a", "status": "ok", "run_id": "r1"}, path)
    ledger.append_event({"event": "b", "status": "ok", "run_id": "r1"}, path)
    lines = path.read_text().splitlines()
    first = json.loads(lines[0])
    first["status"] = "bad"
    path.write_text(json.dumps(first) + "\n" + lines[1] + "\n")
    with pytest.raises(ValueError):
        ledger.verify_chain(path)
