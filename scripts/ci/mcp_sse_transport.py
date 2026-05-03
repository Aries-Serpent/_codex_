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
import os
import sys
import urllib.request
from typing import Any, Optional

logger = logging.getLogger(__name__)


def http_post_json_streaming(
    url: str,
    payload: dict[str, Any],
    auth_token: Optional[str] = None,
    timeout: int = 30,
) -> dict[str, Any]:
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
    headers: dict[str, str] = {
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
    chunks: list[dict[str, Any]] = []
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
            "Examples:\n"
            "  python scripts/ci/mcp_sse_transport.py \\\n"
            "      --url https://staging.mcp.example.com/stream/ \\\n"
            "      --method tools/repository_access \\\n"
            "      --params '{\"repo\": \"owner/repo\"}'\n\n"
            "  # Retry on failure, YAML output:\n"
            "  python scripts/ci/mcp_sse_transport.py --url ... --method ... --retry 3 --output-format yaml\n\n"
            "  # Batch requests from a JSON file:\n"
            "  python scripts/ci/mcp_sse_transport.py --batch-file requests.json --url ...\n\n"
            "  # Validate auth/schema only (no request sent):\n"
            "  python scripts/ci/mcp_sse_transport.py --validate-only --url ... --method ...\n"
        ),
    )
    p.add_argument(
        "--url", required=True, help="MCP endpoint URL (http:// or https://)"
    )
    p.add_argument(
        "--method",
        default=None,
        help="JSON-RPC method name, e.g. 'tools/repository_access' (required unless --batch-file)",
    )
    p.add_argument(
        "--params",
        default="{}",
        help="JSON-encoded params dict (default: '{}')",
    )
    p.add_argument(
        "--token",
        default=None,
        help="Bearer auth token (optional; falls back to MCP_AUTH_TOKEN env var)",
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
    # GAP-021 enhancements
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable DEBUG-level logging for detailed request/response tracing",
    )
    p.add_argument(
        "--output-format",
        choices=["json", "plain", "yaml"],
        default="json",
        help="Output format for the response (default: json)",
    )
    p.add_argument(
        "--retry",
        type=int,
        default=0,
        metavar="N",
        help="Retry up to N times on transient failures (default: 0 = no retry)",
    )
    p.add_argument(
        "--batch-file",
        default=None,
        metavar="FILE",
        help=(
            "Path to a JSON file containing a list of requests "
            '[{"method": "...", "params": {...}}, ...]. '
            "Sends each request sequentially. --method/--params are ignored when this is used."
        ),
    )
    p.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate URL, token and params without sending a request (dry-run connectivity check)",
    )
    p.add_argument(
        "--header",
        action="append",
        dest="headers",
        metavar="KEY=VALUE",
        default=[],
        help="Inject extra HTTP header (may be specified multiple times, e.g. --header X-Trace-Id=abc)",
    )
    return p


def _format_output(result: dict, fmt: str) -> str:
    """Format a result dict according to the requested output format."""
    if fmt == "json":
        return json.dumps(result, indent=2)
    if fmt == "yaml":
        # Best-effort YAML without requiring pyyaml
        try:
            import yaml  # type: ignore[import]
            return yaml.dump(result, default_flow_style=False)
        except ImportError:
            # Fallback: indented JSON as YAML-compatible superset
            return json.dumps(result, indent=2)
    # plain
    lines = []
    for k, v in result.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)


def _send_single(
    url: str,
    payload: dict,
    auth_token: Optional[str],
    timeout: int,
    extra_headers: dict,
    retry: int,
) -> dict:
    """Send one JSON-RPC request, retrying on OSError up to ``retry`` times."""
    attempt = 0
    while True:
        try:
            # Inject extra headers by temporarily monkey-patching urllib if needed.
            # For simplicity we rebuild the request each attempt.
            import urllib.request as _ureq
            data = json.dumps(payload).encode("utf-8")
            headers: dict = {
                "Content-Type": "application/json",
                "Accept": "text/event-stream, application/json",
            }
            if auth_token:
                headers["Authorization"] = f"Bearer {auth_token}"
            headers.update(extra_headers)
            req = _ureq.Request(url, data=data, headers=headers, method="POST")
            with _ureq.urlopen(req, timeout=timeout) as resp:  # nosec B310
                content_type = resp.headers.get("Content-Type", "")
                raw = resp.read()
            if "text/event-stream" not in content_type:
                return json.loads(raw)
            # SSE streaming
            chunks = []
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
                        logger.debug("Skipping invalid JSON SSE data fragment: %r", fragment)
            if not chunks:
                return {"error": {"message": "SSE stream contained no parseable data frames"}}
            final = chunks[-1]
            final["_streaming_chunks"] = len(chunks)
            return final
        except OSError as exc:
            if attempt < retry:
                attempt += 1
                import time
                delay = 2 ** attempt
                logging.getLogger(__name__).warning(
                    "Request failed (%s); retrying in %ds (attempt %d/%d)...",
                    exc, delay, attempt, retry,
                )
                time.sleep(delay)
            else:
                raise


def main(argv: Optional[list] = None) -> int:
    """CLI entry point. Returns exit code (0 = success, 1 = error)."""
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(level=log_level, format="%(levelname)s %(name)s: %(message)s")

    # Resolve auth token (CLI flag > env var)
    auth_token = args.token or os.environ.get("MCP_AUTH_TOKEN")

    # Parse extra headers
    extra_headers: dict = {}
    for header_spec in args.headers:
        if "=" not in header_spec:
            print(f"ERROR: --header must be KEY=VALUE, got: {header_spec!r}", file=sys.stderr)
            return 1
        k, _, v = header_spec.partition("=")
        extra_headers[k.strip()] = v.strip()

    if args.validate_only:
        issues = []
        if not args.url.startswith(("http://", "https://")):
            issues.append(f"URL must start with http:// or https://, got: {args.url!r}")
        if not auth_token:
            issues.append("No auth token provided (--token or MCP_AUTH_TOKEN env var)")
        # In non-batch mode, a method is required for a valid request
        if not args.batch_file and not args.method:
            issues.append("No --method provided (required for single requests; use --batch-file for batch mode)")
        # Validate --params is valid JSON if provided
        if args.params:
            try:
                json.loads(args.params)
            except json.JSONDecodeError as exc:
                issues.append(f"--params is not valid JSON: {exc}")
        if issues:
            for issue in issues:
                print(f"⚠  {issue}")
            return 1
        print("✅ Validation passed — URL, token, method and params look correct")
        return 0

    # Batch-file mode
    if args.batch_file:
        try:
            with open(args.batch_file) as f:
                batch = json.loads(f.read())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: --batch-file: {exc}", file=sys.stderr)
            return 1
        if not isinstance(batch, list):
            print("ERROR: --batch-file must contain a JSON array of request objects", file=sys.stderr)
            return 1
        results = []
        exit_code = 0
        for i, req_obj in enumerate(batch):
            method = req_obj.get("method", "")
            params = req_obj.get("params", {})
            req_id = req_obj.get("id", f"batch-{i+1}")
            payload = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
            try:
                result = _send_single(args.url, payload, auth_token, args.timeout, extra_headers, args.retry)
            except (OSError, ValueError) as exc:
                result = {"error": {"message": str(exc)}}
                exit_code = 1
            results.append(result)
            if "error" in result:
                exit_code = 1
        print(_format_output({"results": results}, args.output_format))
        return exit_code

    # Single-request mode
    if not args.method:
        print("ERROR: --method is required (or use --batch-file)", file=sys.stderr)
        return 1

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
        result = _send_single(args.url, payload, auth_token, args.timeout, extra_headers, args.retry)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR: HTTP request failed: {exc}", file=sys.stderr)
        return 1

    print(_format_output(result, args.output_format))
    if "error" in result:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
