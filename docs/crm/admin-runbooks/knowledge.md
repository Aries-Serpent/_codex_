# Knowledge Pipeline (Offline)

```bash
python -m codex.cli knowledge build-kb --root docs --out artifacts/kb.ndjsonl
python -m codex.cli knowledge archive-and-manifest artifacts/kb.ndjsonl --by "$USER"
python -m codex.cli knowledge pack-release artifacts/knowledge.release.manifest.json --out dist/codex-knowledge.tar.gz
python -m codex.cli release verify dist/codex-knowledge.tar.gz
```

## Notes

- PII masking includes e-mail and phone patterns; GPL text is blocked unless `--allow-gpl`.
- Domain/intent inferred from paths: `zendesk|d365|relocation|sla|ops` and `admin|consultant|runtime|devops`.
- Deduplication: `build-kb` runs SimHash dedup by default; disable via `--no-dedup` when you need raw chunk parity for audits.
- Typer guidance (Ruff B008): prefer `from typing import Annotated` and attach option metadata there, e.g.:
  ```python
  def cmd(
      out: Annotated[Path, typer.Option("--out")] = Path("artifacts/kb.ndjsonl"),
  ) -> None:
      ...
  ```
- SQL identifier safety: never format table names directly. Use parameter binding and fixed allow-lists; on Postgres rely on `psycopg.sql.Identifier` after validation.
