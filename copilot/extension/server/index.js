#!/usr/bin/env node
"use strict";

const express = require("express");
const axios = require("axios");
const { randomUUID } = require("crypto");
const dotenv = require("dotenv");
const helmet = require("helmet");
const morgan = require("morgan");

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3978;
const ITA_URL = process.env.ITA_URL;
const ITA_API_KEY = process.env.ITA_API_KEY;

if (!ITA_URL || !ITA_API_KEY) {
  console.error("ITA_URL and ITA_API_KEY must be set before starting the server.");
  process.exit(1);
}

app.use(express.json({ limit: "1mb" }));
app.use(helmet());
app.use(morgan("combined"));

function buildHeaders(requestId) {
  return {
    "X-API-Key": ITA_API_KEY,
    "X-Request-Id": requestId || randomUUID(),
  };
}

async function forwardToIta(path, payload, requestId) {
  const url = `${ITA_URL.replace(/\/$/, "")}${path}`;
  const headers = buildHeaders(requestId);
  const response = await axios.post(url, payload, { headers });
  return response.data;
}

app.post("/ext/repo/hygiene", async (req, res) => {
  try {
    const data = await forwardToIta("/repo/hygiene", req.body, req.headers["x-request-id"]);
    res.json(data);
  } catch (error) {
    const status = error.response?.status || 500;
    res.status(status).json({ error: error.message, details: error.response?.data });
  }
});

app.post("/ext/tests/run", async (req, res) => {
  try {
    const data = await forwardToIta("/tests/run", req.body, req.headers["x-request-id"]);
    res.json(data);
  } catch (error) {
    const status = error.response?.status || 500;
    res.status(status).json({ error: error.message, details: error.response?.data });
  }
});

app.get("/healthz", (_req, res) => {
  res.json({ status: "ok" });
});

app.listen(PORT, () => {
  console.log(`Copilot extension shim listening on port ${PORT}`);
});
