
import express from "express";
import fetch from "node-fetch";

const app = express();
app.use(express.json());

const ITA_URL = process.env.ITA_URL || "http://localhost:8080";
const ITA_API_KEY = process.env.ITA_API_KEY || "";

// Copilot → Extension → ITA
app.post("/ext/kb/search", async (req, res) => {
  const { query, top_k } = req.body || {};
  const r = await fetch(`${ITA_URL}/kb/search`, {
    method: "POST",
    headers: { "Content-Type":"application/json", "X-API-Key": ITA_API_KEY, "X-Request-Id": "copilot-ext-1" },
    body: JSON.stringify({ query, top_k: top_k ?? 5 }),
  });
  const data = await r.json();
  res.status(r.status).json(data);
});

app.post("/ext/git/create-pr", async (req, res) => {
  const { repo, title, body, base, head, labels, confirm, dry_run } = req.body || {};
  const url = new URL(`${ITA_URL}/git/create-pr`);
  url.searchParams.set("confirm", String(!!confirm));
  url.searchParams.set("dry_run", String(dry_run !== false)); // default true
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type":"application/json", "X-API-Key": ITA_API_KEY, "X-Request-Id": "copilot-ext-1" },
    body: JSON.stringify({ repo, title, body, base, head, labels }),
  });
  const data = await r.json();
  res.status(r.status).json(data);
});

const port = process.env.PORT || 8787;
app.listen(port, () => console.log(`Copilot extension shim on :${port}`));
