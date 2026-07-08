"""Tests for Multi-Locale and Content Diffing enhancements.

PS-06 Enhancement: Tests for Knowledge Crawler enhancements:
- Multi-locale parallel synchronization
- Content diffing for micro-updates
"""

from datetime import datetime, timedelta, timezone

from services.crawler.content_diff import (
    ChangeType,
    ContentDiffer,
    ContentDiffResult,
    DiffSegment,
    IncrementalSyncDecider,
)
from services.crawler.multi_locale_sync import (
    LocaleConfig,
    MultiLocaleSyncManager,
)


class TestLocaleConfig:
    """Test LocaleConfig."""

    def test_create_locale_config(self):
        """Test creating locale configuration."""
        config = LocaleConfig(
            locale_code="en-us",
            priority=10,
            enabled=True,
            sync_interval_hours=24,
        )
        assert config.locale_code == "en-us", "locale_code is not valid"
        assert config.priority == 10, "priority is not valid"
        assert config.enabled is True, "enabled is not valid"

    def test_needs_sync_never_synced(self):
        """Test needs_sync when never synced."""
        config = LocaleConfig("en-us")
        assert config.needs_sync() is True, "Condition must be true"

    def test_needs_sync_recently_synced(self):
        """Test needs_sync when recently synced."""
        config = LocaleConfig(
            locale_code="en-us",
            sync_interval_hours=24,
            last_sync=datetime.now(timezone.utc),
        )
        assert config.needs_sync() is False, "Condition must be true"

    def test_needs_sync_due(self):
        """Test needs_sync when sync is due."""
        config = LocaleConfig(
            locale_code="en-us",
            sync_interval_hours=24,
            last_sync=datetime.now(timezone.utc) - timedelta(hours=25),
        )
        assert config.needs_sync() is True, "Condition must be true"

    def test_disabled_locale(self):
        """Test disabled locale never needs sync."""
        config = LocaleConfig(
            locale_code="en-us",
            enabled=False,
        )
        assert config.needs_sync() is False, "Condition must be true"


class TestMultiLocaleSyncManager:
    """Test MultiLocaleSyncManager."""

    def test_create_manager(self):
        """Test creating sync manager."""
        manager = MultiLocaleSyncManager(max_workers=4)
        assert manager.max_workers == 4, "max_workers is not valid"
        assert len(manager.locales) > 0, "Collection must not be empty"

    def test_add_locale(self):
        """Test adding a locale."""
        manager = MultiLocaleSyncManager()
        initial_count = len(manager.locales)

        manager.add_locale(LocaleConfig("zh-tw", priority=6))

        assert len(manager.locales) == initial_count + 1, "Collection must not be empty"
        assert "zh-tw" in manager.locales, "Condition must be true"

    def test_remove_locale(self):
        """Test removing a locale."""
        manager = MultiLocaleSyncManager()
        manager.add_locale(LocaleConfig("test-locale"))

        result = manager.remove_locale("test-locale")

        assert result is True, "Result must not be empty"
        assert "test-locale" not in manager.locales, "Condition must be true"

    def test_get_sync_schedule(self):
        """Test getting sync schedule."""
        manager = MultiLocaleSyncManager()
        schedule = manager.get_sync_schedule()

        assert len(schedule) > 0, "Schedule must not be empty"
        # Should be sorted by priority (descending)
        priorities = [s["priority"] for s in schedule]
        assert priorities == sorted(priorities, reverse=True)

    def test_sync_locale(self):
        """Test syncing a single locale."""
        manager = MultiLocaleSyncManager()

        def mock_sync_func(locale_code: str) -> tuple[int, int]:
            return (10, 0)  # 10 synced, 0 failed

        result = manager.sync_locale("en-us", mock_sync_func)

        assert result.success is True, "Result must not be empty"
        assert result.articles_synced == 10, "Result must not be empty"
        assert result.locale_code == "en-us", "Result must not be empty"

    def test_sync_locale_failure(self):
        """Test handling sync failure."""
        manager = MultiLocaleSyncManager()

        def failing_sync_func(locale_code: str) -> tuple[int, int]:
            raise RuntimeError("Network error")

        result = manager.sync_locale("en-us", failing_sync_func)

        assert result.success is False, "Result must not be empty"
        assert "Network error" in result.error_message, "Result must not be empty"

    def test_sync_all_locales(self):
        """Test syncing all locales."""
        manager = MultiLocaleSyncManager(max_workers=2)
        # Use only 2 locales for faster test
        manager.locales = {
            "en-us": LocaleConfig("en-us", priority=10),
            "ja": LocaleConfig("ja", priority=8),
        }

        def mock_sync_func(locale_code: str) -> tuple[int, int]:
            return (5, 1)  # 5 synced, 1 failed

        result = manager.sync_all_locales(mock_sync_func, only_due=False)

        assert result.total_locales == 2, "Result must not be empty"
        assert result.successful_locales == 2, "Result must not be empty"
        assert result.total_articles_synced == 10, "Result must not be empty"


class TestContentDiffer:
    """Test ContentDiffer."""

    def test_identical_content(self):
        """Test diffing identical content."""
        differ = ContentDiffer()

        result = differ.diff("Hello World", "Hello World")

        assert result.change_type == ChangeType.NO_CHANGE, "Result must not be empty"
        assert result.change_ratio == 0.0, "Result must not be empty"
        assert result.similarity_ratio == 1.0, "Result must not be empty"

    def test_minor_change(self):
        """Test detecting minor change."""
        differ = ContentDiffer()

        old = "Hello World! This is a test document with some content."
        new = "Hello World! This is a test document with some content!"  # Changed . to !

        result = differ.diff(old, new)

        assert result.change_type == ChangeType.MINOR, "Result must not be empty"
        assert result.change_ratio < 0.05, "Result must not be empty"

    def test_major_change(self):
        """Test detecting major change."""
        differ = ContentDiffer()

        old = "This is the old content."
        new = "Completely different new content that has nothing in common."

        result = differ.diff(old, new)

        assert result.change_type in (ChangeType.MAJOR, ChangeType.COMPLETE)
        assert result.change_ratio > 0.5, "change_ratio must be greater than zero"

    def test_html_stripping(self):
        """Test HTML tag stripping."""
        differ = ContentDiffer(strip_html=True)

        old = "<p>Hello <strong>World</strong></p>"
        new = "<div>Hello <em>World</em></div>"

        result = differ.diff(old, new)

        # After stripping HTML, content should be similar
        assert result.similarity_ratio > 0.8, "similarity_ratio must be greater than zero"

    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        differ = ContentDiffer(ignore_whitespace=True)

        old = "Hello    World"
        new = "Hello World"

        result = differ.diff(old, new)

        assert result.change_type == ChangeType.NO_CHANGE, "Result must not be empty"

    def test_should_resync(self):
        """Test should_resync convenience method."""
        differ = ContentDiffer(min_change_ratio=0.01)

        # No change
        should_sync, _change_type, _ratio = differ.should_resync("Same content", "Same content")
        assert should_sync is False, "should_sync is not valid"

        # Significant change
        should_sync, _change_type, _ratio = differ.should_resync(
            "Old content", "Completely different"
        )
        assert should_sync is True, "should_sync is not valid"


class TestIncrementalSyncDecider:
    """Test IncrementalSyncDecider."""

    def test_skip_no_change(self):
        """Test skip decision for no change."""
        decider = IncrementalSyncDecider()

        decision = decider.decide(
            "Same content",
            "Same content",
        )

        assert decision["action"] == "skip", "Condition must be true"

    def test_micro_update(self):
        """Test micro-update decision.

        Uses non-repetitive natural text to avoid SequenceMatcher heuristic
        fragmentation on periodic patterns (Q003 — deep research confirmed).
        Only a single punctuation character differs: '.' → '!'
        """
        decider = IncrementalSyncDecider(micro_update_threshold=0.10)

        # Natural, non-repetitive text — single trailing punctuation change
        old = (
            "The quick brown fox jumped over the lazy dog near the river bank. "
            "A software engineer reviewed the pull request and left detailed comments. "
            "The deployment pipeline finished successfully after three retries. "
            "Unit tests confirmed that all edge cases were handled correctly. "
            "Documentation was updated to reflect the new API surface."
        )
        new = (
            "The quick brown fox jumped over the lazy dog near the river bank. "
            "A software engineer reviewed the pull request and left detailed comments. "
            "The deployment pipeline finished successfully after three retries. "
            "Unit tests confirmed that all edge cases were handled correctly. "
            "Documentation was updated to reflect the new API surface!"  # '.' → '!'
        )

        decision = decider.decide(old, new)

        assert decision["action"] in ("skip", "micro_update")

    def test_full_update_major_change(self):
        """Test full update for major change."""
        decider = IncrementalSyncDecider(full_update_threshold=0.50)

        decision = decider.decide(
            "Original content here",
            "Completely rewritten new content",
        )

        assert decision["action"] == "full_update", "Condition must be true"


class TestDiffSegment:
    """Test DiffSegment."""

    def test_create_segment(self):
        """Test creating diff segment."""
        segment = DiffSegment(
            change_type="insert",
            old_content="",
            new_content="New line added",
            line_start=5,
            line_end=5,
        )

        assert segment.change_type == "insert", "change_type is not valid"
        assert segment.line_start == 5, "line_start is not valid"

    def test_to_dict(self):
        """Test segment serialization."""
        segment = DiffSegment(
            change_type="delete",
            old_content="Removed line",
            new_content="",
            line_start=10,
            line_end=10,
        )

        d = segment.to_dict()

        assert "change_type" in d, "Condition must be true"
        assert "old_content_preview" in d, "Content must not be empty"


class TestContentDiffResult:
    """Test ContentDiffResult."""

    def test_should_sync_no_change(self):
        """Test should_sync for no change."""
        result = ContentDiffResult(
            change_type=ChangeType.NO_CHANGE,
            change_ratio=0.0,
            similarity_ratio=1.0,
            old_hash="abc",
            new_hash="abc",
        )

        assert result.should_sync() is False, "Result must not be empty"

    def test_should_sync_with_change(self):
        """Test should_sync with change."""
        result = ContentDiffResult(
            change_type=ChangeType.MODERATE,
            change_ratio=0.15,
            similarity_ratio=0.85,
            old_hash="abc",
            new_hash="def",
        )

        assert result.should_sync() is True, "Result must not be empty"

    def test_to_dict(self):
        """Test result serialization."""
        result = ContentDiffResult(
            change_type=ChangeType.MINOR,
            change_ratio=0.03,
            similarity_ratio=0.97,
            old_hash="abc123",
            new_hash="def456",
        )

        d = result.to_dict()

        assert d["change_type"] == "minor", "Condition must be true"
        assert "similarity_ratio" in d, "Condition must be true"
