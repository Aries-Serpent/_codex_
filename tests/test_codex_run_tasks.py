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
            return (
                tmp_path / val,
                tmp_path
                / getattr(
                    mod, next(filter(lambda n: hasattr(mod, n), c_candidates), c_candidates[-1])
                ),
            )
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
    attempts = [
        (1, "tests/does_not_exist.py", kwargs.get("out_dir")),
        ("tests/does_not_exist.py", kwargs.get("out_dir")),
        ("tests/does_not_exist.py",),
    ]
    last_exc: Optional[Exception] = None
    for call_args in attempts:
        try:
            call_args = tuple(a for a in call_args if a is not None)
            rc = func(*call_args)
            return rc
        except TypeError as e:
            last_exc = e
            continue
        except Exception:
            return 1
    raise AssertionError(f"run_task signature not recognized; last error: {last_exc!r}")


def test_run_task_writes_files(tmp_path: Path, monkeypatch=None):
    """
    Ensure run_task writes question & commit comment outputs even on failure.
    """
    q_name = "questions.md"
    c_name = "comment.txt"
    q_path = tmp_path / q_name
    c_path = tmp_path / c_name
    q_path.write_text("", encoding="utf-8")
    c_path.write_text("", encoding="utf-8")

    if monkeypatch is not None:
        _set_module_file_attrs(monkeypatch, q_name, c_name)
    else:
        for attr, val in {
            "QUESTION_FILE": q_name,
            "QUESTIONS": q_name,
            "COMMIT_COMMENT_FILE": c_name,
            "COMMIT_COMMENT": c_name,
        }.items():
            try:
                setattr(mod, attr, val)
            except Exception:
                pass

    try:
        rc = _call_run_task_flexibly(out_dir=tmp_path)
    except AssertionError as e:
        pytest.fail(str(e))
        return

    assert rc != 0

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
    q_resolved = q_resolved or q_path
    c_resolved = c_resolved or c_path

    assert q_resolved.exists(), f"expected questions file at {q_resolved}"
    assert c_resolved.exists(), f"expected commit comment file at {c_resolved}"

    q_text = q_resolved.read_text(encoding="utf-8", errors="replace")
    c_text = c_resolved.read_text(encoding="utf-8", errors="replace")

    assert q_text.strip() != ""
    assert c_text.strip() != ""


def test_fetch_https_allows_https(monkeypatch):
    class DummyResponse:
        def __init__(self):
            self._data = b"ok"

        def getcode(self) -> int:
            return 200

        def read(self) -> bytes:
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    called = {}

    def fake_safe_request(url, *, timeout=0, headers=None, method="GET", data=None):
        called["url"] = url
        called["timeout"] = timeout
        called["headers"] = headers
        called["method"] = method
        called["data"] = data
        return 200, {"Content-Type": "text/plain"}, DummyResponse().read()

    monkeypatch.setattr(mod, "safe_request", fake_safe_request)

    status, body = mod.fetch_https("https://example.com/resource")

    assert status == 200
    assert body == b"ok"
    assert called["url"] == "https://example.com/resource"
    assert called["timeout"] == 20.0
    assert called["headers"] is None
    assert called["method"] == "GET"
    assert called["data"] is None


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",  # non-TLS
        "file:///etc/passwd",  # local file access
        "ftp://example.com/resource",
        "",
    ],
)
def test_fetch_https_rejects_non_https(url):
    with pytest.raises(ValueError):
        mod.fetch_https(url)
