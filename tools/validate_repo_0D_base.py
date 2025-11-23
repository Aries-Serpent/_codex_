#!/usr/bin/env python3
"""
Validate repository contents for the Status Update patchset on branch 0D_base_.

Outputs a JSON object to stdout with:
- branch_checked_out
- git_ref (HEAD sha)
- required_files: {path: {exists: bool, size, sha256 (if exists)}}
- ripgrep_hits: {pattern: [ {file, line_no, line} ... ] }
- detectors: list of files in scripts/space_traversal/detectors
- schemas: list of files in scripts/space_traversal/schemas
- missing_files: [paths]
- summary: quick pass/fail flags for critical items
"""
from __future__ import annotations
import subprocess, json, os, sys, hashlib, shutil
from pathlib import Path

ROOT = Path.cwd()
REPO = ROOT
REQUIRED = [
    "scripts/space_traversal/audit_runner.py",
    "templates/audit/capability_matrix.md.j2",
    ".copilot-space/workflow.yaml",
    "space.mk",
    "scripts/space_traversal/coverage_ingest.py",
    "scripts/space_traversal/detectors",
    "scripts/space_traversal/schemas",
    "tests/audit/test_overrides.py",
    "tests/audit/test_json_companion.py",
]

RIPGREP_PATTERNS = [
    "detect_v2",
    r"def detect\\b",
    "template_hash",
    "capability_matrix_.*\\.json",
    "metrics_schema_version",
    "capabilities_scored",
    "fail_on_missing_detector",
    "fail_on_score_regression",
    "stage_s6_render",
    "render_template\\(",
]

def run(cmd, check=False, capture=True):
    if capture:
        res = subprocess.run(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res
    else:
        return subprocess.run(cmd, shell=False)

def git_head_sha():
    r = run(["git", "rev-parse", "HEAD"])
    if r.returncode != 0:
        return None
    return r.stdout.strip()

def checkout_branch(branch="0D_base_"):
    """Checkout the target branch unless explicitly skipped.

    Set CODEX_SKIP_VALIDATE_CHECKOUT=1 to avoid any git operations. This is
    useful for offline or test environments where changing branches is
    undesirable.
    """
    if os.getenv("CODEX_SKIP_VALIDATE_CHECKOUT", "").lower() in {"1", "true", "yes"}:
        current = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return current.stdout.strip() if current.returncode == 0 else None

    # Try to fetch and checkout branch if present remotely, otherwise attempt local checkout
    run(["git", "fetch", "origin"], check=False)
    r = run(["git", "rev-parse", "--verify", "--quiet", branch])
    if r.returncode == 0:
        run(["git", "checkout", branch])
        return branch
    # try remote
    r2 = run(["git", "ls-remote", "--heads", "origin", branch])
    if r2.stdout.strip():
        run(["git", "checkout", "-b", branch, f"origin/{branch}"])
        return branch
    # fall back to current branch
    r3 = run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    return r3.stdout.strip() if r3.returncode == 0 else None

def file_sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def rg_search(pattern):
    rg = shutil.which("rg")
    if not rg:
        # fallback to git grep
        try:
            p = run(["git", "grep", "-n", "-E", pattern])
            if p.returncode == 0:
                hits = []
                for ln in p.stdout.splitlines():
                    parts = ln.split(":", 2)
                    if len(parts) >= 3:
                        line_txt = parts[2]
                        if len(line_txt) > 240:
                            line_txt = line_txt[:240] + "..."
                        hits.append({"file": parts[0], "line_no": int(parts[1]), "line": line_txt})
                return hits
            return []
        except Exception:
            return []
    else:
        p = run([rg, "--hidden", "--no-ignore", "-n", "-S", pattern])
        hits = []
        if p.returncode == 0 or p.stdout:
            for ln in p.stdout.splitlines():
                parts = ln.split(":", 2)
                if len(parts) >= 3:
                    line_txt = parts[2]
                    if len(line_txt) > 240:
                        line_txt = line_txt[:240] + "..."
                    hits.append({"file": parts[0], "line_no": int(parts[1]), "line": line_txt})
        return hits

def list_dir(path):
    p = Path(path)
    if not p.exists() or not p.is_dir():
        return []
    items = []
    for x in sorted(p.rglob("*")):
        if not x.is_file():
            continue
        try:
            rel = x.resolve().relative_to(ROOT)
        except ValueError:
            rel = x
        items.append(str(rel))
    return items

def main():
    report = {}
    branch = checkout_branch("0D_base_")
    report["branch_checked_out"] = branch
    report["git_head_sha"] = git_head_sha()

    required = {}
    missing = []
    for p in REQUIRED:
        pp = Path(p)
        if pp.exists():
            info = {"exists": True}
            if pp.is_file():
                info["size"] = pp.stat().st_size
                info["sha256"] = file_sha256(pp)
            else:
                info["size"] = None
                info["sha256"] = None
            required[p] = info
        else:
            required[p] = {"exists": False, "size": None, "sha256": None}
            missing.append(p)
    report["required_files"] = required

    # ripgrep patterns
    rg_results = {}
    for pat in RIPGREP_PATTERNS:
        hits = rg_search(pat)
        rg_results[pat] = hits
    zero_hit_patterns = [pat for pat, hits in rg_results.items() if not hits]
    report["ripgrep_hits"] = rg_results
    report["ripgrep_zero_hits"] = zero_hit_patterns

    # detectors & schemas listing
    report["detectors"] = list_dir("scripts/space_traversal/detectors")
    report["schemas"] = list_dir("scripts/space_traversal/schemas")
    report["tests_audit"] = list_dir("tests/audit")

    report["missing_files"] = missing

    # quick summary flags
    report["summary"] = {
        "all_required_present": len(missing) == 0,
        "has_detect_v2": len(rg_results.get("detect_v2", [])) > 0,
        "has_template_j2": Path("templates/audit/capability_matrix.md.j2").exists(),
        "has_schema_dir": Path("scripts/space_traversal/schemas").exists(),
        "has_detectors_dir": Path("scripts/space_traversal/detectors").exists(),
    }

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")

    failures = []
    if missing:
        failures.append(
            "missing required files or directories: " + ", ".join(sorted(missing))
        )
    if zero_hit_patterns:
        failures.append(
            "ripgrep patterns with zero hits: " + ", ".join(zero_hit_patterns)
        )

    if failures:
        sys.stderr.write("Validation failed: " + "; ".join(failures) + "\n")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
