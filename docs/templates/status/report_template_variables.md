# Reference: Report Template Variables (v1.2)
> Generated: 2025-11-02 15:08:30 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Template Author], [Secondary: Reviewer] ⚡ Energy: 5

Variables (suggested)
- metadata.title
- metadata.timestamp_utc
- metadata.git_context.branch
- metadata.environment.python_version
- snapshot.capabilities[*].id|name|status|tags
- snapshot.findings[*].id|title|severity|confidence|links
- tests_gates.coverage_percent
- repro.registry[*].id|category|status
- patches[*].id|title|risk|confidence|diff

Tips
- Keep diffs fenced with Begin/End Patch markers
- Use IDs consistently; validate with tools/link_id_crossref.py
