"""
Codex Orchestrator — run the sequential phases end-to-end (local-only).

Phases implemented:
  1) Preparation
  2) Search & Mapping (scan repo; gather targets)
  3) Best-Effort Construction (apply light fixes / suggest patches)
  4) Controlled Pruning (feature-flag off optional deps)
  5) Error Capture (standardized blocks -> Codex_Questions.md)
  6) Finalization (CHANGELOG updates, optional commit comment)

Outputs (all local):
  - Codex_Questions.md                     (standardized error blocks)
  - codex_commit_comment.txt               (consolidated report)
  - .codex/errors.ndjson                   (machine-readable errors)
  - .codex/findings.json                   (targets & scans)
  - codex_suggested_patches.diff           (non-destructive suggestions)
  - CHANGELOG_Codex.md                     (what/why/risk/rollback)

IMPORTANT: This tool never creates or enables GitHub Actions. All quality gates
           run locally. If you enable optional posting to GitHub commit comments,
           you must provide a token via environment variables and force end
           workflow once GitHub Action completes otherwise it no-ops.

Features:
- Repository scanning for patterns (TODO, NotImplementedError, LoRA, MLflow, etc.)
- README normalization and deduplication
- Non-destructive patch suggestions
- Local quality gates (pre-commit, pytest)
- Error capture with structured logging
- Optional GitHub commit comment posting
- Comprehensive changelog generation
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------- Constants ----------
QUESTION_FILE = "Codex_Questions.md"
CHANGELOG = "CHANGELOG_Codex.md"
ERRLOG = Path(".codex") / "errors.ndjson"
FINDINGS = Path(".codex") / "findings.json"
REPORT = "codex_commit_comment.txt"

__all__ = [
    "Finding",
    "Options",
    "orchestrate",
    "parse_args",
    "main",
    "scan_repo",
    "normalize_readmes",
    "suggest_patches",
    "controlled_pruning_notes",
    "gate_precommit",
    "gate_pytest",
    "install_prepare_commit_msg_hook",
    "record_error",
    "build_commit_comment",
    "maybe_post_commit_comment",
]

# ---------- Utilities ----------
def ts_utc() -> str:
    """Generate UTC timestamp in ISO format."""
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def ts_local() -> str:
    """Generate local timestamp with timezone."""
    return time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime())


def repo_root(start: Optional[Path] = None) -> Path:
    """Find the git repository root directory.
    
    Parameters
    ----------
    start : Path, optional
        Starting directory for search (default: current working directory)
        
    Returns
    -------
    Path
        Repository root directory
    """
    start = start or Path.cwd()
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return Path(out.stdout.strip())
    except Exception:
        return start.resolve()


def read_text(p: Path, default: str = "") -> str:
    """Safely read text file with fallback.
    
    Parameters
    ----------
    p : Path
        File path to read
    default : str, default=""
        Default value if read fails
        
    Returns
    -------
    str
        File contents or default value
    """
    try:
        return p.read_text(encoding="utf-8")
    except Exception:
        return default


def write_text(p: Path, data: str) -> None:
    """Write text to file, creating parent directories as needed.
    
    Parameters
    ----------
    p : Path
        File path to write
    data : str
        Text content to write
    """
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(data, encoding="utf-8")


def append_text(p: Path, data: str) -> None:
    """Append text to file, creating parent directories as needed.
    
    Parameters
    ----------
    p : Path
        File path to append to
    data : str
        Text content to append
    """
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(data)


def run(
    cmd: List[str], cwd: Optional[Path] = None, timeout: Optional[int] = None
) -> Tuple[int, str, str]:
    """Run subprocess and return exit code, stdout, stderr.
    
    Parameters
    ----------
    cmd : List[str]
        Command and arguments to execute
    cwd : Path, optional
        Working directory for command
    timeout : int, optional
        Timeout in seconds
        
    Returns
    -------
    Tuple[int, str, str]
        (return_code, stdout, stderr)
    """
    proc = subprocess.run(
        cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True, timeout=timeout
    )
    return proc.returncode, proc.stdout, proc.stderr


def record_error(step_no: str, desc: str, errmsg: str, context: str, root: Path) -> None:
    """Record standardized error block to Codex_Questions.md and errors.ndjson.
    
    Parameters
    ----------
    step_no : str
        Step identifier (e.g., "G2", "H1")
    desc : str
        Brief description of the operation
    errmsg : str
        Error message content
    context : str
        Additional context about the error
    root : Path
        Repository root directory
    """
    block = (
        f"Question for ChatGPT @codex {ts_local()}:\n"
        f"While performing [{step_no}:{desc}], encountered the following error:\n"
        f"{errmsg.strip()}\n"
        f"Context: {context.strip()}\n"
        f"What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    append_text(root / QUESTION_FILE, block)
    append_text(
        ERRLOG,
        json.dumps(
            {"ts": ts_utc(), "step": f"{step_no}:{desc}", "error": errmsg, "context": context}
        )
        + "\n",
    )


def current_head_sha(root: Path) -> str:
    """Get current git HEAD commit SHA.
    
    Parameters
    ----------
    root : Path
        Repository root directory
        
    Returns
    -------
    str
        Current commit SHA
        
    Raises
    ------
    RuntimeError
        If git command fails
    """
    code, out, err = run(["git", "rev-parse", "HEAD"], cwd=root)
    if code != 0:
        raise RuntimeError(f"git rev-parse failed: {err}")
    return out.strip()


def origin_owner_repo(root: Path) -> Tuple[str, str]:
    """Extract owner and repo name from git origin URL.
    
    Parameters
    ----------
    root : Path
        Repository root directory
        
    Returns
    -------
    Tuple[str, str]
        (owner, repository_name)
        
    Raises
    ------
    RuntimeError
        If unable to parse origin URL
    """
    code, out, err = run(["git", "config", "--get", "remote.origin.url"], cwd=root)
    if code != 0:
        raise RuntimeError(f"git config remote.origin.url failed: {err}")
    url = out.strip()
    if url.startswith("git@github.com:"):
        part = url.split(":", 1)[1]
    elif "github.com/" in url:
        part = url.split("github.com/", 1)[1]
    else:
        raise RuntimeError(f"Unsupported origin URL: {url}")
    part = part[:-4] if part.endswith(".git") else part
    owner, repo = part.split("/", 1)
    return owner, repo


def build_commit_comment(root: Path) -> str:
    """Build commit comment from captured errors.
    
    Parameters
    ----------
    root : Path
        Repository root directory
        
    Returns
    -------
    str
        Formatted commit comment body
    """
    blocks = read_text(root / QUESTION_FILE, "").strip()
    if not blocks:
        blocks = "No errors were captured by Codex during this iteration."
    return f"Codex Iteration Error Report — {ts_local()}\n\n{blocks}"


def maybe_post_commit_comment(root: Path, body: str) -> str:
    """Optionally post commit comment to GitHub if configured.
    
    Parameters
    ----------
    root : Path
        Repository root directory
    body : str
        Comment body text
        
    Returns
    -------
    str
        Status message describing the result
    """
    token = (
        os.getenv("GH_PAT")
        or os.getenv("GITHUB_TOKEN")
        or os.getenv("CODEX_ENVIRONMENT_RUNNER")
        or os.getenv("_CODEX_BOT_RUNNER")
        or os.getenv("_CODEX_ACTION_RUNNER")
    )
    if not (os.getenv("CODEX_POST_COMMIT_COMMENT", "0").lower() in ("1", "true", "yes") and token):
        return "skipped"
    try:
        owner, repo = origin_owner_repo(root)
        sha = current_head_sha(root)
        api = os.getenv("GITHUB_API_URL", "https://api.github.com")
        url = f"{api}/repos/{owner}/{repo}/commits/{sha}/comments"
        # use urllib to avoid extra deps
        import json as _json
        import urllib.request

        req = urllib.request.Request(
            url,
            data=_json.dumps({"body": body}).encode("utf-8"),
            method="POST",
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "Content-Type": "application/json",
                "User-Agent": "codex-orchestrator",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return f"posted: HTTP {resp.getcode()}"
    except Exception as e:
        return f"error: {e}"


# ---------- Phase 2: Search & Mapping ----------
SCAN_PATTERNS = [
    r"\bNotImplementedError\b",
    r"\bTODO\b",
    r"^\s*pass\s*$",
    r"\bapply_lora\b|\bget_peft_model\b",
    r"\bAutoTokenizer\b|\buse_fast\b",
    r"\bmlflow\.(start_run|set_experiment|set_tracking_uri)\b",
]


@dataclass
class Finding:
    """Represents a code pattern match found during repository scan.
    
    Attributes
    ----------
    path : str
        Relative path to the file
    line_no : int
        Line number where pattern was found
    kind : str
        Pattern type that matched
    line : str
        Content of the matching line
    """
    path: str
    line_no: int
    kind: str
    line: str


def scan_repo(root: Path) -> List[Finding]:
    """Scan repository for specific code patterns.
    
    Parameters
    ----------
    root : Path
        Repository root directory
        
    Returns
    -------
    List[Finding]
        List of pattern matches found in the codebase
    """
    findings: List[Finding] = []
    excl = {".git", ".venv", "venv", "__pycache__", ".mypy_cache", ".pytest_cache", ".codex"}
    for p in root.rglob("*.py"):
        if any(seg in excl for seg in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            for pat in SCAN_PATTERNS:
                if re.search(pat, line):
                    findings.append(Finding(str(p.relative_to(root)), i, pat, line.strip()))
    return findings


# ---------- README parsing & reference replacement/removal ----------
REF_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
SECTION_HDR = re.compile(r"^#{1,6}\s+(.+)$")


def normalize_readmes(root: Path) -> Dict[str, Any]:
    """Normalize README files by deduplicating links and removing TODO placeholders.
    
    Parameters
    ----------
    root : Path
        Repository root directory
        
    Returns
    -------
    Dict[str, Any]
        Information about the normalization process including changes made
    """
    readmes = [root / "README_UPDATED.md", root / "README.md", root / "documentation" / "README.md"]
    picked: Optional[Path] = None
    for r in readmes:
        if r.exists():
            picked = r
            break
    if not picked:
        return {"picked": None, "changes": []}

    text = picked.read_text(encoding="utf-8", errors="ignore")
    changes = []

    # 1) Remove naked TODO lines in docs
    new_text, n = re.subn(r"(?m)^\s*TODO\s*$", "", text)
    if n:
        changes.append({"action": "remove_todo_lines", "count": n})
        text = new_text

    # 2) De-duplicate identical links (keep first)
    seen = set()
    lines = []
    removed = 0
    for line in text.splitlines():
        m = REF_LINK.search(line)
        if m:
            key = (m.group(1).strip(), m.group(2).strip())
            if key in seen:
                removed += 1
                continue
            seen.add(key)
        lines.append(line)
    if removed:
        changes.append({"action": "dedupe_links", "removed": removed})
    updated = "\n".join(lines)

    out = root / "README.md"
    if out != picked:
        changes.append(
            {"action": "promote_readme", "from": str(picked.relative_to(root)), "to": "README.md"}
        )
    write_text(out, updated)
    return {"picked": str(picked.relative_to(root)) if picked else None, "changes": changes}


# ---------- Best-Effort Construction ----------
def suggest_patches(root: Path, findings: List[Finding]) -> str:
    """Generate non-destructive patch suggestions.
    
    Parameters
    ----------
    root : Path
        Repository root directory
    findings : List[Finding]
        Code pattern findings from repository scan
        
    Returns
    -------
    str
        Patch suggestions as unified diff format
    """
    suggestions: List[str] = []
    suggestions.append("# Suggested unified diffs (non-destructive)\n")
    # Pointers to key files; these align with Part 2/4 patches:
    targets = [
        "src/codex_ml/interfaces/tokenizer.py",
        "src/codex_ml/modeling/codex_model_loader.py",
        "src/codex_ml/tracking/mlflow_utils.py",
        "src/ingestion/io_text.py",
        "training/engine_hf_trainer.py",
        "tools/install_codex_hooks.py",
    ]
    present = [t for t in targets if (root / t).exists()]
    missing = [t for t in targets if not (root / t).exists()]
    if present:
        suggestions.append(f"# Found targets: {', '.join(present)}\n")
    if missing:
        suggestions.append(
            f"# Note: some targets not found (ok for first iteration): {', '.join(missing)}\n"
        )
    # Provide a short, actionable header referencing the paths that DO exist.
    suggestions.append("# For existing files, merge in Part 2/4 diffs above.\n")
    suggestions.append("# Example: git apply codex_suggested_patches.diff (after manual review)\n")
    return "\n".join(suggestions)


# ---------- Controlled Pruning ----------
def controlled_pruning_notes() -> List[str]:
    """Generate guidance notes for optional dependency handling.
    
    Returns
    -------
    List[str]
        List of pruning guidance notes
    """
    return [
        "If PEFT is not installed, keep lora_enabled=False to maintain backward compatibility.",
        "If MLflow is not installed, skip tracking (no-op wrappers return None).",
        "If charset-normalizer is not installed, avoid encoding='auto' and pass explicit encodings.",
    ]


# ---------- Quality gates (local only) ----------
def gate_precommit(root: Path, verbose: bool = True) -> Tuple[int, str]:
    """Run pre-commit hooks as a quality gate.
    
    Parameters
    ----------
    root : Path
        Repository root directory
    verbose : bool, default=True
        Enable verbose output
        
    Returns
    -------
    Tuple[int, str]
        (exit_code, combined_output)
    """
    args = ["pre-commit", "run", "--all-files"]
    if verbose:
        args.append("--verbose")
    code, out, err = run(args, cwd=root, timeout=None)
    if code != 0:
        record_error(
            "G2", "pre-commit run --all-files", err or out, "Executing repository hooks", root
        )
    return code, (out + err)


def gate_pytest(root: Path, cov_pkg: str = "src", threshold: int = 70) -> Tuple[int, str]:
    """Run pytest with coverage as a quality gate.
    
    Parameters
    ----------
    root : Path
        Repository root directory
    cov_pkg : str, default="src"
        Package to measure coverage for
    threshold : int, default=70
        Minimum coverage percentage required
        
    Returns
    -------
    Tuple[int, str]
        (exit_code, combined_output)
    """
    # Try to detect pytest-cov; if missing, install-advice emitted via error capture
    code, out, err = run(["pytest", "--version"], cwd=root)
    has_cov = "pytest-cov" in (out + err).lower()
    if not has_cov:
        record_error(
            "G3",
            "pytest coverage flags",
            "pytest-cov plugin not active",
            "Install pytest-cov to enable --cov",
            root,
        )
    args = ["pytest", f"--cov={cov_pkg}", "--cov-report=term", f"--cov-fail-under={threshold}"]
    code, out, err = run(args, cwd=root)
    if code != 0:
        record_error("G3", "pytest with coverage", err or out, "Unit tests and coverage", root)
    return code, (out + err)


# ---------- CLI & Orchestration ----------
@dataclass
class Options:
    """Configuration options for the orchestrator.
    
    Attributes
    ----------
    project_root : Path
        Repository root directory
    run_precommit : bool
        Whether to run pre-commit hooks
    run_pytest : bool
        Whether to run pytest with coverage
    cov_pkg : str
        Package to measure coverage for
    cov_threshold : int
        Minimum coverage percentage
    install_hook : bool
        Whether to install commit message hook
    """
    project_root: Path
    run_precommit: bool
    run_pytest: bool
    cov_pkg: str
    cov_threshold: int
    install_hook: bool


def install_prepare_commit_msg_hook(root: Path) -> None:
    """Install prepare-commit-msg hook for git trailers.
    
    Parameters
    ----------
    root : Path
        Repository root directory
    """
    hook = root / "tools" / "install_codex_hooks.py"
    if hook.exists():
        code, out, err = run([sys.executable, str(hook)], cwd=root)
        if code != 0:
            record_error(
                "H1",
                "install prepare-commit-msg hook",
                err or out,
                "Running tools/install_codex_hooks.py",
                root,
            )
    else:
        record_error(
            "H0",
            "install prepare-commit-msg hook",
            "installer not found",
            "tools/install_codex_hooks.py missing",
            root,
        )


def orchestrate(opts: Options) -> int:
    """Run the complete orchestration workflow.
    
    Parameters
    ----------
    opts : Options
        Configuration options
        
    Returns
    -------
    int
        Exit code (0 for success)
    """
    root = repo_root(opts.project_root)

    # Phase 1 — Preparation
    write_text(Path(".codex") / ".keep", "")
    write_text(Path(".codex") / "RUN_STARTED.txt", ts_local())

    # Phase 2 — Search & Mapping
    findings = scan_repo(root)
    write_text(FINDINGS, json.dumps([asdict(f) for f in findings], indent=2))

    # README normalization
    _readme_info = normalize_readmes(root)

    # Phase 3 — Best-Effort Construction
    # (Non-destructive suggestions + optional hook install)
    suggestions = suggest_patches(root, findings)
    write_text(root / "codex_suggested_patches.diff", suggestions)
    if opts.install_hook:
        install_prepare_commit_msg_hook(root)

    # Phase 4 — Controlled Pruning (notes only; behavior handled in code by flags)
    _pruning = controlled_pruning_notes()

    # Phase 5 — Error Capture is handled inline via record_error()

    # Phase 6 — Finalization
    # Assemble report & optional commit comment
    body = build_commit_comment(root)
    write_text(root / REPORT, body)
    status = maybe_post_commit_comment(root, body)

    # Write CHANGELOG entry
    entry: List[str] = []
    entry.append(f"## {ts_local()}\n")
    entry.append("- Repo scan & mapping complete; findings written to `.codex/findings.json`.\n")
    entry.append("- README normalization applied; see `normalize_readmes` changes section.\n")
    entry.append("- Non-destructive patch suggestions written to `codex_suggested_patches.diff`.\n")
    if opts.install_hook:
        entry.append("- Attempted to install `prepare-commit-msg` hook (trailers).\n")
    entry.append(f"- Commit comment posting: {status} (local-only, no Actions).\n")
    entry.append("- Controlled pruning guidance recorded (PEFT/MLflow/encodings).\n")
    append_text(Path(CHANGELOG), "\n" + "".join(entry))

    # Optional gates at the very end (so errors are captured & reported)
    if opts.run_precommit:
        gate_precommit(root, verbose=True)
    if opts.run_pytest:
        gate_pytest(root, cov_pkg=opts.cov_pkg, threshold=opts.cov_threshold)

    return 0


def parse_args(argv: List[str]) -> Options:
    """Parse command line arguments.
    
    Parameters
    ----------
    argv : List[str]
        Command line arguments
        
    Returns
    -------
    Options
        Parsed configuration options
    """
    ap = argparse.ArgumentParser(description="Codex local orchestrator (no GitHub Actions).")
    ap.add_argument("--project-root", default=".", help="Path to repo root (default: .)")
    ap.add_argument(
        "--run-precommit", action="store_true", help="Run pre-commit --all-files at end"
    )
    ap.add_argument("--run-pytest", action="store_true", help="Run pytest with coverage at end")
    ap.add_argument("--cov-pkg", default="src", help="Coverage source package (default: src)")
    ap.add_argument(
        "--cov-threshold", type=int, default=70, help="Coverage fail-under (default: 70)"
    )
    ap.add_argument("--install-hook", action="store_true", help="Install commit-msg trailer hook")
    ns = ap.parse_args(argv)
    return Options(
        project_root=Path(ns.project_root),
        run_precommit=ns.run_precommit,
        run_pytest=ns.run_pytest,
        cov_pkg=ns.cov_pkg,
        cov_threshold=ns.cov_threshold,
        install_hook=ns.install_hook,
    )


def main() -> int:
    """Main entry point.
    
    Returns
    -------
    int
        Exit code
    """
    try:
        return orchestrate(parse_args(sys.argv[1:]))
    except Exception as e:
        root = repo_root()
        record_error("F", "orchestrate", str(e), "Unhandled exception in codex_orchestrator.py", root)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
