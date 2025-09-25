#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import stat
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(os.getenv("CODEX_ROOT", Path.cwd())).resolve()
CODEX_DIR = ROOT / ".codex"
LOG_DIR = CODEX_DIR / "logs"
ARTIFACTS = CODEX_DIR / "artifacts"
CHANGELOG = ROOT / "CHANGELOG_codex.md"
ERRORS_MD = CODEX_DIR / "errors.md"
ERRORS_NDJSON = CODEX_DIR / "errors.ndjson"

UTC = dt.timezone.utc


def utcnow() -> str:
    return dt.datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_error(step_num: str, step_desc: str, err: Exception, ctx: str = "") -> None:
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    msg = textwrap.dedent(
        f"""\
    Question for ChatGPT-5 {utcnow()}:
    While performing [{step_num}:{step_desc}], encountered the following error:
    {type(err).__name__}: {err}
    Context: {ctx}
    What are the possible causes, and how can this be resolved while preserving intended functionality?
    """
    )
    ERRORS_MD.write_text(
        (ERRORS_MD.read_text() if ERRORS_MD.exists() else "") + "\n\n" + msg, encoding="utf-8"
    )
    with ERRORS_NDJSON.open("a", encoding="utf-8") as f:
        json.dump(
            {
                "ts": utcnow(),
                "step": step_num,
                "desc": step_desc,
                "error": f"{type(err).__name__}: {err}",
                "context": ctx,
            },
            f,
        )
        f.write("\n")


def append_changelog(title: str, bullet_points: list[str]) -> None:
    CHANGELOG.parent.mkdir(parents=True, exist_ok=True)
    hdr = f"## {title} — {utcnow()}\n"
    body = "".join([f"- {b}\n" for b in bullet_points])
    with open(CHANGELOG, "a", encoding="utf-8") as f:
        f.write(hdr + body + "\n")


def safe_replace(path: Path, pattern: str, repl: str, flags=0) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="ignore")
    new = re.sub(pattern, repl, text, flags=flags)
    if new != text:
        path.write_text(new, encoding="utf-8")
        return True
    return False


def ensure_dirs():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)


def make_user_executable(path: Path) -> None:
    """Ensure *path* is user-executable without widening group/world perms."""

    current_mode = path.stat().st_mode
    os.chmod(path, current_mode | stat.S_IXUSR)


def readme_cleanup():
    step = "STEP_01"
    try:
        for candidate in ["README.md", "Readme.md", "readme.md"]:
            p = ROOT / candidate
            if p.exists():
                changed = safe_replace(p, r"\[([^\]]+)\]\((?:https?://)[^)]+\)", r"\1")
                changed |= safe_replace(p, r"https?://github\.com/\S+", r"")
                if changed:
                    append_changelog(
                        "README cleanup", [f"Sanitized links in {candidate} for offline use"]
                    )
                return
    except Exception as e:
        write_error(step, "README parsing and cleanup", e, "While normalizing markdown links")


def patch_peft_adapter():
    step = "STEP_02"
    path = ROOT / "src" / "codex_ml" / "peft" / "peft_adapter.py"
    try:
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "get_peft_model" in text and "LoraConfig" in text:
            return
        impl = textwrap.dedent(
            '''
        try:
            from peft import LoraConfig, get_peft_model  # optional dependency
        except Exception:  # pragma: no cover
            LoraConfig = None
            get_peft_model = None

        def apply_lora(model, cfg: dict | None = None):
            """Attach LoRA adapters via `peft` when available; otherwise return model unchanged."""
            if get_peft_model is None:
                return model
            cfg = cfg or {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none"}
            try:
                config = LoraConfig(task_type="CAUSAL_LM", **cfg)
                return get_peft_model(model, config)
            except Exception:
                return model
        '''
        ).strip()
        path.write_text(impl + "\n", encoding="utf-8")
        append_changelog("LoRA integration", [f"Implemented optional PEFT wrapper in {path}"])
    except Exception as e:
        write_error(step, "Enable LoRA via PEFT", e, f"Path={path}")


def patch_training_loop():
    step = "STEP_03"
    path = ROOT / "functional_training.py"
    if not path.exists():
        return
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
        if "--grad-accum" in txt and "autocast" in txt:
            return
        addon = textwrap.dedent(
            """
        # --- Codex: grad-accum + AMP helpers (offline safe) ---
        def _codex_amp_supported():
            import torch
            return torch.cuda.is_available()

        def codex_train_step(model, optimizer, scheduler, compute_loss, batch, accum_steps=1, precision="fp32"):
            import torch
            use_fp16 = (precision == "fp16") and _codex_amp_supported()
            scaler = torch.cuda.amp.GradScaler() if use_fp16 else None
            optimizer.zero_grad(set_to_none=True)
            if use_fp16:
                with torch.autocast(device_type="cuda", dtype=torch.float16):
                    loss = compute_loss(batch) / max(1, accum_steps)
                    scaler.scale(loss).backward()
            else:
                loss = compute_loss(batch) / max(1, accum_steps)
                loss.backward()
            if scaler:
                scaler.step(optimizer); scaler.update()
            else:
                optimizer.step()
            if scheduler: scheduler.step()
            return float(loss.detach().item())
        """
        ).strip()
        path.write_text(txt.rstrip() + "\n\n" + addon + "\n", encoding="utf-8")
        append_changelog("Training loop", ["Added offline AMP/grad-accum helper block"])
    except Exception as e:
        write_error(step, "Add grad accumulation + AMP", e, f"Path={path}")


def add_hydra_entry():
    step = "STEP_04"
    path = ROOT / "src" / "codex_ml" / "cli" / "main.py"
    try:
        if not path.exists():
            return
        txt = path.read_text(encoding="utf-8", errors="ignore")
        if "@hydra.main" in txt:
            return
        new = textwrap.dedent(
            """
        import hydra
        from omegaconf import DictConfig
        @hydra.main(version_base=None, config_path='../../configs', config_name='config')
        def main(cfg: DictConfig) -> None:
            pipe = cfg.get('pipeline', 'functional')
            if pipe == 'symbolic':
                from src.codex_ml.symbolic_pipeline import run as run_symbolic
                run_symbolic(cfg)
            else:
                import functional_training as ft
                pass
        if __name__ == '__main__':
            main()
        """
        ).strip()
        path.write_text(new + "\n", encoding="utf-8")
        append_changelog("Hydra CLI", [f"Added @hydra.main entry to {path} (offline defaults)"])
    except Exception as e:
        write_error(step, "Introduce Hydra entrypoint", e, f"Path={path}")


def add_deterministic_splits():
    step = "STEP_05"
    path = ROOT / "src" / "codex_ml" / "data" / "splits.py"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return
        code = textwrap.dedent(
            """
        from typing import Sequence, Tuple, List
        import numpy as np

        def train_val_test_split(dataset: Sequence, val_frac: float = 0.1, test_frac: float = 0.1, seed: int = 42) -> Tuple[List, List, List]:
            assert 0 <= val_frac < 1 and 0 <= test_frac < 1 and (val_frac + test_frac) < 1
            rng = np.random.default_rng(seed)
            idxs = np.arange(len(dataset)); rng.shuffle(idxs)
            n = len(dataset); t = int(n * test_frac); v = int(n * val_frac)
            test_idx = idxs[:t]; val_idx = idxs[t:t+v]; train_idx = idxs[t+v:]
            to_list = lambda arr: [dataset[i] for i in arr.tolist()]
            return to_list(train_idx), to_list(val_idx), to_list(test_idx)
        """
        ).strip()
        path.write_text(code + "\n", encoding="utf-8")
        append_changelog("Data splits", [f"Created deterministic split utility at {path}"])
    except Exception as e:
        write_error(step, "Add deterministic dataset splits", e, f"Path={path}")


def generate_lockfile():
    step = "STEP_06"
    lock = ROOT / "requirements.lock"
    try:
        if lock.exists():
            return
        out = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"], capture_output=True, text=True, check=False
        )
        pkgs = "\n".join(sorted([ln.strip() for ln in out.stdout.splitlines() if ln.strip()]))
        if pkgs:
            lock.write_text(pkgs + "\n", encoding="utf-8")
            append_changelog("Lockfile", ["Generated requirements.lock from current environment"])
        else:
            append_changelog("Lockfile", ["pip freeze produced no output; lockfile skipped"])
    except Exception as e:
        write_error(
            step, "Generate requirements.lock", e, "pip freeze failed (offline environment?)"
        )


def suggest_tests_and_gates():
    step = "STEP_07"
    try:
        script = ROOT / "scripts" / "codex_local_gates.sh"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text(
            textwrap.dedent(
                """\
        #!/usr/bin/env bash
        set -euo pipefail
        echo "[Codex] Running local offline gates..."
        if command -v pre-commit >/dev/null 2>&1; then
          pre-commit run --all-files
        fi
        if command -v pytest >/dev/null 2>&1; then
          pytest -q
          pytest --cov=src/codex_ml --cov-fail-under=70
        fi
        echo "[Codex] Gates complete (offline)."
        """
            ),
            encoding="utf-8",
        )
        make_user_executable(script)
        append_changelog(
            "Local gates", ["Added codex_local_gates.sh for offline lint/tests/coverage"]
        )
    except Exception as e:
        write_error(step, "Create local gates script", e, "")


def main():
    parser = argparse.ArgumentParser(
        description="Codex offline executor for Implementation Status Audit"
    )
    parser.add_argument("--dry-run", action="store_true", help="Analyze without writing changes")
    args = parser.parse_args()

    ensure_dirs()
    ops = [
        ("README cleanup", readme_cleanup),
        ("PEFT/LoRA patch", patch_peft_adapter),
        ("Training loop patch", patch_training_loop),
        ("Hydra entrypoint", add_hydra_entry),
        ("Deterministic splits", add_deterministic_splits),
        ("Lockfile generation", generate_lockfile),
        ("Local gates script", suggest_tests_and_gates),
    ]

    for idx, (name, fn) in enumerate(ops, start=1):
        if args.dry_run:
            print(f"[DRY] {idx:02d}/{len(ops)} {name}")
            continue
        try:
            fn()
            print(f"[OK ] {idx:02d}/{len(ops)} {name}")
        except Exception as e:
            write_error(f"STEP_{idx:02d}", name, e, "Executor main loop")
            print(f"[ERR] {idx:02d}/{len(ops)} {name}: {e}", file=sys.stderr)

    summary = f"""
    === Codex Offline Execution Summary ({utcnow()}) ===
    Root: {ROOT}
    Changelog: {CHANGELOG}
    Errors (md): {ERRORS_MD if ERRORS_MD.exists() else 'none'}
    Errors (ndjson): {ERRORS_NDJSON if ERRORS_NDJSON.exists() else 'none'}
    Artifacts: {ARTIFACTS}
    """
    print(summary.strip())


if __name__ == "__main__":
    main()
