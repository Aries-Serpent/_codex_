#!/usr/bin/env python3
"""
Normalize Codex plaintext survey output into well-formed Markdown.
Goals:
  - Collapse any 4+ backtick fences to triple fences.
  - Wrap [BEGIN CONTENT] ... [END CONTENT] blocks in ```text fences (omit markers).
  - Avoid nested/empty code fences that break rendering.
"""
import sys
import re

text = sys.stdin.read()

# Normalize any fence of 4+ backticks to classic triple-fence.
text = re.sub(r"`{4,}", "```", text)

lines = text.splitlines()
out = []
i = 0
while i < len(lines):
    line = lines[i].strip()
    if line == "[BEGIN CONTENT]":
        out.append("```text")
        i += 1
        while i < len(lines) and lines[i].strip() != "[END CONTENT]":
            out.append(lines[i])
            i += 1
        out.append("```")
        # Skip the [END CONTENT] marker if present
        if i < len(lines) and lines[i].strip() == "[END CONTENT]":
            pass
    else:
        out.append(lines[i])
    i += 1

rendered = "\n".join(out)
# Remove accidental empty code blocks like ```\n``` (rare but safe to guard)
rendered = re.sub(r"```[a-zA-Z]*\n```", "", rendered)

sys.stdout.write(rendered)

