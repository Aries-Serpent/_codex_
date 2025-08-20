PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;

CREATE TABLE IF NOT EXISTS snippet (
    id INTEGER PRIMARY KEY,
    body TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS snippet_fts USING fts5(
    body,
    content='snippet',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS snippet_ai AFTER INSERT ON snippet BEGIN
    INSERT INTO snippet_fts(rowid, body) VALUES (new.id, new.body);
END;

CREATE TRIGGER IF NOT EXISTS snippet_ad AFTER DELETE ON snippet BEGIN
    INSERT INTO snippet_fts(snippet_fts, rowid, body) VALUES('delete', old.id, old.body);
END;

CREATE TRIGGER IF NOT EXISTS snippet_au AFTER UPDATE ON snippet BEGIN
    INSERT INTO snippet_fts(snippet_fts, rowid, body) VALUES('delete', old.id, old.body);
    INSERT INTO snippet_fts(rowid, body) VALUES(new.id, new.body);
END;
