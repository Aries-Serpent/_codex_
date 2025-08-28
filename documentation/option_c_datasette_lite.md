# Option C: Datasette Lite

Host the `.artifacts/snippets.db` snapshot on a static file server that sends `Access-Control-Allow-Origin: *`.
With the file available at a public URL, load it directly in the browser using [Datasette Lite](https://lite.datasette.io/):

```
https://lite.datasette.io/?url=https://files.catbox.moe/zw7qio.db
```

The page runs SQLite in WebAssembly and exposes the database through Datasette's interface for ad-hoc queries.
No server-side Python is required; everything runs in the browser.

## Manual checklist

1. Build the latest `.artifacts/snippets.db` snapshot.
1. Host the database on a static server that sets `Access-Control-Allow-Origin: *`.
1. Open `https://lite.datasette.io/?url=PUBLIC_DB_URL` in your browser.
1. Confirm the list of tables appears as expected.
