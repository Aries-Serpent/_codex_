# Option A: SQLite CLI

Query the `.artifacts/snippets.db` snapshot directly using the SQLite command-line utility.

## Interactive shell

```bash
sqlite3 .artifacts/snippets.db
```

Once inside the shell you can run standard SQL statements:

```sql
.tables
SELECT * FROM snippet LIMIT 5;
```

Open the file in immutable mode to guarantee no writes:

```bash
sqlite3 'file:.artifacts/snippets.db?immutable=1'
```
