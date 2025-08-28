# Manual Verification Template

Use these steps to manually validate `.artifacts/snippets.db` or its derivatives. Choose one of the options below and complete the associated steps.

Automated helper: `python tools/verify_data_paths.py` runs Option A and B steps and prints a Datasette Lite URL for Option C.

## Option A: SQLite CLI

1. **A1** – Open the snapshot:
   ```bash
   sqlite3 .artifacts/snippets.db
   ```
1. **A2** – List available tables:
   ```sql
   .tables
   ```
1. **A3** – Run a sample query:
   ```sql
   SELECT * FROM snippet LIMIT 5;
   ```
1. **A4** – Reopen in immutable (read‑only) mode to confirm no writes:
   ```bash
   sqlite3 'file:.artifacts/snippets.db?immutable=1'
   ```

## Option B: DuckDB Parquet Export

1. **B1** – Export the snapshot to Parquet:
   ```bash
   python tools/export_to_parquet.py
   ```
1. **B2** – Inspect a partition with DuckDB:
   ```sql
   SELECT * FROM read_parquet('parquet/snippet/id=1/*.parquet');
   ```

## Option C: Datasette Lite

1. **C1** – Build the `.artifacts/snippets.db` snapshot.
1. **C2** – Host the database on a static server that sets `Access-Control-Allow-Origin: *`.
1. **C3** – Open Datasette Lite with the URL to your database:
   ```
   https://lite.datasette.io/?url=https://files.example.com/snippets.db
   ```
1. **C4** – Confirm the tables list appears as expected.
   The database runs entirely in the browser for ad‑hoc queries.
