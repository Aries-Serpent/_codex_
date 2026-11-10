"use strict";

const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const { once } = require("node:events");
const http = require("node:http");
const path = require("node:path");
const { test } = require("node:test");

const serverPath = path.resolve(__dirname, "../server/index.js");

function childEnv(extra = {}) {
  return {
    PATH: process.env.PATH,
    LD_LIBRARY_PATH: process.env.LD_LIBRARY_PATH,
    ICU_DATA: process.env.ICU_DATA,
    ...extra,
  };
}

async function listen(server) {
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
  return server.address().port;
}

async function stopChild(child) {
  if (child.exitCode !== null || child.signalCode !== null) return;
  const exited = once(child, "exit");
  child.kill("SIGTERM");
  await exited;
}

test("real shim forwards requests and preserves error and body-limit behavior", {
  timeout: 15000,
}, async (t) => {
  const requests = [];
  const upstream = http.createServer(async (req, res) => {
    let body = "";
    for await (const chunk of req) body += chunk;
    const payload = JSON.parse(body);
    requests.push({ path: req.url, headers: req.headers, payload });
    res.setHeader("Content-Type", "application/json");
    if (payload.fail) {
      res.writeHead(422);
      res.end(JSON.stringify({ reason: "synthetic upstream rejection" }));
    } else {
      res.end(JSON.stringify({ received: payload }));
    }
  });
  const upstreamPort = await listen(upstream);
  t.after(() => new Promise((resolve) => upstream.close(resolve)));

  const child = spawn(process.execPath, [serverPath], {
    env: childEnv({
      PORT: "0",
      ITA_URL: `http://127.0.0.1:${upstreamPort}/`,
      ITA_API_KEY: "synthetic-test-value",
    }),
    stdio: ["ignore", "pipe", "pipe"],
    cwd: __dirname,
  });
  t.after(() => stopChild(child));
  let errors = "";
  child.stderr.on("data", (chunk) => { errors += chunk; });
  const port = await new Promise((resolve, reject) => {
    let output = "";
    const timer = setTimeout(() => reject(new Error("shim did not start")), 5000);
    child.once("error", (error) => { clearTimeout(timer); reject(error); });
    child.once("exit", (code) => {
      clearTimeout(timer);
      reject(new Error(`shim exited ${code}: ${errors}`));
    });
    child.stdout.on("data", (chunk) => {
      output += chunk;
      const listening = output.match(/listening on port (\d+)(?:\r?\n)/);
      if (listening) {
        clearTimeout(timer);
        resolve(Number(listening[1]));
      }
    });
  });
  const base = `http://127.0.0.1:${port}`;
  assert.ok(port > 0 && port <= 65535);
  const health = await fetch(`${base}/healthz`);
  assert.equal(health.status, 200);
  assert.deepEqual(await health.json(), { status: "ok" });

  for (const [route, destination] of [
    ["/ext/repo/hygiene", "/repo/hygiene"],
    ["/ext/tests/run", "/tests/run"],
  ]) {
    const payload = { marker: route };
    const response = await fetch(`${base}${route}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-Request-Id": "fixture-request" },
      body: JSON.stringify(payload),
    });
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { received: payload });
    const received = requests.at(-1);
    assert.equal(received.path, destination);
    assert.deepEqual(received.payload, payload);
    assert.equal(received.headers["x-request-id"], "fixture-request");
    assert.equal(received.headers["x-api-key"], "synthetic-test-value");
  }

  const failed = await fetch(`${base}/ext/tests/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ fail: true }),
  });
  assert.equal(failed.status, 422);
  const failure = await failed.json();
  assert.match(failure.error, /422/);
  assert.deepEqual(failure.details, { reason: "synthetic upstream rejection" });
  assert.match(requests.at(-1).headers["x-request-id"], /^[0-9a-f-]{36}$/);

  const count = requests.length;
  const oversized = await fetch(`${base}/ext/tests/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data: "x".repeat(1024 * 1024) }),
  });
  assert.equal(oversized.status, 413);
  assert.equal(requests.length, count);
});

for (const missing of ["ITA_URL", "ITA_API_KEY"]) {
  test(`startup fails when ${missing} is missing`, { timeout: 10000 }, async (t) => {
    const env = childEnv({
      ITA_URL: "http://127.0.0.1:1",
      ITA_API_KEY: "synthetic-test-value",
    });
    delete env[missing];
    const child = spawn(process.execPath, [serverPath], {
      env, cwd: __dirname, stdio: ["ignore", "ignore", "pipe"],
    });
    t.after(() => stopChild(child));
    let error = "";
    child.stderr.on("data", (chunk) => { error += chunk; });
    const [code] = await once(child, "exit");
    assert.equal(code, 1);
    assert.match(error, /ITA_URL and ITA_API_KEY must be set/);
  });
}
