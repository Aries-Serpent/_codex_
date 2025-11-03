from pathlib import Path
import json, time

class JsonLogger:
    def __init__(self, path: str):
        self.p = Path(path); self.p.parent.mkdir(parents=True, exist_ok=True)
    def write(self, **row):
        row.setdefault("ts_unix", time.time())
        with self.p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
