"""Append-only JSON ledger with hash chaining.

Provides helpers to append events and verify the chain integrity.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

LEDGER_PATH = Path(".codex/ledger.jsonl")


def _canonical(obj: Dict[str, Any]) -> bytes:
    """Return canonical JSON bytes for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def append_event(event: Dict[str, Any], path: Path = LEDGER_PATH) -> Dict[str, Any]:
    """Append an event to the ledger and return the full record.

    Parameters
    ----------
    event: dict
        Must contain ``event`` and ``status`` keys. ``run_id`` and ``data``
        are optional. ``ts`` is auto-populated in UTC if absent.
    path: Path
        Location of the ledger file.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "ts": _dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "run_id": event.get("run_id")
        or os.environ.get("CODEX_RUN_ID")
        or _dt.datetime.utcnow().strftime("%Y%m%d%H%M%S"),
        "event": event.get("event"),
        "status": event.get("status"),
        "data": event.get("data"),
    }
    prev_hash: Optional[str]
    if path.exists():
        last = path.read_text().splitlines()[-1]
        prev_hash = json.loads(last)["hash"]
    else:
        prev_hash = None
    rec["prev_hash"] = prev_hash
    hash_payload = {k: v for k, v in rec.items() if k != "hash"}
    rec["hash"] = hashlib.sha256(_canonical(hash_payload)).hexdigest()
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True) + "\n")
    return rec


def verify_chain(path: Path = LEDGER_PATH) -> Optional[str]:
    """Validate the ledger chain and return the last hash."""
    if not path.exists():
        return None
    prev: Optional[str] = None
    last_hash: Optional[str] = None
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            rec = json.loads(line)
            payload = {k: v for k, v in rec.items() if k != "hash"}
            calc = hashlib.sha256(_canonical(payload)).hexdigest()
            if calc != rec["hash"]:
                raise ValueError("hash mismatch")
            if rec.get("prev_hash") != prev:
                raise ValueError("prev_hash mismatch")
            prev = rec["hash"]
            last_hash = rec["hash"]
    return last_hash


def _parse_kv(items: list[str]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for item in items:
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v
    return out


def _main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    ap_a = sub.add_parser("append", help="append a ledger event")
    ap_a.add_argument("--event", required=True)
    ap_a.add_argument("--status", required=True)
    ap_a.add_argument("--run-id")
    ap_a.add_argument("--data", action="append", default=[], help="k=v pairs")

    ap_v = sub.add_parser("verify", help="verify ledger chain")
    ap_v.add_argument("--path", default=str(LEDGER_PATH))

    ns = ap.parse_args()
    if ns.cmd == "append":
        data = _parse_kv(ns.data)
        rec = append_event({
            "run_id": ns.run_id,
            "event": ns.event,
            "status": ns.status,
            "data": data,
        })
        print(json.dumps(rec, indent=2))
        return 0
    else:  # verify
        last = verify_chain(Path(ns.path))
        print(last or "")
        return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
