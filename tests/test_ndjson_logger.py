from pathlib import Path


def test_ndjson_logger_writes_lines(tmp_path: Path):
    from codex_utils.ndjson import NDJSONLogger

    path = tmp_path / "metrics.ndjson"
    with NDJSONLogger(str(path)) as log:
        log.write({"metric": "loss", "value": 1.0, "_step": 0})
        log.write({"metric": "loss", "value": 0.9, "_step": 1})

    assert path.exists()
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert "\"metric\": \"loss\"" in lines[0]
    assert "\"_step\": 1" in lines[1]

