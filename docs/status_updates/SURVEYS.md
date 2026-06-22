# Survey Reports (Ring/PR Ground Truth)

**Last Updated:** 2026-06-22

This folder captures **human-readable** surveys that embed raw, normalized output
from Codex or other tools, without breaking Markdown rendering.

## Template & Naming
- **Template:** `docs/status_updates/TEMPLATE_survey.md`
- **Save As:** `docs/status_updates/survey-<ring>-and-<pr-or-ref>-<YYYY-MM-DD>.md`
- **Artifacts:** `docs/status_updates/artifacts/<YYYY-MM-DD>-<slug>/`

## Why a Template?
- Normalizes headings/sections for quick scanning
- Ensures raw tool output is fenced (triple backticks) to preserve formatting
- Mirrors the style validated in prior surveys (e.g., survey-0D_base_-and-1926-YYYY-MM-DD.md)

## Quick Start
1. Copy the template:
   ```bash
   cp docs/status_updates/TEMPLATE_survey.md \
      docs/status_updates/survey-0C_base_-and-<PR>-$(date -u +%F).md
   ```
2. Paste Codex survey output under **4) Ground Truth Artifacts**, inside fenced blocks.
3. Fill the metadata, highlights, docs parity, and next steps.
4. Save supporting files under `docs/status_updates/artifacts/<date>-<slug>/`.

## Tips
- Use plain text fences even for code to avoid accidental Markdown transforms.
- Prepend each excerpt with a line like: `>>> FILE: <path>@<ref>`
- Keep section order intact for DIFFs across time.
