import express from 'express';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';
import os from 'os';
import url from 'url';

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));

function readJSON(p, fallback = {}) {
  try {
    return JSON.parse(fs.readFileSync(p, 'utf8'));
  } catch {
    return fallback;
  }
}

const env = process.env;
const rootDir = path.join(__dirname, '..');
const cfgFromFile = readJSON(path.join(rootDir, 'config', 'bridge.config.json'));

// Strong defaults (deny-by-default beyond allowed set)
const defaultAllowTools = ['shell', 'git', 'gh', 'write'];
const defaultDenyTools = [
  'shell(rm)',
  'shell(sudo)',
  'shell(dd)',
  'shell(curl -X POST)',
  'shell(wget)',
  'shell(docker push)'
];

const config = {
  bind: env.BRIDGE_BIND || '127.0.0.1',
  port: parseInt(env.BRIDGE_PORT || '7777', 10),
  defaultCwd: env.DEFAULT_CWD || cfgFromFile.defaultCwd || process.cwd(),
  defaultTimeoutMs: parseInt(env.DEFAULT_TIMEOUT_MS || String(cfgFromFile.defaultTimeoutMs || 600000), 10),
  allowAllTools: (env.ALLOW_ALL_TOOLS || String(cfgFromFile.allowAllTools || false)).toLowerCase() === 'true',
  allowTools: (env.DEFAULT_ALLOW_TOOLS || (cfgFromFile.allowTools || defaultAllowTools).join(','))
    .split(',').map(s => s.trim()).filter(Boolean),
  denyTools: (env.DEFAULT_DENY_TOOLS || (cfgFromFile.denyTools || defaultDenyTools).join(','))
    .split(',').map(s => s.trim()).filter(Boolean),
  manifestDir: env.MANIFEST_DIR || cfgFromFile.manifestDir || path.join(rootDir, 'var', 'manifests'),
  logDir: env.LOG_DIR || cfgFromFile.logDir || path.join(rootDir, 'var', 'logs')
};

// Ensure runtime dirs exist (resolve relative to project rootDir)
for (const d of [config.manifestDir, config.logDir]) {
  const resolved = path.isAbsolute(d) ? d : path.join(rootDir, d);
  fs.mkdirSync(resolved, { recursive: true });
}

const app = express();
app.use(express.json({ limit: '2mb' }));

app.get('/health', (_req, res) => {
  res.json({
    ok: true,
    service: 'copilot-bridge',
    node: process.version,
    pid: process.pid,
    now: new Date().toISOString()
  });
});

function hashSha256(buf) {
  return crypto.createHash('sha256').update(buf).digest('hex');
}

function findLatestCliManifest(cwd) {
  try {
    const entries = fs.readdirSync(cwd).filter(f => f.startsWith('.copilot.manifest.') && f.endsWith('.json'));
    if (entries.length === 0) return { path: '', sha256: '' };
    const full = entries.map(f => path.join(cwd, f));
    full.sort((a, b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
    const p = full[0];
    const sha = hashSha256(fs.readFileSync(p));
    return { path: p, sha256: sha };
  } catch {
    return { path: '', sha256: '' };
  }
}

function writeBridgeManifest(dir, data) {
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  const fname = `bridge.manifest.${ts}.json`;
  const outDir = path.isAbsolute(dir) ? dir : path.join(rootDir, dir);
  const p = path.join(outDir, fname);
  const buf = Buffer.from(JSON.stringify(data, null, 2), 'utf8');
  fs.writeFileSync(p, buf);
  return { path: p, sha256: hashSha256(buf) };
}

app.post('/copilot/run', async (req, res) => {
  const started = new Date();
  const {
    prompt,
    cwd = config.defaultCwd,
    timeoutMs = config.defaultTimeoutMs,
    allowAllTools = config.allowAllTools,
    allowTools = config.allowTools,
    denyTools = config.denyTools
  } = req.body || {};

  if (!prompt || typeof prompt !== 'string' || prompt.trim().length === 0) {
    return res.status(400).json({ ok: false, error: 'prompt is required' });
  }

  const workdir = cwd;
  if (!fs.existsSync(workdir)) {
    return res.status(400).json({ ok: false, error: `cwd does not exist: ${workdir}` });
  }

  const cmd = 'copilot';
  const args = ['-p', prompt];

  if (allowAllTools) {
    args.push('--allow-all-tools');
  } else {
    for (const t of allowTools || []) args.push('--allow-tool', t);
    for (const t of denyTools || []) args.push('--deny-tool', t);
  }

  const child = spawn(cmd, args, { cwd: workdir, env: { ...process.env }, shell: false });

  let stdout = '';
  let stderr = '';
  child.stdout.on('data', d => (stdout += d.toString()));
  child.stderr.on('data', d => (stderr += d.toString()));

  let killedByTimeout = false;
  const killer = setTimeout(() => {
    killedByTimeout = true;
    child.kill('SIGTERM');
    setTimeout(() => child.kill('SIGKILL'), 5000);
  }, Math.max(1, timeoutMs));

  child.on('error', (e) => {
    clearTimeout(killer);
    const ended = new Date();
    const bridgeManifest = writeBridgeManifest(config.manifestDir, {
      version: 1,
      started_at: started.toISOString(),
      ended_at: ended.toISOString(),
      duration_ms: ended - started,
      host: os.hostname(),
      user: os.userInfo().username,
      pid: process.pid,
      exec: { cmd, args, cwd: workdir },
      result: { rc: -1, bytes_stdout: 0, bytes_stderr: 0, error: String(e) }
    });

    res.status(500).json({
      ok: false,
      error: `spawn error: ${String(e)}`,
      rc: -1,
      stdout: '',
      stderr: String(e),
      bytes_stdout: 0,
      bytes_stderr: 0,
      started_at: started.toISOString(),
      ended_at: ended.toISOString(),
      duration_ms: ended - started,
      manifest_path: '',
      manifest_sha256: '',
      bridge_manifest_path: bridgeManifest.path,
      bridge_manifest_sha256: bridgeManifest.sha256
    });
  });

  child.on('close', (rc) => {
    clearTimeout(killer);
    const ended = new Date();
    const { path: cliManifestPath, sha256: cliManifestSha } = findLatestCliManifest(workdir);

    const bridgeManifest = writeBridgeManifest(config.manifestDir, {
      version: 1,
      started_at: started.toISOString(),
      ended_at: ended.toISOString(),
      duration_ms: ended - started,
      host: os.hostname(),
      user: os.userInfo().username,
      pid: process.pid,
      exec: { cmd, args, cwd: workdir, killed_by_timeout: killedByTimeout },
      input: { allowAllTools, allowTools, denyTools, prompt_bytes: Buffer.byteLength(prompt, 'utf8') },
      output: { bytes_stdout: Buffer.byteLength(stdout, 'utf8'), bytes_stderr: Buffer.byteLength(stderr, 'utf8') },
      result: { rc },
      cli_manifest: { path: cliManifestPath, sha256: cliManifestSha }
    });

    res.status(200).json({
      ok: rc === 0,
      rc,
      stdout,
      stderr,
      bytes_stdout: Buffer.byteLength(stdout, 'utf8'),
      bytes_stderr: Buffer.byteLength(stderr, 'utf8'),
      started_at: started.toISOString(),
      ended_at: ended.toISOString(),
      duration_ms: ended - started,
      manifest_path: cliManifestPath,
      manifest_sha256: cliManifestSha,
      bridge_manifest_path: bridgeManifest.path,
      bridge_manifest_sha256: bridgeManifest.sha256
    });
  });
});

app.listen(config.port, config.bind, () => {
  console.log(`[copilot-bridge] listening on http://${config.bind}:${config.port}`);
  console.log(`[copilot-bridge] default cwd: ${config.defaultCwd}`);
  console.log(`[copilot-bridge] node version: ${process.version}`);
});
