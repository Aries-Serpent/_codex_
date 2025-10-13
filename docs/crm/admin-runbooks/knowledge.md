# Codex Knowledge Pipeline (Offline)

**Objective:** Ingest existing documentation and “applicable aspect files”, normalize, chunk, scrub PII/license risks, and emit deterministic **NDJSON** corpora for assistants (Codex/Copilot/Claude). Archive artifacts and optionally **Release-pack** into a portable knowledge bundle.

## Build KB
```bash
# Scan docs/ for .md/.txt/.html/.pdf, normalize → chunk → write artifacts/kb.ndjsonl
python -m codex.cli knowledge build-kb --root docs --out artifacts/kb.ndjsonl
```

## Archive + Manifest
```bash
# Archive KB (and optional instructions/eval) and emit a release manifest
python -m codex.cli knowledge archive-and-manifest artifacts/kb.ndjsonl --by "$USER"
# => artifacts/knowledge.release.manifest.json
```

## Pack knowledge bundle
```bash
python -m codex.cli knowledge pack-release artifacts/knowledge.release.manifest.json --out dist/codex-knowledge.tar.gz
python -m codex.cli release verify dist/codex-knowledge.tar.gz
```

### Guarantees
- Offline-only; never hard-delete.
- Evidence lines written to `.codex/evidence/archive_ops.jsonl` via Archive/Release calls.
- Schema-validated NDJSON; each record has `id,text,meta{source_path,domain,intent,lang}`.

### Notes
- PII masking includes e-mail and phone patterns; GPL text is blocked unless `--allow-gpl`.
- Domain/intent inferred from paths: `zendesk|d365|relocation|sla|ops` and `admin|consultant|runtime|devops`.
