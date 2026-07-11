# Release Checklist
**Last Updated:** 2026-07-11
**Version:** v0.2.1

## Pro-safe notes (no-cost)
- Prefer **GitHub Releases** for binaries (≤ 2 GiB/asset, no bandwidth cap).
- Avoid **Git LFS** unless you're certain you'll stay within the free 1 GiB storage / 1 GiB/month bandwidth.
- If you must include generated reports as Actions artifacts, set `retention-days: 1`.
- When pushing doc-only commits, include `[skip ci]` in the commit message to skip workflows.
