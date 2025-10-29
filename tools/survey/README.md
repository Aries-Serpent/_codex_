# Survey Normalizer Tool

**Goal:** ensure Codex/plain-text survey results always render as readable Markdown.

## Usage
1) Save Codex raw output to a text file (e.g., `tmp/codex_survey.txt`).
2) Run:
   ```bash
   python tools/survey/normalize_survey_md.py \
     --input  tmp/codex_survey.txt \
     --output docs/status_updates/survey-0C_base_-and-<PR>-$(date -u +%F).md \
     --ring   0C_base_ \
     --ref    0C_base_ \
     --pr     <PR or N/A> \
     --owner  "Marc J"
   ```
3) Commit the generated Markdown and any attachments under:
   ```
   docs/status_updates/artifacts/<YYYY-MM-DD>-<slug>/
   ```

## Why this exists
- Codex responses can be mixed formatting; this tool ensures **triple-fenced** blocks under section 4 so GitHub renders them cleanly.
- Mirrors the style validated in `survey-0D_base_-and-1926-<YYYY-MM-DD>.md`. 
