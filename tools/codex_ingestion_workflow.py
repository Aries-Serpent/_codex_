#!/usr/bin/env python3
# tools/codex_ingestion_workflow.py
# Purpose: Implement ingestion signature/behavior, docs, tests, and script cleanup with logs + research-question errors.

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional

REPO_ROOT = Path.cwd()
CODEX_DIR = REPO_ROOT / ".codex"
CHANGE_LOG = CODEX_DIR / "change_log.md"
ERRORS_LOG = CODEX_DIR / "errors.ndjson"
RESULTS_MD = CODEX_DIR / "results.md"

DO_NOT_ACTIVATE_GITHUB_ACTIONS = True

# ---------- utilities ----------


def ts() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def ensure_codex_dirs():
    CODEX_DIR.mkdir(parents=True, exist_ok=True)
    if not CHANGE_LOG.exists():
        CHANGE_LOG.write_text(f"# Change Log ({ts()})\n\n", encoding="utf-8")
    if not ERRORS_LOG.exists():
        ERRORS_LOG.write_text("", encoding="utf-8")
    if not RESULTS_MD.exists():
        RESULTS_MD.write_text(f"# Results ({ts()})\n\n", encoding="utf-8")


def log_change(
    path: Path, action: str, rationale: str, before: Optional[str], after: Optional[str]
) -> None:
    diff = ""
    if before is not None and after is not None:
        ud = difflib.unified_diff(
            before.splitlines(True),
            after.splitlines(True),
            fromfile=f"a/{path.as_posix()}",
            tofile=f"b/{path.as_posix()}",
            n=3,
        )
        diff = "".join(ud)
    entry = textwrap.dedent(f"""\
    ## {ts()} — {action}: `{path.as_posix()}`
    **Rationale:** {rationale}
    {"```diff\n" + diff + "\n```" if diff else ""}
    """)
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")


def log_error(step: str, message: str, context: str, files: list[str] | None = None):
    record = {
        "timestamp": ts(),
        "step": step,
        "error": message,
        "context": context,
        "files": files or [],
        "question_for_chatgpt_5": textwrap.dedent(f"""\
            Question for ChatGPT-5:
            While performing [{step}], encountered the following error:
            {message}
            Context: {context}
            What are the possible causes, and how can this be resolved while preserving intended functionality?
        """).strip(),
    }
    with ERRORS_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print("\n" + record["question_for_chatgpt_5"] + "\n", file=sys.stderr)


def run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return p.returncode, out, err


def git_root() -> Path:
    rc, out, err = run(["git", "rev-parse", "--show-toplevel"])
    if rc != 0:
        return REPO_ROOT
    return Path(out.strip())


def git_is_clean() -> bool:
    rc, out, err = run(["git", "status", "--porcelain"])
    return rc == 0 and out.strip() == ""


def read(path: Path) -> Optional[str]:
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, content: str, dry_run: bool, rationale: str):
    before = read(path)
    if before == content:
        return
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    log_change(
        path, "create" if before is None else "update", rationale, before, content
    )


def patch_file_transform(path: Path, transform, dry_run: bool, rationale: str):
    before = read(path)
    after = transform(before)
    if after is None or after == before:
        return
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(after, encoding="utf-8")
    log_change(
        path, "update" if before is not None else "create", rationale, before, after
    )


# ---------- Phase 1: prep ----------


def phase1_prep():
    ensure_codex_dirs()
    root = git_root()
    clean = git_is_clean()
    with RESULTS_MD.open("a", encoding="utf-8") as f:
        f.write(
            f"- Repo root: `{root}`\n- Git clean: `{clean}`\n- DO_NOT_ACTIVATE_GITHUB_ACTIONS: `{DO_NOT_ACTIVATE_GITHUB_ACTIONS}`\n\n"
        )
    inventory = []
    for rel in ("src", "tests", "scripts", "documentation", ".github", ".codex"):
        p = REPO_ROOT / rel
        if p.exists():
            for file in p.rglob("*"):
                if file.is_file():
                    inventory.append(file.as_posix())
    with RESULTS_MD.open("a", encoding="utf-8") as f:
        f.write("## Inventory (paths)\n")
        for it in sorted(inventory):
            f.write(f"- {it}\n")
        f.write("\n")


# ---------- Phase 3: construction ----------

INGESTION_HEADER = '''"""
Ingestion utilities.

Extended to support:
- encoding: str = "utf-8"
- chunk_size: Optional[int] | None = None

Behavior:
- If chunk_size is None: return the full text (Path.read_text(encoding)).
- If chunk_size > 0: yield successive string chunks of at most chunk_size characters.

Raises:
- FileNotFoundError when the provided path resolves to a directory.
"""
from __future__ import annotations
from pathlib import Path
from typing import Iterator, Optional, Union
'''

INGEST_FUNCTION = '''
def ingest(path: Union[str, Path], encoding: str = "utf-8", chunk_size: Optional[int] | None = None):
    """
    Read or stream text content from a file.

    Parameters
    ----------
    path : Union[str, Path]
        File path to read.
    encoding : str, default "utf-8"
        Text encoding used to decode bytes.
    chunk_size : Optional[int]
        If None, return the entire file as a single string.
        If an int > 0, yield successive chunks of at most `chunk_size` characters.

    Returns
    -------
    str or Iterator[str]
        A full string when chunk_size is None; otherwise, an iterator of string chunks.

    Raises
    ------
    FileNotFoundError
        If `path` points to a directory.
    """
    p = Path(path)
    if p.is_dir():
        raise FileNotFoundError(f"Path is a directory: {p}")
    if chunk_size is None:
        return p.read_text(encoding=encoding)
    if not isinstance(chunk_size, int) or chunk_size <= 0:
        raise ValueError("chunk_size must be a positive integer when provided")
    with p.open("r", encoding=encoding) as fh:
        while True:
            chunk = fh.read(chunk_size)
            if not chunk:
                break
            yield chunk
'''

INGESTOR_SHIM = '''
# Provide a minimal Ingestor if one does not already exist.
try:
    Ingestor  # type: ignore[name-defined]
except NameError:  # pragma: no cover
    class Ingestor:
        """Shim Ingestor exposing ingest(...) as a staticmethod."""
        @staticmethod
        def ingest(path: Union[str, Path], encoding: str = "utf-8", chunk_size: Optional[int] | None = None):
            return ingest(path, encoding=encoding, chunk_size=chunk_size)
'''


def patch_ingestion_module(dry_run: bool):
    target = REPO_ROOT / "src" / "ingestion" / "__init__.py"

    def transform(before: Optional[str]) -> str:
        base = before or ""
        add_header = (
            INGESTION_HEADER
            if "from pathlib import Path" not in base
            and "Ingestion utilities." not in base
            else ""
        )
        new = base
        new = re.sub(
            r"(?ms)^def\s+ingest\s*\(.*?^\)",
            lambda m: "# ORIGINAL_INGEST_REMOVED\n"
            + "\n".join("# " + ln for ln in m.group(0).splitlines())
            + "\n",
            new,
        )
        if not new.strip():
            new = add_header + "\n"
        elif add_header:
            new = add_header + "\n" + new
        new = (
            new.rstrip()
            + "\n"
            + INGEST_FUNCTION.strip()
            + "\n"
            + INGESTOR_SHIM.strip()
            + "\n"
        )
        return new

    rationale = "Add/normalize ingest(path, encoding, chunk_size) semantics and directory-guard; provide Ingestor shim if absent."
    patch_file_transform(target, transform, dry_run, rationale)


def patch_ingestion_readme(dry_run: bool):
    target = REPO_ROOT / "src" / "ingestion" / "README.md"
    before = read(target) or ""
    section = textwrap.dedent("""\
        # Ingestion

        ## Parameters

        - `path: Union[str, Path]` — file to read.
        - `encoding: str = \"utf-8\"` — decoding for text mode.
        - `chunk_size: Optional[int] = None` — if `None`, returns full string; if an int > 0, yields chunks.

        ## Examples

        ```python
        from ingestion import ingest

        # Full read
        text = ingest("data/sample.txt")  # utf-8, full string

        # Chunked streaming
        for chunk in ingest("data/sample.txt", encoding="utf-8", chunk_size=4096):
            process(chunk)
        ```
    """)
    after = section if not before.strip() else before.rstrip() + "\n\n" + section
    write_if_changed(
        target,
        after,
        dry_run,
        "Document encoding and chunk_size behavior with examples.",
    )


def ensure_tests(dry_run: bool):
    target = REPO_ROOT / "tests" / "test_ingestion_io.py"
    content = textwrap.dedent("""\
        import io
        from pathlib import Path
        import pytest

        # Try both module-level ingest and optional Ingestor shim
        def _call_ingest(p, **kw):
            import importlib
            ingestion = importlib.import_module("ingestion")
            if hasattr(ingestion, "Ingestor") and hasattr(ingestion.Ingestor, "ingest"):
                return ingestion.Ingestor.ingest(p, **kw)
            return ingestion.ingest(p, **kw)

        def test_full_read_default_encoding(tmp_path: Path):
            p = tmp_path / "hello.txt"
            text = "héllø—世界"
            p.write_text(text, encoding="utf-8")
            out = _call_ingest(p)
            assert isinstance(out, str)
            assert out == text

        def test_chunked_read_and_reassembly(tmp_path: Path):
            p = tmp_path / "lorem.txt"
            text = "abc" * 5000  # 15k chars
            p.write_text(text, encoding="utf-8")
            chunks = list(_call_ingest(p, chunk_size=4096))
            assert all(isinstance(c, str) for c in chunks)
            assert "".join(chunks) == text
            assert all(len(c) <= 4096 for c in chunks)

        def test_accepts_str_path(tmp_path: Path):
            p = tmp_path / "s.txt"
            p.write_text("OK", encoding="utf-8")
            out = _call_ingest(str(p))
            assert out == "OK"

        def test_directory_raises_filenotfound(tmp_path: Path):
            d = tmp_path / "a_dir"
            d.mkdir()
            with pytest.raises(FileNotFoundError):
                _call_ingest(d)
    """)
    write_if_changed(
        target,
        content,
        dry_run,
        "Add tests for encoding, chunk_size, str(path), and directory error behavior.",
    )


def patch_deep_research_script(dry_run: bool):
    target = REPO_ROOT / "scripts" / "deep_research_task_process.py"
    if not target.exists():
        with RESULTS_MD.open("a", encoding="utf-8") as f:
            f.write(
                "- Note: scripts/deep_research_task_process.py not found; skipped.\n"
            )
        return

    def transform(before: Optional[str]) -> Optional[str]:
        if before is None:
            return None
        new = before
        removed = []
        for name in ("_task_ingestion_scaffold", "_task_ingestion_test"):
            if re.search(rf"def\s+{name}\s*\(", new):
                removed.append(name)
                new = re.sub(
                    rf"(?ms)^def\s+{name}\s*\(.*?^\)",
                    lambda m: "# PRUNED_PLACEHOLDER\n"
                    + "\n".join("# " + ln for ln in m.group(0).splitlines())
                    + "\n",
                    new,
                )
        if "from ingestion import ingest" not in new:
            new = "from ingestion import ingest\n" + new
        if removed:
            helper = textwrap.dedent('''

                # Replaced placeholder ingestion tasks with actual calls:
                def run_ingestion_example(path: str):
                    """
                    Example bridge to real ingestion implementation.
                    """
                    data = ingest(path)
                    return data
            ''')
            new = new.rstrip() + "\n" + helper
        return new

    patch_file_transform(
        target,
        transform,
        dry_run,
        "Remove/replace placeholder ingestion task helpers; reference real ingestion implementation.",
    )


def record_prune(
    item: str,
    purpose: str,
    alternatives: list[str],
    failures: list[str],
    evidence: str,
    decision: str,
):
    entry = textwrap.dedent(f"""\
    ### Pruning
    - Item: {item}
    - Purpose: {purpose}
    - Alternatives evaluated: {alternatives}
    - Failure modes: {failures}
    - Evidence: {evidence}
    - Decision: {decision}
    """)
    with CHANGE_LOG.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")


# ---------- Phase 6: finalization ----------


def finalize():
    with RESULTS_MD.open("a", encoding="utf-8") as f:
        f.write("\n## Final Notes\n- **DO NOT ACTIVATE ANY GitHub Actions files.**\n")
    unresolved = False
    try:
        if ERRORS_LOG.exists() and ERRORS_LOG.read_text(encoding="utf-8").strip():
            unresolved = True
    except Exception:
        unresolved = True
    return 1 if unresolved else 0


# ---------- main ----------


def main():
    parser = argparse.ArgumentParser(
        description="Apply ingestion updates with logs and tests."
    )
    g = parser.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true", help="Apply changes to disk.")
    g.add_argument(
        "--dry-run",
        action="store_true",
        help="Analyze and propose changes without writing.",
    )
    args = parser.parse_args()
    dry = not args.write

    try:
        phase1_prep()
        patch_ingestion_module(dry)
        patch_ingestion_readme(dry)
        ensure_tests(dry)
        patch_deep_research_script(dry)
    except Exception as e:
        log_error("PHASE_EXECUTION", str(e), "Unhandled exception in workflow.", [])
        return 1

    return finalize()


if __name__ == "__main__":
    sys.exit(main())
