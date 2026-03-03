import { useState, useCallback, useRef } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import {
  Globe, ArrowRight, Trash, Clock, CheckCircle, XCircle,
  Copy, CaretDown, CaretRight
} from '@phosphor-icons/react';

// ── Types ──────────────────────────────────────────────────────────────────

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

interface ApiProxyResponse {
  status_code: number;
  headers: Record<string, string>;
  body: unknown;
  duration_ms: number;
  url: string;
  method: string;
}

// ── Constants ─────────────────────────────────────────────────────────────

const CLI_API = (import.meta.env.VITE_CLI_API_URL as string | undefined) ?? 'http://localhost:8765';

const METHOD_COLORS: Record<HttpMethod, string> = {
  GET:    'bg-blue-500/20 text-blue-300 border-blue-500/40',
  POST:   'bg-green-500/20 text-green-300 border-green-500/40',
  PUT:    'bg-yellow-500/20 text-yellow-300 border-yellow-500/40',
  PATCH:  'bg-orange-500/20 text-orange-300 border-orange-500/40',
  DELETE: 'bg-red-500/20 text-red-300 border-red-500/40',
};

const STATUS_COLOR = (code: number) =>
  code >= 500 ? 'text-red-400' :
  code >= 400 ? 'text-orange-400' :
  code >= 300 ? 'text-yellow-400' :
  code >= 200 ? 'text-green-400' : 'text-muted-foreground';

// Preset endpoints — wired to the cognitive brain / CI server
const PRESETS = [
  { label: 'Brain Health',  method: 'GET'    as HttpMethod, url: 'http://localhost:8765/api/health',        body: '' },
  { label: 'CLI History',   method: 'GET'    as HttpMethod, url: 'http://localhost:8765/api/cli/history',   body: '' },
  { label: 'Clear History', method: 'DELETE' as HttpMethod, url: 'http://localhost:8765/api/cli/history',   body: '' },
  { label: 'Run Command',   method: 'POST'   as HttpMethod, url: 'http://localhost:8765/api/cli/run',
    body: JSON.stringify({ command: 'git status --short', timeout: 10 }, null, 2) },
  { label: 'GH Repo',       method: 'GET'    as HttpMethod, url: 'https://api.github.com/repos/Aries-Serpent/_codex_', body: '' },
  { label: 'GH Runs',       method: 'GET'    as HttpMethod, url: 'https://api.github.com/repos/Aries-Serpent/_codex_/actions/runs?per_page=5', body: '' },
];

// ── Component ─────────────────────────────────────────────────────────────

export function ApiClient() {
  const [method, setMethod]     = useState<HttpMethod>('GET');
  const [url, setUrl]           = useState('http://localhost:8765/api/health');
  const [headers, setHeaders]   = useState('{\n  "Accept": "application/json"\n}');
  const [params, setParams]     = useState('');
  const [body, setBody]         = useState('');
  const [loading, setLoading]   = useState(false);
  const [entries, setEntries]   = useState<ApiEntry[]>([]);
  const [showHeaders, setShowHeaders] = useState(false);
  const [showParams, setShowParams]   = useState(false);

  const entryId = useRef(1);

  const sendRequest = useCallback(async () => {
    setLoading(true);
    const id = entryId.current++;
    const start = Date.now();

    let parsedHeaders: Record<string, string> = {};
    let parsedParams:  Record<string, string> = {};
    let parsedBody: unknown = undefined;

    try { if (headers.trim()) parsedHeaders = JSON.parse(headers); } catch { parsedHeaders = {}; }
    try { if (params.trim())  parsedParams  = JSON.parse(params);  } catch { parsedParams  = {}; }
    try {
      if (body.trim()) parsedBody = JSON.parse(body);
    } catch { parsedBody = body.trim() || undefined; }

    try {
      const resp = await fetch(`${CLI_API}/api/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method, url,
          headers: Object.keys(parsedHeaders).length ? parsedHeaders : undefined,
          params:  Object.keys(parsedParams).length  ? parsedParams  : undefined,
          body:    parsedBody,
          timeout: 30,
        }),
      });

      const data: ApiProxyResponse | { detail: string } = await resp.json().catch(() => ({ detail: resp.statusText }));

      if (!resp.ok || 'detail' in data) {
        setEntries(prev => [{
          id, method, url,
          statusCode: resp.status,
          durationMs: Date.now() - start,
          body: data,

          timestamp: new Date().toISOString(),
          error: ('detail' in data ? data.detail : undefined) || resp.statusText,
          expanded: true,
        }, ...prev]);
        return;
      }

      const r = data as ApiProxyResponse;
      setEntries(prev => [{
        id,
        method: r.method as HttpMethod,
        url: r.url,
        statusCode: r.status_code,
        durationMs: r.duration_ms,
        body: r.body,

        timestamp: new Date().toISOString(),
        expanded: true,
      }, ...prev]);
    } catch (err) {
      // Backend proxy unreachable (e.g. static GitHub Pages deploy without local server).
      // Fall back to a direct browser fetch so public URLs like api.github.com still work.
      if (err instanceof TypeError) {
        try {
          const directUrl = new URL(url);
          for (const [k, v] of Object.entries(parsedParams)) directUrl.searchParams.set(k, v);
          const directResp = await fetch(directUrl.toString(), {
            method,
            headers: Object.keys(parsedHeaders).length ? (parsedHeaders as HeadersInit) : undefined,
            body: method !== 'GET' && method !== 'DELETE' && parsedBody !== undefined
              ? JSON.stringify(parsedBody) : undefined,
          });
          const directData: unknown = await directResp.json().catch(async () => directResp.text());
          setEntries(prev => [{
            id, method, url: directUrl.toString(),
            statusCode: directResp.status,
            durationMs: Date.now() - start,
            body: directData,
            timestamp: new Date().toISOString(),
            expanded: true,
          }, ...prev]);
          return;
        } catch { /* fall through to original error entry */ }
      }
      setEntries(prev => [{
        id, method, url,
        statusCode: 0,
        durationMs: 0,
        body: null,
        timestamp: new Date().toISOString(),
        error: `Network error: ${err instanceof Error ? err.message : String(err)}`,
        expanded: true,
      }, ...prev]);
    } finally {
      setLoading(false);
    }
  }, [method, url, headers, params, body]);

  const applyPreset = (p: typeof PRESETS[0]) => {
    setMethod(p.method);
    setUrl(p.url);
    setBody(p.body);
  };

  const toggleExpanded = (id: number) =>
    setEntries(prev => prev.map(e => e.id === id ? { ...e, expanded: !e.expanded } : e));

  const copyToClipboard = (text: string) =>
    navigator.clipboard.writeText(text).catch(() => {});

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe weight="duotone" className="w-5 h-5 text-accent" />
          <h2 className="text-lg font-semibold">API Client</h2>
          <Badge variant="outline" className="text-xs">GET · POST · PUT · PATCH · DELETE</Badge>
        </div>
        {entries.length > 0 && (
          <Button size="sm" variant="ghost" onClick={() => setEntries([])}>
            <Trash className="w-4 h-4 mr-1" /> Clear
          </Button>
        )}
      </div>

      {/* Presets */}
      <div className="flex flex-wrap gap-1">
        {PRESETS.map(p => (
          <Button key={p.label} size="sm" variant="outline"
            className="text-xs h-6 px-2"
            onClick={() => applyPreset(p)}>
            <span className={`mr-1 text-[10px] font-bold`}>{p.method}</span>
            {p.label}
          </Button>
        ))}
      </div>

      {/* Request builder */}
      <Card className="p-4 space-y-3">
        <div className="flex gap-2">
          <select
            value={method}
            onChange={e => setMethod(e.target.value as HttpMethod)}
            className={`shrink-0 rounded border px-2 py-1.5 text-sm font-bold font-mono bg-background ${METHOD_COLORS[method]}`}>
            {(['GET','POST','PUT','PATCH','DELETE'] as HttpMethod[]).map(m => (
              <option key={m} value={m}>{m}</option>
            ))}
          </select>
          <Input
            value={url}
            onChange={e => setUrl(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !loading && sendRequest()}
            placeholder="https://api.example.com/endpoint"
            className="flex-1 font-mono text-sm"
          />
          <Button onClick={sendRequest} disabled={loading || !url.trim()} className="shrink-0">
            {loading
              ? <span className="animate-spin mr-1 text-xs">⏳</span>
              : <ArrowRight className="w-4 h-4 mr-1" />}
            Send
          </Button>
        </div>

        <div>
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setShowHeaders(v => !v)}>
            {showHeaders ? <CaretDown className="w-3 h-3" /> : <CaretRight className="w-3 h-3" />}
            Headers (JSON)
          </button>
          {showHeaders && (
            <Textarea value={headers} onChange={e => setHeaders(e.target.value)}
              className="mt-1 font-mono text-xs h-20 resize-none"
              placeholder='{ "Authorization": "Bearer ..." }' />
          )}
        </div>

        <div>
          <button className="flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
            onClick={() => setShowParams(v => !v)}>
            {showParams ? <CaretDown className="w-3 h-3" /> : <CaretRight className="w-3 h-3" />}
            Query params (JSON)
          </button>
          {showParams && (
            <Textarea value={params} onChange={e => setParams(e.target.value)}
              className="mt-1 font-mono text-xs h-16 resize-none"
              placeholder='{ "per_page": "10" }' />
          )}
        </div>

        {method !== 'GET' && (
          <div>
            <label className="text-xs text-muted-foreground">Request body (JSON)</label>
            <Textarea value={body} onChange={e => setBody(e.target.value)}
              className="mt-1 font-mono text-xs h-28 resize-none"
              placeholder='{ "key": "value" }' />
          </div>
        )}
      </Card>

      {/* Response history */}
      {entries.length > 0 && (
        <div className="space-y-2">
          <p className="text-xs text-muted-foreground">{entries.length} response{entries.length > 1 ? 's' : ''}</p>
          {entries.map(entry => (
            <Card key={entry.id} className="overflow-hidden">
              <button
                className="w-full flex items-center gap-3 px-4 py-2 hover:bg-accent/5 text-left"
                onClick={() => toggleExpanded(entry.id)}>
                <Badge className={`text-xs font-bold shrink-0 border ${METHOD_COLORS[entry.method]}`}>
                  {entry.method}
                </Badge>
                <span className={`text-sm font-bold shrink-0 ${STATUS_COLOR(entry.statusCode)}`}>
                  {entry.statusCode || '—'}
                </span>
                <span className="flex-1 text-xs font-mono truncate text-muted-foreground">{entry.url}</span>
                <span className="flex items-center gap-1 text-xs text-muted-foreground shrink-0">
                  <Clock className="w-3 h-3" />{entry.durationMs.toFixed(0)}ms
                </span>
                {entry.error
                  ? <XCircle className="w-4 h-4 text-red-400 shrink-0" />
                  : <CheckCircle className="w-4 h-4 text-green-400 shrink-0" />}
                {entry.expanded
                  ? <CaretDown className="w-3 h-3 text-muted-foreground shrink-0" />
                  : <CaretRight className="w-3 h-3 text-muted-foreground shrink-0" />}
              </button>

              {entry.expanded && (
                <div className="border-t border-border">
                  {entry.error && (
                    <div className="px-4 py-2 text-sm text-red-400 font-mono">{entry.error}</div>
                  )}
                  <div className="relative">
                    <Button size="sm" variant="ghost"
                      className="absolute top-2 right-2 z-10 h-6 px-2 text-xs opacity-60 hover:opacity-100"
                      onClick={() => copyToClipboard(JSON.stringify(entry.body, null, 2))}>
                      <Copy className="w-3 h-3 mr-1" /> Copy
                    </Button>
                    <ScrollArea className="max-h-60">
                      <pre className="px-4 py-3 text-xs font-mono text-foreground/90 whitespace-pre-wrap break-all">
                        {typeof entry.body === 'string'
                          ? entry.body
                          : JSON.stringify(entry.body, null, 2)}
                      </pre>
                    </ScrollArea>
                  </div>
                </div>
              )}
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
