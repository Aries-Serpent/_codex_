from src.codex.logging.session_logger import fetch_messages, get_session_id, log_event


def generate_reply(prompt: str) -> str:
    return f"echo:{prompt}"


def test_readme_snippet(tmp_path, monkeypatch):
    db = tmp_path / "session_logs.db"
    monkeypatch.setenv("CODEX_LOG_DB_PATH", str(db))
    session_id = get_session_id()

    def handle_user_message(prompt: str) -> str:
        log_event(session_id, "user", prompt)
        reply = generate_reply(prompt)
        log_event(session_id, "assistant", reply)
        return reply

    out = handle_user_message("hi")
    assert out == "echo:hi"
    rows = fetch_messages(session_id, db_path=db)
    messages = {r["message"] for r in rows}
    assert "hi" in messages and "echo:hi" in messages
