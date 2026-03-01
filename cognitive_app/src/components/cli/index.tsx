import { useState, useCallback, useRef, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Trash, Clock, CheckCircle, XCircle, Copy, CaretDown, CaretRight, Terminal, Stop, ArrowRight, Globe } from '@phosphor-icons/react';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';

// ── CliTerminal ────────────────────────────────────────────────────────────

interface CliEntry {
  id: number;
  type: 'input' | 'output' | 'error' | 'system';
  text: string;
  timestamp: string;
  durationMs?: number;
  returncode?: number;
}

interface CliRunResponse {
  stdout: string;
  stderr: string;
  returncode: number;
  duration_ms: number;
  cwd: string;
  timestamp: string;
}

const CLI_API = 'http://localhost:8765';

const QUICK_COMMANDS = [
  { label: 'Health',     cmd: 'python -m codex.cli health 2>/dev/null || echo "CLI unavailable"' },
  { label: 'Tests',      cmd: 'python -m pytest tests/ -q --no-header --tb=no -x 2>&1 | tail -8' },
  { label: 'Lint',       cmd: 'ruff check src/ --quiet 2>&1 | head -20 || echo "No issues"' },
  { label: 'Git log',    cmd: 'git --no-pager log --oneline -8' },
  { label: 'Git status', cmd: 'git status --short' },
  { label: 'Workflows',  cmd: 'ls .github/workflows/ | wc -l && echo workflows' },
  { label: 'CI telemetry', cmd: 'python scripts/ci/collect_telemetry.py --help 2>&1 | head -8' },
  { label: 'Vars',       cmd: 'cat .codex/pending_var_updates.json 2>/dev/null || echo "(no pending vars)"' },
];

export function CliTerminal() {
  const [entries, setEntries] = useState<CliEntry[]>([{
    id: 0, type: 'system',
    text: '🧠 Codex Cognitive Brain — CLI Terminal\nServer: http://localhost:8765\nType a command and press Enter. ↑↓ for history. Ctrl+L to clear.\n',
    timestamp: new Date().toISOString(),
  }]);
  const [input, setInput]       = useState('');
  const [running, setRunning]   = useState(false);
  const [history, setHistory]   = useState<string[]>([]);
  const [historyIdx, setHistoryIdx] = useState(-1);
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);
  const [cwd, setCwd]           = useState('~');
  const entryId = useRef(1);
  const inputRef = useRef<HTMLInputElement>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  const checkServer = useCallback(async () => {
    try {
      const r = await fetch(`${CLI_API}/api/health`, { signal: AbortSignal.timeout(2000) });
      setServerOnline(r.ok);
    } catch { setServerOnline(false); }
  }, []);

  // Check server health on mount
  useEffect(() => { checkServer(); }, [checkServer]);

  const append = (entry: Omit<CliEntry, 'id'>) => {
    setEntries(prev => {
      const next = [...prev, { ...entry, id: entryId.current++ }];
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: 'smooth' }), 30);
      return next;
    });
  };

  const runCommand = useCallback(async (cmd: string) => {
    const trimmed = cmd.trim();
    if (!trimmed) return;
    setHistory(prev => [trimmed, ...prev.slice(0, 99)]);
    setHistoryIdx(-1);
    setInput('');
    setRunning(true);
    append({ type: 'input', text: `❯ ${trimmed}`, timestamp: new Date().toISOString() });

    if (!serverOnline) {
      append({ type: 'error', text: '⚠ CLI server offline.\nStart: uvicorn cognitive_app.src.server.cli_api_server:app --port 8765', timestamp: new Date().toISOString() });
      setRunning(false);
      return;
    }

    try {
      const resp = await fetch(`${CLI_API}/api/cli/run`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: trimmed, timeout: 30 }),
      });
      if (!resp.ok) {
        const e = await resp.json().catch(() => ({ detail: resp.statusText }));
        throw new Error(e.detail || resp.statusText);
      }
      const data: CliRunResponse = await resp.json();
      setCwd(data.cwd.replace(/\/home\/runner\/work\/_codex_\/_codex_/, '~'));
      const combined = [data.stdout, data.stderr].filter(Boolean).join('');
      append({
        type: data.returncode === 0 ? 'output' : 'error',
        text: combined || '(no output)',
        timestamp: data.timestamp,
        durationMs: data.duration_ms,
        returncode: data.returncode,
      });
    } catch (err) {
      append({ type: 'error', text: `Error: ${err instanceof Error ? err.message : String(err)}`, timestamp: new Date().toISOString() });
    } finally {
      setRunning(false);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [serverOnline]);

  const handleKey = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !running) { runCommand(input); }
    else if (e.key === 'ArrowUp')   { e.preventDefault(); const i = Math.min(historyIdx+1, history.length-1); setHistoryIdx(i); setInput(history[i] ?? ''); }
    else if (e.key === 'ArrowDown') { e.preventDefault(); const i = Math.max(historyIdx-1, -1); setHistoryIdx(i); setInput(i === -1 ? '' : history[i]); }
    else if (e.key === 'l' && e.ctrlKey) { e.preventDefault(); setEntries([]); }
  };

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Terminal weight="duotone" className="w-5 h-5 text-accent" />
          <h2 className="text-lg font-semibold">CLI Terminal</h2>
          <Badge variant={serverOnline === true ? 'default' : serverOnline === false ? 'destructive' : 'secondary'} className="text-xs cursor-pointer" onClick={checkServer}>
            {serverOnline === true ? '● online' : serverOnline === false ? '○ offline' : '◌ checking'}
          </Badge>
          <span className="text-xs text-muted-foreground font-mono">{cwd}</span>
        </div>
        <Button size="sm" variant="ghost" onClick={() => setEntries([])} title="Clear (Ctrl+L)"><Trash className="w-4 h-4" /></Button>
      </div>

      <div className="flex flex-wrap gap-1">
        {QUICK_COMMANDS.map(({ label, cmd }) => (
          <Button key={label} size="sm" variant="outline" className="text-xs h-6 px-2 font-mono" disabled={running} onClick={() => runCommand(cmd)}>{label}</Button>
        ))}
      </div>

      <Card className="bg-[oklch(0.12_0.02_260)] border-border">
        <ScrollArea className="h-72">
          <div className="p-3 font-mono text-sm space-y-1">
            {entries.map(e => (
              <div key={e.id}>
                {e.type === 'input'  && <div className="text-[oklch(0.85_0.15_195)]">{e.text}</div>}
                {e.type === 'output' && <pre className="text-[oklch(0.90_0.02_260)] whitespace-pre-wrap break-all">{e.text}{e.durationMs !== undefined && <span className="text-[oklch(0.55_0.05_260)] text-xs"> [{e.durationMs.toFixed(0)}ms]</span>}</pre>}
                {e.type === 'error'  && <pre className="text-[oklch(0.75_0.18_25)] whitespace-pre-wrap break-all">{e.text}{e.returncode !== 0 && e.returncode !== undefined && <span className="text-xs"> [exit {e.returncode}]</span>}</pre>}
                {e.type === 'system' && <pre className="text-[oklch(0.65_0.10_280)] whitespace-pre-wrap">{e.text}</pre>}
              </div>
            ))}
            {running && <div className="text-[oklch(0.75_0.15_195)] animate-pulse">▋</div>}
            <div ref={bottomRef} />
          </div>
        </ScrollArea>
        <div className="flex items-center gap-2 px-3 py-2 border-t border-border">
          <span className="text-[oklch(0.85_0.15_195)] font-mono text-sm select-none">❯</span>
          <input ref={inputRef} value={input} onChange={e => setInput(e.target.value)} onKeyDown={handleKey}
            disabled={running} placeholder={running ? 'Running…' : 'Enter command…'}
            className="flex-1 bg-transparent text-sm font-mono text-foreground outline-none placeholder:text-muted-foreground/50 disabled:opacity-50"
            autoComplete="off" spellCheck={false} autoFocus />
          {running && <Stop className="w-4 h-4 text-muted-foreground animate-spin" />}
        </div>
      </Card>
    </div>
  );
}

// ── ApiClient ──────────────────────────────────────────────────────────────

type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';

interface ApiEntry {
  id: number;
  method: HttpMethod;
  url: string;
  statusCode: number;
  durationMs: number;
  body: unknown;
  timestamp: string;
  error?: string;
  expanded: boolean;
}

const METHOD_COLORS: Record<HttpMethod, string> = {
  GET:    'bg-blue-500/20 text-blue-300 border-blue-500/40',
  POST:   'bg-green-500/20 text-green-300 border-green-500/40',
  PUT:    'bg-yellow-500/20 text-yellow-300 border-yellow-500/40',
  PATCH:  'bg-orange-500/20 text-orange-300 border-orange-500/40',
  DELETE: 'bg-red-500/20 text-red-300 border-red-500/40',
};

const statusColor = (c: number) =>
  c >= 500 ? 'text-red-400' : c >= 400 ? 'text-orange-400' : c >= 300 ? 'text-yellow-400' : c >= 200 ? 'text-green-400' : 'text-muted-foreground';

const PRESETS = [
  { label: 'Brain Health',  method: 'GET'    as HttpMethod, url: `${CLI_API}/api/health`,           body: '' },
  { label: 'CLI History',   method: 'GET'    as HttpMethod, url: `${CLI_API}/api/cli/history`,      body: '' },
  { label: 'Clear History', method: 'DELETE' as HttpMethod, url: `${CLI_API}/api/cli/history`,      body: '' },
  { label: 'Run cmd',       method: 'POST'   as HttpMethod, url: `${CLI_API}/api/cli/run`,          body: JSON.stringify({ command: 'git status --short', timeout: 10 }, null, 2) },
  { label: 'GH Repo',       method: 'GET'    as HttpMethod, url: 'https://api.github.com/repos/Aries-Serpent/_codex_', body: '' },
  { label: 'GH Runs',       method: 'GET'    as HttpMethod, url: 'https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs?per_page=5', body: '' },
];

export function ApiClient() {
  const [method, setMethod]   = useState<HttpMethod>('GET');
  const [url, setUrl]         = useState(`${CLI_API}/api/health`);
  const [hdrs, setHdrs]       = useState('{\n  "Accept": "application/json"\n}');
  const [prms, setPrms]       = useState('');
  const [body, setBody]       = useState('');
  const [loading, setLoading] = useState(false);
  const [entries, setEntries] = useState<ApiEntry[]>([]);
  const [showH, setShowH]     = useState(false);
  const [showP, setShowP]     = useState(false);
  const eid = useRef(1);

  const send = useCallback(async () => {
    setLoading(true);
    const id = eid.current++;
    let ph: Record<string,string>={}, pp: Record<string,string>={}, pb: unknown;
    try { if (hdrs.trim()) ph = JSON.parse(hdrs); } catch {}
    try { if (prms.trim()) pp = JSON.parse(prms); } catch {}
    try { if (body.trim()) pb = JSON.parse(body);  } catch { pb = body.trim()||undefined; }

    try {
      const r = await fetch(`${CLI_API}/api/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ method, url,
          headers: Object.keys(ph).length ? ph : undefined,
          params:  Object.keys(pp).length ? pp : undefined,
          body: pb, timeout: 30 }),
      });
      const d = await r.json().catch(() => ({ detail: r.statusText }));
      if (!r.ok || 'detail' in d) {
        setEntries(p => [{ id, method, url, statusCode: r.status, durationMs: 0, body: d,
          timestamp: new Date().toISOString(), error: d.detail || r.statusText, expanded: true }, ...p]);
        return;
      }
      setEntries(p => [{ id, method: d.method as HttpMethod, url: d.url,
        statusCode: d.status_code, durationMs: d.duration_ms, body: d.body,
        timestamp: new Date().toISOString(), expanded: true }, ...p]);
    } catch (e) {
      setEntries(p => [{ id, method, url, statusCode: 0, durationMs: 0, body: null,
        timestamp: new Date().toISOString(),
        error: `Network error: ${e instanceof Error ? e.message : String(e)}`, expanded: true }, ...p]);
    } finally { setLoading(false); }
  }, [method, url, hdrs, prms, body]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe weight="duotone" className="w-5 h-5 text-accent" />
          <h2 className="text-lg font-semibold">API Client</h2>
          <Badge variant="outline" className="text-xs">GET · POST · PUT · PATCH · DELETE</Badge>
        </div>
        {entries.length > 0 && <Button size="sm" variant="ghost" onClick={() => setEntries([])}><Trash className="w-4 h-4 mr-1" />Clear</Button>}
      </div>

      <div className="flex flex-wrap gap-1">
        {PRESETS.map(p => (
          <Button key={p.label} size="sm" variant="outline" className="text-xs h-6 px-2"
            onClick={() => { setMethod(p.method); setUrl(p.url); setBody(p.body); }}>
            <span className={`mr-1 text-[10px] font-bold ${METHOD_COLORS[p.method].split(' ')[1]}`}>{p.method}</span>{p.label}
          </Button>
        ))}
      </div>

      <Card className="p-4 space-y-3">
        <div className="flex gap-2">
          <select value={method} onChange={e => setMethod(e.target.value as HttpMethod)}
            className={`shrink-0 rounded border px-2 py-1.5 text-sm font-bold font-mono bg-background ${METHOD_COLORS[method]}`}>
            {(['GET','POST','PUT','PATCH','DELETE'] as HttpMethod[]).map(m => <option key={m} value={m}>{m}</option>)}
          </select>
          <Input value={url} onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key==='Enter' && !loading && send()}
            placeholder="https://…" className="flex-1 font-mono text-sm" />
          <Button onClick={send} disabled={loading||!url.trim()} className="shrink-0">
            {loading ? <span className="animate-spin mr-1">⏳</span> : <ArrowRight className="w-4 h-4 mr-1" />}Send
          </Button>
        </div>

        <div>
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => setShowH(v=>!v)}>
            {showH ? <CaretDown className="w-3 h-3" /> : <CaretRight className="w-3 h-3" />}Headers (JSON)
          </button>
          {showH && <Textarea value={hdrs} onChange={e=>setHdrs(e.target.value)} className="mt-1 font-mono text-xs h-20 resize-none" placeholder='{ "Authorization": "Bearer …" }' />}
        </div>
        <div>
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground" onClick={() => setShowP(v=>!v)}>
            {showP ? <CaretDown className="w-3 h-3" /> : <CaretRight className="w-3 h-3" />}Query params (JSON)
          </button>
          {showP && <Textarea value={prms} onChange={e=>setPrms(e.target.value)} className="mt-1 font-mono text-xs h-16 resize-none" placeholder='{ "per_page": "10" }' />}
        </div>
        {method !== 'GET' && (
          <div>
            <label className="text-xs text-muted-foreground">Body (JSON)</label>
            <Textarea value={body} onChange={e=>setBody(e.target.value)} className="mt-1 font-mono text-xs h-28 resize-none" placeholder='{ "key": "value" }' />
          </div>
        )}
      </Card>

      {entries.map(en => (
        <Card key={en.id} className="overflow-hidden">
          <button className="w-full flex items-center gap-3 px-4 py-2 hover:bg-accent/5 text-left"
            onClick={() => setEntries(p => p.map(e => e.id===en.id ? {...e, expanded:!e.expanded} : e))}>
            <Badge className={`text-xs font-bold shrink-0 border ${METHOD_COLORS[en.method]}`}>{en.method}</Badge>
            <span className={`text-sm font-bold shrink-0 ${statusColor(en.statusCode)}`}>{en.statusCode||'—'}</span>
            <span className="flex-1 text-xs font-mono truncate text-muted-foreground">{en.url}</span>
            <span className="flex items-center gap-1 text-xs text-muted-foreground shrink-0"><Clock className="w-3 h-3"/>{en.durationMs.toFixed(0)}ms</span>
            {en.error ? <XCircle className="w-4 h-4 text-red-400 shrink-0"/> : <CheckCircle className="w-4 h-4 text-green-400 shrink-0"/>}
            {en.expanded ? <CaretDown className="w-3 h-3 text-muted-foreground"/> : <CaretRight className="w-3 h-3 text-muted-foreground"/>}
          </button>
          {en.expanded && (
            <div className="border-t border-border">
              {en.error && <div className="px-4 py-2 text-sm text-red-400 font-mono">{en.error}</div>}
              <div className="relative">
                <Button size="sm" variant="ghost" className="absolute top-2 right-2 z-10 h-6 px-2 text-xs opacity-60 hover:opacity-100"
                  onClick={() => navigator.clipboard.writeText(JSON.stringify(en.body, null, 2)).catch(()=>{})}>
                  <Copy className="w-3 h-3 mr-1"/>Copy
                </Button>
                <ScrollArea className="max-h-60">
                  <pre className="px-4 py-3 text-xs font-mono text-foreground/90 whitespace-pre-wrap break-all">
                    {typeof en.body==='string' ? en.body : JSON.stringify(en.body, null, 2)}
                  </pre>
                </ScrollArea>
              </div>
            </div>
          )}
        </Card>
      ))}
    </div>
  );
}
