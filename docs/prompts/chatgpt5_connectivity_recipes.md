# ChatGPT-5 Connectivity Recipes (CustomGPT Actions + Offline-first)

## Branch Targeting
> Preferred: call `/repo/most_recent_branch` and use the returned `branch` as `ref`.
> Fallback: if unavailable, list from `/repo/branches` and approximate by recency.

## Evidence-Gathering
1. Call `/repo/search?q=<term>&ref=<branch>` for discovery.
2. For each matched path, call `/repo/files?ref=<branch>&path=<path>` to retrieve **exact** text.
3. Quote canonical line snippets in answers and write an entry in `reports/citations/<UTC>.md`
   (or call `actions_cli.py cite` out-of-band in human workflows).

## Example Instruction (paste into CustomGPT system message)
```text
Always read the Actions schema first, pick the newest branch via /repo/most_recent_branch, then:
- search with narrow terms
- fetch and quote exact lines
- never infer content not retrieved
- log file paths in the final answer
```text