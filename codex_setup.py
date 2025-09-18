#!/usr/bin/env python3
"""
Codex .codex/ bootstrapper & append-only writer.

- Creates `.codex/` and seeds:
  - change_log.md       -> "# Codex Change Log"
  - errors.ndjson       -> (empty, NDJSON/JSON Lines)
  - results.md          -> "# Codex Results"
- Guarantees append-only behavior:
  - Prefers POSIX O_APPEND for atomic appends (multi-process safe) [open(2)].
  - Falls back to text append mode "a" cross-platform.

Refs:
- NDJSON / JSON Lines: jsonlines.org, ndjson-spec (newline-delimited JSON).
- Append-only semantics: POSIX O_APPEND (open(2)).

DO NOT ACTIVATE ANY GitHub Actions files. ALL GitHub Action.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import uuid
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path.cwd()
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"
README_MD = REPO_ROOT / "README.md"

try:  # pragma: no cover - defensive import
    from codex.logging.session_logger import get_session_id, log_message
except Exception:  # pragma: no cover - logging remains best-effort
    get_session_id = None  # type: ignore[assignment]
    log_message = None  # type: ignore[assignment]


def _current_session_id() -> str:
    if get_session_id is not None:  # type: ignore[truthy-function]
        try:
            return get_session_id()
        except Exception:  # pragma: no cover - fallback if helper misbehaves
            pass
    sid = os.getenv("CODEX_SESSION_ID")
    if sid:
        return sid
    generated = f"codex-setup-{uuid.uuid4()}"
    os.environ.setdefault("CODEX_SESSION_ID", generated)
    return generated


def session_log(message: str, *, meta: dict | None = None, role: str = "system") -> None:
    if log_message is None:
        return
    try:
        log_message(_current_session_id(), role, message, meta=meta)
    except Exception:  # pragma: no cover - logging failures should be silent
        pass


def check_cli_version(tool: str, *args: str) -> dict:
    cmd = (tool, *args) if args else (tool, "--version")
    joined_cmd = " ".join(cmd)
    meta: dict[str, object] = {
        "tool": tool,
        "command": joined_cmd,
        "source": "codex_setup.init",
    }
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        version = (result.stdout or result.stderr).strip()
        meta.update(
            {
                "available": True,
                "returncode": result.returncode,
                "stdout": version,
            }
        )
        session_log(
            f"{tool} available",
            meta=meta,
        )
    except FileNotFoundError as exc:
        meta.update({"available": False, "error": "not found", "exception": repr(exc)})
        session_log(f"{tool} missing", meta=meta, role="WARN")
    except subprocess.CalledProcessError as exc:
        output = ((exc.stdout or exc.stderr) or str(exc)).strip()
        meta.update(
            {
                "available": False,
                "returncode": exc.returncode,
                "error": output,
            }
        )
        session_log(f"{tool} invocation failed", meta=meta, role="WARN")
    return meta


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _posix_append_bytes(path: Path, data: bytes) -> None:
    """
    POSIX-safe append using O_APPEND for atomic end-of-file writes.
    Falls back to text append if O_APPEND not available.
    """
    flags = getattr(os, "O_APPEND", None)
    if flags is None or os.name == "nt":
        # Fallback: text append (not guaranteed atomic across processes)
        with open(path, "ab") as f:
            f.write(data)
        return
    # POSIX path
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, data)
    finally:
        os.close(fd)


def append_line(path: Path, line: str) -> None:
    if not line.endswith("\n"):
        line += "\n"
    _posix_append_bytes(path, line.encode("utf-8"))


def error_capture(step_no: str, step_desc: str, err_msg: str, ctx: str = "") -> None:
    """Write error to NDJSON and print ChatGPT-5 research question."""
    record = {
        "ts": now_iso(),
        "step": f"{step_no}: {step_desc}",
        "error": err_msg,
        "context": ctx,
    }
    try:
        append_line(ERRORS_NDJSON, json.dumps(record, ensure_ascii=False))
    finally:
        sys.stderr.write(
            f"Question for ChatGPT-5 {now_iso()}:\n"
            f"While performing [{step_no}:{step_desc}], "
            f"encountered the following error:\n"
            f"{err_msg}\n"
            f"Context: {ctx}\n"
            "What are the possible causes, and how can this be resolved "
            "while preserving intended functionality?\n"
        )


def init_codex_dir() -> None:
    # Phase 1: Preparation
    try:
        CODEX_DIR.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        error_capture("1.1", "Create .codex/", str(e), f"path={CODEX_DIR}")
        raise

    # Create/seed files (idempotent, never truncate)
    try:
        if not CHANGE_LOG.exists():
            append_line(CHANGE_LOG, "# Codex Change Log")
        if not ERRORS_NDJSON.exists():
            ERRORS_NDJSON.touch()
        if not RESULTS_MD.exists():
            append_line(RESULTS_MD, "# Codex Results")
    except Exception as e:
        error_capture(
            "1.2",
            "Seed .codex files",
            str(e),
            "change_log.md, errors.ndjson, results.md",
        )
        raise


def update_readme_best_effort() -> None:
    """Non-destructive: ensure README has a minimal 'Codex Logs' section."""
    try:
        if not README_MD.exists():
            return
        text = README_MD.read_text(encoding="utf-8", errors="ignore")
        if "## Codex Logs" in text:
            return
        extra = (
            "\n## Codex Logs\n"
            "- `.codex/change_log.md`: human-readable changes\n"
            "- `.codex/errors.ndjson`: NDJSON (one JSON object per line)\n"
            "- `.codex/results.md`: summaries/results\n"
        )
        # Append (no truncation)
        with open(README_MD, "a", encoding="utf-8") as f:
            f.write(extra)
    except Exception as e:
        error_capture("2.1", "README best-effort update", str(e), f"readme={README_MD}")


def finalize_results(summary: str) -> None:
    try:
        append_line(
            RESULTS_MD,
            f"\n## {now_iso()} — Setup Summary\n{summary}",
        )
        append_line(
            CHANGE_LOG,
            (f"- {now_iso()} Initialized/verified .codex/ and log files (append-only guarantees)."),
        )
    except Exception as e:
        error_capture(
            "6.1",
            "Finalize results",
            str(e),
            "write summaries to results.md & change_log.md",
        )


def verify() -> str:
    """Return a small report with sizes and last line samples."""

    def tail(path: Path, n=3) -> str:
        if not path.exists():
            return "(missing)"
        try:
            data = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            return "\n".join(data[-n:])
        except Exception as e:
            return f"(error reading: {e})"

    change_log_size = CHANGE_LOG.stat().st_size if CHANGE_LOG.exists() else 0
    errors_size = ERRORS_NDJSON.stat().st_size if ERRORS_NDJSON.exists() else 0
    results_size = RESULTS_MD.stat().st_size if RESULTS_MD.exists() else 0
    report = [
        f"Root: {REPO_ROOT}",
        f".codex/: {CODEX_DIR.exists()}",
        f"change_log.md: {CHANGE_LOG.exists()} size={change_log_size}",
        f"errors.ndjson: {ERRORS_NDJSON.exists()} size={errors_size}",
        f"results.md: {RESULTS_MD.exists()} size={results_size}",
        "\n--- Tails ---",
        "[change_log.md]",
        tail(CHANGE_LOG),
        "[errors.ndjson]",
        tail(ERRORS_NDJSON),
        "[results.md]",
        tail(RESULTS_MD),
        "\nNOTE: DO NOT ACTIVATE ANY GitHub Actions files. ALL GitHub Action.",
    ]
    return "\n".join(report)


def append_demo_lines() -> None:
    """Demonstrate append-only behavior with a sample entry in each file."""
    try:
        append_line(CHANGE_LOG, f"- {now_iso()} Demo change appended safely.")
        append_line(
            ERRORS_NDJSON,
            json.dumps(
                {"ts": now_iso(), "demo": True, "msg": "sample ndjson line"},
                ensure_ascii=False,
            ),
        )
        append_line(RESULTS_MD, f"- {now_iso()} Demo result appended safely.")
    except Exception as e:
        error_capture("3.1", "Append demo lines", str(e))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Codex .codex/ bootstrapper")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init", help="Create .codex/ and seed files (idempotent).")
    sub.add_parser("verify", help="Print sizes and tails of .codex files.")
    sub.add_parser("append-demo", help="Append one demo line to each file.")
    append_p = sub.add_parser("append", help="Append a single line to change_log|errors|results")
    append_p.add_argument("which", choices=["change_log", "errors", "results"])
    append_p.add_argument("text", help="Text or JSON (for errors) to append")

    args = parser.parse_args(argv)

    try:
        if args.cmd == "init":
            init_codex_dir()
            precommit_status = check_cli_version("pre-commit", "--version")
            update_readme_best_effort()
            availability = "available" if precommit_status.get("available") else "missing"
            version = precommit_status.get("stdout") or precommit_status.get("error") or "unknown"
            summary_lines = [
                "- Initialized .codex and seeded files.",
                f"- pre-commit availability: {availability} ({version})",
            ]
            finalize_results("\n".join(summary_lines))
            if not precommit_status.get("available"):
                print(
                    "[codex_setup] pre-commit is not available; install the pinned version "
                    "from requirements-dev.txt before running gates.",
                    file=sys.stderr,
                )
        elif args.cmd == "verify":
            init_codex_dir()
            print(verify())
        elif args.cmd == "append-demo":
            init_codex_dir()
            append_demo_lines()
            print("Demo lines appended.")
        elif args.cmd == "append":
            init_codex_dir()
            if args.which == "change_log":
                append_line(CHANGE_LOG, args.text)
            elif args.which == "errors":
                # If user passes raw text, wrap into a JSON record with message
                try:
                    obj = json.loads(args.text)
                except json.JSONDecodeError:
                    obj = {"ts": now_iso(), "message": args.text}
                append_line(ERRORS_NDJSON, json.dumps(obj, ensure_ascii=False))
            else:
                append_line(RESULTS_MD, args.text)
            print(f"Appended to {args.which}.")
        return 0
    except KeyboardInterrupt:
        error_capture("0.0", "Interrupted by user", "KeyboardInterrupt")
        return 130
    except Exception as e:
        error_capture("0.1", "Unhandled exception", repr(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())
