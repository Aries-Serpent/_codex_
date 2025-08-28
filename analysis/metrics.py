import datetime
import json
from pathlib import Path


def log_metric(path: Path, name: str, value, extra: dict | None = None) -> None:
    record = {
        "ts": datetime.datetime.now().isoformat(),
        "name": name,
        "value": value,
    }
    if extra:
        record.update(extra)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")
