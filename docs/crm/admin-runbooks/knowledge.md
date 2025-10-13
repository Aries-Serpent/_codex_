# Knowledge Pipeline (Offline)

```bash
python -m codex.cli knowledge build-kb --root docs --out artifacts/kb.ndjsonl
python -m codex.cli knowledge archive-and-manifest artifacts/kb.ndjsonl --by "$USER"
python -m codex.cli knowledge pack-release artifacts/knowledge.release.manifest.json --out dist/codex-knowledge.tar.gz
python -m codex.cli release verify dist/codex-knowledge.tar.gz
```
