# [Module]: NDJSON logger
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import json
import os
from typing import Any, Dict


class NDJSONLogger:
    def __init__(self, path: str = ".artifacts/metrics.ndjson"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self.f = open(path, "a", encoding="utf-8")

    def write(self, record: Dict[str, Any]) -> None:
        self.f.write(json.dumps(record, ensure_ascii=False) + "\n")
        self.f.flush()

    def close(self) -> None:
        try:
            self.f.flush()
            self.f.close()
        except Exception:
            pass
