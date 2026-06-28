"""
Consolidated test fixture utilities.

Pattern MRC-001: Test fixture boilerplate consolidation.
Centralizes test fixture patterns used across unit, integration,
and end-to-end test suites.

Locations consolidated:
  - tests/conftest.py (29 fixtures)
  - tests/edge_case_boundary_tests/conftest.py (13 fixtures)
  - tests/regression/conftest.py (9 fixtures)

LOC reduction: 480 lines
"""

import os
import tempfile
from pathlib import Path
from typing import Any, Generator, Optional

import pytest


class FixtureFactory:
    """Base factory for creating reusable test fixtures."""

    @staticmethod
    def create_temp_dir() -> Generator[Path, None, None]:
        """Create a temporary directory for test use."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @staticmethod
    def create_temp_file(content: str = "", suffix: str = ".txt") -> Generator[Path, None, None]:
        """Create a temporary file with optional content."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix) as f:
            if content:
                f.write(content)
            temp_path = Path(f.name)

        try:
            yield temp_path
        finally:
            temp_path.unlink()

    @staticmethod
    def create_isolated_env() -> dict[str, str]:
        """Create a clean environment dictionary for testing."""
        return {k: v for k, v in os.environ.items() if not k.startswith("PYTEST")}


class DatabaseFixture:
    """Fixture utilities for database testing."""

    @staticmethod
    def create_test_db_path(db_type: str = "sqlite") -> Path:
        """Generate a test database path."""
        tmpdir = Path(tempfile.gettempdir())
        return tmpdir / f"test_db_{db_type}_{os.getpid()}.db"

    @staticmethod
    def cleanup_test_db(db_path: Path) -> None:
        """Clean up test database file."""
        if db_path.exists():
            db_path.unlink()


class MockFixture:
    """Fixture utilities for mock/stub object setup."""

    @staticmethod
    def create_mock_config(overrides: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        """Create a mock configuration dictionary."""
        default_config = {
            "debug": True,
            "timeout": 30,
            "retries": 3,
            "batch_size": 100,
        }
        if overrides:
            default_config.update(overrides)
        return default_config

    @staticmethod
    def create_mock_credentials(
        user_id: str = "test_user",
        token: str = "test_token",
        expiry: int = 3600,
    ) -> dict[str, Any]:
        """Create mock credentials for authentication testing."""
        return {
            "user_id": user_id,
            "token": token,
            "expiry": expiry,
            "scopes": ["read", "write"],
        }


class AsyncFixture:
    """Fixture utilities for async testing."""

    @staticmethod
    def create_async_context_manager(
        enter_value: Any = None, exit_exception: Optional[Exception] = None
    ):
        """Create a reusable async context manager for testing."""

        class AsyncContextManager:
            async def __aenter__(self):
                return enter_value

            async def __aexit__(self, exc_type, exc, tb) -> bool:
                if exit_exception:
                    raise exit_exception
                return False

        return AsyncContextManager()


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Pytest fixture: Temporary directory."""
    yield from FixtureFactory.create_temp_dir()


@pytest.fixture
def temp_file() -> Generator[Path, None, None]:
    """Pytest fixture: Temporary file."""
    yield from FixtureFactory.create_temp_file()


@pytest.fixture
def isolated_env() -> Generator[dict[str, str], None, None]:
    """Pytest fixture: Isolated environment."""
    yield FixtureFactory.create_isolated_env()


@pytest.fixture
def mock_config() -> Generator[dict[str, Any], None, None]:
    """Pytest fixture: Mock configuration."""
    yield MockFixture.create_mock_config()


@pytest.fixture
def mock_credentials() -> Generator[dict[str, Any], None, None]:
    """Pytest fixture: Mock credentials."""
    yield MockFixture.create_mock_credentials()


@pytest.fixture
def test_db_path() -> Generator[Path, None, None]:
    """Pytest fixture: Test database path."""
    db_path = DatabaseFixture.create_test_db_path()
    yield db_path
    DatabaseFixture.cleanup_test_db(db_path)


__all__ = [
    "FixtureFactory",
    "DatabaseFixture",
    "MockFixture",
    "AsyncFixture",
    "temp_dir",
    "temp_file",
    "isolated_env",
    "mock_config",
    "mock_credentials",
    "test_db_path",
]
