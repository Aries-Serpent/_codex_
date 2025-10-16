#!/usr/bin/env python3
"""
Tiny GitHub API wrapper (installation token or PAT).

Features:
  - Methods: GET/POST/PATCH/DELETE
  - Query params via repeated --param key=value
  - JSON body via --data '{"k":"v"}' or --data-file file.json
  - --print-curl emits a redacted curl command (no network)
  - Clean stdout (JSON) / stderr (diagnostics) separation
  - Pagination via --paginate (follows RFC5988 Link rel="next")
  - Local cache via --cache-dir, --use-cache-only, --refresh-cache
  - Optional JSON envelope via --json-envelope

Auth:
  - Reads token from GH_TOKEN or GITHUB_TOKEN
  - Header scheme defaults to "token"; override with GITHUB_AUTH_SCHEME=Bearer if needed
  - API base defaults to https://api.github.com (override with GITHUB_API)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from codex_ml.logging.structured import capture_exceptions, init_logger
from codex_ml.utils.jsonio import print_error_json, print_json

DEFAULT_API = os.environ.get("GITHUB_API", "https://api.github.com")
DEFAULT_SCHEME = os.environ.get("GITHUB_AUTH_SCHEME", "token")
DEFAULT_CACHE_DIR = os.environ.get("GH_API_CACHE_DIR", "")


def _stdout_write(text: str) -> None:
    sys.stdout.write(text if text.endswith("\n") else text + "\n")


def _read_token(env=os.environ) -> str:
    tok = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if not tok:
        raise SystemExit("[gh_api] missing GH_TOKEN/GITHUB_TOKEN")
    return tok.strip()


def _parse_params(kvs: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for kv in kvs:
        if "=" not in kv:
            raise SystemExit(f"[gh_api] invalid --param '{kv}', expected key=value")
        key, value = kv.split("=", 1)
        params[key] = value
    return params


def _compose_url(api_base: str, path: str, params: dict[str, str]) -> str:
    path = path.strip()
    if path.startswith("/"):
        path = path[1:]
    url = f"{api_base.rstrip('/')}/{path}"
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    return url


def _load_body(data: str | None, data_file: str | None) -> bytes | None:
    if data and data_file:
        raise SystemExit("[gh_api] use only one of --data or --data-file")
    if data_file:
        with open(data_file, "rb") as handle:
            return handle.read()
    if data:
        return data.encode("utf-8")
    return None


def _redact(value: str) -> str:
    return "***REDACTED***" if value else value


def _emit_curl(method: str, url: str, token: str, scheme: str, body: bytes | None) -> None:
    parts: list[str] = [
        "curl",
        "-sS",
        "-X",
        method,
        "-H",
        "'Accept: application/vnd.github+json'",
        "-H",
        f"'Authorization: {scheme} {_redact(token)}'",
        "-H",
        "'X-GitHub-Api-Version: 2022-11-28'",
    ]
    if body is not None:
        try:
            decoded = body.decode("utf-8")
        except UnicodeDecodeError:
            decoded = None
        else:
            try:
                json.loads(decoded)
            except json.JSONDecodeError:
                pass
            else:
                parts.extend(["-H", "'Content-Type: application/json'", "--data", f"'{decoded}'"])
                decoded = None
        if decoded is not None:
            parts.extend(["--data-binary", "'<binary>'"])
    parts.append(f"'{url}'")
    _stdout_write(" ".join(parts))


def _request(
    method: str,
    url: str,
    token: str,
    scheme: str,
    body: bytes | None,
) -> tuple[int, str, dict[str, str]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"{scheme} {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url=url, data=body, method=method, headers=headers)  # noqa: S310
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310
            return resp.getcode(), resp.read().decode("utf-8"), dict(resp.headers)
    except urllib.error.HTTPError as err:
        sys.stderr.write(f"[gh_api] HTTP {err.code} {err.reason}\n")
        try:
            err_body = err.read().decode("utf-8")
            if err_body:
                sys.stderr.write(err_body + "\n")
        except Exception as exc:  # pragma: no cover - defensive read guard
            sys.stderr.write(f"[gh_api] failed to read error body: {exc}\n")
        return err.code, "", {}


_LINK_NEXT_RE = re.compile(r"<([^>]+)>;\s*rel=\"next\"")


def _parse_next_link(headers: dict[str, str]) -> str | None:
    link_header = headers.get("Link") or headers.get("link")
    if not link_header:
        return None
    match = _LINK_NEXT_RE.search(link_header)
    return match.group(1) if match else None


def _cache_key(
    method: str,
    url: str,
    body: bytes | None,
    *,
    extra: Iterable[tuple[str, str]] | None = None,
) -> str:
    digest = hashlib.sha256()
    digest.update(method.encode("utf-8"))
    digest.update(b"|")
    digest.update(url.encode("utf-8"))
    digest.update(b"|")
    if body:
        digest.update(body)
    if extra:
        for key, value in extra:
            digest.update(b"|")
            digest.update(key.encode("utf-8"))
            digest.update(b"=")
            digest.update(value.encode("utf-8"))
    return digest.hexdigest()


def _cache_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}.json"


def _cache_get(cache_dir: str | None, key: str) -> str | None:
    if not cache_dir:
        return None
    path = _cache_path(Path(cache_dir), key)
    try:
        if path.exists():
            return path.read_text(encoding="utf-8")
    except Exception as exc:
        sys.stderr.write(f"[gh_api] failed to read cache {path}: {exc}\n")
        return None
    return None


def _cache_put(cache_dir: str | None, key: str, payload: str) -> None:
    if not cache_dir:
        return
    path = _cache_path(Path(cache_dir), key)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    except Exception as exc:
        sys.stderr.write(f"[gh_api] failed to write cache {path}: {exc}\n")


def _emit_success(payload: Any, *, json_envelope: bool) -> None:
    if json_envelope:
        print_json({"ok": True, "data": payload})
    else:
        if isinstance(payload, str):
            _stdout_write(payload)
        else:
            _stdout_write(json.dumps(payload))


def _emit_error(message: str, *, json_envelope: bool, code: int | None = None) -> None:
    if json_envelope:
        print_error_json(message, code=code)
    else:
        sys.stderr.write(f"{message}\n")


def _parse_cached_payload(text: str) -> Any:
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Tiny GitHub API wrapper (App token or PAT).")
    parser.add_argument("--method", default="GET", choices=["GET", "POST", "PATCH", "DELETE"])
    parser.add_argument(
        "--path", required=True, help="API path, e.g., /repos/{owner}/{repo}/branches"
    )
    parser.add_argument(
        "--param", action="append", default=[], help="Query param key=value (repeatable)"
    )
    parser.add_argument("--data", help="Raw JSON for request body")
    parser.add_argument("--data-file", help="Path to JSON file for request body")
    parser.add_argument("--api-base", default=DEFAULT_API, help="API base URL")
    parser.add_argument(
        "--scheme", default=DEFAULT_SCHEME, help='Auth scheme (token or Bearer), default "token"'
    )
    parser.add_argument(
        "--print-curl", action="store_true", help="Print a redacted curl command (no network)"
    )
    parser.add_argument(
        "--paginate",
        action="store_true",
        help="Follow Link rel=next and aggregate JSON arrays",
    )
    parser.add_argument(
        "--per-page",
        type=int,
        default=None,
        help="Convenience helper to set per_page when not already provided",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Safety guard to stop pagination after N pages",
    )
    parser.add_argument(
        "--cache-dir",
        default=DEFAULT_CACHE_DIR,
        help="Directory used for response cache (optional)",
    )
    parser.add_argument(
        "--use-cache-only",
        action="store_true",
        help="Serve response from cache only; fail if cache entry missing",
    )
    parser.add_argument(
        "--refresh-cache",
        action="store_true",
        help="Bypass cache and force a fresh request",
    )
    parser.add_argument(
        "--json-envelope",
        action="store_true",
        help="Wrap responses/errors in a JSON envelope (machine readable)",
    )
    args = parser.parse_args(argv)

    params = _parse_params(args.param)
    if args.per_page is not None and "per_page" not in params:
        params["per_page"] = str(args.per_page)
    url = _compose_url(args.api_base, args.path, params)
    body = _load_body(args.data, args.data_file)
    token = _read_token()
    extra_flags = (
        ("paginate", "1" if args.paginate else "0"),
        ("max_pages", str(args.max_pages) if args.max_pages is not None else "none"),
    )
    cache_key = _cache_key(args.method, url, body, extra=extra_flags)

    if args.print_curl:
        _emit_curl(args.method, url, token, args.scheme, body)
        return 0

    init_logger(level="WARNING", json_mode=args.json_envelope)

    with capture_exceptions(
        exit_code=2, emit_json=args.json_envelope, errmsg="[gh_api] request failed"
    ):
        if args.use_cache_only:
            cached = _cache_get(args.cache_dir, cache_key)
            if cached is None:
                _emit_error(
                    "[gh_api] cache miss and --use-cache-only set", json_envelope=args.json_envelope
                )
                return 2
            payload = _parse_cached_payload(cached)
            if args.json_envelope:
                _emit_success(payload, json_envelope=True)
            else:
                if isinstance(payload, str):
                    _stdout_write(payload)
                elif cached:
                    _stdout_write(json.dumps(payload))
            return 0

        if not args.refresh_cache:
            cached = _cache_get(args.cache_dir, cache_key)
            if cached is not None:
                payload = _parse_cached_payload(cached)
                if args.json_envelope:
                    _emit_success(payload, json_envelope=True)
                else:
                    if isinstance(payload, str):
                        _stdout_write(payload)
                    elif cached:
                        _stdout_write(json.dumps(payload))
                return 0

        aggregated: Any = None
        current_url = url
        page_count = 0

        while True:
            code, text, headers = _request(args.method, current_url, token, args.scheme, body)
            if not (200 <= code < 300):
                _emit_error(f"[gh_api] HTTP {code}", json_envelope=args.json_envelope, code=code)
                return 2

            parsed: Any = None
            if text:
                try:
                    parsed = json.loads(text)
                except json.JSONDecodeError:
                    parsed = text

            if args.paginate:
                if aggregated is None:
                    if isinstance(parsed, list):
                        aggregated = []
                    elif isinstance(parsed, dict) and isinstance(parsed.get("items"), list):
                        aggregated = {"items": []}
                    else:
                        aggregated = []

                if isinstance(aggregated, list) and isinstance(parsed, list):
                    aggregated.extend(parsed)
                elif (
                    isinstance(aggregated, dict)
                    and isinstance(parsed, dict)
                    and isinstance(parsed.get("items"), list)
                ):
                    aggregated["items"].extend(parsed["items"])
                else:
                    aggregated.append(parsed)

                page_count += 1
                next_link = _parse_next_link(headers)
                if not next_link or (args.max_pages is not None and page_count >= args.max_pages):
                    dump = json.dumps(aggregated)
                    if args.json_envelope:
                        _emit_success(aggregated, json_envelope=True)
                    else:
                        _stdout_write(dump)
                    if not args.refresh_cache:
                        _cache_put(args.cache_dir, cache_key, dump)
                    return 0
                current_url = urllib.parse.urljoin(current_url, next_link)
                continue

            payload = parsed if parsed is not None else text
            if args.json_envelope:
                _emit_success(payload, json_envelope=True)
            else:
                if isinstance(payload, str):
                    _stdout_write(payload)
                elif payload is not None:
                    _stdout_write(json.dumps(payload))

            if not args.refresh_cache:
                if isinstance(payload, str) and payload:
                    _cache_put(args.cache_dir, cache_key, payload)
                elif payload is not None:
                    _cache_put(args.cache_dir, cache_key, json.dumps(payload))
            return 0

    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
