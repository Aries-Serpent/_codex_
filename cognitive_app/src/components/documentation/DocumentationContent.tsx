/**
 * DocumentationContent — renders fetched Markdown as sanitized HTML.
 *
 * Uses the `marked` library for Markdown → HTML conversion.
 * Mermaid fenced code blocks (```mermaid) are extracted and rendered
 * via <MermaidDiagram>.
 * GitHub-flavoured links of the form `[file:path]` are converted to
 * in-app navigation callbacks.
 */

import React, { useMemo } from 'react';
import { MermaidDiagram } from './MermaidDiagram';

interface DocumentationContentProps {
  markdown: string;
  onNavigate?: (docId: string) => void;
  className?: string;
}

// Simple HTML sanitizer — strips <script> and event attributes
function sanitize(html: string): string {
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/\s+on\w+="[^"]*"/gi, '')
    .replace(/\s+on\w+='[^']*'/gi, '');
}

// Split markdown into text segments and mermaid blocks
interface Segment {
  type: 'markdown' | 'mermaid';
  content: string;
}

function splitSegments(markdown: string): Segment[] {
  const segments: Segment[] = [];
  const mermaidRe = /```mermaid\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = mermaidRe.exec(markdown)) !== null) {
    if (match.index > lastIndex) {
      segments.push({
        type: 'markdown',
        content: markdown.slice(lastIndex, match.index),
      });
    }
    segments.push({ type: 'mermaid', content: match[1].trim() });
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < markdown.length) {
    segments.push({ type: 'markdown', content: markdown.slice(lastIndex) });
  }
  return segments;
}

// Convert [file:some/path.md] → clickable spans
function processFileLinks(
  html: string,
  onNavigate?: (id: string) => void,
): string {
  if (!onNavigate) return html;
  // We embed a data-docid attribute and handle in the click handler below
  return html.replace(
    /\[file:([^\]]+)\]/g,
    (_, path: string) =>
      `<span class="doc-file-link cursor-pointer text-accent underline underline-offset-2" data-docid="${path}">${path}</span>`,
  );
}

export const DocumentationContent: React.FC<DocumentationContentProps> = ({
  markdown,
  onNavigate,
  className = '',
}) => {
  const segments = useMemo(() => splitSegments(markdown), [markdown]);

  const renderMarkdown = (md: string): string => {
    // Inline marked asynchronously — fall back to preformatted if unavailable
    try {
      // Dynamic require at call-site avoids top-level await
      // eslint-disable-next-line @typescript-eslint/no-var-requires
      const { marked } = require('marked') as typeof import('marked');
      const raw = marked.parse(md, { async: false }) as string;
      return sanitize(processFileLinks(raw, onNavigate));
    } catch {
      return `<pre class="font-mono text-sm whitespace-pre-wrap">${md
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')}</pre>`;
    }
  };

  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    const docId = target.getAttribute('data-docid');
    if (docId && onNavigate) {
      e.preventDefault();
      onNavigate(docId);
    }
  };

  return (
    <div className={`doc-content ${className}`} onClick={handleClick}>
      {segments.map((seg, i) =>
        seg.type === 'mermaid' ? (
          <MermaidDiagram key={i} chart={seg.content} className="my-6" />
        ) : (
          <div
            key={i}
            className="prose prose-sm prose-invert max-w-none leading-relaxed"
            // eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{ __html: renderMarkdown(seg.content) }}
          />
        ),
      )}
    </div>
  );
};
