/**
 * DocumentationContent — renders fetched Markdown as sanitized HTML.
 *
 * Uses the `marked` library for Markdown → HTML conversion.
 * Mermaid fenced code blocks (```mermaid) are extracted and rendered
 * via <MermaidDiagram>.
 * GitHub-flavoured links of the form `[file:path]` are converted to
 * in-app navigation callbacks.
 *
 * Content originates from the repository's own Markdown files (trusted
 * source). The sanitizer strips all event handlers, javascript: URLs,
 * <script>, <iframe>, and <object> elements before rendering.
 */

import React, { useMemo } from 'react';
import { marked } from 'marked';
import { MermaidDiagram } from './MermaidDiagram';

interface DocumentationContentProps {
  markdown: string;
  onNavigate?: (docId: string) => void;
  className?: string;
}

// HTML sanitizer — removes dangerous tags and attributes.
// Strips <script>, <iframe>, <object>, <embed>, event handlers, and
// javascript:/data: URL schemes before the HTML reaches the DOM.
function sanitize(html: string): string {
  return html
    // Remove script, iframe, object, embed blocks entirely
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
    .replace(/<embed\b[^>]*>/gi, '')
    // Remove inline event handlers (on*)
    .replace(/\s+on\w+\s*=\s*"[^"]*"/gi, '')
    .replace(/\s+on\w+\s*=\s*'[^']*'/gi, '')
    .replace(/\s+on\w+\s*=\s*[^\s>]*/gi, '')
    // Strip javascript: and data: URL schemes from href/src attributes
    .replace(/(href|src)\s*=\s*["']\s*javascript:[^"']*/gi, '$1="#"')
    .replace(/(href|src)\s*=\s*["']\s*data:[^"']*/gi, '$1="#"');
}

// Escape a string for safe insertion into HTML attribute values
function escapeAttr(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/"/g, '&quot;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// Escape a string for safe display as HTML text content
function escapeHtml(s: string): string {
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
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

// Convert [file:some/path.md] → clickable spans with safe attribute values
function processFileLinks(
  html: string,
  onNavigate?: (id: string) => void,
): string {
  if (!onNavigate) return html;
  return html.replace(
    /\[file:([^\]]+)\]/g,
    (_, rawPath: string) => {
      const safePath = escapeAttr(rawPath);
      const displayPath = escapeHtml(rawPath);
      return `<span class="doc-file-link cursor-pointer text-accent underline underline-offset-2" data-docid="${safePath}">${displayPath}</span>`;
    },
  );
}

export const DocumentationContent: React.FC<DocumentationContentProps> = ({
  markdown,
  onNavigate,
  className = '',
}) => {
  const segments = useMemo(() => splitSegments(markdown), [markdown]);

  const renderMarkdown = (md: string): string => {
    try {
      const raw = marked.parse(md, { async: false }) as string;
      return sanitize(processFileLinks(raw, onNavigate));
    } catch {
      return `<pre class="font-mono text-sm whitespace-pre-wrap">${escapeHtml(md)}</pre>`;
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
