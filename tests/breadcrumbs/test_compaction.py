from pathlib import Path

import pytest

pytest.importorskip("pandas")

from tools import compact_ledger_to_parquet as clp  # noqa: E402
from tools import ledger  # noqa: E402


def test_parquet_roundtrip(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger.append_event({"event": "start", "status": "ok", "run_id": "r1"}, ledger_path)
    outs = clp.compact(ledger_path)
    assert len(outs) == 1
    assert outs[0].exists()
