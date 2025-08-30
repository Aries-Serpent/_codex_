from __future__ import annotations

import inspect
from pathlib import Path
from typing import Optional

import pytest

from tools import codex_run_tasks as mod


def _set_module_file_attrs(monkeypatch, q_name: str, c_name: str) -> None:
    """
    Try to set a variety of possible attribute names on the module so the
    test works with different historical constant names.
    """
    question_attrs = ("QUESTION_FILE", "QUESTIONS", "QUESTION", "QUESTIONS_FILE")
    commit_attrs = ("COMMIT_COMMENT_FILE", "COMMIT_COMMENT", "COMMIT", "COMMIT_FILE")

    for a in question_attrs:
        monkeypatch.setattr(mod, a, q_name, raising=False)
    for a in commit_attrs:
        monkeypatch.setattr(mod, a, c_name, raising=False)


def _resolve_paths_from_module(tmp_path: Path) -> tuple[Path, Path]:
    """
    Inspect the module for common names and return (questions_path, commit_path).
    If none found, fall back to default file names created in the test directory.
    """
    q_candidates = ("QUESTION_FILE", "QUESTIONS", "QUESTION", "QUESTIONS_FILE")
    c_candidates = ("COMMIT_COMMENT_FILE", "COMMIT_COMMENT", "COMMIT", "COMMIT_FILE")

    for name in q_candidates:
        if hasattr(mod, name):
            val = getattr(mod, name)
            # if the module constant is a Path already, use it as-is; otherwise
            # treat it as a filename relative to tmp_path
            return (tmp_path / val, tmp_path / getattr(mod, next(filter(lambda n: hasattr(mod, n), c_candidates), c_candidates[-1])))
    # fallback names
    return (tmp_path / "questions.md", tmp_path / "comment.txt")


def _call_run_task_flexibly(*args, **kwargs) -> int:
    """
    Attempt to call mod.run_task with a few common signatures to remain
    compatible with different versions:
      - run_task(task_id, task_path, out_dir)
      - run_task(task_path, out_dir)
      - run_task(task_path)
    Returns the integer return code. Raises AssertionError on unexpected failures.
    """
    func = mod.run_task
    # Try a sequence of common invocations
    attempts = [
        (1, "tests/does_not_exist.py", kwargs.get("out_dir")),
        ("tests/does_not_exist.py", kwargs.get("out_dir")),
        ("tests/does_not_exist.py",),
    ]
    last_exc: Optional[Exception] = None
    for call_args in attempts:
        try:
            # filter out None values (e.g., out_dir may be None for some attempts)
            call_args = tuple(a for a in call_args if a is not None)
            rc = func(*call_args)
            return rc
        except TypeError as e:
            last_exc = e
            continue
        except Exception as e:
            # Non-TypeError means the invocation ran but failed (expected for a missing test file).
            # Propagate the return code if available, otherwise wrap
            # If the function raises, we treat it as a failing run and return non-zero.
            return 1
    raise AssertionError(f"run_task signature not recognized; last error: {last_exc!r}")


def test_run_task_writes_files(tmp_path: Path, monkeypatch=None):
    """
    Ensure run_task writes question & commit comment outputs even on failure.

    This test is intentionally flexible:
      - It supports older/newer constant names on the target module.
      - It tolerates multiple run_task signatures by trying them in order.
    """
    # Prepare local files that will be used for output
    q_name = "questions.md"
    c_name = "comment.txt"
    q_path = tmp_path / q_name
    c_path = tmp_path / c_name
    q_path.write_text("", encoding="utf-8")
    c_path.write_text("", encoding="utf-8")

    # If pytest injected monkeypatch, use it to set module constants; otherwise,
    # attempt to set attributes directly (best-effort).
    if monkeypatch is not None:
        _set_module_file_attrs(monkeypatch, q_name, c_name)
    else:
        # Best-effort: set attributes without fixture (may be overwritten elsewhere)
        for attr, val in {
            "QUESTION_FILE": q_name,
            "QUESTIONS": q_name,
            "COMMIT_COMMENT_FILE": c_name,
            "COMMIT_COMMENT": c_name,
        }.items():
            try:
                setattr(mod, attr, val)
            except Exception:
                # ignore if attribute cannot be set
                pass

    # Attempt to call run_task using flexible calling logic
    try:
        rc = _call_run_task_flexibly(out_dir=tmp_path)
    except AssertionError as e:
        pytest.fail(str(e))
        return

    # The invocation should indicate failure when targeting a non-existent test path
    assert rc != 0

    # Resolve the output paths (prefer module attributes if present)
    q_resolved = None
    c_resolved = None
    for name in ("QUESTION_FILE", "QUESTIONS", "QUESTION", "QUESTIONS_FILE"):
        if hasattr(mod, name):
            q_resolved = tmp_path / getattr(mod, name)
            break
    for name in ("COMMIT_COMMENT_FILE", "COMMIT_COMMENT", "COMMIT", "COMMIT_FILE"):
        if hasattr(mod, name):
            c_resolved = tmp_path / getattr(mod, name)
            break
    # fallback
    q_resolved = q_resolved or q_path
    c_resolved = c_resolved or c_path

    # Ensure files were written and contain some content
    assert q_resolved.exists(), f"expected questions file at {q_resolved}"
    assert c_resolved.exists(), f"expected commit comment file at {c_resolved}"

    q_text = q_resolved.read_text(encoding="utf-8", errors="replace")
    c_text = c_resolved.read_text(encoding="utf-8", errors="replace")

    assert q_text.strip() != "", "questions file should not be empty after run_task"
    assert c_text.strip() != "", "commit comment file should not be empty after run_task"
    