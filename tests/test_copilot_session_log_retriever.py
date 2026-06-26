"""Tests for Copilot Session Log Retriever."""

import json
import sqlite3

# Add scripts to path
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from copilot_session_log_retriever import (
    CopilotSessionRetriever,
    ExpectedFile,
    SessionLogEntry,
    SessionSummary,
)


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    yield Path(db_path)

    # Cleanup
    Path(db_path).unlink(missing_ok=True)


@pytest.fixture
def temp_repo():
    """Create a temporary repository directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)

        # Create some test files
        (repo_path / "src").mkdir()
        (repo_path / "src" / "module.py").touch()
        (repo_path / "README.md").touch()

        yield repo_path


@pytest.fixture
def sample_session_data():
    """Sample session data for testing."""
    return [
        {
            "session_id": "test-session-1",
            "timestamp": "2026-02-05T08:00:00Z",
            "role": "user",
            "message": "Create a new module",
            "metadata": {},
        },
        {
            "session_id": "test-session-1",
            "timestamp": "2026-02-05T08:01:00Z",
            "role": "assistant",
            "message": 'Created file: "src/new_module.py" with the implementation',
            "metadata": {},
        },
        {
            "session_id": "test-session-1",
            "timestamp": "2026-02-05T08:02:00Z",
            "role": "assistant",
            "message": 'Updated file: "README.md" with documentation',
            "metadata": {},
        },
        {
            "session_id": "test-session-2",
            "timestamp": "2026-02-05T09:00:00Z",
            "role": "user",
            "message": "Fix the tests",
            "metadata": {},
        },
        {
            "session_id": "test-session-2",
            "timestamp": "2026-02-05T09:01:00Z",
            "role": "assistant",
            "message": 'Modified file: "tests/test_module.py"',
            "metadata": {},
        },
    ]


def populate_test_db(db_path: Path, data: list):
    """Populate test database with sample data."""
    conn = sqlite3.connect(str(db_path))

    # Create schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT,
            metadata TEXT
        )
    """)

    # Insert data
    for entry in data:
        conn.execute(
            "INSERT INTO logs (session_id, timestamp, role, message, metadata) VALUES (?, ?, ?, ?, ?)",
            (
                entry["session_id"],
                entry["timestamp"],
                entry["role"],
                entry["message"],
                json.dumps(entry["metadata"]),
            ),
        )

    conn.commit()
    conn.close()


class TestCopilotSessionRetriever:
    """Test suite for CopilotSessionRetriever."""

    def test_initialization(self, temp_db, temp_repo):
        """Test retriever initialization."""
        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        assert retriever.db_path == temp_db, "db_path is not valid"
        assert retriever.repo_root == temp_repo, "repo_root is not valid"

    def test_create_schema(self, temp_db):
        """Test database schema creation."""
        retriever = CopilotSessionRetriever(db_path=str(temp_db))
        retriever._create_schema()

        # Verify schema exists
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
        result = cursor.fetchone()
        conn.close()

        assert result is not None, "result must be initialized"
        assert result[0] == "logs", "Result must not be empty"

    def test_list_sessions(self, temp_db, sample_session_data):
        """Test listing sessions."""
        populate_test_db(temp_db, sample_session_data)

        retriever = CopilotSessionRetriever(db_path=str(temp_db))
        sessions = retriever.list_sessions(limit=10)

        assert len(sessions) == 2, "Sessions must not be empty"
        assert sessions[0]["session_id"] == "test-session-2", "Condition must be true"
        assert sessions[1]["session_id"] == "test-session-1", "Condition must be true"

    def test_get_last_n_sessions(self, temp_db, sample_session_data):
        """Test getting last N sessions."""
        populate_test_db(temp_db, sample_session_data)

        retriever = CopilotSessionRetriever(db_path=str(temp_db))
        session_ids = retriever.get_last_n_sessions(n=1)

        assert len(session_ids) == 1, "Session_ids must not be empty"
        assert session_ids[0] == "test-session-2", "Condition must be true"

    def test_get_session_logs(self, temp_db, sample_session_data):
        """Test retrieving session logs."""
        populate_test_db(temp_db, sample_session_data)

        retriever = CopilotSessionRetriever(db_path=str(temp_db))
        logs = retriever.get_session_logs("test-session-1")

        assert len(logs) == 3, "Logs must not be empty"
        assert all(isinstance(log, SessionLogEntry) for log in logs)
        assert logs[0].role == "user", "role is not valid"
        assert logs[1].role == "assistant", "role is not valid"

    def test_extract_expected_files(self, temp_db, sample_session_data):
        """Test extracting expected files from logs."""
        populate_test_db(temp_db, sample_session_data)

        retriever = CopilotSessionRetriever(db_path=str(temp_db))
        logs = retriever.get_session_logs("test-session-1")
        expected_files = retriever.extract_expected_files(logs)

        assert len(expected_files) > 0, "Expected_files must not be empty"

        # Check that we extracted the files mentioned
        paths = [f.path for f in expected_files]
        assert "src/new_module.py" in paths, "Condition must be true"
        assert "README.md" in paths, "Condition must be true"

    def test_verify_files_existing(self, temp_db, temp_repo):
        """Test verifying existing files."""
        # Create a file in temp repo
        test_file = temp_repo / "test_file.py"
        test_file.touch()

        expected = ExpectedFile(
            path="test_file.py",
            operation="create",
            session_id="test",
            timestamp="2026-02-05T08:00:00Z",
        )

        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        verified = retriever.verify_files([expected])

        assert len(verified) == 1, "Verified must not be empty"
        assert verified[0].exists is True, "exists is not valid"
        assert verified[0].verified is True, "verified is not valid"

    def test_verify_files_missing(self, temp_db, temp_repo):
        """Test verifying missing files."""
        expected = ExpectedFile(
            path="nonexistent_file.py",
            operation="create",
            session_id="test",
            timestamp="2026-02-05T08:00:00Z",
        )

        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        verified = retriever.verify_files([expected])

        assert len(verified) == 1, "Verified must not be empty"
        assert verified[0].exists is False, "exists is not valid"
        assert verified[0].verified is False, "verified is not valid"

    def test_analyze_session(self, temp_db, temp_repo, sample_session_data):
        """Test analyzing a complete session."""
        populate_test_db(temp_db, sample_session_data)

        # Create one of the expected files
        (temp_repo / "README.md").write_text("# Test")

        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        summary = retriever.analyze_session("test-session-1")

        assert isinstance(summary, SessionSummary)
        assert summary.session_id == "test-session-1", "session_id is not valid"
        assert summary.message_count == 3, "Count must be greater than zero"
        assert len(summary.expected_files) > 0, "Collection must not be empty"
        # At least README.md should be verified
        assert summary.verified_files >= 1, "verified_files must be greater than zero"

    def test_process_sessions_in_batches(self, temp_db, temp_repo, sample_session_data):
        """Test processing multiple sessions in batches."""
        populate_test_db(temp_db, sample_session_data)

        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        session_ids = ["test-session-1", "test-session-2"]
        summaries = retriever.process_sessions_in_batches(session_ids, batch_size=2)

        assert len(summaries) == 2, "Summaries must not be empty"
        assert all(isinstance(s, SessionSummary) for s in summaries)

    def test_generate_report(self, temp_db, temp_repo, sample_session_data):
        """Test report generation."""
        populate_test_db(temp_db, sample_session_data)

        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        summary = retriever.analyze_session("test-session-1")
        report = retriever.generate_report([summary])

        assert "Copilot Session Log Verification Report" in report, "Condition must be true"
        assert "test-session-1" in report, "Condition must be true"
        assert "Overall Statistics" in report, "Condition must be true"

    def test_file_operation_patterns(self):
        """Test file operation pattern matching."""
        test_cases = [
            ('Created file: "src/module.py"', "src/module.py", "create"),
            ('Modified file: "tests/test.py"', "tests/test.py", "edit"),
            ('Updated file: "README.md"', "README.md", "edit"),
            ('create path="src/new.py"', "src/new.py", "create"),
            ('edit path="src/old.py"', "src/old.py", "edit"),
        ]

        retriever = CopilotSessionRetriever()

        for message, expected_path, expected_op in test_cases:
            log = SessionLogEntry(
                session_id="test",
                timestamp="2026-02-05T08:00:00Z",
                role="assistant",
                message=message,
            )

            files = retriever.extract_expected_files([log])

            # Should extract at least one file
            assert len(files) >= 1, f"Failed to extract file from: {message}"

            # Check if expected path is in results
            paths = [f.path for f in files]
            assert expected_path in paths, f"Expected {expected_path} in {paths}"

    def test_empty_database(self, temp_db, temp_repo):
        """Test handling of empty database."""
        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        # Schema should be auto-created
        retriever._create_schema()

        sessions = retriever.list_sessions()
        assert sessions == [], "sessions is not valid"

        session_ids = retriever.get_last_n_sessions(n=10)
        assert session_ids == [], "session_ids is not valid"

    def test_missing_session(self, temp_db, temp_repo):
        """Test handling of missing session."""
        retriever = CopilotSessionRetriever(db_path=str(temp_db), repo_root=str(temp_repo))

        # Schema should be auto-created
        retriever._create_schema()

        summary = retriever.analyze_session("nonexistent-session")

        assert summary.message_count == 0, "Count must be greater than zero"
        assert len(summary.expected_files) == 0, "Collection must not be empty"
        assert "No logs found" in summary.notes, "Condition must be true"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
