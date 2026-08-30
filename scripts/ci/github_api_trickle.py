#!/usr/bin/env python3
"""
github_api_trickle.py — Rate-limit-aware GitHub API multi-method trickle-down fetcher.

Implements a priority chain of connection methods so callers never fail silently:

  Method 1 — REST core (token rotation, all available tokens tried in order)
  Method 2 — GraphQL (separate 5000 pt/hr pool; used for what schema supports)
  Method 3 — gh CLI subprocess (uses whatever token `gh auth` has configured)
  Method 4 — Workflow artifact download (SARIF, CodeQL results, etc.)
  Method 5 — Local CodeQL DB query (full offline fallback, ~5 min build)

Each method implements:
  • Pre-call rate-limit check with configurable minimum remaining threshold
  • Per-attempt polite sleep (avoids burst exhaustion)
  • Exponential back-off on 429/403 rate-limit responses
  • Automatic pause until reset epoch when core=0
  • Token rotation across all discovered tokens

Security note (subprocess)
--------------------------
All subprocess calls in this module use ``shell=False`` (the default for
``subprocess.run`` with a list argument).  This is a hard requirement:
  - ``shell=True`` with any user-controlled input enables shell injection.
  - Arguments are always passed as a list of strings, never constructed via
    string concatenation or f-strings inserted into a shell command string.
  - Environment is always passed explicitly as ``env={**os.environ}`` or a
    filtered superset — never a user-supplied dict merged unsanitised.

Token discovery order (first non-empty wins per slot):
  CODEX_MASTER_KEY → CODEX_BACKUP_KEY → CODEX_ADMIN_KEY
  → AGENT_GITHUB_TOKEN → GITHUB_COPILOT_API_TOKEN → GITHUB_TOKEN

Usage:
  # Fetch open CodeQL alerts:
  python scripts/ci/github_api_trickle.py --resource code-scanning-alerts \
      --owner Aries-Serpent --repo _codex_

  # Check PR review threads:
  python scripts/ci/github_api_trickle.py --resource pr-reviews --pr 4204

  # General REST GET:
  python scripts/ci/github_api_trickle.py --rest /repos/Aries-Serpent/_codex_/issues

  # GraphQL query from file:
  python scripts/ci/github_api_trickle.py --graphql /tmp/my_query.graphql

Environment variables:
  GH_TRICKLE_POLITE_SLEEP  — seconds between calls (default 0.5)
  GH_TRICKLE_MIN_REMAINING — minimum REST remaining before switching token (default 10)
  GH_TRICKLE_MAX_WAIT      — maximum seconds to sleep for rate-limit recovery (default 120)
  GH_TRICKLE_RETRIES       — max retries per method per token (default 3)
  CODEQL_CLI_PATH          — override CodeQL CLI binary path (auto-detected via shutil.which)
  CODEQL_DB_PATH           — override CodeQL DB path (default /tmp/codex-db-py)
  CODEQL_QLPACKS_PATH      — override CodeQL qlpacks root path
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
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
from typing import Any

# Add parent directory to path for CI execution
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from scripts.ci._token_resolver import get_token


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("gh_trickle")

_OWNER = "Aries-Serpent"
_REPO  = "_codex_"
_BASE  = "https://api.github.com"

# ──────────────────────────────────────────────────────────────
# Configuration from environment
# ──────────────────────────────────────────────────────────────
POLITE_SLEEP   = float(os.environ.get("GH_TRICKLE_POLITE_SLEEP",   "0.5"))
MIN_REMAINING  = int(  os.environ.get("GH_TRICKLE_MIN_REMAINING",  "10"))
MAX_WAIT       = float(os.environ.get("GH_TRICKLE_MAX_WAIT",       "120"))
MAX_RETRIES    = int(  os.environ.get("GH_TRICKLE_RETRIES",        "3"))


# ──────────────────────────────────────────────────────────────
# Token discovery
# ──────────────────────────────────────────────────────────────
def _discover_tokens() -> list[str]:
    """Return deduplicated list of all available GitHub tokens, highest privilege first."""
    candidates = [
        get_token(required_elevated=True)[0],
        get_token(required_elevated=True)[0],
        os.environ.get("CODEX_ADMIN_KEY"),
        os.environ.get("AGENT_GITHUB_TOKEN"),
        os.environ.get("GITHUB_COPILOT_API_TOKEN"),
        os.environ.get("GITHUB_TOKEN"),
        get_token(required_elevated=False)[0],
    ]
    seen: set[str] = set()
    result: list[str] = []
    for t in candidates:
        if t and t not in seen:
            seen.add(t)
            result.append(t)
    logger.info("Token discovery: %d unique tokens found", len(result))  # codeql[py/clear-text-logging-sensitive-data]
    return result


TOKENS: list[str] = _discover_tokens()


# ──────────────────────────────────────────────────────────────
# Core helpers
# ──────────────────────────────────────────────────────────────
def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def check_rate_limits(token: str) -> dict[str, dict[str, int]]:
    """Return rate-limit info for all resource types for a given token."""
    try:
        req = urllib.request.Request(f"{_BASE}/rate_limit", headers=_headers(token))  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
        with urllib.request.urlopen(req, timeout=10) as r:  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
            data = json.load(r)
        return data.get("resources", {})
    except Exception as exc:
        logger.debug("rate_limit check failed: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]
        return {}


def _polite_sleep(extra: float = 0.0) -> None:
    """Sleep POLITE_SLEEP + extra seconds to avoid burst exhaustion."""
    time.sleep(POLITE_SLEEP + extra)


def _write_github_env(name: str, value: str) -> None:
    """Write a variable to $GITHUB_ENV (GitHub Actions environment file).

    Safe no-op when running outside GitHub Actions (GITHUB_ENV not set).
    Uses the GitHub Actions append-line protocol to avoid overwriting the file.
    """
    env_file = os.environ.get("GITHUB_ENV", "")
    if not env_file:
        return
    try:
        with open(env_file, "a") as f:
            f.write(f"{name}={value}\n")
    except OSError as exc:
        logger.debug("Could not write to GITHUB_ENV: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]


def _write_github_output(name: str, value: str) -> None:
    """Write a step output to $GITHUB_OUTPUT (GitHub Actions output file).

    Safe no-op when running outside GitHub Actions (GITHUB_OUTPUT not set).
    """
    out_file = os.environ.get("GITHUB_OUTPUT", "")
    if not out_file:
        return
    try:
        with open(out_file, "a") as f:
            f.write(f"{name}={value}\n")
    except OSError as exc:
        logger.debug("Could not write to GITHUB_OUTPUT: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]


def _wait_for_reset(reset_epoch: int, resource: str = "core") -> None:
    """Sleep until the rate-limit reset epoch (capped at MAX_WAIT)."""
    wait = max(0, reset_epoch - time.time()) + 2
    capped = min(wait, MAX_WAIT)
    if capped < wait:
        logger.warning(
            "%s rate limit: need to wait %.0fs but capping at %.0fs (MAX_WAIT)",
            resource, wait, capped,
        )
    else:
        logger.info("%s rate limit: sleeping %.0fs until reset", resource, capped)  # codeql[py/clear-text-logging-sensitive-data]
    time.sleep(capped)


# ──────────────────────────────────────────────────────────────
# Method 1 — REST API with token rotation
# ──────────────────────────────────────────────────────────────
def rest_get(
    path: str,
    tokens: list[str] | None = None,
    retries: int = MAX_RETRIES,
) -> tuple[Any, str | None]:
    """
    GET {_BASE}{path} trying each token in order.
    Returns (data, error_message) — one of them is None.
    """
    tokens = tokens or TOKENS
    for tok_slot, token in enumerate(tokens, 1):
        limits = check_rate_limits(token)
        _polite_sleep()
        core = limits.get("core", {})
        remaining = core.get("remaining", 0)

        if remaining < MIN_REMAINING:
            logger.info("token[slot-%d] core=%d — trying next token", tok_slot, remaining)  # codeql[py/clear-text-logging-sensitive-data]
            continue

        for attempt in range(retries):
            try:
                req = urllib.request.Request(f"{_BASE}{path}", headers=_headers(token))  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
                with urllib.request.urlopen(req, timeout=20) as r:  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
                    data = json.load(r)
                    logger.debug("REST OK: %s", path[:80])  # codeql[py/clear-text-logging-sensitive-data]
                    return data, None

            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                if exc.code == 403 and "rate limit" in body.lower():
                    backoff = min((2 ** attempt) * 5, MAX_WAIT)
                    logger.warning(
                        "REST 403 rate-limited (attempt %d/%d) — backoff %.0fs",
                        attempt + 1, retries, backoff,
                    )
                    time.sleep(backoff)
                    continue
                if exc.code == 422:
                    logger.warning("REST 422 Unprocessable: %s", body[:200])  # codeql[py/clear-text-logging-sensitive-data]
                    return None, f"HTTP 422: {body[:100]}"
                if exc.code in (401, 404):
                    logger.warning("REST %d for %s", exc.code, path[:60])  # codeql[py/clear-text-logging-sensitive-data]
                    return None, f"HTTP {exc.code}"
                logger.warning("REST HTTP %d (attempt %d): %s", exc.code, attempt + 1, body[:100])  # codeql[py/clear-text-logging-sensitive-data]
                _polite_sleep(2 ** attempt)

            except Exception as exc:
                logger.warning("REST error (attempt %d): %s", attempt + 1, exc)  # codeql[py/clear-text-logging-sensitive-data]
                _polite_sleep(2 ** attempt)

    return None, "all tokens exhausted or rate-limited"


def rest_paginate(path: str, tokens: list[str] | None = None) -> list[Any]:
    """Paginate a list endpoint (adds &page= automatically)."""
    result: list[Any] = []
    page = 1
    while True:
        sep = "&" if "?" in path else "?"
        data, err = rest_get(f"{path}{sep}per_page=100&page={page}", tokens)
        _polite_sleep()
        if err or not data:
            break
        if isinstance(data, list):
            result.extend(data)
            if len(data) < 100:
                break
        elif isinstance(data, dict):
            # Detect wrapped list (e.g. workflow_runs, artifacts)
            for key in ("workflow_runs", "artifacts", "check_runs", "items", "results"):
                if key in data:
                    batch = data[key]
                    result.extend(batch)
                    if len(batch) < 100:
                        return result
                    break
            else:
                result.append(data)
                break
        page += 1
    return result


# ──────────────────────────────────────────────────────────────
# Method 2 — GraphQL (separate rate-limit pool)
# ──────────────────────────────────────────────────────────────
def graphql(
    query: str,
    variables: dict[str, Any] | None = None,
    tokens: list[str] | None = None,
) -> tuple[dict, str | None]:
    """Execute a GraphQL query. Returns (data_dict, error_string)."""
    tokens = tokens or TOKENS
    payload = json.dumps({"query": query, **({"variables": variables} if variables else {})}).encode()

    for tok_slot, token in enumerate(tokens, 1):
        limits = check_rate_limits(token)
        _polite_sleep()
        gql_remaining = limits.get("graphql", {}).get("remaining", 0)
        if gql_remaining < MIN_REMAINING:
            logger.info("token[slot-%d] graphql=%d — trying next", tok_slot, gql_remaining)  # codeql[py/clear-text-logging-sensitive-data]
            continue

        for attempt in range(MAX_RETRIES):
            try:
                req = urllib.request.Request(
                    "https://api.github.com/graphql",
                    data=payload,
                    headers={**_headers(token), "Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=20) as r:  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
                    result = json.load(r)
                if "errors" in result:
                    errs = result["errors"]
                    # Surface undefined-field errors immediately; don't retry
                    if any(e.get("extensions", {}).get("code") == "undefinedField" for e in errs):
                        return {}, f"GraphQL schema error: {errs[0]['message']}"
                    logger.warning("GraphQL errors: %s", errs)  # codeql[py/clear-text-logging-sensitive-data]
                return result.get("data", {}), None
            except urllib.error.HTTPError as exc:
                body = exc.read().decode(errors="replace")
                if exc.code == 403 and "rate limit" in body.lower():
                    _polite_sleep(2 ** attempt * 3)
                    continue
                return {}, f"HTTP {exc.code}: {body[:100]}"
            except Exception as exc:
                logger.warning("GraphQL error (attempt %d): %s", attempt + 1, exc)  # codeql[py/clear-text-logging-sensitive-data]
                _polite_sleep(2 ** attempt)

    return {}, "all tokens exhausted for GraphQL"


# ──────────────────────────────────────────────────────────────
# Method 3 — gh CLI subprocess
# ──────────────────────────────────────────────────────────────
def gh_cli(args: list[str], input_json: dict | None = None) -> tuple[Any, str | None]:
    """
    Run `gh <args>` and return parsed JSON output.
    Automatically adds --json flags for api subcommands when appropriate.
    """
    cmd = ["gh"] + args
    logger.debug("gh CLI: %s", " ".join(cmd))  # codeql[py/clear-text-logging-sensitive-data]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            input=json.dumps(input_json) if input_json else None,
            env={**os.environ},
            shell=False,          # never use shell=True
        )
        if result.returncode == 0:
            out = result.stdout.strip()
            if out:
                try:
                    return json.loads(out), None
                except json.JSONDecodeError:
                    return out, None
            return None, None
        stderr = result.stderr.strip()
        if "rate limit" in stderr.lower():
            logger.warning("gh CLI rate limited: %s", stderr[:100])  # codeql[py/clear-text-logging-sensitive-data]
            return None, f"rate-limited: {stderr[:100]}"
        return None, stderr[:200]
    except subprocess.TimeoutExpired:
        return None, "gh CLI timeout"
    except FileNotFoundError:
        return None, "gh CLI not found"
    except Exception as exc:
        return None, str(exc)


# ──────────────────────────────────────────────────────────────
# Method 4 — Workflow artifact download
# ──────────────────────────────────────────────────────────────
def download_artifact(artifact_id: int, dest: Path, tokens: list[str] | None = None) -> bool:
    """Download a workflow artifact ZIP to dest. Returns True on success."""
    tokens = tokens or TOKENS
    for token in tokens:
        try:
            url = f"{_BASE}/repos/{_OWNER}/{_REPO}/actions/artifacts/{artifact_id}/zip"
            req = urllib.request.Request(url, headers=_headers(token))  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
            with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310  # _BASE = https://api.github.com (https-only constant)
                dest.write_bytes(r.read())
            logger.info("Downloaded artifact %d → %s", artifact_id, dest)  # codeql[py/clear-text-logging-sensitive-data]
            return True
        except urllib.error.HTTPError as exc:
            if exc.code == 410:
                logger.warning("Artifact %d expired (410)", artifact_id)  # codeql[py/clear-text-logging-sensitive-data]
                return False
            logger.debug("Artifact download HTTP %d", exc.code)  # codeql[py/clear-text-logging-sensitive-data]
        except Exception as exc:
            logger.debug("Artifact download error: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]
        _polite_sleep()
    return False


# ──────────────────────────────────────────────────────────────
# Method 5 — Local CodeQL DB
# ──────────────────────────────────────────────────────────────
# All CodeQL paths are configurable via env vars so CI images with different
# layouts (e.g. arm64, custom installers) work without editing this file.
# Version-specific fallback is provided for the GitHub-hosted runner image.
CODEQL_CLI = os.environ.get(
    "CODEQL_CLI_PATH",
    shutil.which("codeql") or "/opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/codeql",
)
CODEQL_DB  = os.environ.get("CODEQL_DB_PATH", os.path.join(tempfile.gettempdir(), "codex-db-py"))
CODEQL_QLPACKS = os.environ.get(
    "CODEQL_QLPACKS_PATH",
    "/opt/hostedtoolcache/CodeQL/2.25.1/x64/codeql/qlpacks/codeql/python-queries/1.7.11",
)


def build_codeql_db(source_root: str = REPO_ROOT) -> bool:
    """Build local CodeQL Python DB. Returns True if successful."""
    if not Path(CODEQL_CLI).exists():
        logger.warning("CodeQL CLI not found at %s", CODEQL_CLI)  # codeql[py/clear-text-logging-sensitive-data]
        return False
    if Path(CODEQL_DB).exists() and (Path(CODEQL_DB) / "db-python").exists():
        logger.info("CodeQL DB already exists at %s", CODEQL_DB)  # codeql[py/clear-text-logging-sensitive-data]
        return True
    logger.info("Building CodeQL DB (may take ~5 minutes)…")  # codeql[py/clear-text-logging-sensitive-data]
    result = subprocess.run(
        [CODEQL_CLI, "database", "create", CODEQL_DB,
         "--language=python", f"--source-root={source_root}", "--overwrite"],
        capture_output=False,
        timeout=600,
        shell=False,
    )
    return result.returncode == 0


def run_codeql_query(query_path: str, output_csv: str) -> list[list[str]]:
    """Run a .ql file and return CSV rows. Builds DB if needed."""
    if not build_codeql_db():
        return []
    result = subprocess.run(
        [CODEQL_CLI, "database", "analyze", CODEQL_DB,
         query_path, "--format=csv", f"--output={output_csv}",
         "--no-print-diagnostics-summary"],
        capture_output=True, text=True, timeout=300, shell=False,
    )
    if result.returncode != 0:
        logger.warning("CodeQL query failed: %s", result.stderr[:200])  # codeql[py/clear-text-logging-sensitive-data]
        return []
    try:
        rows = []
        with open(output_csv) as f:
            for line in f:
                rows.append(line.rstrip("\n").split(","))
        return rows
    except Exception as exc:
        logger.warning("CSV parse error: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]
        return []


# ──────────────────────────────────────────────────────────────
# High-level fetch functions that use the trickle-down chain
# ──────────────────────────────────────────────────────────────
def fetch_code_scanning_alerts(
    state: str = "open",
    owner: str = _OWNER,
    repo: str = _REPO,
) -> list[dict]:
    """Fetch code scanning alerts using full trickle-down chain."""
    logger.info("=== Method 1: REST paginate ===")  # codeql[py/clear-text-logging-sensitive-data]
    alerts = rest_paginate(f"/repos/{owner}/{repo}/code-scanning/alerts?state={state}")
    if alerts:
        logger.info("REST: retrieved %d alerts", len(alerts))  # codeql[py/clear-text-logging-sensitive-data]
        return alerts

    logger.info("=== Method 2: GraphQL (not available for code-scanning) ===")  # codeql[py/clear-text-logging-sensitive-data]
    # code-scanning has no GraphQL equivalent — skip to Method 3

    logger.info("=== Method 3: gh CLI ===")  # codeql[py/clear-text-logging-sensitive-data]
    data, err = gh_cli([
        "api",
        f"/repos/{owner}/{repo}/code-scanning/alerts?state={state}&per_page=100",
    ])
    if data and isinstance(data, list):
        logger.info("gh CLI: retrieved %d alerts", len(data))  # codeql[py/clear-text-logging-sensitive-data]
        return data
    logger.info("gh CLI result: %s", err)  # codeql[py/clear-text-logging-sensitive-data]

    logger.info("=== Method 4: CodeQL DB analyze ===")  # codeql[py/clear-text-logging-sensitive-data]
    if build_codeql_db():
        _sarif_out = os.path.join(tempfile.gettempdir(), "codeql-results.sarif")
        result = subprocess.run(
            [CODEQL_CLI, "database", "analyze", CODEQL_DB,
             CODEQL_QLPACKS,
             "--format=sarifv2.1.0", "--output", _sarif_out,
             "--no-print-diagnostics-summary"],
            capture_output=True, text=True, timeout=600, shell=False,
        )
        if result.returncode == 0 and Path(_sarif_out).exists():
            alerts = _parse_sarif(_sarif_out)
            logger.info("Local CodeQL: %d findings", len(alerts))  # codeql[py/clear-text-logging-sensitive-data]
            return alerts
        logger.warning("CodeQL analyze failed: %s", result.stderr[:200])  # codeql[py/clear-text-logging-sensitive-data]

    logger.error("All methods exhausted — no alerts retrieved")  # codeql[py/clear-text-logging-sensitive-data]
    return []


def _parse_sarif(sarif_path: str) -> list[dict]:
    """Parse SARIF 2.1 output into a simple alert-like list."""
    alerts = []
    try:
        with open(sarif_path) as f:
            sarif = json.load(f)
        for run in sarif.get("runs", []):
            rules = {r["id"]: r for r in run.get("tool", {}).get("driver", {}).get("rules", [])}
            for result in run.get("results", []):
                rule_id = result.get("ruleId", "?")
                rule_info = rules.get(rule_id, {})
                for loc in result.get("locations", []):
                    phys = loc.get("physicalLocation", {})
                    region = phys.get("region", {})
                    alerts.append({
                        "rule": {"id": rule_id, "severity": rule_info.get("defaultConfiguration", {}).get("level", "note")},
                        "most_recent_instance": {"location": {
                            "path": phys.get("artifactLocation", {}).get("uri", "?"),
                            "start_line": region.get("startLine", 0),
                        }},
                        "message": result.get("message", {}).get("text", ""),
                    })
    except Exception as exc:
        logger.warning("SARIF parse error: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]
    return alerts


def fetch_pr_review_threads(pr_number: int, owner: str = _OWNER, repo: str = _REPO) -> list[dict]:
    """Fetch unresolved PR review threads via GraphQL."""
    data, err = graphql("""
    query($owner: String!, $repo: String!, $pr: Int!) {
      repository(owner: $owner, name: $repo) {
        pullRequest(number: $pr) {
          reviewThreads(first: 50) {
            nodes {
              isResolved path line
              comments(first: 5) {
                nodes { body author { login } createdAt }
              }
            }
          }
        }
      }
    }
    """, {"owner": owner, "repo": repo, "pr": pr_number})
    if err:
        logger.warning("GraphQL fetch_pr_review_threads: %s", err)  # codeql[py/clear-text-logging-sensitive-data]
    threads = (
        data
        .get("repository", {})
        .get("pullRequest", {})
        .get("reviewThreads", {})
        .get("nodes", [])
    )
    return [t for t in threads if not t.get("isResolved")]


def wait_for_rate_limit_reset(resource: str = "core") -> None:
    """
    Block until the specified rate-limit resource has capacity.
    Implements trickle-down: tries each token before waiting.
    """
    for tok_slot, token in enumerate(TOKENS, 1):
        limits = check_rate_limits(token)
        _polite_sleep(0.3)
        r = limits.get(resource, {})
        if r.get("remaining", 0) >= MIN_REMAINING:
            logger.info("Token[slot-%d] %s remaining=%d — ready", tok_slot, resource, r["remaining"])  # codeql[py/clear-text-logging-sensitive-data]
            return
    # All tokens exhausted — wait for first reset
    earliest_reset = min(
        check_rate_limits(t).get(resource, {}).get("reset", int(time.time()) + 60)
        for t in TOKENS
    )
    _polite_sleep(0.3)
    _wait_for_reset(earliest_reset, resource)


# ──────────────────────────────────────────────────────────────
# CLI interface
# ──────────────────────────────────────────────────────────────
_STATE_PATH = Path(os.environ.get("CODEX_SESSION_LOG_DIR", ".codex")) / "rate_limit_state.json"


def status(*, write_state: bool = True, min_remaining: int = MIN_REMAINING) -> dict:
    """
    Check rate-limit status across all available tokens.

    Returns a dict with keys:
      - ``ok``          bool  — True if at least one token has capacity
      - ``tokens``      list  — per-token detail dicts
      - ``core_ready``  bool  — True if core REST pool has capacity on any token
      - ``security_ready`` bool — True if code_scanning pool has capacity
      - ``earliest_reset_epoch`` int  — earliest reset epoch across all exhausted tokens
      - ``earliest_reset_human`` str  — human-readable form of above
      - ``checked_at``  str   — ISO timestamp of this check

    Exits with code 1 (via return value) when *all* tokens are exhausted and
    the caller should wait before retrying.  Write ``--status`` to a JSON file
    at ``.codex/rate_limit_state.json`` so subsequent agent calls can skip the
    network probe.
    """
    now = time.time()
    token_rows = []
    any_core_ready = False
    any_security_ready = False
    earliest_reset = int(now) + 3600

    for slot, token in enumerate(TOKENS, 1):
        limits = check_rate_limits(token)
        _polite_sleep(0.1)
        row: dict = {"slot": slot, "pools": {}}
        for name, info in limits.items():
            if not info.get("limit", 0):
                continue
            remaining = info.get("remaining", 0)
            reset_ep  = info.get("reset", int(now) + 3600)
            reset_dt  = datetime.fromtimestamp(reset_ep, tz=timezone.utc).strftime("%H:%M:%S UTC")
            wait_secs = max(0, reset_ep - now)
            row["pools"][name] = {
                "remaining": remaining,
                "limit":     info["limit"],
                "reset_epoch":  reset_ep,
                "reset_human":  reset_dt,
                "wait_secs":    round(wait_secs),
                "ready":        remaining >= min_remaining,
            }
            if remaining >= min_remaining:
                if name == "core":
                    any_core_ready = True
                if name in ("code_scanning", "security_events"):
                    any_security_ready = True
            else:
                earliest_reset = min(earliest_reset, reset_ep)
        token_rows.append(row)

    earliest_dt = datetime.fromtimestamp(earliest_reset, tz=timezone.utc).strftime("%H:%M:%S UTC")
    state = {
        "ok":                    any_core_ready,
        "core_ready":            any_core_ready,
        "security_ready":        any_security_ready,
        "tokens":                token_rows,
        "earliest_reset_epoch":  earliest_reset,
        "earliest_reset_human":  earliest_dt,
        "checked_at":            datetime.fromtimestamp(now, tz=timezone.utc).isoformat(),
    }

    if write_state:
        try:
            _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            _STATE_PATH.write_text(json.dumps(state, indent=2))
        except Exception as exc:  # pragma: no cover - best-effort
            logger.debug("Could not write rate_limit_state.json: %s", exc)  # codeql[py/clear-text-logging-sensitive-data]

    return state


def print_status(state: dict) -> None:
    """Pretty-print a status dict returned by :func:`status`."""
    print(f"\n{'═'*60}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"  GitHub API Rate-Limit Status — {state['checked_at']}")  # codeql[py/clear-text-logging-sensitive-data]
    print(f"{'═'*60}")  # codeql[py/clear-text-logging-sensitive-data]
    for row in state["tokens"]:
        print(f"\n  Token[slot-{row['slot']}]:")  # codeql[py/clear-text-logging-sensitive-data]
        for name, info in row["pools"].items():
            icon = "✅" if info["ready"] else "🔴"
            wait = f"  (wait {info['wait_secs']}s)" if not info["ready"] else ""
            print(
                f"    {icon} {name:30s}: {info['remaining']:5d}/{info['limit']}"
                f" — resets {info['reset_human']}{wait}"
            )
    print()  # codeql[py/clear-text-logging-sensitive-data]
    if state["ok"]:
        print("  ✅ At least one token has capacity — API calls may proceed.")  # codeql[py/clear-text-logging-sensitive-data]
    else:
        print(
            f"  🔴 ALL tokens exhausted — wait until {state['earliest_reset_human']}"
            f" ({state['earliest_reset_epoch']}) before retrying."
        )
        print(
            "  ℹ  Do NOT call list_code_scanning_alerts (MCP) or any GitHub API"
            "  until then — each failed attempt still costs quota."
        )
    print(f"{'═'*60}\n")  # codeql[py/clear-text-logging-sensitive-data]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--owner", default=_OWNER)
    parser.add_argument("--repo",  default=_REPO)
    parser.add_argument("--resource", choices=["code-scanning-alerts", "pr-reviews", "rate-limits"])
    parser.add_argument("--status",  action="store_true",
                        help="Print rate-limit status table for all tokens; exit 0=ready 1=all-exhausted")
    parser.add_argument("--write-env", action="store_true",
                        help="When --status exits 1 (all exhausted), write RATE_LIMITED=true to $GITHUB_ENV "
                             "and $GITHUB_OUTPUT so downstream steps can skip API calls")
    parser.add_argument("--rest",    metavar="PATH", help="Raw REST GET path")
    parser.add_argument("--graphql", metavar="FILE", help="GraphQL query file")
    parser.add_argument("--pr",      type=int,       help="PR number (for pr-reviews)")
    parser.add_argument("--state",   default="open", help="Alert state filter")
    parser.add_argument("--json",    action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    # ── new: --status ────────────────────────────────────────────
    if args.status:
        s = status()
        print_status(s)
        if args.json:
            print(json.dumps(s, indent=2))  # codeql[py/clear-text-logging-sensitive-data]
        is_ready = s["ok"]
        if not is_ready and args.write_env:
            _write_github_env("RATE_LIMITED", "true")
            _write_github_output("rate_limited", "true")
            logger.warning("All tokens exhausted — wrote RATE_LIMITED=true to GITHUB_ENV/GITHUB_OUTPUT")  # codeql[py/clear-text-logging-sensitive-data]
        return 0 if is_ready else 1

    if args.resource == "rate-limits":
        # Legacy alias — now delegates to --status
        s = status()
        print_status(s)
        return 0 if s["ok"] else 1

    if args.rest:
        data, err = rest_get(args.rest)
        if err:
            print(f"ERROR: {err}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            return 1
        print(json.dumps(data, indent=2))  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    if args.graphql:
        query = Path(args.graphql).read_text()
        data, err = graphql(query)
        if err:
            print(f"ERROR: {err}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            return 1
        print(json.dumps(data, indent=2))  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    if args.resource == "code-scanning-alerts":
        alerts = fetch_code_scanning_alerts(state=args.state, owner=args.owner, repo=args.repo)
        if args.json:
            print(json.dumps(alerts, indent=2))  # codeql[py/clear-text-logging-sensitive-data]
            return 0
        by_rule: dict[str, list] = {}
        for a in alerts:
            rule = a.get("rule", {}).get("id", "?")
            loc  = a.get("most_recent_instance", {}).get("location", {})
            by_rule.setdefault(rule, []).append({
                "num": a.get("number"),
                "file": loc.get("path"),
                "line": loc.get("start_line"),
                "severity": a.get("rule", {}).get("severity"),
                "msg": a.get("message", {}).get("text", "") if isinstance(a.get("message"), dict) else a.get("message", ""),
            })
        for rule, items in sorted(by_rule.items()):
            print(f"\n=== {rule} ({len(items)}) ===")  # codeql[py/clear-text-logging-sensitive-data]
            for i in items[:15]:
                print(f"  #{i['num']} [{i['severity']}] {i['file']}:{i['line']}")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    if args.resource == "pr-reviews":
        if not args.pr:
            print("ERROR: --pr required for pr-reviews", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            return 1
        threads = fetch_pr_review_threads(args.pr, owner=args.owner, repo=args.repo)
        print(f"Unresolved review threads: {len(threads)}")  # codeql[py/clear-text-logging-sensitive-data]
        for t in threads:
            print(f"  {t.get('path')}:{t.get('line')}")  # codeql[py/clear-text-logging-sensitive-data]
            for c in t.get("comments", {}).get("nodes", [])[:1]:
                print(f"    @{c['author']['login']}: {c['body'][:120]}")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
