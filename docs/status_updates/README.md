# Status Updates: Surveys & Promotion Logs

This folder hosts branch-agnostic reports and artifacts created during ring-by-ring promotion (0A → 0D → main).

## Quick Flow
1) **Collect survey plaintext** from Codex (no nested fences; use the template in `templates/SURVEY_TEMPLATE.md`).
2) **Write the report** with the branch-aware writer:
   ```bash
   # from repo root
   scripts/survey.sh --pr 1926 --stdin << 'EOF'
   <paste Codex plaintext survey here>
   EOF
   ```
3) **Resulting paths**:
   - Report: `docs/status_updates/survey-<branch>-and-<PR>-<YYYY-MM-DD>.md`
   - Artifacts: `docs/status_updates/artifacts/<YYYY-MM-DD>-survey-<branch>-and-<PR>/`

## Notes
- The writer auto-detects the **current branch** via `git rev-parse --abbrev-ref HEAD`.
- The sanitizer ensures **triple backtick** fences and wraps `[BEGIN CONTENT]... [END CONTENT]` blocks in ```text fences for readable Markdown.
- Readiness uses \( R = \alpha E + \beta T + \gamma D \) with \( \alpha+\beta+\gamma=1 \).

