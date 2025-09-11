from pathlib import Path

from tools import compact_ledger_to_parquet as clp
from tools import ledger


def test_parquet_roundtrip(tmp_path: Path) -> None:
    ledger_path = tmp_path / 'ledger.jsonl'
    ledger.append_event({'event': 'start', 'status': 'ok', 'run_id': 'r1'}, ledger_path)
    out = clp.compact(ledger_path)
    assert out.exists()
