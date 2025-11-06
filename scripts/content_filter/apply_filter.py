#!/usr/bin/env python
"""
Content Filter (P2 Full Implementation with Knob Normalization)

- Allowlist filtering (profiles A/B/C with combinable syntax e.g. A+B+C)
- PII redaction (minimal / extended / custom) with merge modes:
    PII_MODE=union-minimal | union-extended | replace
- Deterministic masking tokens <REDACT:n>
- Combined mode: allowlist filtering then PII redaction
- Invalid regex patterns skipped & recorded as warnings
- Report JSON: audit_artifacts/content_filter_report.json

Knobs normalized via scripts.config.parse_knobs.normalize_from_env()
"""
from __future__ import annotations
import json, os, re, sys
from pathlib import Path
from typing import List, Dict, Tuple

try:
    from scripts.config.parse_knobs import normalize_from_env
except Exception:
    print("[WARN] parse_knobs not available; falling back to raw env usage", file=sys.stderr)
    def normalize_from_env():
        import os as _os
        return dict(_os.environ), []

ARTIFACTS_DIR = Path("audit_artifacts")
REPORT_PATH = ARTIFACTS_DIR / "content_filter_report.json"

PROFILE_MAP = {
    "A": {".md", ".json", ".py"},
    "B": {".md", ".json", ".py", ".yaml", ".yml", ".toml"},
    "C": {".md", ".json", ".py", ".yaml", ".yml", ".toml", ".rst"},
}

PII_PACKS = {
    "minimal": [
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        r"\b[A-F0-9]{16,24}\b",
    ],
    "extended": [
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        r"\b[A-F0-9]{16,24}\b",
        r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b",
        r"\+?\d[\d\- ]{7,14}\d",
        r"AKIA[0-9A-Z]{16}",
    ],
}

TEXT_EXTENSIONS = {".md",".json",".py",".yaml",".yml",".toml",".rst",".txt",".cfg",".ini"}


def build_extension_set(profile: str, custom_exts: list[str]) -> List[str]:
    exts = set()
    for seg in profile.split("+"):
        if seg in PROFILE_MAP:
            exts |= PROFILE_MAP[seg]
    for t in custom_exts or []:
        t = t if t.startswith(".") else "." + t
        exts.add(t.lower())
    return sorted(exts)


def compile_patterns(base_set: str, custom_list: list[str], merge_mode: str) -> Tuple[List[re.Pattern], List[str], List[str]]:
    invalid: List[str] = []
    base_patterns = PII_PACKS.get(base_set, PII_PACKS["minimal"])
    
    if merge_mode == "replace":
        merged = custom_list or base_patterns
    elif merge_mode == "union-extended":
        merged = list(dict.fromkeys(PII_PACKS["extended"] + custom_list))
    else:  # union-minimal
        merged = list(dict.fromkeys(base_patterns + custom_list))
    
    compiled: List[re.Pattern] = []
    for pat in sorted(merged):
        try:
            compiled.append(re.compile(pat))
        except re.error:
            invalid.append(pat)
    
    return compiled, merged, invalid


def is_text_file(path: Path) -> bool:
    return path.suffix.lower() in TEXT_EXTENSIONS


def redact_text_lines(lines: List[str], compiled_patterns: List[re.Pattern]) -> Tuple[List[str], int]:
    redactions = 0
    mask_counter = 0
    out = []
    for line in lines:
        for rx in compiled_patterns:
            while True:
                m = rx.search(line)
                if not m:
                    break
                mask = f"<REDACT:{mask_counter}>"
                s, e = m.span()
                line = line[:s] + mask + line[e:]
                mask_counter += 1
                redactions += 1
        out.append(line)
    return out, redactions


def process_allowlist(exts: List[str]) -> Tuple[List[str], List[str]]:
    kept, skipped = [], []
    for path in sorted(ARTIFACTS_DIR.rglob("*")):
        if path.is_dir():
            continue
        if path.is_absolute():
            try:
                rel = path.relative_to(Path.cwd()).as_posix()
            except ValueError:
                rel = path.as_posix()
        else:
            rel = path.as_posix()
        if path.suffix.lower() in exts:
            kept.append(rel)
        else:
            skipped.append(rel)
    return kept, skipped


def main():
    knobs, knob_warnings = normalize_from_env()
    
    # Extract normalized values (handle missing keys gracefully)
    mode = knobs.get("CONTENT_FILTER_MODE", "allowlist")
    profile = knobs.get("ALLOWLIST_PROFILE", "A")
    custom_exts = knobs.get("ALLOWLIST_EXT", [])
    base_set = knobs.get("PII_PATTERN_SET", "minimal")
    custom_list = knobs.get("PII_CUSTOM_LIST", [])
    merge_mode = knobs.get("PII_MODE", "union-minimal")
    strategy = knobs.get("PII_REGEX_STRATEGY", "skip-manifest")
    
    if not ARTIFACTS_DIR.exists():
        print("[INFO] No artifacts directory present; skipping filtering.", file=sys.stderr)
        return 0
    
    warnings: list[str] = list(knob_warnings)
    
    if mode == "allowlist":
        exts = build_extension_set(profile, custom_exts)
        kept, skipped = process_allowlist(exts)
        report = {
            "mode": "allowlist",
            "profile": profile,
            "allowlist_extensions": exts,
            "kept_count": len(kept),
            "skipped_count": len(skipped),
            "kept": kept[:200],
            "skipped_sample": skipped[:200],
            "pii_redactions": 0,
            "pii_patterns_applied": [],
            "invalid_patterns": [],
            "warnings": warnings,
        }
    else:
        exts = build_extension_set(profile, custom_exts)
        kept, skipped = process_allowlist(exts)
        compiled, merged_raw, invalid_raw = compile_patterns(base_set, custom_list, merge_mode)
        
        if invalid_raw:
            if strategy == "abort":
                report = {
                    "mode": "pii" if mode == "pii" else "combined",
                    "profile": profile,
                    "allowlist_extensions": exts,
                    "error": "invalid_regex_abort",
                    "invalid_patterns": invalid_raw,
                    "warnings": warnings,
                }
                REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
                REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
                print("[ERR] Aborting due to invalid regex patterns.", file=sys.stderr)
                return 2
            warnings.append(f"invalid_regex:{len(invalid_raw)}")
        
        redactions_total = 0
        for rel in kept:
            p = Path(rel)
            if not p.exists() or not is_text_file(p):
                continue
            try:
                lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
            except Exception:
                continue
            
            redacted_lines, count = redact_text_lines(lines, compiled)
            redactions_total += count
            
            if count > 0:
                sidecar = Path(rel + ".redacted")
                try:
                    sidecar.write_text("\n".join(redacted_lines), encoding="utf-8")
                except Exception as e:
                    warnings.append(f"write_fail:{rel}:{e}")
        
        report = {
            "mode": "combined" if mode == "combined" else "pii",
            "profile": profile,
            "allowlist_extensions": exts,
            "kept_count": len(kept),
            "skipped_count": len(skipped),
            "kept": kept[:200],
            "skipped_sample": skipped[:200],
            "pii_redactions": redactions_total,
            "pii_patterns_applied": merged_raw,
            "invalid_patterns": invalid_raw,
            "warnings": warnings,
        }
    
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"[INFO] Content filter report written: {REPORT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
