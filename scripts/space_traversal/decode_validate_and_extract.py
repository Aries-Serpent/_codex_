#!/usr/bin/env python3
"""
Decode and extract Phase-A validator snapshot(s) committed as base64+gz.
Provides options: --stable-output, --generate-baseline, --baseline-path
"""
from __future__ import annotations
import argparse
import base64
import gzip
import json
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional
from urllib.request import urlopen, Request

DEFAULT_MAX_BYTES = 200 * 1024 * 1024
GAP_KEYS = {"gaps", "missing_files", "missing", "evidence", "failures", "errors"}
DEFAULT_INPUT = Path("tests/fixtures/pasted.txt")
DEFAULT_DECODED = Path("audit_artifacts/decoded_snapshot.json")
DEFAULT_EXTRACT = Path("audit_artifacts/gaps_extracted.json")

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def decode_b64_gz_bytes(b64_bytes: bytes) -> bytes:
    try:
        decoded = base64.b64decode(b64_bytes)
    except Exception as exc:
        raise RuntimeError(f"base64 decode error: {exc}")
    try:
        return gzip.decompress(decoded)
    except Exception as exc:
        raise RuntimeError(f"gunzip decompress error: {exc}")

def decode_base64_gzip(input_path: Path) -> dict[str, Any]:
    payload = input_path.read_text(encoding="utf-8").strip()
    data = base64.b64decode(payload)
    decompressed = gzip.decompress(data)
    return json.loads(decompressed.decode("utf-8"))

def load_from_local(path: str, max_bytes: int) -> Any:
    with open(path, "rb") as fh:
        b64 = fh.read()
    if len(b64) > max_bytes:
        eprint(f"Input file size {len(b64)} > max_bytes {max_bytes}, aborting")
        raise RuntimeError("input exceeds max_bytes")
    decoded_bytes = decode_b64_gz_bytes(b64)
    return json.loads(decoded_bytes)

def load_from_url(url: str, max_bytes: int) -> Any:
    req = Request(url, headers={"User-Agent": "artifact-decoder/1.0"})
    with urlopen(req, timeout=30) as r:
        b64 = r.read()
    if len(b64) > max_bytes:
        eprint(f"Remote content size {len(b64)} > max_bytes {max_bytes}, aborting")
        raise RuntimeError("remote content exceeds max_bytes")
    decoded_bytes = decode_b64_gz_bytes(b64)
    return json.loads(decoded_bytes)

def _path_str(p: Tuple[str, ...]) -> str:
    return "/" + "/".join(p) if p else "/"

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
    return (repr(value)[:200] + "...") if not isinstance(value, (str, int, float)) else repr(value)

def walk_for_gaps(obj: Any, path: Tuple[str, ...] = ()) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = path + (str(k),)
            if k in GAP_KEYS:
                findings.append(
                    {"locator": _path_str(p), "key": k, "value": v, "summary": summarize_gap_value(k, v)}
                )
            if isinstance(v, (dict, list)):
                findings.extend(walk_for_gaps(v, p))
            else:
                if isinstance(v, str) and ("missing" in v.lower() or "error" in v.lower() or "gap" in v.lower()):
                    findings.append({"locator": _path_str(p), "key": k, "value": v, "summary": f"Suspicious message: {v}"})
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            p = path + (f"[{idx}]",)
            if isinstance(item, (dict, list)):
                findings.extend(walk_for_gaps(item, p))
            else:
                if isinstance(item, str) and ("missing" in item.lower() or item.endswith(".py") or item.endswith(".md")):
                    findings.append({"locator": _path_str(p), "key": "list-item", "value": item, "summary": f"List item: {item}"})
    return findings

def normalize_findings(findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for f in findings:
        value = f.get("value")
        try:
            if isinstance(value, (dict, list)):
                value_preview = json.dumps(value, sort_keys=True)[:1000] + ("..." if len(json.dumps(value)) > 1000 else "")
            else:
                value_preview = repr(value)
        except Exception:
            value_preview = repr(value)
        out.append({
            "locator": f.get("locator"),
            "key": f.get("key"),
            "summary": f.get("summary"),
            "value_preview": value_preview,
        })
    out.sort(key=lambda x: x.get("locator") or "")
    return out

def write_outputs(out_dir: str, decoded_json: Any, findings: List[Dict[str, Any]]) -> None:
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
            preview = (f.get("value_preview") or "").replace("|", "\\|")
            fh.write(f"| `{locator}` | `{key}` | {summary} | `{preview}` |\n")
        if not findings:
            fh.write("\nNo GAP-like findings detected.\n")
        fh.write("\n\n---\n\n")
        fh.write("Run instructions:\n\n")
        fh.write("```bash\n")
        fh.write("python3 scripts/space_traversal/decode_validate_and_extract.py --input artifacts/validate_report_20251119.json.gz.b64 --out-dir ./artifacts/extracted_validate\n")
        fh.write("```\n")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Decode artifact and validate schema")
    parser.add_argument("--input", type=str, default=str(DEFAULT_INPUT), help="Base64+gzip input file")
    parser.add_argument("--url", type=str, help="raw URL to fetch the b64+gz file")
    parser.add_argument("--out-dir", type=str, help="output directory (default: artifacts/extracted_validate_<timestamp>)")
    parser.add_argument("--stable-output", action="store_true", help="use deterministic output dir (omit timestamp)")
    parser.add_argument("--generate-baseline", action="store_true", help="generate baseline from decoded JSON (writing capabilities_scored if present)")
    parser.add_argument("--baseline-path", type=str, help="path to write baseline JSON if --generate-baseline is set (overrides default)")
    parser.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES, help="max input size in bytes")
    parser.add_argument("--fail-on-missing-keys", help="comma separated top-level keys that must exist in decoded JSON")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args()

def decode_and_validate(
    input_path: Path,
    output_path: Path,
    extract_path: Path,
    schema_path: Path = None,
    stable_output: bool = False,
    generate_baseline: bool = False
) -> dict:
    # Decode
    decoded_json = decode_base64_gzip(input_path)
    output_path.write_text(json.dumps(decoded_json, indent=2, ensure_ascii=False))
    findings_raw = walk_for_gaps(decoded_json)
    findings = normalize_findings(findings_raw)
    # Write extracted findings
    extract_path.write_text(json.dumps({"count": len(findings)}, indent=2))
    # Validate against schema if provided
    if schema_path:
        import scripts.space_traversal.validate_snapshot_schema as validate
        validate.validate_snapshot(decoded_json, schema_path)
    result = {
        "decoded": decoded_json,
        "findings": findings,
    }
    return result

def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args() if argv is None else parse_args(argv)

    if not args.input and not args.url:
        eprint("Either --input or --url must be provided")
        return 2

    try:
        if args.url:
            decoded_json = load_from_url(args.url, args.max_bytes)
        else:
            if not os.path.exists(args.input):
                eprint(f"Input file not found: {args.input}")
                return 2
            decoded_json = load_from_local(args.input, args.max_bytes)
    except RuntimeError as exc:
        eprint(f"Decode/Gunzip error: {exc}")
        return 3
    except json.JSONDecodeError as exc:
        eprint(f"JSON parse error: {exc}")
        return 4
    except Exception as exc:
        eprint(f"Unexpected error loading input: {exc}")
        return 3

    # optional top-level validation
    if args.fail_on_missing_keys:
        missing = []
        required = [k.strip() for k in args.fail_on_missing_keys.split(",") if k.strip()]
        for k in required:
            if not (isinstance(decoded_json, dict) and k in decoded_json):
                missing.append(k)
        if missing:
            eprint(f"Missing required keys in decoded JSON: {missing}")
            out_base = args.out_dir or ("artifacts/extracted_validate")
            out_dir = out_base if args.stable_output else f"{out_base}_{time.strftime('%Y%m%d_%H%M%S')}"
            write_outputs(out_dir, decoded_json, [])
            return 5

    findings_raw = walk_for_gaps(decoded_json)
    findings = normalize_findings(findings_raw)

    out_base = args.out_dir or ("artifacts/extracted_validate")
    out_dir = out_base if args.stable_output else f"{out_base}_{time.strftime('%Y%m%d_%H%M%S')}"

    try:
        write_outputs(out_dir, decoded_json, findings)
    except Exception as exc:
        eprint(f"Error writing outputs: {exc}")
        return 5

    # Optional: generate baseline from decoded JSON
    if args.generate_baseline:
        try:
            if args.baseline_path:
                baseline_path = args.baseline_path
            else:
                baseline_dir = os.path.join(out_dir, "baseline")
                os.makedirs(baseline_dir, exist_ok=True)
                baseline_path = os.path.join(baseline_dir, "capabilities_scored.json")
            gen_script = os.path.join(os.path.dirname(__file__), "generate_baseline.py")
            if os.path.exists(gen_script):
                ret = subprocess.run([sys.executable, gen_script, "--input", args.input if args.input else "", "--baseline-path", baseline_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if ret.returncode != 0:
                    eprint(f"generate_baseline.py failed: stdout:\n{ret.stdout}\nstderr:\n{ret.stderr}")
                else:
                    if not args.quiet:
                        print(f"Wrote baseline to: {baseline_path}")
            else:
                if isinstance(decoded_json, dict) and "capabilities_scored" in decoded_json:
                    with open(baseline_path, "w", encoding="utf-8") as fh:
                        json.dump(decoded_json["capabilities_scored"], fh, indent=2, ensure_ascii=False)
                else:
                    with open(baseline_path, "w", encoding="utf-8") as fh:
                        json.dump(decoded_json, fh, indent=2, ensure_ascii=False)
                if not args.quiet:
                    print(f"Wrote baseline to: {baseline_path}")
        except Exception as exc:
            eprint(f"Baseline write failed: {exc}")

    # Optional: produce stable manifest for deterministic tests when requested
    if args.stable_output:
        try:
            try:
                from scripts.space_traversal.stable_manifest import manifest_for_dir
                manifest = manifest_for_dir(out_dir)
                manifest_path = os.path.join(out_dir, "stable_manifest.json")
                with open(manifest_path, "w", encoding="utf-8") as fh:
                    json.dump(manifest, fh, indent=2, ensure_ascii=False)
                if not args.quiet:
                    print(f"Wrote stable manifest to: {manifest_path}")
            except Exception:
                pass
        except Exception:
            pass

    if not args.quiet:
        print(f"Wrote outputs to: {out_dir}")
        print(f"Found {len(findings)} GAP-like findings.")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
