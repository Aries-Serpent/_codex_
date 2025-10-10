"""
Tamper-Evident Audit Logger

Implements a simple hash-chained NDJSON audit log:
Each event includes the SHA256 of the previous record to detect tampering.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class AuditLogger:
    path: Path

    def _last_hash(self) -> str:
        if not self.path.exists():
            return "0" * 64
        lines = [ln for ln in self.path.read_text(encoding="utf-8").splitlines() if ln.strip()]
        if not lines:
            return "0" * 64
        last = json.loads(lines[-1])
        value = last.get("hash")
        return value if isinstance(value, str) else "0" * 64

    def append(self, event: dict[str, Any], *, ts: float | None = None) -> dict[str, Any]:
        prev = self._last_hash()
        payload: dict[str, Any] = {
            "ts": float(ts if ts is not None else time.time()),
            "event": event,
            "prev_hash": prev,
        }
        record_bytes = json.dumps(payload, sort_keys=True).encode("utf-8")
        digest = _sha256_bytes(record_bytes)
        payload["hash"] = digest
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
        return payload

    def verify_chain(self) -> bool:
        if not self.path.exists():
            return True
        prev = "0" * 64
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if not isinstance(rec, dict):
                return False
            expected_prev = prev
            if rec.get("prev_hash") != expected_prev:
                return False
            computed = _sha256_bytes(
                json.dumps({k: rec[k] for k in rec if k != "hash"}, sort_keys=True).encode("utf-8")
            )
            hash_value = rec.get("hash")
            if not isinstance(hash_value, str) or hash_value != computed:
                return False
            prev = hash_value
        return True
