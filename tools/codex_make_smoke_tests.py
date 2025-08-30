#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Codex CLI — Generate Hello-Dataset HF-Trainer smoke tests and Logging Flags E2E tests.
Policy: DO NOT ACTIVATE ANY GitHub Actions Online files. All validations run locally.
"""
from __future__ import annotations
import os, sys, json, textwrap, subprocess, hashlib, tempfile
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
CODEX = ROOT / ".codex"
CHANGE_LOG = CODEX / "change_log.md"
ERRORS = CODEX / "errors.ndjson"
RESULTS = CODEX / "results.md"

SMOKE_DIR = ROOT / "tests" / "smoke"
SMOKE_DIR.mkdir(parents=True, exist_ok=True)

TB_SENT = "# BEGIN: CODEX_SMOKE_LOGGING_FLAGS"
TR_SENT = "# BEGIN: CODEX_SMOKE_TRAINER"
MLF_SENT = "# BEGIN: CODEX_SMOKE_MLFLOW_NOOP"
READ_SENT = "<!-- BEGIN: CODEX_SMOKE_README -->"

FILE_TRAINER = SMOKE_DIR / "test_hf_trainer_hello.py"
FILE_FLAGS = SMOKE_DIR / "test_logging_flags_end_to_end.py"
FILE_MLNOOP = SMOKE_DIR / "test_mlflow_utils_noop.py"

TRAINER_CODE = f"{TR_SENT}\n" + """
import os, tempfile
from pathlib import Path
import pytest

def test_hf_trainer_on_tiny_hello_dataset():
    try:
        from datasets import Dataset
        from transformers import (
            AutoTokenizer, AutoModelForCausalLM,
            DataCollatorForLanguageModeling, Trainer, TrainingArguments
        )
    except Exception as e:
        pytest.skip(f"missing libs: {e}")

    texts = [
        "Hello Codex, this is a tiny trainer smoke test.",
        "Small data, small model, single-step training.",
    ]
    ds = Dataset.from_list([{"text": t} for t in texts])

    model_id = "sshleifer/tiny-gpt2"
    tok = AutoTokenizer.from_pretrained(model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    def tok_fn(batch):
        return tok(batch["text"], truncation=True, padding="max_length", max_length=64)

    ds_tok = ds.map(tok_fn, batched=True, remove_columns=["text"])
    collator = DataCollatorForLanguageModeling(tokenizer=tok, mlm=False)
    model = AutoModelForCausalLM.from_pretrained(model_id)

    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out"
        args = TrainingArguments(
            output_dir=str(out), overwrite_output_dir=True,
            per_device_train_batch_size=2, num_train_epochs=1, max_steps=1,
            logging_steps=1, save_steps=1, report_to=[], fp16=False,
        )
        trainer = Trainer(model=model, args=args, train_dataset=ds_tok, data_collator=collator)
        trainer.train()
        trainer.save_state()
        assert (out / "trainer_state.json").exists()
        assert any(out.glob("checkpoint-*"))
"""

FLAGS_CODE = f"{TB_SENT}\n" + """
import os, argparse, tempfile, importlib.util
from pathlib import Path
import pytest

def test_deploy_logging_flags_bootstrap_and_log():
    # dynamic import of deploy_codex_pipeline.py
    target = Path("deploy_codex_pipeline.py").resolve()
    if not target.exists():
        pytest.skip("deploy_codex_pipeline.py not present; generate or patch first")

    spec = importlib.util.spec_from_file_location("deploy_codex_pipeline", str(target))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore

    ap = argparse.ArgumentParser()
    if hasattr(mod, "_codex_patch_argparse"):
        mod._codex_patch_argparse(ap)
    else:
        pytest.skip("_codex_patch_argparse not found")

    ns = ap.parse_args([
        "--enable-wandb", "--mlflow-enable", "--mlflow-experiment", "codex-smoke",
    ])

    os.environ.setdefault("WANDB_MODE", "offline")

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "run"
        run_dir.mkdir(parents=True, exist_ok=True)
        if not hasattr(mod, "_codex_logging_bootstrap") or not hasattr(mod, "_codex_log_all"):
            pytest.skip("logging helpers missing; patch deploy_codex_pipeline.py")

        handles = mod._codex_logging_bootstrap(ns, run_dir, params={"wandb_project": "codex-smoke"})
        mod._codex_log_all(handles, step=1, metrics={"loss": 0.123})
        tb_dir = run_dir / "tb"
        if handles.get("tb") is not None:
            assert any(tb_dir.glob("events.*")), "TensorBoard events missing"
"""

MLNOOP_CODE = f"{MLF_SENT}\n" + """
import pytest

def test_mlflow_utils_tolerant_when_missing():
    try:
        from codex_ml.tracking import (
            MlflowConfig,
            log_artifacts,
            log_metrics,
            log_params,
            start_run,
        )
    except Exception as e:
        pytest.skip(f"tracking utils missing: {e}")
    cfg = MlflowConfig(enable=False)
    with start_run(cfg) as run:
        assert run is False
    log_params({"lr": 1e-3})
    log_metrics({"loss": 0.1}, step=1)
    log_artifacts([])
    assert True
"""

README_NOTE = f"""{READ_SENT}
## Smoke Tests & Offline Logging
This repository includes CPU-friendly smoke tests for HF Trainer and end-to-end logging flags. All logging integrations are offline-safe for local validation.
"""

# -------------- helpers --------------
def _ensure_files():
    CODEX.mkdir(parents=True, exist_ok=True)
    for p in (CHANGE_LOG, ERRORS, RESULTS):
        if not p.exists():
            p.write_text("", encoding="utf-8")

def _log_change(action: str, path: Path, why: str, preview: str):
    if not CHANGE_LOG.exists() or CHANGE_LOG.stat().st_size == 0:
        CHANGE_LOG.write_text("# Codex Change Log\n", encoding="utf-8")
    with CHANGE_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"## {datetime.utcnow().isoformat()}Z — {path.relative_to(ROOT)}\n- **Action:** {action}\n- **Rationale:** {why}\n")
        fh.write("```diff\n" + preview[:6000] + "\n```\n\n")

def _q5(step: str, err: str, ctx: str):
    block = f"""
Question for ChatGPT-5 {datetime.utcnow().isoformat()}Z:
While performing [{step}], encountered the following error:
{err}
Context: {ctx}
What are the possible causes, and how can this be resolved while preserving intended functionality?
""".strip()
    with ERRORS.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"ts": datetime.utcnow().isoformat()+"Z", "step": step, "error": err, "context": ctx}) + "\n")
    sys.stderr.write(block + "\n")

def _upsert(path: Path, content: str, sentinel: str):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            existing = path.read_text(encoding="utf-8", errors="ignore")
            if sentinel in existing:
                return
            new_text = existing + ("\n" if not existing.endswith("\n") else "") + content
            path.write_text(new_text, encoding="utf-8")
            _log_change("append", path, f"guarded by {sentinel}", content)
        else:
            path.write_text(content, encoding="utf-8")
            _log_change("create", path, f"guarded by {sentinel}", content)
    except Exception as e:
        _q5("3: upsert file", str(e), f"path={path}")

# -------------- README parsing / reference cleanup --------------
def _readme_cleanup():
    p = ROOT / "README.md"
    if not p.exists():
        _upsert(p, README_NOTE, READ_SENT)
        return
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
        cleaned = txt.replace(":contentReference", "")
        if cleaned == txt:
            _upsert(p, README_NOTE, READ_SENT)
        else:
            p.write_text(cleaned, encoding="utf-8")
            _log_change("edit", p, "Removed contentReference tokens", cleaned)
            _upsert(p, README_NOTE, READ_SENT)
    except Exception as e:
        _q5("2: README parsing", str(e), str(p))

# -------------- main ops --------------
def apply():
    _ensure_files()
    _upsert(FILE_TRAINER, TRAINER_CODE, TR_SENT)
    _upsert(FILE_FLAGS, FLAGS_CODE, TB_SENT)
    _upsert(FILE_MLNOOP, MLNOOP_CODE, MLF_SENT)
    _readme_cleanup()

def validate():
    with RESULTS.open("a", encoding="utf-8") as fh:
        fh.write(f"\n# Validation {datetime.utcnow().isoformat()}Z\n")
        cmds = [
            ("python -m compileall .", ["python", "-m", "compileall", "."]),
            ("pytest -q -k smoke --maxfail=1", ["pytest", "-q", "-k", "smoke", "--maxfail", "1"]),
        ]
        for name, cmd in cmds:
            fh.write(f"\n## {name}\n````\n")
            try:
                p = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
                fh.write((p.stdout or "") + (p.stderr or "") + f"\n(exit={p.returncode})\n")
                if p.returncode != 0:
                    _q5("6: Finalization — validation", f"exit {p.returncode}", " ".join(cmd))
            except Exception as e:
                fh.write(f"ERROR: {e}\n")
                _q5("6: Finalization — validation", str(e), " ".join(cmd))
            fh.write("````\n")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Create smoke tests and README note (idempotent)")
    ap.add_argument("--validate", action="store_true", help="Run local validations (no CI activation)")
    args = ap.parse_args()
    if args.apply:
        apply()
    if args.validate:
        validate()
    if not (args.apply or args.validate):
        print("Usage: --apply [--validate]")

if __name__ == "__main__":
    main()
