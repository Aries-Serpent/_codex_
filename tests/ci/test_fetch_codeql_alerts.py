from scripts.ci import fetch_codeql_alerts


def test_all_tool_filter_requests_every_code_scanning_alert(monkeypatch):
    requested_urls = []

    def fake_api_get(url, token, min_remaining, page_sleep):
        requested_urls.append(url)
        return [], {}

    monkeypatch.setattr(fetch_codeql_alerts, "_api_get", fake_api_get)

    alerts = fetch_codeql_alerts.fetch_alerts(
        state="open",
        tool_name="all",
        per_page=100,
        max_pages=10,
        page_sleep=0,
        min_remaining=20,
        token="test-token",
    )

    assert alerts == []
    assert len(requested_urls) == 1
    assert "tool_name=" not in requested_urls[0]
    assert "state=open" in requested_urls[0]


def test_named_tool_filter_remains_supported(monkeypatch):
    requested_urls = []

    def fake_api_get(url, token, min_remaining, page_sleep):
        requested_urls.append(url)
        return [], {}

    monkeypatch.setattr(fetch_codeql_alerts, "_api_get", fake_api_get)

    fetch_codeql_alerts.fetch_alerts(
        state="open",
        tool_name="CodeQL",
        per_page=100,
        max_pages=10,
        page_sleep=0,
        min_remaining=20,
        token="test-token",
    )

    assert "tool_name=CodeQL" in requested_urls[0]
