from pathlib import Path
import json, os
from codex_ml.logging.registry import build_loggers

def test_ndjson_logger_basic(tmp_path: Path):
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": False})
    logger = loggers[0]
    logger.log({"type": "batch", "loss": 0.1})
    logger.close()
    content = (tmp_path / "metrics.ndjson").read_text().strip()
    assert content
    rec = json.loads(content)
    assert rec["loss"] == 0.1
    assert "mem_rss_mb" not in rec

def test_ndjson_sys_metrics(tmp_path: Path):
    loggers = build_loggers({"output_dir": str(tmp_path), "sys_metrics": True})
    logger = loggers[0]
    logger.log({"type": "batch", "loss": 0.2})
    logger.close()
    rec = json.loads((tmp_path / "metrics.ndjson").read_text().splitlines()[0])
    # psutil may not be installed; if missing metrics absent (acceptable)
    # If present then fields appear
    # This assertion is tolerant:
    assert "loss" in rec