#!/usr/bin/env python3
"""
session_access_probe.py — GitHub Copilot Cloud Agent Session Access Manifest Builder
═══════════════════════════════════════════════════════════════════════════════════════

Runs at the START of every Copilot coding agent session (via copilot-setup-steps.yml).

Probes ALL available connection methods and writes a structured access manifest so the
agent knows exactly what is available — before writing a single line of code.

Probed capabilities
───────────────────
  REST API        — core remaining, reset epoch, which tokens work
  GraphQL API     — remaining points, available schemas
  gh CLI          — version, auth status, which scopes the active token has
  CodeQL CLI      — presence, version, DB status (built/not built)
  MCP GitHub      — reachability via api.github.com
  Playwright      — browser availability (chromium/firefox/webkit)
  CODEX secrets   — CODEX_MASTER_KEY / CODEX_BACKUP_KEY presence + privilege level
  Scanning API    — scanning-api.github.com availability
  Repository      — current branch, HEAD SHA, open PR numbers

Output (written to multiple sinks)
───────────────────────────────────
  1. GITHUB_ENV           — exports ACCESS_* + RATE_* vars for the whole session
  2. GITHUB_STEP_SUMMARY  — pretty Markdown table in Actions UI
  3. .codex/session_access_manifest.json  — machine-readable for scripts
  4. stdout               — compact status table for agent context injection

Exit codes
──────────
  0  Probe complete (even if some methods unavailable — degraded is still OK)
  1  Fatal error (e.g. no token at all, cannot write manifest)

Usage
─────
  # In copilot-setup-steps.yml:
  python3 scripts/ci/session_access_probe.py

  # Standalone (verbose):
  python3 scripts/ci/session_access_probe.py --verbose

  # JSON output only:
  python3 scripts/ci/session_access_probe.py --json
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ── Constants ─────────────────────────────────────────────────────────────────
_BASE     = "https://api.github.com"
_SCAN_API = "https://scanning-api.github.com"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
MANIFEST_PATH = REPO_ROOT / ".codex" / "session_access_manifest.json"

# CodeQL paths — configurable via env so CI images with different layouts work.
# Fallback: auto-detect with shutil.which("codeql") in _probe_codeql().
CODEQL_CLI_PATH = os.environ.get(
    "CODEQL_CLI_PATH",
    "/opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/codeql",
)
CODEQL_DB_PATH = os.environ.get("CODEQL_DB_PATH", os.path.join(tempfile.gettempdir(), "codex-db-py"))

# Tuning — all overridable via env (applied by session_access_probe.py at startup).
POLITE_SLEEP    = float(os.environ.get("GH_TRICKLE_POLITE_SLEEP",  "0.4"))
HTTP_TIMEOUT    = int(os.environ.get("GH_PROBE_HTTP_TIMEOUT",      "10"))
MIN_REMAINING   = int(os.environ.get("GH_TRICKLE_MIN_REMAINING",   "50"))


# ── Data model ─────────────────────────────────────────────────────────────────
@dataclass
class MethodStatus:
    available: bool
    detail: str
    extra: dict[str, Any] = field(default_factory=dict)

    def emoji(self) -> str:
        return "✅" if self.available else "❌"


@dataclass
class RateLimitInfo:
    resource: str
    remaining: int
    limit: int
    reset_epoch: int
    reset_human: str

    def is_available(self, min_remaining: int = 10) -> bool:
        return self.remaining >= min_remaining

    def pct(self) -> int:
        return int(self.remaining / max(self.limit, 1) * 100)


@dataclass
class TokenInfo:
    token_tail: str          # last 4 chars (safe to log)
    source_var: str          # env var name it came from
    is_elevated: bool        # CODEX_MASTER_KEY / CODEX_BACKUP_KEY
    rate_limits: dict[str, RateLimitInfo] = field(default_factory=dict)
    scopes: list[str] = field(default_factory=list)
    error: str = ""


@dataclass
class AccessManifest:
    generated_at: str
    session_sha: str
    branch: str
    repo: str

    # Per-method availability
    rest: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))
    graphql: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))
    gh_cli: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))
    codeql_cli: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))
    playwright: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))
    scanning_api: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))
    mcp_github: MethodStatus = field(default_factory=lambda: MethodStatus(False, "not probed"))

    # Token inventory
    tokens: list[TokenInfo] = field(default_factory=list)

    # Best available token (for use in scripts)
    best_token_var: str = ""
    best_token_rest_remaining: int = 0
    rest_reset_epoch: int = 0
    graphql_remaining: int = 0

    # Repository context
    open_prs: list[int] = field(default_factory=list)
    head_sha: str = ""

    # Trickle-down recommendation
    recommended_method: str = ""
    recommended_method_detail: str = ""


# ── Helpers ────────────────────────────────────────────────────────────────────
def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _http_get(url: str, token: str, timeout: int = 10) -> tuple[Any, int, dict]:
    """Return (parsed_body, http_status_code, response_headers)."""
    try:
        req = urllib.request.Request(url, headers=_headers(token))  # noqa: S310  # _BASE/_SCAN_API are https-only constants
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310  # _BASE/_SCAN_API are https-only constants
            return json.load(r), r.status, dict(r.headers)
    except urllib.error.HTTPError as exc:
        try:
            body = json.loads(exc.read())
        except Exception:
            body = {}
        return body, exc.code, {}
    except Exception as exc:
        return {"error": str(exc)}, 0, {}


def _polite() -> None:
    time.sleep(POLITE_SLEEP)


def _discover_tokens() -> list[tuple[str, str, bool]]:
    """Return list of (token_value, env_var_name, is_elevated)."""
    candidates = [
        ("CODEX_MASTER_KEY",          True),
        ("CODEX_BACKUP_KEY",          True),
        ("CODEX_ADMIN_KEY",           True),
        ("AGENT_GITHUB_TOKEN",        False),
        ("GITHUB_COPILOT_API_TOKEN",  False),
        ("GITHUB_TOKEN",              False),
        ("GH_TOKEN",                  False),
    ]
    seen: set[str] = set()
    result = []
    for var, elevated in candidates:
        val = os.environ.get(var, "")
        if val and val not in seen:
            seen.add(val)
            result.append((val, var, elevated))
    return result


# ── Probes ─────────────────────────────────────────────────────────────────────
def probe_token(token: str, var_name: str, is_elevated: bool, owner: str, repo: str) -> TokenInfo:
    """Probe a single token: rate limits + scopes."""
    info = TokenInfo(
        token_tail=token[-4:] if len(token) >= 4 else "????",
        source_var=var_name,
        is_elevated=is_elevated,
    )
    _polite()
    body, status, headers = _http_get(f"{_BASE}/rate_limit", token)
    if status == 200:
        resources = body.get("resources", {})
        for name, r in resources.items():
            if r.get("limit", 0) > 0:
                reset_dt = datetime.fromtimestamp(r["reset"], tz=timezone.utc).strftime("%H:%M:%SZ")
                info.rate_limits[name] = RateLimitInfo(
                    resource=name,
                    remaining=r["remaining"],
                    limit=r["limit"],
                    reset_epoch=r["reset"],
                    reset_human=reset_dt,
                )
        # Extract scopes from X-OAuth-Scopes if present
        scope_header = headers.get("X-OAuth-Scopes", "") or headers.get("x-oauth-scopes", "")
        if scope_header:
            info.scopes = [s.strip() for s in scope_header.split(",") if s.strip()]
    elif status == 401:
        info.error = "invalid/expired token"
    elif status == 403:
        msg = body.get("message", "")
        if "rate limit" in msg.lower():
            info.error = "rate-limited (403)"
        else:
            info.error = f"forbidden: {msg[:80]}"
    else:
        info.error = f"HTTP {status}"
    return info


def probe_rest(tokens: list[tuple[str, str, bool]], owner: str, repo: str) -> tuple[MethodStatus, str, int, int]:
    """
    Probe REST availability across all tokens.
    Returns (status, best_token_var, best_remaining, reset_epoch).
    """
    best_remaining = 0
    best_var = ""
    best_reset = int(time.time()) + 3600

    for token, var_name, _ in tokens:
        _polite()
        body, status, _ = _http_get(f"{_BASE}/rate_limit", token)
        if status != 200:
            continue
        core = body.get("resources", {}).get("core", {})
        remaining = core.get("remaining", 0)
        reset_ep  = core.get("reset", best_reset)
        if remaining > best_remaining:
            best_remaining = remaining
            best_var = var_name
            best_reset = reset_ep

    if best_remaining > 0:
        reset_human = datetime.fromtimestamp(best_reset, tz=timezone.utc).strftime("%H:%M:%SZ")
        return (
            MethodStatus(True, f"{best_remaining} remaining via {best_var}, resets {reset_human}",
                         {"remaining": best_remaining, "reset_epoch": best_reset}),
            best_var, best_remaining, best_reset,
        )

    # All exhausted — find earliest reset
    earliest_reset = best_reset
    for token, _var_name, _ in tokens:
        _polite()
        body, status, _ = _http_get(f"{_BASE}/rate_limit", token)
        if status == 200:
            r = body.get("resources", {}).get("core", {}).get("reset", earliest_reset)
            earliest_reset = min(earliest_reset, r)
    wait_secs = max(0, earliest_reset - int(time.time()))
    reset_human = datetime.fromtimestamp(earliest_reset, tz=timezone.utc).strftime("%H:%M:%SZ")
    return (
        MethodStatus(False, f"ALL TOKENS EXHAUSTED — resets {reset_human} (~{wait_secs//60}m {wait_secs%60}s)",
                     {"reset_epoch": earliest_reset, "wait_seconds": wait_secs}),
        "", 0, earliest_reset,
    )


def probe_graphql(tokens: list[tuple[str, str, bool]]) -> tuple[MethodStatus, int]:
    """Probe GraphQL availability. Returns (status, best_remaining)."""
    best = 0
    best_var = ""
    for token, var_name, _ in tokens:
        _polite()
        body, status, _ = _http_get(f"{_BASE}/rate_limit", token)
        if status == 200:
            gql = body.get("resources", {}).get("graphql", {})
            if gql.get("remaining", 0) > best:
                best = gql["remaining"]
                best_var = var_name

    # Quick schema test
    schema_ok = False
    if best > 0 and tokens:
        token = next((t for t, v, _ in tokens if v == best_var), tokens[0][0])
        _polite()
        try:
            payload = json.dumps({"query": "{ viewer { login } }"}).encode()
            req = urllib.request.Request(  # noqa: S310  # _BASE/_SCAN_API are https-only constants
                f"{_BASE}/graphql",
                data=payload,
                headers={**_headers(token), "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:  # noqa: S310  # _BASE/_SCAN_API are https-only constants
                result = json.load(r)
            if "data" in result and "viewer" in result["data"]:
                schema_ok = True
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    if best > 0 and schema_ok:
        return MethodStatus(True, f"{best} pts remaining via {best_var}", {"remaining": best}), best
    if best > 0:
        return MethodStatus(True, f"{best} pts remaining (schema probe failed)", {"remaining": best}), best
    return MethodStatus(False, "GraphQL exhausted or unavailable"), 0


def probe_gh_cli() -> MethodStatus:
    """Probe `gh` CLI availability and auth status."""
    gh = shutil.which("gh")
    if not gh:
        return MethodStatus(False, "gh CLI not found on PATH")
    try:
        ver = subprocess.run([gh, "version"], capture_output=True, text=True, timeout=5, shell=False)
        version_line = ver.stdout.splitlines()[0] if ver.stdout else "unknown"

        auth = subprocess.run([gh, "auth", "status"], capture_output=True, text=True, timeout=HTTP_TIMEOUT, shell=False)
        auth_ok = auth.returncode == 0
        _ = (auth.stdout + auth.stderr).strip()[:200]  # kept for debug logging

        # Try a lightweight API call
        api_ok = False
        _polite()
        api_test = subprocess.run(
            [gh, "api", "/rate_limit", "--jq", ".resources.core.remaining"],
            capture_output=True, text=True, timeout=HTTP_TIMEOUT, shell=False,
        )
        if api_test.returncode == 0:
            try:
                remaining = int(api_test.stdout.strip())
                api_ok = remaining > 0
                api_detail = f"core.remaining={remaining}"
            except ValueError:
                api_detail = "parse error"
        else:
            api_detail = api_test.stderr.strip()[:80]

        return MethodStatus(
            auth_ok and api_ok,
            f"{version_line} | auth={'OK' if auth_ok else 'FAIL'} | api={api_detail}",
            {"version": version_line, "auth_ok": auth_ok, "api_ok": api_ok},
        )
    except subprocess.TimeoutExpired:
        return MethodStatus(False, "gh CLI timeout")
    except Exception as exc:
        return MethodStatus(False, f"gh CLI error: {exc}")


def probe_codeql() -> MethodStatus:
    """Probe CodeQL CLI presence and DB status."""
    cli = Path(CODEQL_CLI_PATH)
    if not cli.exists():
        # Try PATH
        alt = shutil.which("codeql")
        if alt:
            cli = Path(alt)
        else:
            return MethodStatus(False, "CodeQL CLI not found")

    try:
        ver = subprocess.run(
            [str(cli), "version", "--format=json"],
            capture_output=True, text=True, timeout=15, shell=False,
        )
        version_info = json.loads(ver.stdout) if ver.returncode == 0 else {}
        version_str = version_info.get("version", "unknown")
    except Exception as exc:
        return MethodStatus(False, f"CodeQL version error: {exc}")

    db_ready = (Path(CODEQL_DB_PATH) / "db-python").exists()
    db_detail = f"DB={'ready' if db_ready else 'not built'} at {CODEQL_DB_PATH}"

    return MethodStatus(
        True,
        f"v{version_str} | {db_detail}",
        {"version": version_str, "cli_path": str(cli), "db_ready": db_ready, "db_path": CODEQL_DB_PATH},
    )


def probe_playwright() -> MethodStatus:
    """Probe Playwright browser availability."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", "import playwright; print(playwright.__version__)"],
            capture_output=True, text=True, timeout=HTTP_TIMEOUT, shell=False,
        )
        if result.returncode != 0:
            return MethodStatus(False, "playwright package not installed")
        version = result.stdout.strip()

        # Check for chromium executable
        browsers = []
        for browser in ("chromium", "firefox", "webkit"):
            check = subprocess.run(
                [sys.executable, "-m", "playwright", "install", "--dry-run", browser],
                capture_output=True, text=True, timeout=HTTP_TIMEOUT, shell=False,
            )
            if check.returncode == 0 or "already installed" in (check.stdout + check.stderr).lower():
                browsers.append(browser)

        available = len(browsers) > 0
        return MethodStatus(
            available,
            f"v{version} | browsers: {browsers or 'none installed'}",
            {"version": version, "browsers": browsers},
        )
    except Exception as exc:
        return MethodStatus(False, f"Playwright probe error: {exc}")


def probe_scanning_api(tokens: list[tuple[str, str, bool]]) -> MethodStatus:
    """Probe scanning-api.github.com (separate rate-limit pool)."""
    if not tokens:
        return MethodStatus(False, "no tokens to test")
    token = tokens[0][0]
    _polite()
    try:
        req = urllib.request.Request(  # noqa: S310  # _BASE/_SCAN_API are https-only constants
            f"{_SCAN_API}/rate_limit",
            headers=_headers(token),
        )
        with urllib.request.urlopen(req, timeout=8) as r:  # noqa: S310  # _BASE/_SCAN_API are https-only constants
            body = json.load(r)
        core = body.get("resources", {}).get("core", {})
        return MethodStatus(
            True,
            f"scanning-api.github.com reachable, core.remaining={core.get('remaining', '?')}",
            {"remaining": core.get("remaining")},
        )
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return MethodStatus(False, "scanning-api.github.com: 404 (endpoint not available for this token)")
        if exc.code == 403:
            return MethodStatus(False, "scanning-api.github.com: 403 (insufficient permissions)")
        return MethodStatus(False, f"scanning-api.github.com HTTP {exc.code}")
    except Exception as exc:
        return MethodStatus(False, f"scanning-api.github.com unreachable: {exc}")


def probe_repo_context(tokens: list[tuple[str, str, bool]], owner: str, repo: str) -> tuple[str, list[int]]:
    """Return (head_sha, open_pr_numbers) using best available token."""
    head_sha = os.environ.get("GITHUB_SHA", "")
    if not head_sha:
        try:
            r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=5, shell=False)
            head_sha = r.stdout.strip()[:40]
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    open_prs: list[int] = []
    if not tokens:
        return head_sha, open_prs

    # Only try if we have REST capacity
    token, _, _ = tokens[0]
    _polite()
    body, status, _ = _http_get(
        f"{_BASE}/repos/{owner}/{repo}/pulls?state=open&per_page=10", token,
    )
    if status == 200 and isinstance(body, list):
        open_prs = [pr["number"] for pr in body]

    return head_sha, open_prs


def _determine_best_method(manifest: AccessManifest) -> tuple[str, str]:
    """Determine the recommended trickle-down method for this session."""
    if manifest.rest.available and manifest.best_token_rest_remaining >= 100:
        return "REST", f"core.remaining={manifest.best_token_rest_remaining} via {manifest.best_token_var}"
    if manifest.graphql.available and manifest.graphql_remaining >= 100:
        return "GraphQL", f"graphql.remaining={manifest.graphql_remaining}"
    if manifest.gh_cli.available:
        return "gh_cli", manifest.gh_cli.detail
    if manifest.codeql_cli.available:
        return "codeql_local", "CodeQL CLI available for offline analysis"
    if manifest.rest.available:
        return "REST_limited", f"core.remaining={manifest.best_token_rest_remaining} (low)"
    # All rate-limited — compute wait time
    wait = max(0, manifest.rest_reset_epoch - int(time.time()))
    reset_human = datetime.fromtimestamp(manifest.rest_reset_epoch, tz=timezone.utc).strftime("%H:%M:%SZ")
    return "WAIT", f"All REST tokens exhausted — resets {reset_human} (~{wait//60}m {wait%60}s)"


# ── Main probe orchestrator ─────────────────────────────────────────────────────
def run_probe(owner: str = "Aries-Serpent", repo: str = "_codex_", verbose: bool = False) -> AccessManifest:
    branch = os.environ.get("GITHUB_REF_NAME", os.environ.get("GITHUB_HEAD_REF", "unknown"))
    sha    = os.environ.get("GITHUB_SHA", "")[:12] or "local"
    full_repo = f"{owner}/{repo}"

    manifest = AccessManifest(
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        session_sha=sha,
        branch=branch,
        repo=full_repo,
    )

    # ── Discover tokens ──────────────────────────────────────────────────────
    raw_tokens = _discover_tokens()
    print(f"[probe] Discovered {len(raw_tokens)} unique token(s)", file=sys.stderr)

    # ── Probe each token ─────────────────────────────────────────────────────
    for token, var_name, is_elevated in raw_tokens:
        info = probe_token(token, var_name, is_elevated, owner, repo)
        manifest.tokens.append(info)
        if verbose:
            core = info.rate_limits.get("core")
            gql  = info.rate_limits.get("graphql")
            print(
                f"  [{var_name}] core={core.remaining if core else 'N/A'}"
                f"  graphql={gql.remaining if gql else 'N/A'}"
                f"  elevated={is_elevated}",
                file=sys.stderr,
            )

    # ── REST probe ───────────────────────────────────────────────────────────
    rest_status, best_var, best_remaining, reset_epoch = probe_rest(raw_tokens, owner, repo)
    manifest.rest                 = rest_status
    manifest.best_token_var       = best_var
    manifest.best_token_rest_remaining = best_remaining
    manifest.rest_reset_epoch     = reset_epoch

    # ── GraphQL probe ────────────────────────────────────────────────────────
    gql_status, gql_remaining = probe_graphql(raw_tokens)
    manifest.graphql           = gql_status
    manifest.graphql_remaining = gql_remaining

    # ── gh CLI probe ─────────────────────────────────────────────────────────
    manifest.gh_cli = probe_gh_cli()

    # ── CodeQL CLI probe ─────────────────────────────────────────────────────
    manifest.codeql_cli = probe_codeql()

    # ── Playwright probe ─────────────────────────────────────────────────────
    manifest.playwright = probe_playwright()

    # ── Scanning API probe ───────────────────────────────────────────────────
    manifest.scanning_api = probe_scanning_api(raw_tokens)

    # ── MCP GitHub probe (reachability) ─────────────────────────────────────
    # MCP uses the same api.github.com endpoint; proxy through the REST result
    manifest.mcp_github = MethodStatus(
        manifest.rest.available or manifest.graphql.available,
        "github-mcp-server uses api.github.com — same rate pool as REST/GraphQL",
    )

    # ── Repository context ───────────────────────────────────────────────────
    manifest.head_sha, manifest.open_prs = probe_repo_context(raw_tokens, owner, repo)

    # ── Determine recommended method ─────────────────────────────────────────
    manifest.recommended_method, manifest.recommended_method_detail = _determine_best_method(manifest)

    return manifest


# ── Output writers ──────────────────────────────────────────────────────────────
def write_github_env(manifest: AccessManifest) -> None:
    """Export ACCESS_* and RATE_* variables to GITHUB_ENV for the whole session."""
    gh_env = os.environ.get("GITHUB_ENV")
    if not gh_env:
        return
    lines = [
        f"ACCESS_REST={'available' if manifest.rest.available else 'exhausted'}",
        f"ACCESS_REST_REMAINING={manifest.best_token_rest_remaining}",
        f"ACCESS_REST_RESET_EPOCH={manifest.rest_reset_epoch}",
        f"ACCESS_REST_BEST_TOKEN_VAR={manifest.best_token_var}",
        f"ACCESS_GRAPHQL={'available' if manifest.graphql.available else 'exhausted'}",
        f"ACCESS_GRAPHQL_REMAINING={manifest.graphql_remaining}",
        f"ACCESS_GH_CLI={'available' if manifest.gh_cli.available else 'unavailable'}",
        f"ACCESS_CODEQL_CLI={'available' if manifest.codeql_cli.available else 'unavailable'}",
        f"ACCESS_CODEQL_DB_READY={manifest.codeql_cli.extra.get('db_ready', False)}",
        f"ACCESS_PLAYWRIGHT={'available' if manifest.playwright.available else 'unavailable'}",
        f"ACCESS_MCP_GITHUB={'available' if manifest.mcp_github.available else 'unavailable'}",
        f"ACCESS_SCANNING_API={'available' if manifest.scanning_api.available else 'unavailable'}",
        f"ACCESS_ELEVATED_TOKEN={'true' if any(t.is_elevated for t in manifest.tokens if not t.error) else 'false'}",
        f"ACCESS_RECOMMENDED_METHOD={manifest.recommended_method}",
        f"ACCESS_TOKEN_COUNT={len(manifest.tokens)}",
        f"SESSION_HEAD_SHA={manifest.head_sha}",
        f"SESSION_OPEN_PRS={','.join(str(p) for p in manifest.open_prs)}",
        f"SESSION_BRANCH={manifest.branch}",
    ]
    with open(gh_env, "a") as f:
        f.writelines(line + "\n" for line in lines)


def write_step_summary(manifest: AccessManifest) -> None:
    """Write Markdown access table to GITHUB_STEP_SUMMARY."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    reset_human = datetime.fromtimestamp(
        manifest.rest_reset_epoch, tz=timezone.utc,
    ).strftime("%H:%M:%S UTC") if manifest.rest_reset_epoch else "N/A"

    lines = [
        "## 🔌 Session Access Manifest",
        f"_Generated: {manifest.generated_at} · Branch: `{manifest.branch}` · SHA: `{manifest.head_sha}`_",
        "",
        "### Connection Methods",
        "| Method | Status | Detail |",
        "|--------|--------|--------|",
        f"| REST API | {manifest.rest.emoji()} | {manifest.rest.detail} |",
        f"| GraphQL | {manifest.graphql.emoji()} | {manifest.graphql.detail} |",
        f"| gh CLI | {manifest.gh_cli.emoji()} | {manifest.gh_cli.detail[:80]} |",
        f"| CodeQL CLI | {manifest.codeql_cli.emoji()} | {manifest.codeql_cli.detail[:80]} |",
        f"| Playwright | {manifest.playwright.emoji()} | {manifest.playwright.detail[:80]} |",
        f"| MCP GitHub | {manifest.mcp_github.emoji()} | {manifest.mcp_github.detail[:80]} |",
        f"| Scanning API | {manifest.scanning_api.emoji()} | {manifest.scanning_api.detail[:80]} |",
        "",
        "### Token Inventory",
        "| Token | Elevated | REST Remaining | GraphQL Remaining | Scopes |",
        "|-------|----------|---------------|-------------------|--------|",
    ]
    for t in manifest.tokens:
        core = t.rate_limits.get("core")
        gql  = t.rate_limits.get("graphql")
        lines.append(
            f"| `..{t.token_tail}` ({t.source_var}) "
            f"| {'⭐' if t.is_elevated else '—'} "
            f"| {core.remaining if core else ('ERR: ' + t.error[:20])} "
            f"| {gql.remaining if gql else '—'} "
            f"| {', '.join(t.scopes[:4]) or 'not exposed'} |",
        )

    lines += [
        "",
        "### Rate Limit Status",
        f"- **REST core** resets at `{reset_human}`",
        f"- **GraphQL** remaining: `{manifest.graphql_remaining} / 5000`",
        "",
        f"### 🎯 Recommended Method: `{manifest.recommended_method}`",
        f"> {manifest.recommended_method_detail}",
        "",
        "### Trickle-Down Priority",
        "1. `REST` → if core.remaining ≥ 100",
        "2. `GraphQL` → if graphql.remaining ≥ 100 (for schema-supported queries)",
        "3. `gh_cli` → subprocess fallback",
        "4. `codeql_local` → offline analysis via local DB",
        "5. `WAIT` → sleep until earliest reset epoch, then retry from step 1",
        "",
        f"Open PRs: {manifest.open_prs or 'none found'}",
    ]

    with open(summary_path, "a") as f:
        f.write("\n".join(lines) + "\n")


def write_manifest_json(manifest: AccessManifest) -> None:
    """Write machine-readable JSON to .codex/session_access_manifest.json."""
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Convert dataclasses to dicts cleanly
    def _serialize(obj: Any) -> Any:
        if hasattr(obj, "__dataclass_fields__"):
            return {k: _serialize(v) for k, v in asdict(obj).items()}
        if isinstance(obj, list):
            return [_serialize(i) for i in obj]
        return obj

    data = _serialize(manifest)
    MANIFEST_PATH.write_text(json.dumps(data, indent=2))


def print_summary_table(manifest: AccessManifest) -> None:
    """Print compact access summary to stdout for agent context injection."""
    reset_human = datetime.fromtimestamp(
        manifest.rest_reset_epoch, tz=timezone.utc,
    ).strftime("%H:%M:%SZ") if manifest.rest_reset_epoch else "?"

    print("\n╔═══════════════════════════════════════════════════════════╗")
    print("║           SESSION ACCESS MANIFEST (startup probe)        ║")
    print("╠═══════════════════════════════════════════════════════════╣")
    print(f"║  Branch: {manifest.branch:<20}  SHA: {manifest.head_sha[:10]:<12} ║")
    print("╠══════════════════════╦════════════════════════════════════╣")
    print("║ Method               ║ Status                             ║")
    print("╠══════════════════════╬════════════════════════════════════╣")
    for label, status in [
        ("REST API",        manifest.rest),
        ("GraphQL",         manifest.graphql),
        ("gh CLI",          manifest.gh_cli),
        ("CodeQL CLI",      manifest.codeql_cli),
        ("Playwright",      manifest.playwright),
        ("MCP GitHub",      manifest.mcp_github),
        ("Scanning API",    manifest.scanning_api),
    ]:
        icon = "✅" if status.available else "❌"
        detail = status.detail[:35].ljust(36)
        print(f"║ {icon} {label:<18} ║ {detail} ║")
    print("╠══════════════════════╩════════════════════════════════════╣")
    print(f"║  Tokens found: {len(manifest.tokens)}  Elevated: "
          f"{'YES' if any(t.is_elevated for t in manifest.tokens) else 'NO':<4}"
          f"  REST resets: {reset_human:<12} ║")
    print(f"║  Recommended: {manifest.recommended_method:<10}  "
          f"REST remaining: {manifest.best_token_rest_remaining:<6}"
          f" GQL: {manifest.graphql_remaining:<6} ║")
    print("╚═══════════════════════════════════════════════════════════╝")

    if manifest.recommended_method == "WAIT":
        wait = max(0, manifest.rest_reset_epoch - int(time.time()))
        print(f"\n⚠️  ALL REST TOKENS EXHAUSTED — use GraphQL/gh CLI or wait {wait//60}m {wait%60}s")
    print(f"\n→ Use method: {manifest.recommended_method} ({manifest.recommended_method_detail})")
    print(f"→ Open PRs: {manifest.open_prs or 'none'}")
    print(f"→ Manifest: {MANIFEST_PATH}\n")


# ── Entry point ─────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--owner",   default=os.environ.get("GITHUB_REPOSITORY_OWNER", "Aries-Serpent"))
    parser.add_argument("--repo",    default=os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_").split("/")[-1])
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json",    action="store_true", help="Print JSON manifest to stdout")
    args = parser.parse_args()

    manifest = run_probe(owner=args.owner, repo=args.repo, verbose=args.verbose)

    # Write all sinks
    write_github_env(manifest)
    write_step_summary(manifest)
    write_manifest_json(manifest)

    if args.json:
        print(json.dumps(asdict(manifest), indent=2, default=str))
    else:
        print_summary_table(manifest)

    return 0


if __name__ == "__main__":
    sys.exit(main())
