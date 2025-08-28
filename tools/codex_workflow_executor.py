#!/usr/bin/env python3
"""
Codex Workflow Executor (no remote CI activation)

Features:
- README parsing and reference normalization (replaces legacy secret names with CODEX_* equivalents).
- Ensures tiny Make target that shells to ci_local.sh.
- Ensures ci_local.sh uses venv and runs pre-commit + pytest deterministically.
- Best-effort local gates, runner bring-up, autoscaler, and doctor (only if GH_PAT or CODEX_RUNNER_TOKEN present).
- Gap documentation to .codex/codex_change_log.md
- Error capture formatted as ChatGPT-5 research questions to .codex/research_questions.md
- Final summary printout.

Note: DOES NOT modify or enable GitHub Actions workflows.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CODEX_DIR = ROOT / ".codex"
CHANGELOG = CODEX_DIR / "codex_change_log.md"
QUESTIONS = CODEX_DIR / "research_questions.md"
README = ROOT / "README.md"
MAKEFILE = ROOT / "Makefile"
CI_LOCAL = ROOT / "ci_local.sh"


def ts() -> str:
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def ensure_codex_dir() -> None:
    CODEX_DIR.mkdir(exist_ok=True)


def log_change(msg: str) -> None:
    ensure_codex_dir()
    with CHANGELOG.open("a", encoding="utf-8") as f:
        f.write(f"- [{ts()}] {msg}\n")


def ask_gpt5(step: str, err: str, ctx: str) -> None:
    ensure_codex_dir()
    with QUESTIONS.open("a", encoding="utf-8") as f:
        f.write(
            "Question for ChatGPT-5:\n"
            f"While performing {step}, encountered the following error:\n"
            f"{err}\n"
            f"Context: {ctx}\n"
            "What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
        )


def run(cmd: list[str], step_label: str, check: bool = True, env: dict[str, str] | None = None):
    try:
        res = subprocess.run(
            cmd,
            cwd=ROOT,
            env=env or os.environ,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        print(res.stdout)
        if check and res.returncode != 0:
            raise RuntimeError(f"exit {res.returncode}\n{res.stdout}")
        return res.returncode, res.stdout
    except Exception as e:  # pragma: no cover - error path
        ask_gpt5(step_label, str(e), f"cmd={' '.join(cmd)}")
        log_change(f"❌ {step_label} failed: {e}")
        if check:
            raise
        return 1, str(e)


def normalize_readme() -> None:
    if not README.exists():
        return
    text = README.read_text(encoding="utf-8")
    repls = {
        r"\brunner[-_]?sha256\b": "CODEX_RUNNER_SHA256",
        r"\brunner[-_]?token\b": "CODEX_RUNNER_TOKEN",
    }
    orig = text
    for pat, to in repls.items():
        text = re.sub(pat, to, text, flags=re.IGNORECASE)
    if text != orig:
        README.write_text(text, encoding="utf-8")
        log_change("README normalized env secret references to CODEX_*")


def ensure_make_target_shells() -> None:
    snippet = ".PHONY: codex-gates\ncodex-gates:\n\t@bash ci_local.sh\n"
    if MAKEFILE.exists():
        mf = MAKEFILE.read_text(encoding="utf-8")
        if "codex-gates" not in mf or "@bash ci_local.sh" not in mf:
            MAKEFILE.write_text(mf.rstrip() + "\n\n" + snippet, encoding="utf-8")
            log_change("Added tiny Make target that shells to ci_local.sh")
    else:
        MAKEFILE.write_text(snippet, encoding="utf-8")
        log_change("Created Makefile with tiny codex-gates target")


def ensure_ci_local_present() -> None:
    expected = (
        "#!/usr/bin/env bash\n"
        "set -euo pipefail\n"
        "HERE=\"$(cd \"$(dirname \"${BASH_SOURCE[0]}\")\" && pwd)\"\n"
        "bash \"$HERE/tools/bootstrap_dev_env.sh\"\n"
        "source \"$HERE/.venv/bin/activate\"\n"
        ".venv/bin/pre-commit run --all-files\n"
        ".venv/bin/pytest\n"
    )
    if not CI_LOCAL.exists():
        CI_LOCAL.write_text(expected, encoding="utf-8")
        os.chmod(CI_LOCAL, 0o755)
        log_change("Created ci_local.sh (venv-pinned)")
        return
    cur = CI_LOCAL.read_text(encoding="utf-8")
    if ".venv/bin/pre-commit" not in cur or ".venv/bin/pytest" not in cur:
        CI_LOCAL.write_text(expected, encoding="utf-8")
        os.chmod(CI_LOCAL, 0o755)
        log_change("Hardened ci_local.sh to use venv binaries")


def maybe_run_gates():
    return run(["bash", "ci_local.sh"], "Phase 3.1: Run local gates", check=False)


def maybe_runner_and_autoscaler() -> None:
    env = os.environ.copy()
    if not env.get("GH_PAT") and not env.get("CODEX_RUNNER_TOKEN"):
        log_change("Skipped runner/autoscaler (no GH_PAT or CODEX_RUNNER_TOKEN)")
        return
    run(
        ["bash", "tools/ephem_runner.sh", "--labels", "linux,x64,codex"],
        "Phase 3.2: Bring up ephemeral runner",
        check=False,
        env=env,
    )
    run(
        ["bash", "tools/ephem_autoscaler.sh", "--branch", "0B_base_", "--scale-from-queue", "--cap", "4"],
        "Phase 3.3: Autoscale from queue",
        check=False,
        env=env,
    )


def doctor_pass() -> None:
    env = os.environ.copy()
    if not env.get("GH_PAT"):
        log_change("Skipped doctor (no GH_PAT)")
        return
    run(
        [
            "python3",
            "tools/runner_doctor.py",
            "--cleanup-offline",
            "--cleanup-dirs",
            "--min-age-mins",
            "60",
        ],
        "Phase 3.4: Runner doctor",
        check=False,
        env=env,
    )


def main() -> int:
    ensure_codex_dir()
    log_change("Begin codex_workflow_executor")
    try:
        normalize_readme()
    except Exception as e:  # pragma: no cover
        ask_gpt5("Phase 1: README normalization", str(e), "updating env secret references")
    try:
        ensure_make_target_shells()
        ensure_ci_local_present()
    except Exception as e:  # pragma: no cover
        ask_gpt5("Phase 1: Ensure make/entrypoint", str(e), "creating Make target and ci_local.sh")

    gates_rc, gates_out = 1, ""
    try:
        gates_rc, gates_out = maybe_run_gates()
        log_change(f"Local gates completed with exit={gates_rc}")
    except Exception as e:  # pragma: no cover
        ask_gpt5("Phase 3.1: Run local gates", str(e), "pre-commit/pytest via venv")

    try:
        maybe_runner_and_autoscaler()
        log_change("Runner bring-up and autoscaler attempted (best-effort)")
    except Exception as e:  # pragma: no cover
        ask_gpt5("Phase 3.2/3.3: Runner & autoscaler", str(e), "ephemeral config and queue scaling")

    try:
        doctor_pass()
        log_change("Doctor sweep attempted (cleanup offline runners & stale dirs)")
    except Exception as e:  # pragma: no cover
        ask_gpt5("Phase 3.4: Runner doctor", str(e), "cleanup cycle")

    try:
        ensure_codex_dir()
        summary = {
            "gates_exit_code": gates_rc,
            "change_log": str(CHANGELOG),
            "research_questions": str(QUESTIONS),
        }
        (CODEX_DIR / "last_summary.json").write_text(
            json.dumps(summary, indent=2), encoding="utf-8"
        )
        print(json.dumps(summary, indent=2))
        log_change("End codex_workflow_executor")
    except Exception as e:  # pragma: no cover
        ask_gpt5("Phase 6: Finalization", str(e), "writing last_summary.json / logs")
    return 0


if __name__ == "__main__":  # pragma: no cover
    try:
        sys.exit(main())
    except KeyboardInterrupt:  # pragma: no cover
        ask_gpt5("Global", "KeyboardInterrupt", "User interrupted script")
        log_change("Interrupted by user (KeyboardInterrupt)")
        sys.exit(130)
    except Exception as e:  # pragma: no cover
        ask_gpt5("Global", str(e), "Unhandled exception at toplevel")
        sys.exit(1)
