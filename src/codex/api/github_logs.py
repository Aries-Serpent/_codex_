"""Compatibility shim for `codex.api.github_logs`."""

from __future__ import annotations

import asyncio


class GitHubLogsAPI:
    """Minimal compatibility GitHub Actions log client."""

    def __init__(self, token=None, **kwargs):
        if token is None or token == "":
            raise ValueError("token is required")
        self.token = token
        self._kwargs = kwargs

    def get_logs(self, *, run_id=None, repo=None, **kwargs):
        if repo is None or repo == "":
            raise ValueError("repo is required")
        if run_id is None:
            raise TypeError("run_id is required")
        if run_id < 0:
            raise ValueError("run_id must be non-negative")
        return ""

    async def fetch_logs(self, *, repo=None, run_id=None, **kwargs):
        if repo is None or repo == "":
            raise ValueError("repo is required")
        if run_id is None:
            raise TypeError("run_id is required")
        if run_id < 0:
            raise ValueError("run_id must be non-negative")
        await asyncio.sleep(0)
        return ""


__all__ = ["GitHubLogsAPI"]
