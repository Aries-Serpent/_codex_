"""Bridge utilities for requesting LLM-generated patches."""

from __future__ import annotations

import json
import os
import textwrap
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

PATCH_DIR = Path(".codex/patches")
DEFAULT_TIMEOUT = float(os.environ.get("CODEX_LLM_TIMEOUT", "60"))
DEFAULT_MODEL = os.environ.get("CODEX_LLM_MODEL", "")


@dataclass
class BridgeResponse:
    patch: str
    artifact_path: Optional[Path]
    raw_response: Optional[Dict[str, Any]]


def _build_prompt(diff: str, errors: str) -> str:
    diff_block = diff.strip() or "<no staged diff>"
    error_block = errors.strip() or "<no errors captured>"
    return textwrap.dedent(
        f"""
        You are the Codex auto-fix assistant. Review the provided git diff of staged
        changes and the lint/test errors. Respond with a unified diff that fixes the
        issues without introducing unrelated edits. Only emit the diff.

        <staged_diff>
        {diff_block}
        </staged_diff>

        <errors>
        {error_block}
        </errors>
        """
    ).strip()


def _extract_patch(payload: Dict[str, Any]) -> Optional[str]:
    if "patch" in payload and isinstance(payload["patch"], str):
        return payload["patch"]
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0]
        if isinstance(message, dict):
            content = message.get("message") or message
            if isinstance(content, dict):
                text = content.get("content")
                if isinstance(text, str):
                    return text
        text = message.get("text") if isinstance(message, dict) else None
        if isinstance(text, str):
            return text
    return None


def _store_patch(patch: str) -> Path:
    PATCH_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    path = PATCH_DIR / f"llm_patch_{ts}.diff"
    path.write_text(patch, encoding="utf-8")
    return path


def request_patch(
    diff: str, errors: str, metadata: Optional[Dict[str, Any]] = None
) -> Optional[BridgeResponse]:
    endpoint = os.environ.get("CODEX_LLM_ENDPOINT")
    if not endpoint:
        print("[llm-bridge] CODEX_LLM_ENDPOINT unset; skipping auto-fix request")
        return None

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
        headers["Authorization"] = f"Bearer {api_key}"

    req = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=DEFAULT_TIMEOUT) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        print(f"[llm-bridge] request failed: {exc}")
        return None

    patch = _extract_patch(resp_data)
    if not patch:
        print("[llm-bridge] response missing unified diff; ignoring")
        return None

    artifact_path = _store_patch(patch)
    return BridgeResponse(patch=patch, artifact_path=artifact_path, raw_response=resp_data)


__all__ = ["request_patch", "BridgeResponse"]
