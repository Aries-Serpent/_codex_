#!/usr/bin/env python3
"""End-to-end workflow for applying codex audit tasks.

This script is intended to run inside the codex environment.  It performs the
following steps:

1. Preparation: create required directories and load context (README, existing
   status update).  Determine repository root from script location.
2. Search & Mapping: walk the repository to collect Python files containing
   specific keywords (token, reward, rl).  This mapping is appended to a
   `.codex/results.md` report.  Parse README for broken links (replace GitHub
   raw links with local references) and store the cleaned README in
   `.codex/clean_readme.md`.
3. Best-Effort Construction: if the `codex_ml/interfaces` package is missing,
   invoke `tools/apply_interfaces.py --apply` to generate interface stubs and
   compatibility tests.  Apply the NVML fallback patch by editing
   `src/codex_ml/callbacks/system_metrics.py`.  Add HFTokenizerAdapter if not
   present.  Generate a default Hydra config.  Append packaging metadata to
   `pyproject.toml` if missing.  All modifications are recorded in the change
   log (`.codex/change_log.md`).
4. Controlled Pruning: for each expected component (RL loop, distributed
   training, HF datasets integration) that cannot be constructed, write a note
   in `.codex/deferred.md` explaining why it is deferred.
5. Error Capture: wrap each modification in a try/except block.  On error,
   append a record to `.codex/errors.ndjson` and print a formatted question for
   ChatGPT @codex describing the error and context.
6. Finalization: update the status update file and generate the codex-ready
   task sequence YAML (`codex_ready_task_sequence.yaml`) reflecting the tasks
   executed.

Note: This script avoids triggering any GitHub actions; all operations occur
locally within the codex environment.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import textwrap
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def ts() -> str:
    """Return an ISO-8601 timestamp without microseconds."""

    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def _append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(text)


def log_change(change_log: Path, action: str, path: Path, why: str, preview: str = "") -> None:
    """Append an entry to the change log."""

    change_log.parent.mkdir(parents=True, exist_ok=True)
    if not change_log.exists():
        change_log.write_text("# Codex Change Log\n\n", encoding="utf-8")
    entry = [
        f"## {ts()} — {_rel(path)}",
        f"- **Action:** {action}",
        f"- **Rationale:** {why}",
    ]
    if preview:
        entry.append("```diff\n" + preview.strip() + "\n```")
    entry.append("")
    _append_text(change_log, "\n".join(entry) + "\n")


def record_error(errors: Path, step: str, err: Exception, ctx: str) -> None:
    """Record an error to the NDJSON log and print a ChatGPT question."""

    errors.parent.mkdir(parents=True, exist_ok=True)
    entry = {"ts": ts(), "step": step, "error": str(err), "context": ctx}
    _append_text(errors, json.dumps(entry) + "\n")
    question = textwrap.dedent(
        f"""
        Question for ChatGPT @codex {ts()}:
        While performing [{step}], encountered the following error:
        {err}
        Context: {ctx}
        What are the possible causes, and how can this be resolved while
        preserving intended functionality?
        """
    )
    sys.stderr.write(question)


def _collect_python_files(patterns: Iterable[str]) -> list[Path]:
    matches: list[Path] = []
    lowered = tuple(p.lower() for p in patterns)
    for candidate in REPO_ROOT.rglob("*.py"):
        rel = candidate.relative_to(REPO_ROOT)
        name = rel.as_posix().lower()
        if any(pat in name for pat in lowered):
            matches.append(rel)
    return matches


def main() -> None:
    codex_dir = REPO_ROOT / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    change_log = codex_dir / "change_log.md"
    errors_log = codex_dir / "errors.ndjson"

    # Phase 1: Preparation
    try:
        readme = REPO_ROOT / "README.md"
        if readme.exists():
            content = readme.read_text(encoding="utf-8", errors="ignore")
            cleaned = re.sub(r"https://raw\.githubusercontent\.com/[^\s]+", "[external]", content)
            cleaned_path = codex_dir / "clean_readme.md"
            cleaned_path.write_text(cleaned, encoding="utf-8")
            preview = "\n".join(cleaned.splitlines()[:10])
            log_change(change_log, "update", readme, "Stored cleaned README", preview)
    except Exception as e:
        record_error(errors_log, "1: Preparation — clean README", e, "README.md")

    # Phase 2: Search & Mapping
    try:
        results = codex_dir / "results.md"
        matches = _collect_python_files(["token", "reward", "rl", "ppo", "agent"])
        header = f"# Repo scan {ts()}\n"
        body = "".join(f"- {path.as_posix()}\n" for path in matches)
        results.write_text(header + body, encoding="utf-8")
        preview_lines = (header + body).splitlines()[:20]
        log_change(
            change_log, "update", results, "Recorded search results", "\n".join(preview_lines)
        )
    except Exception as e:
        record_error(errors_log, "2: Search & Mapping — scanning modules", e, str(REPO_ROOT))

    # Phase 3: Best-Effort Construction
    # 3a: Generate interfaces if missing
    try:
        iface_dir = REPO_ROOT / "src" / "codex_ml" / "interfaces"
        if not iface_dir.exists():
            script = REPO_ROOT / "tools" / "apply_interfaces.py"
            if script.exists():
                subprocess.run([sys.executable, str(script), "--apply"], check=True)
                log_change(
                    change_log,
                    "generate",
                    iface_dir,
                    "Generated interfaces via apply_interfaces script",
                )
    except Exception as e:
        record_error(
            errors_log,
            "3: Best-Effort Construction — generate interfaces",
            e,
            str(iface_dir),
        )

    # 3b: Apply NVML fallback patch
    try:
        sysmet = REPO_ROOT / "src" / "codex_ml" / "callbacks" / "system_metrics.py"
        if sysmet.exists():
            text = sysmet.read_text(encoding="utf-8")
            if "_NVML_AVAILABLE" not in text and "import pynvml" in text:
                replacement = textwrap.dedent(
                    """
                    try:
                        import pynvml
                        _NVML_AVAILABLE = True
                    except Exception:
                        _NVML_AVAILABLE = False
                    """
                ).strip()
                patched = text.replace("import pynvml", replacement)
                patched = patched.replace(
                    "pynvml.nvmlInit()",
                    "if _NVML_AVAILABLE:\n        pynvml.nvmlInit()",
                    1,
                )
                sysmet.write_text(patched, encoding="utf-8")
                preview = "\n".join(patched.splitlines()[:30])
                log_change(
                    change_log,
                    "edit",
                    sysmet,
                    "Added NVML fallback patch",
                    preview,
                )
    except Exception as e:
        record_error(
            errors_log,
            "3: Best-Effort Construction — NVML patch",
            e,
            "src/codex_ml/callbacks/system_metrics.py",
        )

    # 3c: Add HFTokenizerAdapter if missing
    try:
        hf_file = REPO_ROOT / "src" / "codex_ml" / "interfaces" / "tokenizer.py"
        if hf_file.exists():
            content = hf_file.read_text(encoding="utf-8")
            if "HFTokenizerAdapter" not in content:
                adapter_code = textwrap.dedent(
                    """
                    try:
                        from tokenizers import Tokenizer
                    except Exception:
                        Tokenizer = None

                    class HFTokenizerAdapter:
                        '''HF tokenizer adapter bridging TokenizerAdapter.'''

                        def __init__(self, tokenizer_path: str):
                            if Tokenizer is None:
                                raise RuntimeError("tokenizers package not available")
                            self.tokenizer = Tokenizer.from_file(tokenizer_path)
                            pad = self.tokenizer.token_to_id('<pad>')
                            eos = self.tokenizer.token_to_id('</s>')
                            self._pad = pad if pad is not None else 0
                            self._eos = eos if eos is not None else 1

                        def encode(self, text: str, *, add_special_tokens: bool = True):
                            result = self.tokenizer.encode(text)
                            return result.ids

                        def decode(self, ids, *, skip_special_tokens: bool = True):
                            return self.tokenizer.decode(
                                list(ids), skip_special_tokens=skip_special_tokens
                            )

                        def vocab_size(self) -> int:
                            return int(self.tokenizer.get_vocab_size())

                        def pad_id(self) -> int:
                            return self._pad

                        def eos_id(self) -> int:
                            return self._eos
                    """
                ).strip()
                hf_file.write_text(content.rstrip() + "\n\n" + adapter_code, encoding="utf-8")
                preview = "\n".join(adapter_code.splitlines()[:30])
                log_change(
                    change_log,
                    "append",
                    hf_file,
                    "Added HFTokenizerAdapter implementation",
                    preview,
                )
    except Exception as e:
        record_error(
            errors_log,
            "3: Best-Effort Construction — HFTokenizerAdapter",
            e,
            "src/codex_ml/interfaces/tokenizer.py",
        )

    # 3d: Create default Hydra config
    try:
        cfg_dir = REPO_ROOT / "configs"
        cfg_dir.mkdir(exist_ok=True)
        default_yaml = cfg_dir / "default.yaml"
        if not default_yaml.exists():
            default_yaml.write_text(
                "defaults:\n  - override hydra/job_logging: disabled\n"
                "model_name: 'gpt2'\n"
                "dataset_path: 'data/tiny_corpus.txt'\n"
                "epochs: 1\n"
                "batch_size: 1\n"
                "learning_rate: 5e-5\n"
                "use_lora: false\n"
                "lora_rank: 8\n"
                "lora_alpha: 16\n",
                encoding="utf-8",
            )
            preview = default_yaml.read_text(encoding="utf-8")
            log_change(change_log, "create", default_yaml, "Added Hydra default config", preview)
    except Exception as e:
        record_error(
            errors_log,
            "3: Best-Effort Construction — create default.yaml",
            e,
            "configs/default.yaml",
        )

    # 3e: Append packaging metadata
    try:
        pyproject = REPO_ROOT / "pyproject.toml"
        if pyproject.exists():
            content = pyproject.read_text(encoding="utf-8")
            if "[project]" not in content:
                metadata = (
                    "[project]\n"
                    "name = 'codex_ml'\n"
                    "version = '0.1.0'\n"
                    "description = 'Offline-first ML training framework'\n"
                    "requires-python = '>=3.9'\n"
                    "[project.scripts]\n"
                    "codex-ml = 'codex_ml.main:main'\n"
                    "codex-train = 'codex_ml.cli.hydra_main:hydra_main'\n"
                )
                pyproject.write_text(content.rstrip() + "\n\n" + metadata, encoding="utf-8")
                log_change(
                    change_log,
                    "append",
                    pyproject,
                    "Appended packaging metadata",
                    metadata,
                )
    except Exception as e:
        record_error(
            errors_log,
            "3: Best-Effort Construction — append pyproject",
            e,
            "pyproject.toml",
        )

    # Phase 4: Controlled Pruning
    try:
        deferred = codex_dir / "deferred.md"
        deferred.write_text(
            "# Deferred Items\n"
            "- Reinforcement learning loop: deferred due to scope; requires environment\n"
            "  and reward shaping.\n"
            "- Distributed/multi-GPU training: complex; planned for future release.\n"
            "- HF datasets integration: deferred to maintain offline-only operation.\n",
            encoding="utf-8",
        )
        log_change(
            change_log, "create", deferred, "Documented deferred items", deferred.read_text()
        )
    except Exception as e:
        record_error(errors_log, "4: Controlled Pruning", e, str(deferred))

    # Phase 6: Finalization - update codex-ready task sequence YAML
    try:
        yaml_file = REPO_ROOT / "codex_ready_task_sequence.yaml"
        yaml_content = textwrap.dedent(
            """
            **Codex-ready Task Sequence**

            1. **Preparation**
               - Determine repository root and ensure `.codex` directory exists.
               - Read and clean `README.md` by replacing raw GitHub links with
                 placeholder markers.

            2. **Search & Mapping**
               - Recursively scan repository for Python files containing keywords
                 (token, reward, rl, ppo, agent) and append paths to
                 `.codex/results.md`.
               - Parse cleaned README for context and note any external references.

            3. **Best-Effort Construction**
               - If `src/codex_ml/interfaces` is missing, run
                 `tools/apply_interfaces.py --apply` to generate interfaces and tests.
               - Apply NVML fallback patch to `src/codex_ml/callbacks/system_metrics.py`
                 to support CPU-only systems.
               - Append `HFTokenizerAdapter` implementation to
                 `src/codex_ml/interfaces/tokenizer.py` if absent.
               - Create `configs/default.yaml` with safe training defaults and LoRA
                 parameters.
               - Append packaging metadata and CLI entry points to `pyproject.toml`.

            4. **Controlled Pruning**
               - Identify tasks that cannot be implemented (reinforcement learning
                 loop, multi-GPU training, HF datasets integration) and document
                 reasons in `.codex/deferred.md`.

            5. **Error Capture**
               - Wrap each action in try/except and on error append a record to
                 `.codex/errors.ndjson` and print a formatted question for
                 ChatGPT @codex.

            6. **Finalization**
               - Update `.codex/change_log.md` with all modifications and rationale.
               - Write this task sequence to `codex_ready_task_sequence.yaml` for the
                 next codex execution.
            """
        ).strip()
        yaml_file.write_text(yaml_content, encoding="utf-8")
        log_change(
            change_log, "create", yaml_file, "Generated codex-ready task sequence", yaml_content
        )
    except Exception as e:
        record_error(
            errors_log, "6: Finalization — write YAML", e, "codex_ready_task_sequence.yaml"
        )


if __name__ == "__main__":  # pragma: no cover - script entry point guard
    main()
