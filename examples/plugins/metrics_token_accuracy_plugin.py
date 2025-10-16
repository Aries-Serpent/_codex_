from __future__ import annotations

from codex_ml.plugins.base import MetricsPlugin


class TokenAccuracyPlugin(MetricsPlugin):
    def name(self) -> str:
        return "token-accuracy-plugin"

    def version(self) -> str:
        return "0.1.0"

    # Optional: could register callable in future; for now, presence signals capability
    def activate(self, app_ctx=None) -> None:
        return
