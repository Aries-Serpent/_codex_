from tools import codex_run_tasks as mod


def test_run_task_writes_files(tmp_path, monkeypatch):
    q = tmp_path / "questions.md"
    c = tmp_path / "comment.txt"
    q.write_text("", encoding="utf-8")
    c.write_text("", encoding="utf-8")
    monkeypatch.setattr(mod, "QUESTIONS", q)
    monkeypatch.setattr(mod, "COMMIT_COMMENT", c)
    # run a failing pytest command
    rc = mod.run_task("tests/does_not_exist.py")
    assert rc != 0
    assert q.read_text()
    assert c.read_text()
