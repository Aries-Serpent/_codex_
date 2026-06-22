# Secret Masking Policy

**Last Updated:** 2026-06-22
- Never commit secrets. If found, **remove immediately**, rotate, and document incident separately.
- Redact in reports as `[REDACTED:<class>]` (e.g., `[REDACTED:token]`).
- Do not quote entire `.env` files; summarize keys where necessary.
