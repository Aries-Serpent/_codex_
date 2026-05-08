"""Crawler service integration tests (Phase 24)."""

import pytest

from src.services.crawler import (
    ContentDiffer,
    MultiLocaleSyncManager,
    ZendeskKnowledgeSyncService,
)


@pytest.mark.integration
def test_zendesk_sync_initialization():
    """Test ZendeskKnowledgeSyncService initialization."""
    service = ZendeskKnowledgeSyncService(
        api_token="test_token",
        subdomain="test",
    )
    assert service.subdomain == "test"


@pytest.mark.integration
def test_zendesk_sync_error_handling():
    """Test ZendeskKnowledgeSyncService error handling."""
    service = ZendeskKnowledgeSyncService(
        api_token="invalid_token",
        subdomain="test",
    )

    result = service.sync_articles()
    assert result.failed > 0


@pytest.mark.integration
def test_multi_locale_sync_manager():
    """Test MultiLocaleSyncManager coordinates locale syncs."""
    from src.services.crawler.multi_locale_sync import LocaleConfig

    locales = [
        LocaleConfig("en-US", priority=10),
        LocaleConfig("es-ES", priority=8),
        LocaleConfig("fr-FR", priority=7),
    ]
    manager = MultiLocaleSyncManager(locales=locales)
    assert len(manager.locales) == 3


@pytest.mark.integration
def test_content_differ_detects_changes():
    """Test ContentDiffer detects content changes."""
    differ = ContentDiffer()

    old_content = "Original content"
    new_content = "Modified content"

    diff = differ.diff(old_content, new_content)
    assert diff.has_changes
    assert len(diff.segments) > 0


@pytest.mark.integration
def test_content_differ_no_changes():
    """Test ContentDiffer handles identical content."""
    differ = ContentDiffer()

    content = "Same content"
    diff = differ.diff(content, content)
    assert not diff.has_changes


@pytest.mark.integration
def test_zendesk_sync_rate_limiting():
    """Test ZendeskKnowledgeSyncService rate limiting."""
    service = ZendeskKnowledgeSyncService(
        api_token="test_token",
        subdomain="test",
        rate_limit=10,  # 10 requests per minute
    )
    assert service.rate_limit == 10
