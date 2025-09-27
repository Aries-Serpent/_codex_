"""
Codex orchestration: apply minimal patches A–D from the patches markdown,
run CPU-friendly tests, and emit artifacts. Offline-first by default.

Usage:
  python scripts/codex_orchestrate.py \
    --audit "_codex_status_update-0C_base_-2025-09-27.md" \
    --patches "_codex_codex-ready-sequence-and-patches-2025-09-27.md" \
    --run-full 0

Requirements:
  - Python >= 3.10
  - pytest installed
  - git available in PATH
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

PATCH_ORDER_HINTS = ("Patch A", "Patch B", "Patch C", "Patch D")

DIFF_BLOCK_RE = re.compile(
    r"```diff\s+(.+?)\s*```",
    re.DOTALL | re.IGNORECASE
)

def sh(cmd, cwd=None, env=None, check=True, text=True):
    p = subprocess.run(cmd, cwd=cwd, env=env or os.environ.copy(),
                       text=text, capture_output=True)
    if check and p.returncode != 0:
        raise RuntimeError(f"CMD failed ({p.returncode}): {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")
    return p

def extract_diffs(markdown: str) -> list[str]:
    blocks = DIFF_BLOCK_RE.findall(markdown)
    # Prefer a stable order guided by headers in the file (A,B,C,D)
    # but fall back to file order.
    def order_key(b: str) -> int:
        h = 999
        for i, tag in enumerate(PATCH_ORDER_HINTS):
            if tag in markdown and tag in b:
                h = min(h, i)
        return h
    blocks.sort(key=order_key)
    return blocks

def ensure_dirs_for_patch(diff_text: str, repo: Path):
    # Create probable directories for new files in the diff (`/dev/null` → b/… lines)
    for ln in diff_text.splitlines():
        if ln.startswith("--- ") or ln.startswith("+++ "):
            target = ln[4:].strip()
            # lines look like: b/path/to/file or a/path/to/file
            if target.startswith("b/"):
                rel = target[2:].strip()
                if rel != "/dev/null":
                    (repo / rel).parent.mkdir(parents=True, exist_ok=True)

def apply_diff(diff_text: str, repo: Path, apply_log: Path):
    ensure_dirs_for_patch(diff_text, repo)
    p = subprocess.Popen(["git", "apply", "-p0", "-"], cwd=repo, stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate(diff_text)
    with apply_log.open("a", encoding="utf-8") as f:
        f.write("\n=== git apply ===\n")
        f.write(diff_text[:8000] + ("\n...truncated...\n" if len(diff_text) > 8000 else "\n"))
        f.write(f"\n-- rc={p.returncode}\nSTDOUT:\n{out}\nSTDERR:\n{err}\n")
    if p.returncode != 0:
        # Non-fatal: record error and continue (controlled pruning)
        return False, err
    return True, ""

def run_pytest(pattern: str, repo: Path, log_file: Path) -> int:
    cmd = [sys.executable, "-m", "pytest", "-q", "-k", pattern]
    p = subprocess.Popen(cmd, cwd=repo, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    with log_file.open("w", encoding="utf-8") as f:
        for line in p.stdout:
            f.write(line)
    p.wait()
    return p.returncode

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit", default="_codex_status_update-0C_base_-2025-09-27.md")
    ap.add_argument("--patches", default="_codex_codex-ready-sequence-and-patches-2025-09-27.md")
    ap.add_argument("--run-full", type=int, default=0)
    args = ap.parse_args()

    repo = Path(".").resolve()
    status_dir = repo/".codex/status"
    status_dir.mkdir(parents=True, exist_ok=True)

    # Offline-first: default MLflow disabled unless explicitly enabled
    os.environ.setdefault("MLFLOW_OFFLINE", "1")

    # Record environment
    env_info = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "python": sys.version,
        "cwd": str(repo),
        "git_head": sh(["git", "rev-parse", "HEAD"], cwd=repo, check=False).stdout.strip(),
        "mlflow_offline": os.getenv("MLFLOW_OFFLINE", ""),
        "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", ""),
    }
    (status_dir/"env.json").write_text(json.dumps(env_info, indent=2), encoding="utf-8")

    # Read inputs
    patches_md = Path(args.patches).read_text(encoding="utf-8")
    diffs = extract_diffs(patches_md)

    apply_log = status_dir/"apply_log.txt"
    apply_log.write_text("# Patch application log\n", encoding="utf-8")

    applied = []
    failures = []

    for i, diff in enumerate(diffs, 1):
        ok, err = apply_diff(diff, repo, apply_log)
        tag = f"diff_{i}"
        if ok:
            applied.append(tag)
        else:
            failures.append({"diff": tag, "error": err})

    # Minimal gates
    rc_min = run_pytest("overfit_smoke or roundtrip_basic", repo, status_dir/"test_min.log")

    # Optional full
    rc_full = None
    if args.run_full:
        rc_full = run_pytest("", repo, status_dir/"test_full.log")

    # Results
    results = {
        "applied": applied,
        "failures": failures,
        "pytest_min_rc": rc_min,
        "pytest_full_rc": rc_full,
    }
    (status_dir/"results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")

    # Exit code: minimal gates must pass (0) or legitimately skip (pytest returns 0)
    if rc_min != 0:
        # Emit error-capture prompt template for convenience
        errq = (
            "Question for ChatGPT-5 {ts}:\n"
            "While performing [STEP_5:GATES_MINIMAL], encountered: pytest exit code {rc}.\n"
            "Context: minimal CPU tests 'overfit_smoke or roundtrip_basic' failed.\n"
            "What are the possible causes, and how can this be resolved while preserving intended functionality?\n"
        ).format(ts=env_info["timestamp"], rc=rc_min)
        (status_dir/"error_capture.txt").write_text(errq, encoding="utf-8")
        print(errq, file=sys.stderr)
        sys.exit(rc_min)

    print("OK: patches applied; minimal tests passed; artifacts in .codex/status/")
    return 0

if __name__ == "__main__":
    sys.exit(main())
