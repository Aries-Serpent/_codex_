"use strict";

const assert = require("node:assert/strict");
const { spawn } = require("node:child_process");
const { once } = require("node:events");
const { mkdtemp, rm } = require("node:fs/promises");
const http = require("node:http");
const os = require("node:os");
const path = require("node:path");
const { test } = require("node:test");

const entrypoint = path.resolve(__dirname, "../server/index.js");
const syntheticKey = "synthetic-extension-fixture";

async function startChild(t, configuration) {
  const cwd = await mkdtemp(path.join(os.tmpdir(), "extension-test-"));
  const child = spawn(process.execPath, [entrypoint], {
    cwd,
    env: { NODE_ENV: "test", HOST: "127.0.0.1", PORT: "0", ...configuration },
    stdio: ["ignore", "pipe", "pipe"],
  });
  let output = "";
  child.stdout.on("data", (chunk) => { output += chunk; });
  child.stderr.on("data", (chunk) => { output += chunk; });
  const exited = once(child, "exit");
  t.after(async () => {
    const timer = setTimeout(() => child.kill("SIGKILL"), 2000);
    try {
      if (child.exitCode === null && child.signalCode === null) child.kill("SIGTERM");
      await exited;
    } finally {
      clearTimeout(timer);
      await rm(cwd, { recursive: true, force: true });
    }
  });
  return { child, exited, output: () => output };
}

async function listeningPort(process) {
  const deadline = Date.now() + 10_000;
  while (Date.now() < deadline) {
    const match = process.output().match(/listening on port (\d+)/);
    if (match) return Number(match[1]);
    assert.equal(process.child.exitCode, null, process.output());
    await new Promise((resolve) => setTimeout(resolve, 20));
  }
  assert.fail(`Server startup timed out: ${process.output()}`);
}

test("real server forwards locally and preserves HTTP boundaries", { timeout: 30_000 }, async (t) => {
  const received = [];
  const stub = http.createServer(async (req, res) => {
    let body = "";
    for await (const chunk of req) body += chunk;
    const payload = JSON.parse(body);
    received.push({ url: req.url, headers: req.headers, payload });
    if (payload.disconnect) {
      req.socket.destroy();
      return;
    }
    res.writeHead(payload.fail ? 422 : 200, { "content-type": "application/json" });
    res.end(JSON.stringify(payload.fail ? { reason: "synthetic rejection" } : { accepted: req.url }));
  });
  stub.listen(0, "127.0.0.1");
  await once(stub, "listening");
  t.after(() => new Promise((resolve) => {
    stub.closeAllConnections();
    stub.close(resolve);
  }));
  const process = await startChild(t, {
    ITA_URL: `http://127.0.0.1:${stub.address().port}/`,
    ITA_API_KEY: syntheticKey,
  });
  const port = await listeningPort(process);
  const base = `http://127.0.0.1:${port}`;
  const post = (route, payload, headers = {}) => fetch(`${base}${route}`, {
    method: "POST",
    headers: { "content-type": "application/json", ...headers },
    body: typeof payload === "string" ? payload : JSON.stringify(payload),
    signal: AbortSignal.timeout(5000),
  });

  const health = await fetch(`${base}/healthz`, { signal: AbortSignal.timeout(5000) });
  assert.equal(health.status, 200);
  assert.deepEqual(await health.json(), { status: "ok" });
  assert.equal(health.headers.get("x-content-type-options"), "nosniff");

  for (const [route, upstream] of [
    ["/ext/repo/hygiene", "/repo/hygiene"],
    ["/ext/tests/run", "/tests/run"],
  ]) {
    const payload = { task: "synthetic", nested: { values: [0, false, "binary\u0000"] } };
    const response = await post(route, payload, { "x-request-id": "fixture-request-123" });
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { accepted: upstream });
    assert.deepEqual(received.at(-1).payload, payload);
    assert.equal(received.at(-1).url, upstream);
    assert.equal(received.at(-1).headers["x-api-key"], syntheticKey);
    assert.equal(received.at(-1).headers["x-request-id"], "fixture-request-123");

    const generated = await post(route, {});
    assert.equal(generated.status, 200);
    assert.match(received.at(-1).headers["x-request-id"],
      /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/);

    const failure = await post(route, { fail: true });
    assert.equal(failure.status, 422);
    const error = await failure.json();
    assert.match(error.error, /422/);
    assert.deepEqual(error.details, { reason: "synthetic rejection" });

    const disconnected = await post(route, { disconnect: true });
    assert.equal(disconnected.status, 500);
    assert.equal(typeof (await disconnected.json()).error, "string");
  }

  const limit = 1024 * 1024;
  const overhead = JSON.stringify({ value: "" }).length;
  const exact = JSON.stringify({ value: "x".repeat(limit - overhead) });
  assert.equal(Buffer.byteLength(exact), limit);
  assert.equal((await post("/ext/tests/run", exact)).status, 200);
  const before = received.length;
  assert.equal((await post("/ext/tests/run", `${exact} `)).status, 413);
  assert.equal((await post("/ext/tests/run", "{")).status, 400);
  assert.equal(received.length, before, "invalid bodies must not reach ITA");
});

for (const missing of ["ITA_URL", "ITA_API_KEY"]) {
  test(`startup fails without ${missing}`, { timeout: 10_000 }, async (t) => {
    const configuration = { ITA_URL: "http://127.0.0.1:1", ITA_API_KEY: syntheticKey };
    delete configuration[missing];
    const process = await startChild(t, configuration);
    const [code] = await process.exited;
    assert.equal(code, 1);
    assert.match(process.output(), /ITA_URL and ITA_API_KEY must be set/);
    assert.doesNotMatch(process.output(), /listening on port/);
  });
}
