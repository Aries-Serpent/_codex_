#!/usr/bin/env python
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
import argparse
import json
from pathlib import Path


def parse_requirements(paths: list[Path]) -> list[str]:
    pkgs: list[str] = []
    for p in paths:
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # naive parse
            name = line.split(";", 1)[0].split("==")[0].split(">=")[0].split("<=")[0].strip()
            if name:
                pkgs.append(name.lower())
    return sorted(set(pkgs))


def load_allowlist(p: Path) -> dict[str, str]:
    if not p.exists():
        return {}
    try:
        import yaml

        data = yaml.safe_load(p.read_text())
    except Exception:
        logger.warning("Exception occurred", exc_info=True)
        logger.warning("Exception occurred", exc_info=True)
        data = None
    if isinstance(data, dict):
        return {k.lower(): str(v) for k, v in data.items()}
    return {}


def main():
    ap = argparse.ArgumentParser(description="Dependency allowlist check (offline)")
    ap.add_argument(
        "--req", action="append", default=["requirements.txt"], help="requirements files"
    )
    ap.add_argument("--allowlist", default="configs/security/dependency_allowlist.yaml")
    ap.add_argument("--out", default="artifacts/security/deps_report.json")
    args = ap.parse_args()

    reqs = [Path(r) for r in args.req]
    pkgs = parse_requirements(reqs)
    allow = load_allowlist(Path(args.allowlist))

    unknown = [p for p in pkgs if allow and (p not in allow)]
    payload = {
        "requirements": pkgs,
        "allowlist_size": len(allow),
        "unknown": sorted(unknown),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    if unknown:
        print(f"Unknown dependencies found: {len(unknown)}. See {out}")
        raise SystemExit(3)
    print(f"Dependency check OK. Report: {out}")


if __name__ == "__main__":
    main()
