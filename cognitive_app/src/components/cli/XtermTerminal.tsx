/**
 * XtermTerminal — real PTY WebSocket terminal using xterm.js (P4.4)
 *
 * Replaces the textarea-based CliTerminal for full ANSI/colour/cursor support.
 * Connects to the /ws/cli PTY endpoint on the FastAPI server at :8765.
 */
import { useEffect, useRef } from 'react';
import { ensureBrainSession, getBrainAPIURL } from '@/lib/brain-session';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

const API_BASE = getBrainAPIURL();
const WS_BASE  = API_BASE.replace(/^http/, 'ws');

export function XtermTerminal() {
  const containerRef = useRef<HTMLDivElement>(null);
  const termRef      = useRef<Terminal | null>(null);
  const wsRef        = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const term = new Terminal({
      cursorBlink: true,
      theme: { background: '#0d0d0d', foreground: '#d4d4d4' },
      fontFamily: '"Cascadia Code", "JetBrains Mono", monospace',
      fontSize: 13,
    });
    const fit   = new FitAddon();
    const links = new WebLinksAddon();
    term.loadAddon(fit);
    term.loadAddon(links);
    term.open(containerRef.current);
    fit.fit();
    termRef.current = term;

    let cancelled = false;
    const handleResize = () => {
      fit.fit();
      const ws = wsRef.current;
      if (ws?.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
      }
    };
    window.addEventListener('resize', handleResize);

    void ensureBrainSession(API_BASE).then((authenticated) => {
      if (cancelled) return;
      if (!authenticated) {
        term.write('\r\n\x1b[31m[session denied]\x1b[0m\r\n');
        return;
      }

      const ws = new WebSocket(`${WS_BASE}/ws/cli`);
      wsRef.current = ws;
      ws.onopen = () => {
        ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
      };
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data as string);
          if (msg.type === 'output') term.write(msg.data as string);
        } catch {
          term.write(e.data as string);
        }
      };
      ws.onclose = () => term.write('\r\n\x1b[90m[connection closed]\x1b[0m\r\n');
      ws.onerror = () => term.write('\r\n\x1b[31m[WebSocket error]\x1b[0m\r\n');
      term.onData((data) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'input', data }));
        }
      });
    });

    return () => {
      cancelled = true;
      window.removeEventListener('resize', handleResize);
      wsRef.current?.close();
      term.dispose();
    };
  }, []);

  return (
    <div
      ref={containerRef}
      className="h-full w-full bg-[#0d0d0d] rounded-md overflow-hidden"
      style={{ minHeight: '300px' }}
    />
  );
}
