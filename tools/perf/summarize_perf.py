#!/usr/bin/env python3
"""
Read NDJSON from artifacts/logs/perf.ndjson and produce audit_artifacts/perf_summary.json
Only if CODEX_ENABLE_PERF_SAMPLER=1 or file exists. Safe no-op if missing.
"""
import json
import pathlib
import statistics


def main():
    nd = pathlib.Path("artifacts/logs/perf.ndjson")
    if not nd.exists():
        print("[perf] no perf.ndjson present; skipping")
        return 0
    rows = []
    for line in nd.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    if not rows:
        print("[perf] no rows; skipping")
        return 0
    # aggregate numeric keys
    keys = set().union(*[set(r.keys()) for r in rows])
    agg = {}
    for k in keys:
        vals = [r[k] for r in rows if isinstance(r.get(k), (int, float))]
        if not vals:
            continue
        agg[k] = {
            "count": len(vals),
            "min": min(vals),
            "max": max(vals),
            "mean": statistics.mean(vals),
        }
    outp = pathlib.Path("audit_artifacts/perf_summary.json")
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps({"metrics": agg}, indent=2), encoding="utf-8")
    print(outp)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
