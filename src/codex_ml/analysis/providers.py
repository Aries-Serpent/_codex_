# src/codex_ml/analysis/providers.py
from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

try:  # pragma: no cover - optional dependency
    import requests
except Exception:  # pragma: no cover - requests missing or broken
    requests = None  # type: ignore[assignment]


class SearchProvider:
    def search(self, query: str) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError


class InternalRepoSearch(SearchProvider):
    def __init__(self, root: Path) -> None:
        self.root = root

    def search(self, query: str) -> Dict[str, Any]:
        import glob
        import re

        results: List[Dict[str, Any]] = []
        pattern = re.compile(re.escape(query), re.I)
        for path in glob.glob(str(self.root / "**/*.py"), recursive=True):
            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as handle:
                    for lineno, line in enumerate(handle, 1):
                        if pattern.search(line):
                            results.append(
                                {
                                    "provider": "internal",
                                    "where": path,
                                    "line": lineno,
                                    "snippet": line.strip(),
                                }
                            )
            except Exception:
                continue
        return {"status": "ok", "query": query, "results": results}


def _coerce_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    value = value.strip().lower()
    if value in {"1", "true", "yes", "on"}:
        return True
    if value in {"0", "false", "no", "off"}:
        return False
    try:
        return bool(int(value))
    except (TypeError, ValueError):
        return default


def _normalise_timeout(value: Optional[str], default: float) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


class ExternalWebSearch(SearchProvider):
    """Configurable external search provider with offline-safe defaults."""

    def __init__(
        self,
        endpoint: str | None = None,
        *,
        timeout: float | None = None,
        enabled: bool | None = None,
        http_get: Optional[Callable[..., Any]] = None,
    ) -> None:
        env_enabled = os.getenv("CODEX_ANALYSIS_SEARCH_ENABLED")
        self.enabled = enabled if enabled is not None else _coerce_bool(env_enabled, False)
        self.endpoint = (endpoint or os.getenv("CODEX_ANALYSIS_SEARCH_ENDPOINT", "")).strip()
        env_timeout = os.getenv("CODEX_ANALYSIS_SEARCH_TIMEOUT")
        base_timeout = timeout if timeout is not None else _normalise_timeout(env_timeout, 5.0)
        self.timeout = base_timeout if base_timeout > 0 else 5.0
        self._http_get = http_get

    def search(self, query: str) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "provider": "external_web",
            "query": query,
            "results": [],
        }

        if not self.enabled:
            result["status"] = "disabled"
            return result

        if not self.endpoint:
            result["status"] = "unavailable"
            result["reason"] = "no-endpoint"
            return result

        http_get = self._http_get
        if http_get is None and requests is not None:
            http_get = requests.get  # type: ignore[assignment]

        if http_get is None:
            result["status"] = "unavailable"
            result["reason"] = "requests-missing"
            return result

        try:
            response = http_get(self.endpoint, params={"q": query}, timeout=self.timeout)
        except Exception as exc:  # pragma: no cover - network failures via mocks
            result["status"] = "error"
            result["error"] = str(exc)
            return result

        try:
            status_code = getattr(response, "status_code", None)
            response.raise_for_status()
        except Exception as exc:
            result["status"] = "error"
            if status_code is not None:
                result["status_code"] = status_code
            result["error"] = str(exc)
            return result

        content_type = ""
        headers = getattr(response, "headers", {})
        if isinstance(headers, dict):
            content_type = headers.get("Content-Type", "")
        else:  # pragma: no cover - defensive for custom headers objects
            content_type = str(
                getattr(headers, "get", lambda *_args, **_kwargs: "")("Content-Type", "")
            )

        payload: Any
        if "application/json" in content_type:
            try:
                payload = response.json()
            except Exception as exc:
                result["status"] = "error"
                result["error"] = f"invalid-json: {exc}"
                return result
        else:
            payload = {"raw": getattr(response, "text", "")}

        result["results"] = self._normalise_payload(payload)
        result["status"] = "ok"
        return result

    def _normalise_payload(self, payload: Any) -> List[Dict[str, Any]]:
        def extract(obj: Any) -> Iterable[Dict[str, Any]]:
            if isinstance(obj, dict):
                yield obj
                for key in ("RelatedTopics", "results", "items", "data", "Topics"):
                    value = obj.get(key)
                    if isinstance(value, list):
                        for child in value:
                            yield from extract(child)
            elif isinstance(obj, list):
                for child in obj:
                    yield from extract(child)

        normalised: List[Dict[str, Any]] = []
        for item in extract(payload):
            title = item.get("Text") or item.get("title") or item.get("heading") or ""
            url = item.get("FirstURL") or item.get("url") or item.get("link") or ""
            snippet = item.get("Text") or item.get("snippet") or item.get("description") or ""
            entry = {
                "title": str(title) if title is not None else "",
                "url": str(url) if url is not None else "",
                "snippet": str(snippet) if snippet is not None else "",
            }
            if any(entry.values()):
                entry.setdefault("provider", "external_web")
                normalised.append(entry)
        return normalised
