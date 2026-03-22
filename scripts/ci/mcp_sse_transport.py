"""MCP SSE Transport — standalone HTTP/SSE POST helper.

This module extracts ``_http_post_json_streaming`` from
``.github/copilot-cascade/mcp_server.py`` into a testable, importable
script with a CLI entry-point for manual endpoint probing.

Usage (CLI)
-----------
::

    python scripts/ci/mcp_sse_transport.py \\
        --url https://staging.mcp.example.com/stream/ \\
        --method tools/repository_access \\
        --params '{"repo": "owner/repo"}' \\
        [--token $CODEX_MASTER_KEY] \\
        [--timeout 30]

The script prints the final JSON result to stdout and exits with code 0 on
success, 1 on HTTP / parse error.

Design notes
------------
* Zero third-party dependencies — only stdlib (``json``, ``urllib``, ``logging``).
* ``http_post_json_streaming()`` is a plain function so it can be imported and
  unit-tested without instantiating ``MCPIntegration``.
* ``mcp_server.MCPIntegration._http_post_json_streaming`` delegates to this
  function so behaviour stays in sync (single source of truth).
"""

from __future__ import annotations

import json
import logging
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def http_post_json_streaming(
    url: str,
    payload: Dict[str, Any],
    auth_token: Optional[str] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """POST *payload* as JSON and read the response as SSE or plain JSON.

    If the server responds with ``Content-Type: text/event-stream``, each
    ``data: <json>`` line is parsed and accumulated.  The *last* data frame
    that contains a ``result`` or ``error`` key is returned as the final
    body, with an additional ``_streaming_chunks`` counter.

    If the response is plain JSON (non-SSE), the body is decoded normally —
    providing transparent fallback for non-streaming MCP servers.

    Parameters
    ----------
    url:
        HTTP/HTTPS endpoint — must start with ``http://`` or ``https://``.
    payload:
        JSON-serialisable request body (JSON-RPC 2.0 object).
    auth_token:
        Optional bearer token for the ``Authorization`` header.
    timeout:
        Request timeout in seconds.

    Returns
    -------
    dict
        Final decoded JSON result, plus ``_streaming_chunks`` count when
        SSE streaming was used.

    Raises
    ------
    ValueError
        If *url* does not start with ``http://`` or ``https://``.
    """
    if not url.startswith(("http://", "https://")):
        raise ValueError(
            f"http_post_json_streaming: URL must start with "
            f"http:// or https://, got: {url!r}"
        )

    data = json.dumps(payload).encode("utf-8")
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream, application/json",
    }
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec B310
        content_type = resp.headers.get("Content-Type", "")
        raw = resp.read()

    if "text/event-stream" not in content_type:
        # Non-streaming server — decode as plain JSON (fallback path).
        return json.loads(raw)

    # Parse SSE stream: collect all `data:` frames, return the final one.
    chunks: List[Dict[str, Any]] = []
    for line in raw.decode("utf-8").splitlines():
        line = line.strip()
        if line.startswith("data:"):
            fragment = line.removeprefix("data:").strip()
            if fragment in ("", "[DONE]"):
                continue
            try:
                frame = json.loads(fragment)
                if isinstance(frame, dict):
                    chunks.append(frame)
            except json.JSONDecodeError:
                logger.debug(
                    "MCP SSE: skipping non-JSON fragment: %r", fragment
                )

    if not chunks:
        return {
            "error": {
                "message": "SSE stream contained no parseable data frames"
            }
        }

    # The last frame with result/error wins; merge chunk count for observability.
    final = chunks[-1]
    final["_streaming_chunks"] = len(chunks)
    return final


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

def _build_arg_parser():
    import argparse

    p = argparse.ArgumentParser(
        description="POST a JSON-RPC 2.0 request and print the SSE/JSON response.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Example:\n"
            "  python scripts/ci/mcp_sse_transport.py \\\n"
            "      --url https://staging.mcp.example.com/stream/ \\\n"
            "      --method tools/repository_access \\\n"
            "      --params '{\"repo\": \"owner/repo\"}'"
        ),
    )
    p.add_argument(
        "--url", required=True, help="MCP endpoint URL (http:// or https://)"
    )
    p.add_argument(
        "--method",
        required=True,
        help="JSON-RPC method name, e.g. 'tools/repository_access'",
    )
    p.add_argument(
        "--params",
        default="{}",
        help="JSON-encoded params dict (default: '{}')",
    )
    p.add_argument(
        "--token",
        default=None,
        help="Bearer auth token (optional)",
    )
    p.add_argument(
        "--timeout",
        type=int,
        default=30,
        help="Request timeout in seconds (default: 30)",
    )
    p.add_argument(
        "--id",
        dest="request_id",
        default="cli-1",
        help="JSON-RPC request id (default: 'cli-1')",
    )
    return p


def main(argv: Optional[list] = None) -> int:
    """CLI entry point. Returns exit code (0 = success, 1 = error)."""
    logging.basicConfig(
        level=logging.WARNING,
        format="%(levelname)s %(name)s: %(message)s",
    )
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    try:
        params = json.loads(args.params)
    except json.JSONDecodeError as exc:
        print(f"ERROR: --params is not valid JSON: {exc}", file=sys.stderr)
        return 1

    payload = {
        "jsonrpc": "2.0",
        "id": args.request_id,
        "method": args.method,
        "params": params,
    }

    try:
        result = http_post_json_streaming(
            url=args.url,
            payload=payload,
            auth_token=args.token,
            timeout=args.timeout,
        )
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: HTTP request failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
