#!/usr/bin/env python3
"""Tiny GitHub API wrapper (installation token or PAT).

Features:
  - Methods: GET/POST/PATCH/DELETE
  - Query params via repeated --param key=value
  - JSON body via --data '{"k":"v"}' or --data-file file.json
  - --print-curl emits a redacted curl command (no network)
  - Clean stdout (JSON) / stderr (diagnostics) separation
  - Pagination via --paginate (follows RFC5988 Link rel="next")
  - Local cache via --cache-dir, --use-cache-only, --refresh-cache

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
from collections.abc import Mapping
from pathlib import Path
from typing import Any

DEFAULT_API = os.environ.get("GITHUB_API", "https://api.github.com")
DEFAULT_SCHEME = os.environ.get("GITHUB_AUTH_SCHEME", "token")
DEFAULT_CACHE_DIR = os.environ.get("GH_API_CACHE_DIR", "")


def _read_token(env: Mapping[str, str] = os.environ) -> str:
    tok = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if not tok:
        raise SystemExit("[gh_api] missing GH_TOKEN/GITHUB_TOKEN")
    return tok.strip()


def _parse_params(param_list: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for item in param_list:
        if "=" not in item:
            raise SystemExit(f"[gh_api] invalid --param '{item}', expected key=value")
        key, value = item.split("=", 1)
        params[key] = value
    return params


def _compose_url(api_base: str, path: str, params: dict[str, str]) -> str:
    trimmed = path.strip()
    if trimmed.startswith("/"):
        trimmed = trimmed[1:]
    url = f"{api_base.rstrip('/')}/{trimmed}" if trimmed else api_base.rstrip("/")
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    return url


def _load_body(data: str | None, data_file: str | None) -> bytes | None:
    if data and data_file:
        raise SystemExit("[gh_api] use only one of --data or --data-file")
    if data_file:
        with open(data_file, "rb") as fh:
            return fh.read()
    if data:
        return data.encode("utf-8")
    return None


def _redact(token: str) -> str:
    return "***REDACTED***" if token else token


def _emit_curl(method: str, url: str, token: str, scheme: str, body: bytes | None) -> None:
    parts = [
        "curl -sS -X",
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
            json.loads(decoded)
        except Exception:
            parts += ["--data-binary", "'@-'< <(printf %s)"]
        else:
            parts += ["-H", "'Content-Type: application/json'", "--data", f"'{decoded}'"]
    parts.append(f"'{url}'")
    sys.stdout.write(" ".join(parts) + "\n")


def _request(
    method: str, url: str, token: str, scheme: str, body: bytes | None
) -> tuple[int, str, dict[str, str]]:
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"{scheme} {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(  # noqa: S310
        url=url, data=body, method=method, headers=headers
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as resp:  # noqa: S310
            return resp.getcode(), resp.read().decode("utf-8"), dict(resp.headers)
    except (
        urllib.error.HTTPError
    ) as exc:  # pragma: no cover - exercised via tests using monkeypatch
        sys.stderr.write(f"[gh_api] HTTP {exc.code} {exc.reason}\n")
        try:
            err_body = exc.read().decode("utf-8")
        except Exception:  # pragma: no cover - defensive
            err_body = ""
        if err_body:
            sys.stderr.write(err_body + "\n")
        return exc.code, "", dict(exc.headers or {})
    except urllib.error.URLError as exc:  # pragma: no cover - defensive logging
        sys.stderr.write(f"[gh_api] network error: {exc}\n")
        return 599, "", {}


_LINK_NEXT_RE = re.compile(r"<([^>]+)>;\s*rel=\"next\"")


def _parse_next_link(headers: dict[str, str]) -> str | None:
    link_value = headers.get("Link") or headers.get("link")
    if not link_value:
        return None
    match = _LINK_NEXT_RE.search(link_value)
    if not match:
        return None
    return match.group(1)


def _cache_key(method: str, url: str, body: bytes | None) -> str:
    digest = hashlib.sha256()
    digest.update(method.encode("utf-8"))
    digest.update(b"|")
    digest.update(url.encode("utf-8"))
    digest.update(b"|")
    if body:
        digest.update(body)
    return digest.hexdigest()


def _resolve_cache_dir(raw: str) -> Path | None:
    raw = raw.strip()
    if not raw:
        return None
    return Path(raw).expanduser()


def _cache_path(cache_dir: Path, key: str) -> Path:
    return cache_dir / f"{key}.json"


def _cache_get(cache_dir: Path | None, key: str) -> str | None:
    if not cache_dir:
        return None
    path = _cache_path(cache_dir, key)
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None
    except OSError:
        return None


def _cache_put(cache_dir: Path | None, key: str, payload: str) -> None:
    if not cache_dir:
        return
    path = _cache_path(cache_dir, key)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    except OSError:
        return


def main() -> int:
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
        "--paginate", action="store_true", help="Follow Link rel=next and aggregate JSON arrays"
    )
    parser.add_argument(
        "--per-page", type=int, default=None, help="Optional per_page param (appended to query)"
    )
    parser.add_argument("--max-pages", type=int, default=100, help="Safety cap when paginating")
    parser.add_argument(
        "--cache-dir", default=DEFAULT_CACHE_DIR, help="Directory for response cache (optional)"
    )
    parser.add_argument(
        "--use-cache-only", action="store_true", help="Serve from cache only; do not hit network"
    )
    parser.add_argument("--refresh-cache", action="store_true", help="Ignore cache and re-fetch")
    args = parser.parse_args()

    params = _parse_params(args.param)
    if args.per_page is not None and "per_page" not in params:
        params["per_page"] = str(args.per_page)
    url = _compose_url(args.api_base, args.path, params)
    body = _load_body(args.data, args.data_file)
    token = _read_token()

    if args.print_curl:
        _emit_curl(args.method, url, token, args.scheme, body)
        return 0

    cache_dir = _resolve_cache_dir(args.cache_dir or "")
    cache_key = _cache_key(args.method, url, body)

    if args.use_cache_only:
        cached_only = _cache_get(cache_dir, cache_key)
        if cached_only is None:
            sys.stderr.write("[gh_api] cache miss and --use-cache-only set\n")
            return 2
        if cached_only:
            if not cached_only.endswith("\n"):
                cached_only = cached_only + "\n"
            sys.stdout.write(cached_only)
        return 0

    if cache_dir and not args.refresh_cache:
        cached = _cache_get(cache_dir, cache_key)
        if cached is not None:
            if cached and not cached.endswith("\n"):
                cached = cached + "\n"
            if cached:
                sys.stdout.write(cached)
            return 0

    aggregated: Any = None
    agg_mode: str | None = None
    current_url = url
    pages = 0

    while True:
        code, text, headers = _request(args.method, current_url, token, args.scheme, body)
        if not (200 <= code < 300):
            return 2

        try:
            page_obj = json.loads(text) if text else None
        except json.JSONDecodeError:
            page_obj = None

        if args.paginate:
            if aggregated is None:
                if isinstance(page_obj, list):
                    aggregated = list(page_obj)
                    agg_mode = "list"
                elif isinstance(page_obj, dict) and isinstance(page_obj.get("items"), list):
                    aggregated = dict(page_obj)
                    aggregated["items"] = list(page_obj["items"])
                    agg_mode = "items"
                else:
                    aggregated = [page_obj if page_obj is not None else text]
                    agg_mode = "generic"
            else:
                if agg_mode == "list":
                    if isinstance(page_obj, list):
                        aggregated.extend(page_obj)
                    else:
                        aggregated.append(page_obj if page_obj is not None else text)
                elif agg_mode == "items":
                    if isinstance(page_obj, dict) and isinstance(page_obj.get("items"), list):
                        aggregated["items"].extend(page_obj["items"])
                    else:
                        aggregated = [aggregated]
                        aggregated.append(page_obj if page_obj is not None else text)
                        agg_mode = "generic"
                else:
                    aggregated.append(page_obj if page_obj is not None else text)

            pages += 1
            next_url = _parse_next_link(headers)
            if next_url and not next_url.startswith("http"):
                next_url = urllib.parse.urljoin(args.api_base, next_url)
            if not next_url or pages >= int(args.max_pages):
                output_text = json.dumps(aggregated)
                if not output_text.endswith("\n"):
                    output_text = output_text + "\n"
                sys.stdout.write(output_text)
                _cache_put(cache_dir, cache_key, output_text.rstrip("\n"))
                return 0
            current_url = next_url
            continue

        # Non-paginated execution
        output_text: str
        if text:
            output_text = text
        elif page_obj is not None:
            output_text = json.dumps(page_obj)
        else:
            output_text = ""

        if output_text:
            if not output_text.endswith("\n"):
                output_text = output_text + "\n"
            sys.stdout.write(output_text)
            _cache_put(cache_dir, cache_key, output_text.rstrip("\n"))
        else:
            _cache_put(cache_dir, cache_key, output_text)
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
