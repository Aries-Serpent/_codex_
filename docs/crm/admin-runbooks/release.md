# Codex Release (Offline Pack → Verify → Unpack)

**Goal:** deterministically "roll up" a release from archived tombstones and materialize it on a target host—**offline**, **append-only evidence**, **never hard-delete**.

## Prereqs
```bash
export CODEX_ARCHIVE_BACKEND=sqlite
export CODEX_ARCHIVE_URL=sqlite:///./.codex/archive.sqlite
export CODEX_EVIDENCE_DIR=.codex/evidence
export CODEX_ACTOR="$USER"
mkdir -p "$CODEX_EVIDENCE_DIR" dist/ work/
```

## Create a manifest
```bash
python -m codex.cli release init-manifest
# edit release.manifest.json (set tombstones, paths, modes, template_vars)
```

## Pack
```bash
python -m codex.cli release pack --staging work/release_staging --out dist/codex-release.tar.gz
# emits dist/release.manifest.lock.json (sha256-locked)
```

## Verify
```bash
python -m codex.cli release verify dist/codex-release.tar.gz
```

## Unpack (target)
```bash
python -m codex.cli release unpack dist/codex-release.tar.gz --dest /opt/codex/app
```

### Evidence
Every PACK/VERIFY/UNPACK appends JSONL to:
```text
.codex/evidence/archive_ops.jsonl
```

## Notes & Guardrails
- **No scripts executed** during unpack unless `--allow-scripts` is passed (not recommended).
- Template variables perform **pure string substitution** in text-like files (.json/.txt/.md/.yml/.yaml/.env).
- Use consolidation + archival to pin canonical components before release packing.
