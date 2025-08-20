# Option B: DuckDB Parquet Export

The repository includes a helper to materialize the snapshot SQLite database
into a partitioned Parquet dataset.  This makes it easy to query the snippets
with DuckDB locally or upload them to Azure Blob Storage.

## Export

```bash
python tools/export_to_parquet.py
```

The script attaches the `tools.build_sqlite_snapshot` database, installs the
`httpfs` and `azure` extensions, and writes Parquet files under `parquet/`.
Each partition corresponds to a `snippet.id` value.

## Query in DuckDB

```sql
INSTALL azure;
LOAD azure;
-- Configure credentials (replace with real values)
SET azure_storage_account='ACCOUNT_NAME';
SET azure_storage_access_key='ACCESS_KEY';

-- Read data from Azure Blob Storage
SELECT *
FROM read_parquet('azure://container/snippet/id=1/*.parquet');
```

For a local dataset:

```sql
SELECT * FROM read_parquet('parquet/snippet/id=1/*.parquet');
```
