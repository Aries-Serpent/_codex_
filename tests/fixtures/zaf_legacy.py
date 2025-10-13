"""Fixture data for Zendesk App Framework (ZAF) legacy bundles."""

from __future__ import annotations

from collections.abc import Mapping

Payload = str | bytes

SAMPLE_ZAF_BUNDLE: Mapping[str, Payload] = {
    "app.js": "console.log('hello from legacy ZAF');\n",
    "assets/images/logo.png": bytes(range(256)),
    "assets/images/icons/logo.png": bytes(reversed(range(256))),
    "styles/main.css": "body { font-family: system-ui; }\n",
    "templates/ticket_sidebar.hbs": '<div class="ticket">{{ticket.id}}</div>\n',
    "translations/en.json": '{"app": {"name": "Legacy"}}\n',
    "translations/subdir/duplicate.txt": "nested\n",
    "subdir/duplicate.txt": "root\n",
}

__all__ = ["Payload", "SAMPLE_ZAF_BUNDLE"]
