"""HTTP client wrapper for the Internal Tools API."""

from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Iterable, Optional

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from .config import ClientConfig
from .models import (
    GitCreatePullRequestResponse,
    KnowledgeSearchResponse,
    RepoHygieneResponse,
    TestsRunResponse,
)

logger = logging.getLogger(__name__)


class CodexBridgeClient:
    """Thin convenience wrapper around the ITA endpoints with retry semantics."""

    def __init__(self, config: ClientConfig) -> None:
        self._config = config
        self._client = httpx.Client(timeout=config.request_timeout)

    @property
    def base_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self._config.api_key,
        }

    def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        url = f"{self._config.ita_url}{path}"
        headers = {**self.base_headers, "X-Request-Id": uuid.uuid4().hex}
        logger.debug("Calling %s %s", method.upper(), url)
        response = self._client.request(method, url, json=json_body, params=params, headers=headers)
        response.raise_for_status()
        return response

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    )
    def kb_search(self, query: str, top_k: int = 5) -> KnowledgeSearchResponse:
        payload = {"query": query, "top_k": top_k}
        response = self._request("POST", "/kb/search", json_body=payload)
        return KnowledgeSearchResponse.model_validate(response.json())

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    )
    def repo_hygiene(
        self, diff: str, checks: Optional[Iterable[str]] = None
    ) -> RepoHygieneResponse:
        payload: Dict[str, Any] = {"diff": diff}
        if checks:
            payload["checks"] = list(checks)
        response = self._request("POST", "/repo/hygiene", json_body=payload)
        return RepoHygieneResponse.model_validate(response.json())

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    )
    def tests_run(self, targets: Iterable[str], timeout_s: int = 300) -> TestsRunResponse:
        payload = {"targets": list(targets), "timeout_s": timeout_s}
        response = self._request("POST", "/tests/run", json_body=payload)
        return TestsRunResponse.model_validate(response.json())

    @retry(
        reraise=True,
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=0.5, min=0.5, max=4),
    )
    def git_create_pr(
        self,
        repo: str,
        title: str,
        body: str,
        base: str,
        head: str,
        *,
        dry_run: bool = True,
        confirm: bool = False,
        labels: Optional[Iterable[str]] = None,
    ) -> GitCreatePullRequestResponse:
        payload: Dict[str, Any] = {
            "repo": repo,
            "title": title,
            "body": body,
            "base": base,
            "head": head,
        }
        if labels:
            payload["labels"] = list(labels)
        params = {"dry_run": dry_run, "confirm": confirm}
        response = self._request("POST", "/git/create-pr", json_body=payload, params=params)
        return GitCreatePullRequestResponse.model_validate(response.json())

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "CodexBridgeClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
        self.close()


__all__ = ["CodexBridgeClient"]
