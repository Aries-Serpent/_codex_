#!/usr/bin/env python3
import json
import statistics as stats
from pathlib import Path


def main():
    p = Path("artifacts/logs/perf.ndjson")
    if not p.exists():
        print("no perf log")
        return 0
    cpu, mem = [], []
    for line in p.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
            if "cpu" in row:
                cpu.append(float(row["cpu"]))
            if "mem" in row and isinstance(row["mem"], dict):
                mem.append(float(row["mem"]["percent"]))
        except Exception:
            pass  # Skip malformed lines
    out = {
        "cpu_mean": round(stats.mean(cpu), 3) if cpu else None,
        "mem_mean": round(stats.mean(mem), 3) if mem else None,
    }
    Path("audit_artifacts").mkdir(parents=True, exist_ok=True)
    Path("audit_artifacts/perf_summary.json").write_text(json.dumps(out, indent=2))
    print("audit_artifacts/perf_summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
