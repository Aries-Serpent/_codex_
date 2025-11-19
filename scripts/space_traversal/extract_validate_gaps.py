#!/usr/bin/env python3
"""
Extract validator 'gaps' from a committed gzipped/base64 Phase A snapshot.
"""
from __future__ import annotations
import argparse
import base64
import gzip
import json
import os
import sys
from typing import Any, Dict, List, Tuple

try:
    import requests
except Exception:
    requests = None

GAP_KEYS = {"gaps", "missing_files", "missing", "evidence", "failures", "errors"}

def decode_b64_gz_bytes(b64_bytes: bytes) -> bytes:
    decoded = base64.b64decode(b64_bytes)
    return gzip.decompress(decoded)

def load_from_local(path: str) -> Dict[str, Any]:
    b64 = open(path, "rb").read()
    decoded = decode_b64_gz_bytes(b64)
    return json.loads(decoded)

def load_from_url(url: str) -> Dict[str, Any]:
    if requests is None:
        raise RuntimeError("requests module not available; install requests or provide --input local path")
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    return json.loads(gzip.decompress(base64.b64decode(r.content)))

def walk_for_gaps(obj: Any, path: Tuple[str, ...] = ()) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    def _path_str(p: Tuple[str, ...]) -> str:
        return "/" + "/".join(p) if p else "/"
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + (str(k),)
            if k in GAP_KEYS:
                findings.append(
                    {
                        "locator": _path_str(p),
                        "key": k,
                        "value": v,
                        "summary": summarize_gap_value(k, v),
                    }
                )
            if isinstance(v, (dict, list)):
                findings.extend(walk_for_gaps(v, p))
            else:
                if isinstance(v, str) and ("missing" in v.lower() or "error" in v.lower() or "gap" in v.lower()):
                    findings.append(
                        {"locator": _path_str(p), "key": k, "value": v, "summary": f"Suspicious message: {v}"}
                    )
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            p = path + (f"[{idx}]",)
            if isinstance(item, (dict, list)):
                findings.extend(walk_for_gaps(item, p))
            else:
                if isinstance(item, str) and ("missing" in item.lower() or item.endswith(".py") or item.endswith(".md")):
                    findings.append(
                        {"locator": _path_str(p), "key": "list-item", "value": item, "summary": f"List item: {item}"}
                    )
    return findings

def summarize_gap_value(key: str, value: Any) -> str:
    if key == "missing_files":
        if isinstance(value, list):
            return f"{len(value)} missing files"
        return f"missing_files: {repr(value)}"
    if key == "gaps":
        if isinstance(value, list):
            return f"{len(value)} gap records"
        if isinstance(value, dict):
            return "gaps map"
    if key in ("failures", "errors"):
        if isinstance(value, list):
            return f"{len(value)} failures"
    if key == "evidence":
        if isinstance(value, dict):
            return "evidence object"
    return repr(value)[:160]

def normalize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for f in findings:
        summary = f.get("summary") or ""
        value = f.get("value")
        try:
            short_value = value if isinstance(value, (str, int, float, type(None))) else (value if len(repr(value)) < 800 else repr(value)[:800] + "...")
        except Exception:
            short_value = repr(value)
        out.append(
            {
                "locator": f.get("locator"),
                "key": f.get("key"),
                "summary": summary,
                "value_preview": short_value,
            }
        )
    out.sort(key=lambda x: x.get("locator") or "")
    return out

def write_outputs(out_dir: str, decoded_json: Dict[str, Any], findings: List[Dict[str, Any]]) -> None:
    os.makedirs(out_dir, exist_ok=True)
    full_path = os.path.join(out_dir, "validate_decoded.json")
    gaps_json_path = os.path.join(out_dir, "gaps_extracted.json")
    md_path = os.path.join(out_dir, "gaps_summary.md")
    with open(full_path, "w", encoding="utf-8") as fh:
        json.dump(decoded_json, fh, indent=2, ensure_ascii=False)
    with open(gaps_json_path, "w", encoding="utf-8") as fh:
        json.dump(findings, fh, indent=2, ensure_ascii=False)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write("# Validator GAPs Summary\n\n")
        fh.write("This file enumerates GAP-like findings discovered in the decoded Phase A validator snapshot.\n\n")
        fh.write("| Locator | Key | Summary | Value preview |\n")
        fh.write("|---|---|---|---|\n")
        for f in findings:
            locator = f.get("locator", "")
            key = f.get("key", "")
            summary = (f.get("summary") or "").replace("\n", " ")
            preview = (f.get("value_preview") or "")
            preview = str(preview).replace("|", "\\|")
            fh.write(f"| `{locator}` | `{key}` | {summary} | `{preview}` |\n")
        fh.write("\n\n---\n\n")
        fh.write("Run instructions:\n\n")
        fh.write("```bash\n")
        fh.write("python3 scripts/space_traversal/extract_validate_gaps.py --input artifacts/validate_report_20251119.json.gz.b64 --out-dir ./artifacts/extracted_validate_20251119\n")
        fh.write("```\n")
    print(f"Wrote: {full_path}")
    print(f"Wrote: {gaps_json_path}")
    print(f"Wrote: {md_path}")

def main():
    p = argparse.ArgumentParser(description="Extract validator gaps from committed base64+gz snapshot")
    p.add_argument("--input", help="local b64+gz path to read")
    p.add_argument("--url", help="raw GitHub URL to fetch (optional)")
    p.add_argument("--out-dir", help="output directory", required=True)
    args = p.parse_args()

    if not args.input and not args.url:
        print("Either --input or --url must be provided", file=sys.stderr)
        sys.exit(2)

    if args.url:
        if requests is None:
            print("requests not available; please install or use --input", file=sys.stderr)
            sys.exit(2)
        print(f"Fetching {args.url} ...")
        decoded_json = load_from_url(args.url)
    else:
        if not os.path.exists(args.input):
            print(f"Input file not found: {args.input}", file=sys.stderr)
            sys.exit(2)
        decoded_json = load_from_local(args.input)

    findings_raw = walk_for_gaps(decoded_json)
    findings = normalize_findings(findings_raw)
    write_outputs(args.out_dir, decoded_json, findings)
    print(f"Extracted {len(findings)} gap-like findings (see {args.out_dir})")

if __name__ == "__main__":
    main()
