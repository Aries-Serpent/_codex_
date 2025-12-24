#!/usr/bin/env python
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
import argparse
import base64
import json
import math
import os
import re
from pathlib import Path

DEFAULT_PATTERNS = [
    # Basic secret-like patterns
    r"AKIA[0-9A-Z]{16}",  # AWS Access Key ID
    r"AIza[0-9A-Za-z\-_]{35}",  # Google API Key
    r"ghp_[0-9A-Za-z]{36}",  # GitHub PAT
    r"ssh-rsa\s+[A-Za-z0-9+/=]+",
    r"BEGIN(?:\s|\-)+PRIVATE(?:\s|\-)+KEY",
]

SAFE_TEXT_EXT = {".py", ".md", ".rst", ".toml", ".yaml", ".yml", ".json", ".txt", ".env"}
MAX_FILE_BYTES = 500_000


def load_patterns(config_file: Path | None) -> list[re.Pattern]:
    pats = [re.compile(p) for p in DEFAULT_PATTERNS]
    if config_file and config_file.exists():
        data = json.loads(config_file.read_text()) if config_file.suffix == ".json" else None
        if not data:
            # YAML-like: read lines of regex under a 'patterns' key or simple list
            try:
                import yaml  # optional

                data = yaml.safe_load(config_file.read_text())
            except Exception:
                logger.warning("Exception occurred", exc_info=True)
                logger.warning("Exception occurred", exc_info=True)
                data = None
        extra = []
        if isinstance(data, dict) and "patterns" in data and isinstance(data["patterns"], list):
            extra = data["patterns"]
        elif isinstance(data, list):
            extra = data
        for p in extra:
            try:
                pats.append(re.compile(p))
            except re.error:
                pass
    return pats


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    freq = {}
    for ch in s:
        freq[ch] = freq.get(ch, 0) + 1
    ent = 0.0
    L = len(s)
    for c in freq.values():
        p = c / L
        ent -= p * math.log2(p)
    return ent


def scan_path(
    root: Path, patterns: list[re.Pattern], entropy_thresh: float = 4.0
) -> tuple[list[dict], int]:
    findings: list[dict] = []
    files_scanned = 0
    for p in sorted(root.rglob("*")):
        if p.is_dir():
            continue
        if p.suffix.lower() not in SAFE_TEXT_EXT:
            continue
        if p.stat().st_size > MAX_FILE_BYTES:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            logger.warning("Exception occurred", exc_info=True)
            logger.warning("Exception occurred", exc_info=True)
            continue
        files_scanned += 1
        # regex hits
        for rx in patterns:
            for m in rx.finditer(text):
                snippet = text[max(0, m.start() - 16) : m.end() + 16]
                findings.append(
                    {
                        "type": "pattern",
                        "pattern": rx.pattern,
                        "path": p.as_posix(),
                        "offset": m.start(),
                        "snippet": snippet[:120],
                    }
                )
        # high entropy tokens (base64-ish, hex-ish)
        tokens = re.findall(r"[A-Za-z0-9+/=]{16,}", text)
        for tok in tokens:
            if shannon_entropy(tok) >= entropy_thresh:
                findings.append(
                    {
                        "type": "entropy",
                        "path": p.as_posix(),
                        "token_preview": tok[:32],
                        "len": len(tok),
                        "entropy": shannon_entropy(tok),
                    }
                )
    return findings, files_scanned


def main():
    ap = argparse.ArgumentParser(description="Runtime secrets scanner (offline, repo-scoped)")
    ap.add_argument("--root", default=".", help="Root directory to scan")
    ap.add_argument("--config", default="", help="Optional patterns config (yaml/json)")
    ap.add_argument(
        "--out", default="artifacts/security/secrets_report.json", help="Output report path"
    )
    ap.add_argument("--entropy", type=float, default=4.0, help="Entropy threshold")
    args = ap.parse_args()

    if os.getenv("DISABLE_SECRET_SCAN") == "1":
        print("Secret scan disabled by DISABLE_SECRET_SCAN=1")
        return

    root = Path(args.root)
    patterns = load_patterns(Path(args.config)) if args.config else load_patterns(None)
    findings, count = scan_path(root, patterns, args.entropy)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "scanned_root": str(root.resolve()),
        "files_scanned": count,
        "findings": sorted(findings, key=lambda x: (x["path"], x.get("offset", 0))),
    }
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    # Exit non-zero on critical patterns
    critical = [f for f in findings if f["type"] == "pattern"]
    if critical:
        print(f"Critical findings: {len(critical)}. See {out_path}")
        raise SystemExit(2)
    print(f"Secret scan OK. Files scanned: {count}. Report: {out_path}")


if __name__ == "__main__":
    main()
