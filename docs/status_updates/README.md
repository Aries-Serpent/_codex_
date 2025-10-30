# Status Updates: Surveys & Promotion Logs

This folder hosts branch-agnostic reports and artifacts created during ring-by-ring promotion (0A → 0D → main).

## Quick Flow
1) **Collect survey plaintext** from Codex (no nested fences; use the template in `docs/status_updates/TEMPLATE_status_update.md`).
2) **Write the report** with the branch-aware writer:
   ```bash
   scripts/survey.sh --pr 1926 --stdin <<'EOF'
   <paste Codex plaintext survey here>
   EOF
   ```
   - Use `--from-file <path>` if the plaintext is saved locally.
3) **Resulting paths**:
   - Report: `docs/status_updates/survey-<branch>-and-<PR>-<YYYY-MM-DD>.md`
   - Artifacts: `docs/status_updates/artifacts/<YYYY-MM-DD>-survey-<branch>-and-<PR>/`
   - The artifact folder also mirrors the report at `report.md` for easy packaging.

## Notes
- The writer auto-detects the **current branch** via `git rev-parse --abbrev-ref HEAD` and derives safe slugs for filenames.
- The sanitizer collapses 4+ backtick fences to triples and wraps `[BEGIN CONTENT]... [END CONTENT]` blocks in ```text fences so Markdown renders cleanly.
- Readiness uses \( R = \alpha E + \beta T + \gamma D \) with \( \alpha+\beta+\gamma=1 \).

## Best Practices
- Anchor each update to a specific branch/PR/commit
- Attach NDJSON metrics, logs, and generated reports as artifacts for auditability
- Keep "Gaps & Remediations" short, specific, and assigned to owners
- Update changelog section to reference previous status update file

## Readiness Artifact Validation (optional)
To validate machine-readable readiness files:
```bash
python tools/validate_readiness.py docs/status_updates/artifacts/*/readiness.json \
  --schema docs/status_updates/readiness.schema.json
```
