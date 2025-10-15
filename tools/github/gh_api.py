#!/usr/bin/env python3

"""
Tiny GitHub API wrapper (installation token or PAT).

Features:
  - Methods: GET/POST/PATCH/DELETE
  - Query params via repeated --param key=value
  - JSON body via --data '{"k":"v"}' or --data-file file.json
  - --print-curl emits a redacted curl command (no network)
  - Clean stdout (JSON) / stderr (diagnostics) separation

Auth:
  - Reads token from GH_TOKEN or GITHUB_TOKEN
  - Header scheme defaults to "token"; override with GITHUB_AUTH_SCHEME=Bearer if needed
  - API base defaults to https://api.github.com (override with GITHUB_API)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_API = os.environ.get("GITHUB_API", "https://api.github.com")
DEFAULT_SCHEME = os.environ.get("GITHUB_AUTH_SCHEME", "token")


def _read_token(env=os.environ) -> str:
    tok = env.get("GH_TOKEN") or env.get("GITHUB_TOKEN")
    if not tok:
        raise SystemExit("[gh_api] missing GH_TOKEN/GITHUB_TOKEN")
    return tok.strip()


def _parse_params(kvs: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for kv in kvs:
        if "=" not in kv:
            raise SystemExit(f"[gh_api] invalid --param '{kv}', expected key=value")
        k, v = kv.split("=", 1)
        out[k] = v
    return out


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
        with open(data_file, "rb") as fh:
            return fh.read()
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
            decoded = body.hex()
        else:
            try:
                json.loads(decoded)
                parts.extend(["-H", "'Content-Type: application/json'", "--data", f"'{decoded}'"])
                decoded = None
            except json.JSONDecodeError:
                pass
        if decoded:
            parts.extend(["--data-binary", "'<binary>'"])
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
    req = urllib.request.Request(  # noqa: S310 (GitHub API endpoint)
        url=url, data=body, method=method, headers=headers
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 (api.github.com)
            return resp.getcode(), resp.read().decode("utf-8"), dict(resp.headers)
    except urllib.error.HTTPError as err:
        sys.stderr.write(f"[gh_api] HTTP {err.code} {err.reason}\n")
        try:
            err_body = err.read().decode("utf-8")
            sys.stderr.write(err_body + "\n")
        except Exception as exc:
            sys.stderr.write(f"[gh_api] failed to read error body: {exc}\n")
        return err.code, "", {}


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
    args = parser.parse_args()

    params = _parse_params(args.param)
    url = _compose_url(args.api_base, args.path, params)
    body = _load_body(args.data, args.data_file)
    token = _read_token()

    if args.print_curl:
        _emit_curl(args.method, url, token, args.scheme, body)
        return 0

    code, text, _headers = _request(args.method, url, token, args.scheme, body)
    if text:
        sys.stdout.write(text if text.endswith("\n") else text + "\n")
    return 0 if 200 <= code < 300 else 2


if __name__ == "__main__":
    raise SystemExit(main())
