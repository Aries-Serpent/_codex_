import json
from pathlib import Path

from codex_ml.monitoring.codex_logging import write_ndjson


def test_log_redaction(tmp_path: Path) -> None:
    p = tmp_path / "log.ndjson"
    # GitHub tokens are 36 characters after the ``ghp_`` prefix.
    secret = "ghp_" + "A" * 36  # pragma: allowlist secret
    write_ndjson(p, {"text": secret})
    data = json.loads(p.read_text().strip())
    assert "REDACTED" in data["text"]
    assert data["redactions"]["secrets"] >= 1
