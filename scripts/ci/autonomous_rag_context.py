#!/usr/bin/env python3
"""
autonomous_rag_context.py — Autonomous RAG Context Builder for Copilot Cloud Agent
═══════════════════════════════════════════════════════════════════════════════════

Runs as part of copilot-setup-steps.yml immediately after session_access_probe.py.

What it does (in order)
───────────────────────
1. Load access manifest (.codex/session_access_manifest.json) written by
   session_access_probe.py — knows which methods are live and their rate limits.

2. Pull FRESH session context using the trickle-down chain:
     a. REST API  — PR details, open review threads, CI check run statuses
     b. GraphQL   — richer PR/issue/discussion data if REST is exhausted
     c. gh CLI    — fallback for any REST/GraphQL gap
     d. Local FS  — .codex/, git log, CHANGELOG as offline fallback

3. Query existing RAG index (src/codex/rag/indexer.py FAISS store) for
   patterns matching the session's context (open PR, failing checks, branch).

4. Compress context via src/codex/cognitive/context_compressor.py to fit
   within the agent's token budget (default 128 k tokens).

5. Inject result into .codex/session_context_latest.md  (overwrite)
                       GITHUB_STEP_SUMMARY                (append)
                       GITHUB_ENV                         (export vars)
                       .codex/rag/session_delta.json      (RAG freshness delta)

6. Incremental RAG index update — re-embeds only files changed since last
   session (git diff HEAD~1 --name-only) to keep the index fresh without a
   full rebuild.

7. Emit ACCESS_STRATEGY env var with the ordered list of methods to use for
   the rest of the session (e.g. "graphql,gh_cli,codeql_local").

Architecture
────────────
                 ┌─────────────────────────────┐
                 │   copilot-setup-steps.yml    │
                 │  (step: Autonomous RAG ctx)  │
                 └────────────┬────────────────┘
                              │ runs
                 ┌────────────▼────────────────────────────────────────┐
                 │         autonomous_rag_context.py                    │
                 │                                                      │
                 │  AccessManifest ──► TrickleDownFetcher               │
                 │        │                  │                          │
                 │        │          ┌───────▼──────────────┐          │
                 │        │          │  GitHub Context Pull  │          │
                 │        │          │  (PR/CI/commits/PRs)  │          │
                 │        │          └───────┬──────────────┘          │
                 │        │                  │                          │
                 │        │          ┌───────▼──────────────┐          │
                 │        │          │  LocalContextHarvest  │          │
                 │        │          │  (.codex/ + git log)  │          │
                 │        │          └───────┬──────────────┘          │
                 │        │                  │                          │
                 │        └──────────────────►  RAGContextMerger        │
                 │                           │  (FAISS query + merge)   │
                 │                           └───────┬──────────────┘  │
                 │                                   │                  │
                 │                         ContextCompressor            │
                 │                         (token budget enforcement)   │
                 │                                   │                  │
                 │                    ┌──────────────▼──────────┐      │
                 │                    │  Output sinks            │      │
                 │                    │  • session_context.md    │      │
                 │                    │  • GITHUB_ENV            │      │
                 │                    │  • STEP_SUMMARY          │      │
                 │                    │  • rag/session_delta.json│      │
                 │                    └─────────────────────────┘      │
                 └─────────────────────────────────────────────────────┘

Usage
─────
  python3 scripts/ci/autonomous_rag_context.py               # normal run
  python3 scripts/ci/autonomous_rag_context.py --offline     # no network calls
  python3 scripts/ci/autonomous_rag_context.py --pr 4204     # explicit PR
  python3 scripts/ci/autonomous_rag_context.py --dry-run     # no writes
  python3 scripts/ci/autonomous_rag_context.py --rebuild-rag # force full re-embed
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logger = logging.getLogger("rag_ctx")

# ── Repo constants ─────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
CODEX_DIR   = REPO_ROOT / ".codex"
MANIFEST    = CODEX_DIR / "session_access_manifest.json"
CTX_OUT     = CODEX_DIR / "session_context_latest.md"
RAG_DELTA   = CODEX_DIR / "rag" / "session_delta.json"
ACCESS_STRATEGY_FILE = CODEX_DIR / "session_access_strategy.json"

OWNER = "Aries-Serpent"
REPO  = "_codex_"
BASE  = "https://api.github.com"

# Tuning — all overridable via env / repo variables set by pending_var_updates.json.
#: Max .py files to re-embed per session in incremental RAG update.
MAX_FILES_PER_RAG_UPDATE: int = int(os.environ.get("CODEX_RAG_MAX_FILES_PER_SESSION", "20"))
#: Max file size in bytes to pass to the RAG indexer (skip huge generated files).
MAX_FILE_SIZE_FOR_RAG: int   = int(os.environ.get("CODEX_RAG_MAX_FILE_BYTES", "500000"))
#: Polite sleep between GitHub API calls (seconds) — mirrors GH_TRICKLE_POLITE_SLEEP.
POLITE_SLEEP: float          = float(os.environ.get("GH_TRICKLE_POLITE_SLEEP", "0.4"))

# ── Token discovery (mirrors session_access_probe.py) ─────────────────────────
def _tokens() -> list[tuple[str, str]]:
    """Return [(value, var_name)] for all available tokens."""
    slots = [
        "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY", "CODEX_ADMIN_KEY",
        "AGENT_GITHUB_TOKEN", "GITHUB_COPILOT_API_TOKEN", "GITHUB_TOKEN", "GH_TOKEN",
    ]
    seen: set[str] = set()
    result = []
    for var in slots:
        val = os.environ.get(var, "")
        if val and val not in seen:
            seen.add(val)
            result.append((val, var))
    return result

TOKENS = _tokens()


# ─────────────────────────────────────────────────────────────────────────────
# Access manifest reader
# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class AccessStrategy:
    """Ordered list of methods to try, derived from access manifest."""
    methods: list[str]                       # e.g. ["rest", "graphql", "gh_cli"]
    rest_available: bool      = False
    rest_remaining: int       = 0
    rest_reset_epoch: int     = 0
    graphql_available: bool   = False
    graphql_remaining: int    = 0
    gh_cli_available: bool    = False
    codeql_available: bool    = False
    best_token_var: str       = ""
    open_prs: list[int]       = field(default_factory=list)
    branch: str               = ""

    @classmethod
    def from_manifest(cls) -> "AccessStrategy":
        if MANIFEST.exists():
            try:
                data = json.loads(MANIFEST.read_text())
                methods: list[str] = []
                rest_rem = data.get("best_token_rest_remaining", 0)
                gql_rem  = data.get("graphql_remaining", 0)
                if rest_rem >= 100:
                    methods.append("rest")
                if gql_rem >= 100:
                    methods.append("graphql")
                if data.get("gh_cli", {}).get("available"):
                    methods.append("gh_cli")
                if data.get("codeql_cli", {}).get("available"):
                    methods.append("codeql_local")
                if not methods:
                    methods = ["local_fs"]  # ultimate fallback
                return cls(
                    methods=methods,
                    rest_available=data.get("rest", {}).get("available", False),
                    rest_remaining=rest_rem,
                    rest_reset_epoch=data.get("rest_reset_epoch", 0),
                    graphql_available=data.get("graphql", {}).get("available", False),
                    graphql_remaining=gql_rem,
                    gh_cli_available=data.get("gh_cli", {}).get("available", False),
                    codeql_available=data.get("codeql_cli", {}).get("available", False),
                    best_token_var=data.get("best_token_var", ""),
                    open_prs=data.get("open_prs", []),
                    branch=data.get("branch", ""),
                )
            except Exception as exc:
                logger.warning("Could not load access manifest: %s", exc)
        # Probe inline if manifest missing
        logger.info("Access manifest not found — running inline token check")
        return cls._inline_probe()

    @classmethod
    def _inline_probe(cls) -> "AccessStrategy":
        methods: list[str] = []
        rest_rem = 0
        gql_rem  = 0
        best_var = ""
        for token, var in TOKENS:
            try:
                req = urllib.request.Request(f"{BASE}/rate_limit",  # noqa: S310  # BASE = https://api.github.com (https-only constant)
                    headers={"Authorization": f"Bearer {token}",
                             "Accept": "application/vnd.github+json"})
                with urllib.request.urlopen(req, timeout=8) as r:  # noqa: S310  # BASE = https://api.github.com (https-only constant)
                    d = json.load(r)
                core = d.get("resources", {}).get("core", {})
                gql  = d.get("resources", {}).get("graphql", {})
                if core.get("remaining", 0) > rest_rem:
                    rest_rem = core["remaining"]
                    best_var = var
                if gql.get("remaining", 0) > gql_rem:
                    gql_rem = gql["remaining"]
                time.sleep(0.4)
            except Exception:
                continue
        if rest_rem >= 10:
            methods.append("rest")
        if gql_rem >= 10:
            methods.append("graphql")
        if not methods:
            methods = ["local_fs"]
        return cls(methods=methods, rest_available=rest_rem >= 10,
                   rest_remaining=rest_rem, graphql_remaining=gql_rem,
                   best_token_var=best_var)


# ─────────────────────────────────────────────────────────────────────────────
# Trickle-down GitHub context fetcher
# ─────────────────────────────────────────────────────────────────────────────
class TrickleDownFetcher:
    """Fetch GitHub context using the priority chain from the access strategy."""

    POLITE = POLITE_SLEEP  # mirrors GH_TRICKLE_POLITE_SLEEP env var

    def __init__(self, strategy: AccessStrategy, pr_number: int | None = None) -> None:
        self.strategy = strategy
        self.pr_number = pr_number or (strategy.open_prs[0] if strategy.open_prs else None)
        self._token_map = {var: tok for tok, var in TOKENS}

    def _best_token(self) -> str | None:
        var = self.strategy.best_token_var
        if var and var in self._token_map:
            return self._token_map[var]
        return TOKENS[0][0] if TOKENS else None

    def _headers(self, token: str) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _rest_get(self, path: str) -> Any:
        """GET with polite sleep and error handling."""
        if "rest" not in self.strategy.methods:
            return None
        token = self._best_token()
        if not token:
            return None
        time.sleep(self.POLITE)
        try:
            req = urllib.request.Request(f"{BASE}{path}", headers=self._headers(token))  # noqa: S310  # BASE = https://api.github.com (https-only constant)
            with urllib.request.urlopen(req, timeout=15) as r:  # noqa: S310  # BASE = https://api.github.com (https-only constant)
                return json.load(r)
        except urllib.error.HTTPError as exc:
            if exc.code == 403:
                logger.warning("REST 403 on %s — switching to next method", path[:60])
                if "rest" in self.strategy.methods:
                    self.strategy.methods.remove("rest")
            elif exc.code == 404:
                logger.debug("REST 404: %s", path[:60])
            return None
        except Exception as exc:
            logger.debug("REST error on %s: %s", path[:60], exc)
            return None

    def _graphql(self, query: str, variables: dict | None = None) -> dict:
        """Execute GraphQL query with polite sleep."""
        if "graphql" not in self.strategy.methods:
            return {}
        token = self._best_token()
        if not token:
            return {}
        time.sleep(self.POLITE)
        try:
            payload = json.dumps({"query": query, **({"variables": variables} if variables else {})}).encode()
            req = urllib.request.Request(  # noqa: S310  # BASE = https://api.github.com (https-only constant)
                f"{BASE}/graphql", data=payload,
                headers={**self._headers(token), "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=15) as r:  # noqa: S310  # BASE = https://api.github.com (https-only constant)
                result = json.load(r)
            return result.get("data", {})
        except Exception as exc:
            logger.debug("GraphQL error: %s", exc)
            return {}

    def _gh_cli(self, args: list[str]) -> Any:
        """Run gh CLI command."""
        if "gh_cli" not in self.strategy.methods:
            return None
        try:
            r = subprocess.run(["gh"] + args, capture_output=True, text=True,
                               timeout=20, shell=False)
            if r.returncode == 0:
                try:
                    return json.loads(r.stdout)
                except json.JSONDecodeError:
                    return r.stdout.strip()
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)
        return None

    # ── Fetch methods ──────────────────────────────────────────────────────
    def fetch_pr_context(self) -> dict:
        """Fetch PR title, body, status, failing checks, unresolved threads."""
        if not self.pr_number:
            return {}

        ctx: dict = {"pr_number": self.pr_number}

        # Try REST first
        pr = self._rest_get(f"/repos/{OWNER}/{REPO}/pulls/{self.pr_number}")
        if pr:
            ctx.update({
                "title":  pr.get("title", ""),
                "state":  pr.get("state", ""),
                "head_sha": pr.get("head", {}).get("sha", "")[:12],
                "base_branch": pr.get("base", {}).get("ref", ""),
                "head_branch": pr.get("head", {}).get("ref", ""),
                "mergeable": pr.get("mergeable"),
                "draft": pr.get("draft", False),
            })
            # Check runs for head SHA
            sha = pr.get("head", {}).get("sha", "")
            if sha:
                checks = self._rest_get(
                    f"/repos/{OWNER}/{REPO}/commits/{sha}/check-runs?per_page=50",
                )
                if checks and isinstance(checks, dict):
                    runs = checks.get("check_runs", [])
                    failing = [
                        {"name": r["name"], "conclusion": r.get("conclusion"), "status": r.get("status")}
                        for r in runs if r.get("conclusion") in ("failure", "timed_out", "cancelled")
                    ]
                    ctx["failing_checks"] = failing
                    ctx["total_checks"]   = len(runs)
        else:
            # Fall back to GraphQL
            data = self._graphql("""
            query($owner: String!, $repo: String!, $pr: Int!) {
              repository(owner: $owner, name: $repo) {
                pullRequest(number: $pr) {
                  title state isDraft mergeable
                  headRefName baseRefName
                  headRefOid
                  commits(last: 1) { nodes { commit { statusCheckRollup {
                    state contexts(last: 20) { nodes {
                      ... on CheckRun { name conclusion status }
                    } }
                  } } } }
                  reviewThreads(first: 20) { nodes {
                    isResolved path
                    comments(first: 1) { nodes { body author { login } } }
                  } }
                }
              }
            }""", {"owner": OWNER, "repo": REPO, "pr": self.pr_number})
            pr_data = data.get("repository", {}).get("pullRequest", {}) if data else {}
            if pr_data:
                ctx.update({
                    "title":  pr_data.get("title", ""),
                    "state":  pr_data.get("state", ""),
                    "draft":  pr_data.get("isDraft", False),
                    "head_branch": pr_data.get("headRefName", ""),
                    "base_branch": pr_data.get("baseRefName", ""),
                    "head_sha": pr_data.get("headRefOid", "")[:12],
                })
                # Unresolved review threads
                threads = pr_data.get("reviewThreads", {}).get("nodes", [])
                ctx["unresolved_threads"] = [
                    {"path": t["path"],
                     "comment": t["comments"]["nodes"][0]["body"][:120] if t["comments"]["nodes"] else ""}
                    for t in threads if not t.get("isResolved")
                ]
            elif "gh_cli" in self.strategy.methods:
                gh = self._gh_cli(["pr", "view", str(self.pr_number),
                                   "--json", "title,state,headRefName,isDraft"])
                if gh and isinstance(gh, dict):
                    ctx.update(gh)

        return ctx

    def fetch_recent_ci_failures(self) -> list[dict]:
        """Fetch most recent CI failure patterns from workflow runs."""
        failures: list[dict] = []
        data = self._rest_get(
            f"/repos/{OWNER}/{REPO}/actions/runs?status=failure&per_page=5",
        )
        if data and isinstance(data, dict):
            for run in data.get("workflow_runs", []):
                failures.append({
                    "workflow": run.get("name", ""),
                    "conclusion": run.get("conclusion", ""),
                    "branch": run.get("head_branch", ""),
                    "updated_at": run.get("updated_at", ""),
                    "run_id": run.get("id"),
                })
        return failures[:5]

    def fetch_recent_commits(self, n: int = 10) -> list[dict]:
        """Fetch recent commits on the current branch."""
        branch = self.strategy.branch or os.environ.get("GITHUB_HEAD_REF", "")
        if not branch:
            return _local_git_log(n)
        data = self._rest_get(
            f"/repos/{OWNER}/{REPO}/commits?sha={branch}&per_page={n}",
        )
        if data and isinstance(data, list):
            return [
                {"sha": c["sha"][:8], "message": c["commit"]["message"].splitlines()[0][:80],
                 "author": c["commit"]["author"]["name"], "date": c["commit"]["author"]["date"]}
                for c in data
            ]
        return _local_git_log(n)


# ─────────────────────────────────────────────────────────────────────────────
# Local filesystem context harvester
# ─────────────────────────────────────────────────────────────────────────────
def _local_git_log(n: int = 10) -> list[dict]:
    """Read git log from local repo."""
    try:
        r = subprocess.run(
            ["git", "--no-pager", "log", f"-{n}", "--format=%H|%s|%an|%ai"],
            capture_output=True, text=True, timeout=10, cwd=REPO_ROOT, shell=False,
        )
        result = []
        for line in r.stdout.strip().splitlines():
            parts = line.split("|", 3)
            if len(parts) == 4:
                result.append({"sha": parts[0][:8], "message": parts[1][:80],
                               "author": parts[2], "date": parts[3][:19]})
        return result
    except Exception:
        return []


def _changed_files_since_last_session() -> list[str]:
    """Return list of .py files changed in last commit (for incremental RAG update)."""
    try:
        r = subprocess.run(
            ["git", "--no-pager", "diff", "--name-only", "HEAD~1", "HEAD"],
            capture_output=True, text=True, timeout=10, cwd=REPO_ROOT, shell=False,
        )
        return [f for f in r.stdout.strip().splitlines() if f.endswith(".py")]
    except Exception:
        return []


def _harvest_local_context() -> dict:
    """Harvest key context from local .codex/ and git."""
    ctx: dict = {}

    # agent_context.json — live repo variables
    agent_ctx = CODEX_DIR / "agent_context.json"
    if agent_ctx.exists():
        try:
            ctx["repo_variables"] = json.loads(agent_ctx.read_text())
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    # PDA loop state
    pda = CODEX_DIR / "aftermath" / "pda_iterations.jsonl"
    if pda.exists():
        try:
            lines = pda.read_text().strip().splitlines()
            last_5 = [json.loads(line) for line in lines[-5:] if line.strip()]
            ctx["pda_last_5"] = last_5
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    # Recent session context
    if CTX_OUT.exists():
        try:
            ctx["prev_session_context"] = CTX_OUT.read_text()[:2000]
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    # Git log
    ctx["recent_commits"] = _local_git_log(8)
    ctx["changed_files"]  = _changed_files_since_last_session()

    # CODEBASE_AGENCY_POLICY excerpt
    policy = CODEX_DIR / "CODEBASE_AGENCY_POLICY.md"
    if policy.exists():
        try:
            ctx["policy_excerpt"] = policy.read_text()[:800]
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    # AGENTIC_REPO_STATE
    state = CODEX_DIR / "AGENTIC_REPO_STATE.md"
    if state.exists():
        try:
            ctx["agentic_state"] = state.read_text()[:600]
        except Exception:
            logger.debug("Suppressed exception", exc_info=True)

    return ctx


# ─────────────────────────────────────────────────────────────────────────────
# RAG index query (wraps src/codex/rag/retriever.py gracefully)
# ─────────────────────────────────────────────────────────────────────────────
def _query_rag_index(query: str, top_k: int = 5) -> list[dict]:
    """
    Query the existing FAISS RAG index for relevant patterns.
    Gracefully degrades to [] if the index or dependencies are unavailable.
    """
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from codex.rag.retriever import RAGRetriever  # type: ignore[import]
        retriever = RAGRetriever()
        results = retriever.retrieve(query, top_k=top_k)
        return [{"text": r.text[:300], "score": r.score, "source": r.source} for r in results]
    except ImportError:
        logger.debug("RAGRetriever not available — skipping index query")
    except Exception as exc:
        logger.debug("RAG query failed: %s", exc)
    return []


def _incremental_rag_update(changed_files: list[str]) -> dict:
    """
    Re-embed only the files changed since last session.
    Returns {"updated": N, "skipped": M, "errors": [...]}.
    """
    if not changed_files:
        return {"updated": 0, "skipped": 0, "errors": []}

    result = {"updated": 0, "skipped": 0, "errors": []}
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from codex.rag.indexer import RAGIndexer  # type: ignore[import]
        indexer = RAGIndexer()
        for rel_path in changed_files[:MAX_FILES_PER_RAG_UPDATE]:
            abs_path = REPO_ROOT / rel_path
            if abs_path.exists() and abs_path.stat().st_size < MAX_FILE_SIZE_FOR_RAG:
                try:
                    indexer.index_file(abs_path)
                    result["updated"] += 1
                except Exception as exc:
                    result["errors"].append(f"{rel_path}: {exc!s:.60}")
            else:
                result["skipped"] += 1
        indexer.save()
    except ImportError:
        logger.debug("RAGIndexer not available — skipping incremental update")
    except Exception as exc:
        logger.debug("RAG indexer error: %s", exc)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Context compressor (wraps src/codex/cognitive/context_compressor.py)
# ─────────────────────────────────────────────────────────────────────────────
def _compress_context(text: str, max_tokens: int = 3000) -> str:
    """
    Compress context to fit within token budget.
    Falls back to simple truncation if the compressor isn't available.
    """
    max_chars = max_tokens * 4  # ~4 chars/token
    if len(text) <= max_chars:
        return text
    try:
        sys.path.insert(0, str(REPO_ROOT / "src"))
        from codex.cognitive.context_compressor import ContextCompressor  # type: ignore[import]
        compressor = ContextCompressor()
        compressed = compressor.compress(text, max_tokens=max_tokens)
        return compressed.summary + "\n\nKey points:\n" + "\n".join(f"- {p}" for p in compressed.key_points)
    except Exception:
        logger.debug("Suppressed exception", exc_info=True)
    # Simple truncation with sentinel
    return text[:max_chars] + f"\n\n[TRUNCATED — original {len(text)} chars > {max_chars} limit]"


# ─────────────────────────────────────────────────────────────────────────────
# Context renderer
# ─────────────────────────────────────────────────────────────────────────────
def _render_context_md(
    strategy:  AccessStrategy,
    pr_ctx:    dict,
    ci_fails:  list[dict],
    commits:   list[dict],
    local_ctx: dict,
    rag_hits:  list[dict],
    rag_delta: dict,
) -> str:
    """Render the full session context as Markdown."""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines: list[str] = [
        f"# Session Context — {now}",
        f"**Branch:** `{strategy.branch or 'unknown'}`  "
        f"**PR:** {'#' + str(pr_ctx.get('pr_number')) if pr_ctx.get('pr_number') else 'none'}  "
        f"**Access:** `{', '.join(strategy.methods)}`",
        "",
        "## 🔌 Access Strategy",
        f"- Recommended method chain: `{' → '.join(strategy.methods)}`",
        f"- REST remaining: `{strategy.rest_remaining}` "
        f"({'✅' if strategy.rest_available else '❌'})  ",
        f"- GraphQL remaining: `{strategy.graphql_remaining}` "
        f"({'✅' if strategy.graphql_available else '❌'})  ",
        f"- gh CLI: {'✅' if strategy.gh_cli_available else '❌'}  ",
        f"- CodeQL CLI: {'✅' if strategy.codeql_available else '❌'}",
        "",
    ]

    if pr_ctx:
        lines += [
            f"## 📋 PR #{pr_ctx.get('pr_number')} — {pr_ctx.get('title', 'N/A')}",
            f"State: `{pr_ctx.get('state', '?')}`  Draft: `{pr_ctx.get('draft', False)}`  "
            f"Branch: `{pr_ctx.get('head_branch', '?')}` → `{pr_ctx.get('base_branch', '?')}`",
            "",
        ]
        threads = pr_ctx.get("unresolved_threads", [])
        if threads:
            lines.append(f"### ⚠️ {len(threads)} Unresolved Review Thread(s)")
            for t in threads[:5]:
                lines.append(f"- `{t['path']}` — {t['comment'][:100]}")
            lines.append("")
        failing = pr_ctx.get("failing_checks", [])
        if failing:
            lines.append(f"### ❌ {len(failing)} Failing CI Check(s)")
            for c in failing[:8]:
                lines.append(f"- `{c['name']}` ({c['conclusion']})")
            lines.append("")

    if ci_fails:
        lines.append("## 🚨 Recent CI Failures (last 5 runs)")
        for f in ci_fails:
            lines.append(f"- **{f['workflow']}** — `{f['conclusion']}` on `{f['branch']}` ({f['updated_at'][:10]})")
        lines.append("")

    if commits:
        lines.append("## 📝 Recent Commits")
        for c in commits[:8]:
            lines.append(f"- `{c['sha']}` {c['message']} — {c['author']} ({c.get('date', '')[:10]})")
        lines.append("")

    if rag_hits:
        lines.append("## 🧠 RAG Index — Relevant Patterns")
        for h in rag_hits:
            lines.append(f"- [{h.get('source', '?')}] (score={h.get('score', 0):.2f}): "
                         f"{h.get('text', '')[:120]}")
        lines.append("")

    if rag_delta.get("updated", 0) > 0:
        lines.append(
            f"## 🔄 RAG Index Delta\n"
            f"Re-embedded {rag_delta['updated']} changed file(s), "
            f"skipped {rag_delta.get('skipped', 0)}, "
            f"errors {len(rag_delta.get('errors', []))}",
        )
        lines.append("")

    rv = local_ctx.get("repo_variables", {})
    if rv:
        lines.append("## ⚙️ Repository Variables (live)")
        priority_vars = [
            "COPILOT_AGENT_AUTH_ENABLED", "COPILOT_AGENT_MAX_AUTONOMY_LEVEL",
            "COGNITIVE_BRAIN_SESSION_NUMBER", "CODEX_CI_FAILURE_RATE",
            "CODEX_CI_LAST_GREEN_SHA", "COPILOT_AGENT_FIREWALL_ENABLED",
        ]
        for k in priority_vars:
            v = rv.get(k)
            if v:
                lines.append(f"- `{k}` = `{v}`")
        lines.append("")

    pda = local_ctx.get("pda_last_5")
    if pda:
        lines.append("## 🔁 PDA Loop — Last 5 Iterations")
        for entry in pda[-3:]:
            ts   = entry.get("timestamp", "")[:10]
            act  = entry.get("action", "?")[:60]
            pat  = entry.get("pattern_id", "?")
            lines.append(f"- [{ts}] `{pat}`: {act}")
        lines.append("")

    pol = local_ctx.get("policy_excerpt")
    if pol:
        lines += ["## 📜 Codebase Agency Policy (excerpt)", "```", pol[:600], "```", ""]

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Output writers
# ─────────────────────────────────────────────────────────────────────────────
def _write_github_env(strategy: AccessStrategy, pr_number: int | None) -> None:
    gh_env = os.environ.get("GITHUB_ENV")
    if not gh_env:
        return
    with open(gh_env, "a") as f:
        f.write(f"ACCESS_STRATEGY={','.join(strategy.methods)}\n")
        f.write(f"SESSION_PR_NUMBER={pr_number or ''}\n")
        f.write(f"SESSION_BEST_TOKEN_VAR={strategy.best_token_var}\n")
        f.write(f"SESSION_REST_REMAINING={strategy.rest_remaining}\n")
        f.write(f"SESSION_GQL_REMAINING={strategy.graphql_remaining}\n")


def _write_step_summary(context_md: str) -> None:
    path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not path:
        return
    with open(path, "a") as f:
        f.write("\n## 🧠 Autonomous RAG Session Context\n")
        f.write(context_md[:8000])
        f.write("\n")


def _write_rag_delta(delta: dict, strategy: AccessStrategy) -> None:
    RAG_DELTA.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "rag_delta": delta,
        "access_strategy": strategy.methods,
        "rest_remaining": strategy.rest_remaining,
        "graphql_remaining": strategy.graphql_remaining,
    }
    RAG_DELTA.write_text(json.dumps(payload, indent=2))


def _write_access_strategy(strategy: AccessStrategy) -> None:
    ACCESS_STRATEGY_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "methods": strategy.methods,
        "rest_available": strategy.rest_available,
        "rest_remaining": strategy.rest_remaining,
        "graphql_available": strategy.graphql_available,
        "graphql_remaining": strategy.graphql_remaining,
        "gh_cli_available": strategy.gh_cli_available,
        "codeql_available": strategy.codeql_available,
        "best_token_var": strategy.best_token_var,
        "open_prs": strategy.open_prs,
        "branch": strategy.branch,
        "recommendation": (
            "Use REST for data fetches. "
            if strategy.rest_available and strategy.rest_remaining >= 100
            else "REST exhausted — use GraphQL or gh CLI. "
            if strategy.graphql_available
            else "All API methods exhausted — use local CodeQL/FS only. "
        ),
    }
    ACCESS_STRATEGY_FILE.write_text(json.dumps(payload, indent=2))


# ─────────────────────────────────────────────────────────────────────────────
# Main orchestrator
# ─────────────────────────────────────────────────────────────────────────────
def build_context(
    pr_number:   int | None = None,
    offline:     bool       = False,
    dry_run:     bool       = False,
    rebuild_rag: bool       = False,
) -> str:
    """Full context build pipeline. Returns the rendered Markdown string."""

    # 1. Load access strategy
    strategy = AccessStrategy.from_manifest()
    if offline:
        strategy.methods = ["local_fs"]
    logger.info("Access strategy: %s", strategy.methods)

    # Determine PR number
    pr_num = pr_number or strategy.open_prs[0] if strategy.open_prs else None
    if not pr_num:
        pr_num_env = os.environ.get("GITHUB_PR_NUMBER") or os.environ.get("PR_NUMBER")
        if pr_num_env:
            try:
                pr_num = int(pr_num_env)
            except ValueError:
                logger.debug("Suppressed exception", exc_info=True)

    # 2. Fetch GitHub context
    fetcher = TrickleDownFetcher(strategy, pr_number=pr_num)
    pr_ctx    = fetcher.fetch_pr_context() if pr_num and not offline else {}
    ci_fails  = fetcher.fetch_recent_ci_failures() if not offline else []
    commits   = fetcher.fetch_recent_commits()

    # 3. Local filesystem context
    local_ctx = _harvest_local_context()

    # 4. Build RAG query from current context
    rag_query = " ".join(filter(None, [
        pr_ctx.get("title", ""),
        strategy.branch,
        " ".join(c["message"][:40] for c in commits[:3]),
        " ".join(f["workflow"] for f in ci_fails[:2]),
    ]))[:300]

    rag_hits = _query_rag_index(rag_query) if rag_query.strip() else []

    # 5. Incremental RAG update
    changed = local_ctx.get("changed_files", [])
    if rebuild_rag:
        changed = [str(p.relative_to(REPO_ROOT)) for p in (REPO_ROOT / "src").rglob("*.py")]
    rag_delta = _incremental_rag_update(changed) if changed else {"updated": 0, "skipped": 0, "errors": []}

    # 6. Render + compress
    context_md = _render_context_md(strategy, pr_ctx, ci_fails, commits, local_ctx, rag_hits, rag_delta)
    context_md = _compress_context(context_md, max_tokens=4000)

    if not dry_run:
        # 7. Write outputs
        CTX_OUT.write_text(context_md)
        _write_github_env(strategy, pr_num)
        _write_step_summary(context_md)
        _write_rag_delta(rag_delta, strategy)
        _write_access_strategy(strategy)
        logger.info("Context written to %s (%d chars)", CTX_OUT, len(context_md))

    return context_md


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--pr",          type=int,       help="PR number to fetch context for")
    parser.add_argument("--offline",     action="store_true", help="No network calls — local FS only")
    parser.add_argument("--dry-run",     action="store_true", help="Build context but do not write outputs")
    parser.add_argument("--rebuild-rag", action="store_true", help="Force full RAG index rebuild")
    parser.add_argument("--json",        action="store_true", help="Print access strategy JSON to stdout")
    args = parser.parse_args()

    ctx = build_context(
        pr_number=args.pr,
        offline=args.offline,
        dry_run=args.dry_run,
        rebuild_rag=args.rebuild_rag,
    )

    if args.json:
        strategy = AccessStrategy.from_manifest()
        print(json.dumps({
            "methods": strategy.methods,
            "rest_remaining": strategy.rest_remaining,
            "graphql_remaining": strategy.graphql_remaining,
            "context_chars": len(ctx),
        }, indent=2))
    else:
        print(ctx[:1200])
        print(f"\n→ Full context: {CTX_OUT}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
