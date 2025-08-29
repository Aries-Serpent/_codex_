from tools import codex_run_tasks as mod


def test_run_task_writes_files(tmp_path):
    rc = mod.run_task(1, "tests/does_not_exist.py", tmp_path)
    assert rc != 0
    q = tmp_path / mod.QUESTION_FILE
    c = tmp_path / mod.COMMIT_COMMENT_FILE
    assert q.read_text()
    assert c.read_text()
