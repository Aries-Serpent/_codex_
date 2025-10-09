#!/usr/bin/env python3
"""
Codex Sequential Runner (offline, local-only)
- Parses README
- Applies best-effort patches
- Attempts tests/gates locally
- Captures errors as ChatGPT-5 research questions
- Finalizes deliverables

Invariant: DO NOT ACTIVATE ANY GitHub Actions. All checks run locally here.
"""
import argparse, os, sys, re, json, subprocess, shutil, datetime, hashlib
from pathlib import Path
from typing import List, Tuple, Optional

ROOT = Path.cwd()
SESSION_DIR = ROOT / ".codex" / f"session_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
LOGS = SESSION_DIR / "logs"
PATCHES = SESSION_DIR / "patches"
ARTIFACTS = SESSION_DIR / "artifacts"
CHANGELOG = ROOT / "CHANGELOG_CODEX.md"
RQ = ROOT / "RESEARCH_QUESTIONS.md"

SUPPLIED_TASK_BASENAME = "supplied_task.md"

def ts() -> str:
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_dirs():
    for p in [SESSION_DIR, LOGS, PATCHES, ARTIFACTS]:
        p.mkdir(parents=True, exist_ok=True)

def write_file(p: Path, content: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

def append_file(p: Path, content: str):
    with p.open("a", encoding="utf-8") as f:
        f.write(content)

def sh(cmd: List[str], log_name: str, allow_fail=True) -> Tuple[int, str]:
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=False)
        out = (proc.stdout or "") + ("\n" + (proc.stderr or "") if proc.stderr else "")
        write_file(LOGS / f"{log_name}.log", out)
        if proc.returncode != 0 and not allow_fail:
            raise subprocess.CalledProcessError(proc.returncode, cmd, out)
        return proc.returncode, out
    except Exception as e:
        msg = f"{type(e).__name__}: {e}"
        write_file(LOGS / f"{log_name}.log", msg)
        return 1, msg

def hash_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def snapshot_git():
    code, out = sh(["git", "rev-parse", "--short", "HEAD"], "git_rev", allow_fail=True)
    if code == 0:
        write_file(ARTIFACTS / "commit.txt", out.strip())

def save_supplied_task_text(text: str):
    write_file(ARTIFACTS / SUPPLIED_TASK_BASENAME, text)

def record_rq(step_number: str, step_desc: str, error_message: str, ctx: str):
    block = (
        f"Question for ChatGPT-5 {ts()}:\n"
        f"While performing [{step_number}:{step_desc}], encountered the following error:\n"
        f"{error_message}\n"
        f"Context: {ctx}\n"
        f"What are the possible causes, and how can this be resolved while preserving intended functionality?\n\n"
    )
    append_file(RQ, block)

def record_changelog(entry: str):
    header = f"## {ts()} — Codex Run\n"
    append_file(CHANGELOG, header + entry.strip() + "\n\n")

def safe_load(path: Path) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        record_rq("PH1", f"Read {path}", str(e), "File read failure")
        return None

def replace_readme_refs(readme: Path) -> Tuple[bool, str]:
    s = safe_load(readme)
    if s is None:
        return False, "README not found or unreadable"
    orig = s
    s = re.sub(r"!\[[^\]]*\]\(https?://.*?github.*?/actions.*?\)", "", s, flags=re.I)
    s = re.sub(r"\[!\[[^\]]*\]\(.*?\)\]\(.*?\)", "", s)
    s = re.sub(r"(?i)github actions[^\n]*", "Local CI only: run `pre-commit` and `pytest` locally.", s)
    changed = s != orig
    if changed:
        write_file(readme, s)
        record_changelog("- README: removed online badges and normalized CI to offline/local.")
    return changed, "OK"

def apply_unified_patch(file_path: Path, patch_blocks: List[Tuple[str, str]]) -> Tuple[bool, str]:
    s = safe_load(file_path)
    if s is None:
        return False, f"{file_path} unreadable"
    orig = s
    for idx, (pattern, replacement) in enumerate(patch_blocks, start=1):
        try:
            new_s, _ = re.subn(pattern, replacement, s, count=1, flags=re.DOTALL)
            s = new_s
        except re.error as e:
            record_rq("PH3", f"Regex patch {file_path}#{idx}", str(e), f"pattern={pattern[:80]}...")
    changed = s != orig
    if changed:
        write_file(file_path, s)
    return changed, "OK" if changed else "No matching context; file left unchanged"

def patch_tokenizer_ids(path: Path):
    s = safe_load(path)
    if s is None:
        return False, "missing"
    if "def pad_id" in s:
        record_changelog("- Tokenizer: skip/no change (already has pad_id/eos_id).")
        return False, "already"
    insert_after = (
        r"(class\s+[A-Za-z0-9_]+\([^)]+\):.*?\n)    @property\n    def vocab_size.*?\n        return int\(self.tokenizer.vocab_size\)\n"
    )
    replacement = (
        "\1    @property\n    def vocab_size(self) -> int:  # type: ignore[override]\n        return int(self.tokenizer.vocab_size)\n\n    @property\n    def pad_id(self) -> int:  # type: ignore[override]\n        return int(self.tokenizer.pad_token_id or 0)\n\n    @property\n    def eos_id(self) -> int:  # type: ignore[override]\n        return int(self.tokenizer.eos_token_id or 0)\n"
    )
    changed, msg = apply_unified_patch(path, [(insert_after, replacement)])
    if changed:
        record_changelog("- Tokenizer: added pad_id/eos_id accessors.")
    return changed, msg

def patch_functional_training(path: Path):
    pattern = r"except Exception:\n\s*pass"
    replacement = (
        "except Exception as exc:\n            print(f\"[monitoring-error] {exc}\", file=sys.stderr)"
    )
    changed, msg = apply_unified_patch(path, [(pattern, replacement)])
    if changed:
        record_changelog("- functional_training: surfaced monitoring exceptions to stderr.")
    return changed, msg

def patch_train_loop_grad_accum(path: Path):
    patches = [
        (
            r'(ap.add_argument\("--epochs",.*?\)\))',
            "\\1\n    ap.add_argument(\"--grad-accum\", type=int, default=1, help=\"accumulate gradients over N steps\")",
        ),
        (
            r"(def demo_epoch\(epoch: int\) -> Dict\[str, float\]:)",
            "def demo_epoch(epoch: int, grad_accum: int = 1) -> Dict[str, float]:",
        ),
        (
            r"ppl = perplexity\(logits, targets, from_logits=True\)\n    return {\"acc\": acc, \"ppl\": ppl}\n",
            "ppl = perplexity(logits, targets, from_logits=True)\n    return {\"acc\": acc, \"ppl\": ppl, \"grad_accum\": grad_accum}\n",
        ),
        (
            r"for ep in range\(args.epochs\):\n        m = demo_epoch\(ep\)\n",
            "for ep in range(args.epochs):\n        m = demo_epoch(ep, grad_accum=args.grad_accum)\n",
        ),
    ]
    changed, msg = apply_unified_patch(path, patches)
    if changed:
        record_changelog("- train_loop: added --grad-accum and metric logging.")
    return changed, msg

def patch_checkpoint_system_meta(path: Path):
    pattern = r"_write_json\(ep_dir / \"rng.json\", _rng_dump\(\)\)"
    replacement = (
        "_write_json(ep_dir / \"rng.json\", _rng_dump())\n        _write_json(ep_dir / \"system.json\", _codex_sample_system())"
    )
    changed, msg = apply_unified_patch(path, [(pattern, replacement)])
    if changed:
        record_changelog("- checkpointing: now writes system.json for reproducibility.")
    return changed, msg

def patch_pyproject_cli(path: Path):
    s = safe_load(path)
    if s is None:
        return False, "missing"
    if "codex-ml-cli" in s:
        record_changelog("- pyproject: CLI already present.")
        return False, "already"
    if "[project.scripts]" in s:
        s2 = re.sub(
            r"(\[project.scripts\]\n)",
            "\\1codex-ml-cli = \"codex_ml.cli.main:main\"\n",
            s,
            count=1,
        )
    else:
        s2 = s + "\n[project.scripts]\ncodex-ml-cli = \"codex_ml.cli.main:main\"\n"
    write_file(path, s2)
    record_changelog("- pyproject: added codex-ml-cli entry point.")
    return True, "added"

def add_tests_if_possible():
    tests_dir = ROOT / "tests"
    if not tests_dir.exists():
        record_changelog("- tests: directory not present; skipped adding tests.")
        return
    write_file(
        tests_dir / "test_tokenizer_ids.py",
        "from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter\n\n\n"
        "def test_tokenizer_pad_eos_ids():\n    tok = HFTokenizerAdapter.load()\n    assert isinstance(tok.pad_id, int)\n    assert isinstance(tok.eos_id, int)\n",
    )
    write_file(
        tests_dir / "test_trainloop_grad_accum.py",
        "from codex_ml.train_loop import demo_epoch\n\n\n"
        "def test_demo_epoch_includes_grad_accum():\n    metrics = demo_epoch(0, grad_accum=4)\n    assert metrics['grad_accum'] == 4\n",
    )
    write_file(
        tests_dir / "test_checkpoint_system_meta.py",
        "import json\nfrom codex_ml.utils.checkpointing import CheckpointManager\n\n\n"
        "def test_checkpoint_writes_system_meta(tmp_path):\n"
        "    mgr = CheckpointManager(tmp_path)\n"
        "    mgr.save(0)\n"
        "    path = tmp_path / 'epoch-0' / 'system.json'\n"
        "    assert path.exists()\n"
        "    data = json.loads(path.read_text())\n"
        "    assert isinstance(data, dict)\n",
    )
    record_changelog("- tests: added tokenizer, grad accum, system meta tests.")

def try_local_gates():
    if (ROOT / ".pre-commit-config.yaml").exists():
        code, _ = sh(["bash", "-lc", "pre-commit run --all-files"], "precommit", allow_fail=True)
        if code != 0:
            record_rq("PH6", "Run pre-commit", "Pre-commit exited non-zero", "Local offline gate; see logs/precommit.log")
            record_changelog("- pre-commit: ran with non-zero exit; see logs.")
        else:
            record_changelog("- pre-commit: passed.")
    else:
        record_changelog("- pre-commit: config not found; skipped.")
    code, _ = sh(["bash", "-lc", "pytest -q"], "pytest", allow_fail=True)
    if code != 0:
        record_rq("PH6", "Run pytest", "pytest exited non-zero", "Local tests; see logs/pytest.log")
        record_changelog("- pytest: ran with non-zero exit; see logs.")
    else:
        record_changelog("- pytest: passed.")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--supplied-task-file", type=str, default=None)
    parser.add_argument("--no-gates", action="store_true")
    args = parser.parse_args()

    os.environ["CODEX_OFFLINE_CI"] = "1"
    ensure_dirs()
    snapshot_git()

    supplied_text = ""
    if args.supplied_task_file and Path(args.supplied_task_file).exists():
        supplied_text = Path(args.supplied_task_file).read_text(encoding="utf-8")
    save_supplied_task_text(supplied_text)

    readme = ROOT / "README.md"
    if readme.exists():
        replace_readme_refs(readme)

    targets = {
        "tokenizer": ROOT / "src" / "codex_ml" / "tokenization" / "hf_tokenizer.py",
        "functional_training": ROOT / "functional_training.py",
        "train_loop": ROOT / "src" / "codex_ml" / "train_loop.py",
        "checkpointing": ROOT / "src" / "codex_ml" / "utils" / "checkpointing.py",
        "pyproject": ROOT / "pyproject.toml",
    }

    patch_tokenizer_ids(targets["tokenizer"]) if targets["tokenizer"].exists() else None
    patch_functional_training(targets["functional_training"]) if targets["functional_training"].exists() else None
    patch_train_loop_grad_accum(targets["train_loop"]) if targets["train_loop"].exists() else None
    patch_checkpoint_system_meta(targets["checkpointing"]) if targets["checkpointing"].exists() else None
    patch_pyproject_cli(targets["pyproject"]) if targets["pyproject"].exists() else None

    add_tests_if_possible()

    if not args.no_gates:
        try_local_gates()
    else:
        record_changelog("- Gates: skipped by --no-gates.")

    summary = {
        "timestamp": ts(),
        "session_dir": str(SESSION_DIR),
        "logs": [str(p) for p in LOGS.glob("*.log")],
        "invariant": "GitHub Actions not activated; all checks ran locally.",
    }
    write_file(ARTIFACTS / "summary.json", json.dumps(summary, indent=2))

    print("=== Codex Deliverables ===")
    print(f"- CHANGELOG: {CHANGELOG}")
    print(f"- RESEARCH QUESTIONS: {RQ}")
    print(f"- SESSION: {SESSION_DIR}")
    print(f"- SUMMARY: {ARTIFACTS / 'summary.json'}")
    print("\nInvariant respected: NO GitHub Actions were enabled or modified.")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        record_rq("PH0", "Runner crash", str(e), "Top-level exception")
        print(f"[fatal] {e}", file=sys.stderr)
        sys.exit(1)
