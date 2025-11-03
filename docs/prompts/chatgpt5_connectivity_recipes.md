# ChatGPT-5 Connectivity Recipes (CustomGPT Actions + Offline-first)

## Branch Targeting
> Identify most recently updated branch from `/repo/branches` and use that ref by default.
> When multiple branches share same timestamp, prefer the default branch (`main`).

## Evidence-Gathering
1. Call `/repo/search?q=<term>&ref=<branch>` for discovery.
2. For each matched path, call `/repo/files?ref=<branch>&path=<path>` to retrieve **exact** text.
3. Quote canonical line snippets in answers and write an entry in `reports/citations/<UTC>.md`.

## Example Instruction (paste into CustomGPT system message)
```
Always read the Actions schema first, pick the newest branch via /repo/branches, then:
- search with narrow terms
- fetch and quote exact lines
- never infer content not retrieved
- log file paths in the final answer
```
