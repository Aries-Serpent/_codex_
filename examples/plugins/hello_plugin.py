from __future__ import annotations

from codex_ml.plugins import BasePlugin


class HelloPlugin(BasePlugin):
    def name(self) -> str:
        return "hello"

    def version(self) -> str:
        return "0.1.0"

    def activate(self, app_ctx=None) -> None:
        # No-op activation; example plugin only.
        return
