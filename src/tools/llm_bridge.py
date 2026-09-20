"""Bridge utilities for requesting LLM-generated patches."""

from __future__ import annotations

import json
import os
import re
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
PATCH_DIR = REPO_ROOT / ".codex" / "patches"
AUDIT_LOG = REPO_ROOT / ".codex" / "generation_audit.jsonl"
DEFAULT_TIMEOUT = float(os.environ.get("CODEX_LLM_TIMEOUT", "60"))
DEFAULT_MODEL = os.environ.get("CODEX_LLM_MODEL", "")


@dataclass
class BridgeResponse:
    patch: str
    artifact_path: Optional[Path]
    raw_response: Optional[dict[str, Any]]


def _build_prompt(diff: str, errors: str) -> str:
    diff_block = diff.strip() or "<no staged diff>"
    error_block = errors.strip() or "<no errors captured>"
    return textwrap.dedent(f"""
        You are the Codex auto-fix assistant. Review the provided git diff of staged
        changes and the lint/test errors. Respond with a unified diff that fixes the
        issues without introducing unrelated edits. Only emit the diff.

        <staged_diff>
        {diff_block}
        </staged_diff>

        <errors>
        {error_block}
        </errors>
        """).strip()


def _strip_code_fences(text: str) -> str:
    """Return the content of fenced code blocks when present."""

    if "```" not in text:
        return text.strip()

    blocks = re.findall(r"```(?:[^\n`]*)\n(.*?)```", text, flags=re.S)
    if blocks:
        return "\n\n".join(block.strip() for block in blocks if block.strip())
    return text.replace("```", "").strip()


def _normalize_patch(text: str) -> str:
    """Normalise the patch by removing scaffolding and leading noise."""

    cleaned = _strip_code_fences(text)
    if "diff --git" in cleaned:
        cleaned = cleaned[cleaned.index("diff --git") :]
    cleaned = cleaned.strip()
    if not cleaned:
        return ""
    if not cleaned.endswith("\n"):
        cleaned += "\n"
    return cleaned


def _extract_patch(payload: dict[str, Any]) -> Optional[str]:
    if "patch" in payload and isinstance(payload["patch"], str):
        return _normalize_patch(payload["patch"])
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0]
        if isinstance(message, dict):
            content = message.get("message") or message
            if isinstance(content, dict):
                text = content.get("content")
                if isinstance(text, str):
                    return _normalize_patch(text)
        text = message.get("text") if isinstance(message, dict) else None
        if isinstance(text, str):
            return _normalize_patch(text)
    return None


def _log_audit(event: str, **details: Any) -> None:
    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": event,
        **details,
    }
    with AUDIT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _provider_endpoints() -> list[str]:
    candidates: list[str] = []
    for name in (
        "CODEX_LLM_ENDPOINT",
        "CODEX_LLM_ENDPOINT_FALLBACK",
        "CODEX_LLM_PROVIDER_URL",
        "CODEX_LLM_PROVIDER_URL_FALLBACK",
        "OPENAI_BASE_URL",
    ):
        value = os.environ.get(name, "").strip()
        if not value:
            continue
        for part in value.split(","):
            endpoint = part.strip()
            if endpoint:
                candidates.append(endpoint)
    deduped: list[str] = []
    for endpoint in candidates:
        if endpoint not in deduped:
            deduped.append(endpoint)
    return deduped


def _store_patch(patch: str) -> Path:
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    path = PATCH_DIR / f"llm_patch_{ts}.diff"
    resolved = path.resolve(strict=False)
    if not resolved.is_relative_to(REPO_ROOT.resolve()):
        raise ValueError(f"patch write outside repo root: {resolved}")
    path.write_text(patch, encoding="utf-8")
    _log_audit("patch_stored", path=str(path.relative_to(REPO_ROOT)), bytes=len(patch.encode("utf-8")))
    return path


def request_patch(
    diff: str, errors: str, metadata: Optional[dict[str, Any]] = None
) -> Optional[BridgeResponse]:
    endpoints = _provider_endpoints()
    if not endpoints:
        print("[llm-bridge] no LLM endpoint configured; skipping auto-fix request")
        _log_audit("provider_missing", reason="no provider endpoints configured")
        return None

    for index, endpoint in enumerate(endpoints):
        payload = {
            "model": DEFAULT_MODEL or "",
            "messages": [
                {"role": "system", "content": "You produce minimal unified diffs to fix code issues."},
                {"role": "user", "content": _build_prompt(diff, errors)},
            ],
            "metadata": metadata or {},
        }

        data = json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        api_key = os.environ.get("CODEX_LLM_API_KEY")
        if api_key:
            api_key = api_key.strip()
            headers["Authorization"] = (
                api_key if api_key.lower().startswith("bearer ") else "Bearer " + api_key
            )

        req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
                resp_data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            _log_audit(
                "provider_failed",
                provider_index=index,
                provider=endpoint,
                error=type(exc).__name__,
                message=str(exc),
            )
            continue

        patch = _extract_patch(resp_data)
        if not patch:
            _log_audit("provider_response_missing_patch", provider=endpoint)
            print("[llm-bridge] response missing unified diff; ignoring")
            continue

        preview = patch[:2000]
        _log_audit("patch_preview", provider=endpoint, preview=preview)
        try:
            artifact_path = _store_patch(patch)
        except ValueError as exc:
            _log_audit("patch_rejected", provider=endpoint, reason=str(exc))
            print(f"[llm-bridge] rejected patch outside repo root: {exc}")
            return None
        return BridgeResponse(patch=patch, artifact_path=artifact_path, raw_response=resp_data)

    _log_audit("provider_all_failed", endpoints=endpoints)
    print("[llm-bridge] all configured providers failed; skipping auto-fix request")
    return None


__all__ = ["request_patch", "BridgeResponse"]
