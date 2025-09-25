#!/usr/bin/env python3
"""Derive minimal labels for queued self-hosted jobs on a branch."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.parse
from typing import Any, Dict, List, Optional

from tools.security.net import safe_request

try:
    import yaml
except Exception:  # pragma: no cover - dependency check
    print("Install pyyaml to run preflight.", file=sys.stderr)
    sys.exit(2)

API = "https://api.github.com"
POLICY_PATH = "tools/label_policy.json"


def _request(url: str, token: str, method: str = "GET") -> Dict[str, Any]:
    status, _headers, body = safe_request(
        url,
        timeout=30,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "codex-preflight",
        },
        method=method,
    )
    if status >= 400:
        raise RuntimeError(f"GitHub API request failed with status {status}")
    return json.loads(body.decode("utf-8"))


def list_queued_runs(owner: str, repo: str, branch: str, token: str) -> List[Dict[str, Any]]:
    qs = urllib.parse.urlencode({"status": "queued", "branch": branch, "per_page": 100})
    url = f"{API}/repos/{owner}/{repo}/actions/runs?{qs}"
    data = _request(url, token)
    return data.get("workflow_runs", [])


def get_workflow(owner: str, repo: str, workflow_id: int, token: str) -> Dict[str, Any]:
    url = f"{API}/repos/{owner}/{repo}/actions/workflows/{workflow_id}"
    return _request(url, token)


def get_file_at_sha(owner: str, repo: str, path: str, ref: str, token: str) -> str:
    qs = urllib.parse.urlencode({"ref": ref})
    url = f"{API}/repos/{owner}/{repo}/contents/{urllib.parse.quote(path)}?{qs}"
    obj = _request(url, token)
    if obj.get("encoding") == "base64":
        return base64.b64decode(obj["content"]).decode("utf-8")
    return obj.get("content", "")


def minimal_labels_from_yaml(
    yaml_text: str,
    allowed: set[str],
    required_base: set[str],
    defaults_for_string: List[str],
) -> Optional[List[str]]:
    doc = yaml.safe_load(yaml_text) or {}
    jobs = doc.get("jobs", {})
    for job in (jobs or {}).values():
        runs_on = job.get("runs-on")
        if runs_on is None:
            continue
        labels = [runs_on] if isinstance(runs_on, str) else list(runs_on)
        if "self-hosted" in labels:
            if labels == ["self-hosted"]:
                labels = ["self-hosted", *defaults_for_string]
            label_set = set(labels)
            if not required_base.issubset(label_set):
                label_set |= required_base
            if not label_set.issubset(allowed):
                label_set = (label_set & allowed) | required_base
                label_set.add("self-hosted")
            return [label for label in label_set if label != "self-hosted"]
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--owner", default=os.environ.get("OWNER", "Aries-Serpent"))
    parser.add_argument("--repo", default=os.environ.get("REPO", "_codex_"))
    parser.add_argument("--branch", default=os.environ.get("BRANCH", "0B_base_"))
    parser.add_argument("--gh-pat", default=os.environ.get("GH_PAT"))
    args = parser.parse_args()

    if not args.gh_pat:
        print("GH_PAT required", file=sys.stderr)
        return 2

    policy = json.loads(open(POLICY_PATH, "r", encoding="utf-8").read())
    allowed = set(policy["allowed_labels"])
    required_base = set(policy.get("required_base", []))
    defaults = policy.get("defaults_for_string_runs_on", [])

    runs = list_queued_runs(args.owner, args.repo, args.branch, args.gh_pat)
    if not runs:
        fallback = [label for label in (*required_base, "codex") if label != "self-hosted"]
        print(",".join(sorted(fallback)))
        return 0
    run = sorted(runs, key=lambda r: r.get("created_at", ""))[0]
    wf_id = run.get("workflow_id")
    sha = run.get("head_sha")
    if not wf_id or not sha:
        fallback = [label for label in (*required_base, "codex") if label != "self-hosted"]
        print(",".join(sorted(fallback)))
        return 0
    workflow = get_workflow(args.owner, args.repo, wf_id, args.gh_pat)
    path = workflow.get("path")
    if not path:
        fallback = [label for label in (*required_base, "codex") if label != "self-hosted"]
        print(",".join(sorted(fallback)))
        return 0
    yml = get_file_at_sha(args.owner, args.repo, path, sha, args.gh_pat)
    labels = minimal_labels_from_yaml(yml, allowed, required_base, defaults)
    if labels:
        print(",".join(sorted(set(labels))))
        return 0
    fallback = [label for label in (*required_base, "codex") if label != "self-hosted"]
    print(",".join(sorted(set(fallback))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
