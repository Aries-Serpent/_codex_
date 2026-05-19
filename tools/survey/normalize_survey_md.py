#!/usr/bin/env python3
"""Normalize Codex plain-text survey output into a Markdown-safe section.

Usage:
  python tools/survey/normalize_survey_md.py \\
      --input  /path/to/codex_survey.txt \\
      --output docs/status_updates/survey-0C_base_-and-<PR>-<YYYY-MM-DD>.md \\
      --ring   0C_base_ \\
      --ref    <branch-or-sha> \\
      --pr     <PR or N/A> \\
      --owner  "<name>"

Notes:
  - We wrap the raw survey body inside a fenced block under section 4.* to guarantee readability.
  - We DO NOT alter content semantics; we only ensure it renders as readable Markdown.
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path

TEMPLATE_HEADER = """# Survey — {ring} and {pr_or_ref} — {date}

## 1) Metadata
- **Ring:** `{ring}`
- **Branch/Ref:** `{ref}`
- **PR:** `{pr}`
- **Commit:** `{commit}`
- **Date (UTC):** `{date}`
- **Owner(s):** `{owner}`
- **Artifacts dir:** `docs/status_updates/artifacts/{date}-{slug}/`

## 2) Survey Scope
This survey collects key code/doc surfaces and deployment promises from the specified ring/PR/ref.

## 3) Highlights (Summary for Humans)
- **Wins:** `<bullets>`
- **Gaps:** `<bullets>`
- **Actions recommended:** `<bullets>`
"""

_RAW_SENTINEL = "__RAW_SURVEY_BODY__"


TEMPLATE_BODY = """
## 4) Ground Truth Artifacts (Normalized)
{fence_open}__RAW_SURVEY_BODY__{fence_close}

## 5) Docs Parity (Promises vs Assets)
- Example: `docs/deployment/reasoning_pod.md` → `<FOUND | MISSING>`
- Example: `configs/deploy/reasoning_pod.yaml` → `<FOUND | MISSING>`

## 6) Readiness Aide (Optional)
- α=`<0..1>`, β=`<0..1>`, γ=`<0..1>`; E,T,D ∈ [0,1]
- `R = α·E + β·T + γ·D = <value>`

## 7) Attachments
- `docs/status_updates/artifacts/{date}-{slug}/report.md`
- `docs/status_updates/artifacts/{date}-{slug}/metrics/*.ndjson`
- `docs/status_updates/artifacts/{date}-{slug}/logs/*.txt`

## 8) Changelog
- `<bullet>`

## 9) Next Steps
- `<short plan>`
"""


def _slugify(s: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "-" for ch in s).strip("-")


def _fence_delimiters(raw: str, language: str = "text") -> tuple[str, str]:
    longest_run = 0
    current_run = 0
    for ch in raw:
        if ch == "`":
            current_run += 1
            if current_run > longest_run:
                longest_run = current_run
        else:
            current_run = 0

    fence_length = max(3, longest_run + 1)
    fence = "`" * fence_length
    opening = f"{fence}{language}\n"
    closing = f"{fence}\n"
    return opening, closing


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Raw Codex survey text file")
    ap.add_argument("--output", required=True, help="Destination Markdown path")
    ap.add_argument("--ring", required=True)
    ap.add_argument("--ref", required=True)
    ap.add_argument("--pr", default="N/A")
    ap.add_argument("--commit", default="<short-sha>")
    ap.add_argument("--owner", default="<owner>")
    args = ap.parse_args()

    raw = Path(args.input).read_text(encoding="utf-8").rstrip() + "\n"
    today = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d")
    pr_or_ref = args.pr if args.pr != "N/A" else args.ref
    slug = _slugify(f"{args.ring}-{pr_or_ref}")

    header = TEMPLATE_HEADER.format(
        ring=args.ring,
        pr_or_ref=pr_or_ref,
        ref=args.ref,
        pr=args.pr,
        commit=args.commit,
        date=today,
        owner=args.owner,
        slug=slug,
    )
    fence_open, fence_close = _fence_delimiters(raw)
    body = TEMPLATE_BODY.format(
        date=today,
        slug=slug,
        fence_open=fence_open,
        fence_close=fence_close,
    )
    body = body.replace(_RAW_SENTINEL, raw)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(header + "\n" + body + "\n", encoding="utf-8")
    print(f"Wrote normalized survey to: {out}")


if __name__ == "__main__":
    main()
