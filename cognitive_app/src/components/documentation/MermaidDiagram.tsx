/**
 * MermaidDiagram — renders a Mermaid diagram string as an inline SVG.
 *
 * Features:
 * - Dark-theme aware (uses CSS var --mermaid-theme: dark/default)
 * - Error fallback renders the raw source in a code block
 * - Copy-code button copies the Mermaid source to clipboard
 */

import React, { useEffect, useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Copy, Check, Warning } from '@phosphor-icons/react';

interface MermaidDiagramProps {
  chart: string;
  id?: string;
  className?: string;
}

let mermaidInstance: typeof import('mermaid') | null = null;

async function getMermaid() {
  if (!mermaidInstance) {
    const mod = await import('mermaid');
    mermaidInstance = mod;
    mod.default.initialize({
      startOnLoad: false,
      theme: 'dark',
      securityLevel: 'loose',
      fontFamily: 'inherit',
    });
  }
  return mermaidInstance.default;
}

export const MermaidDiagram: React.FC<MermaidDiagramProps> = ({
  chart,
  id,
  className = '',
}) => {
  const containerId =
    id ?? `mermaid-${Math.random().toString(36).substring(2, 10)}`;
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    let cancelled = false;

    async function render() {
      try {
        setError(null);
        const mermaid = await getMermaid();
        const { svg } = await mermaid.render(containerId, chart);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      }
    }

    render();
    return () => {
      cancelled = true;
    };
  }, [chart, containerId]);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(chart);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`relative group ${className}`}>
      <Button
        size="icon"
        variant="ghost"
        className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity z-10 h-7 w-7"
        onClick={handleCopy}
        title="Copy Mermaid source"
      >
        {copied ? (
          <Check className="h-3.5 w-3.5 text-green-400" />
        ) : (
          <Copy className="h-3.5 w-3.5" />
        )}
      </Button>

      {error ? (
        <div className="flex flex-col gap-2 rounded-md border border-destructive/40 bg-destructive/10 p-4">
          <div className="flex items-center gap-2 text-sm text-destructive font-medium">
            <Warning className="h-4 w-4" weight="fill" />
            Diagram render error
          </div>
          <p className="text-xs text-muted-foreground">{error}</p>
          <pre className="mt-2 overflow-auto rounded bg-muted p-3 text-xs font-mono">
            {chart}
          </pre>
        </div>
      ) : (
        <div
          ref={containerRef}
          className="flex justify-center overflow-auto rounded-md bg-muted/30 p-4 [&_svg]:max-w-full"
        />
      )}
    </div>
  );
};
