/**
 * DocumentationContent — renders fetched Markdown as sanitized HTML.
 *
 * Uses the `marked` library for Markdown → HTML conversion.
 * Mermaid fenced code blocks (```mermaid) are extracted and rendered
 * via <MermaidDiagram>.
 * Math expressions ($$...$$  block, $...$ inline) are rendered via KaTeX.
 * GitHub-flavoured links of the form `[file:path]` are converted to
 * in-app navigation callbacks.
 * Template variables ({{var}}) are substituted via DocVariableContext.
 *
 * Content originates from the repository's own Markdown files (trusted
 * source). The sanitizer strips all event handlers, javascript: URLs,
 * <script>, <iframe>, and <object> elements before rendering.
 */

import React, { useMemo, useContext } from 'react';
import { marked } from 'marked';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import { MermaidDiagram } from './MermaidDiagram';
import { DocVariableContext, applyVariables } from './DocVariableContext';

interface DocumentationContentProps {
  markdown: string;
  onNavigate?: (docId: string) => void;
  className?: string;
}

// HTML sanitizer — removes dangerous tags and attributes using DOMParser.
//
// Using DOMParser (browser-native) instead of regex is more robust: it
// handles all malformed markup edge-cases that regex approaches miss
// (e.g. `<script >`, event handlers without leading whitespace, mixed-case
// tag names, CDATA sections, etc.).
//
// Dangerous element types are removed from the parsed DOM tree entirely.
// On every remaining element, event-handler attributes (on*) are stripped
// and URL attributes are checked against an allowlist of safe schemes.
//
// A conservative HTML-entity-encoding fallback is provided for non-browser contexts.
function sanitize(html: string): string {
  if (typeof document === 'undefined') {
    // Non-browser (SSR/test) fallback: encode every character that has HTML
    // special meaning so nothing in the string can be interpreted as markup.
    return html
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }

  const parser = new DOMParser();
  const doc = parser.parseFromString(html, 'text/html');

  // Remove dangerous element types entirely
  const DANGEROUS_TAGS = [
    'script', 'iframe', 'object', 'embed', 'link', 'meta',
    'base', 'form', 'input', 'button', 'select', 'textarea',
    'style', 'frame', 'frameset', 'applet', 'svg', 'math',
  ];
  DANGEROUS_TAGS.forEach((tag) => {
    doc.querySelectorAll(tag).forEach((el) => el.remove());
  });

  // Attributes that carry URLs and therefore need scheme validation
  const URL_ATTRS = new Set([
    'href', 'src', 'action', 'xlink:href', 'formaction',
    'data', 'poster', 'background', 'cite', 'longdesc',
  ]);

  // Allowlist: only these URL schemes are considered safe.
  // This is safer than a denylist because it automatically blocks new
  // dangerous schemes (vbscript:, blob:, file:, etc.) without explicit listing.
  const SAFE_URL_RE = /^\s*(https?:|mailto:|#|\/)/i;

  // On every remaining element, strip dangerous attributes
  doc.querySelectorAll('*').forEach((el) => {
    const toRemove: string[] = [];
    for (const attr of Array.from(el.attributes)) {
      const name = attr.name.toLowerCase();
      const value = attr.value;

      // Remove all event-handler attributes (onclick, onmouseover, etc.)
      if (name.startsWith('on')) {
        toRemove.push(attr.name);
        continue;
      }

      // Remove srcdoc (embeds arbitrary HTML)
      if (name === 'srcdoc') {
        toRemove.push(attr.name);
        continue;
      }

      // For URL attributes: only allow safe schemes (allowlist approach)
      if (URL_ATTRS.has(name) && value.trim() !== '' && !SAFE_URL_RE.test(value)) {
        toRemove.push(attr.name);
        continue;
      }
    }
    toRemove.forEach((n) => el.removeAttribute(n));
  });

  return doc.body.innerHTML;
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

// ---------------------------------------------------------------------------
// KaTeX math rendering
// ---------------------------------------------------------------------------

/**
 * Render a KaTeX math expression to HTML.
 * Returns an error span on parse failure (never throws).
 */
function renderMath(expr: string, displayMode: boolean): string {
  try {
    return katex.renderToString(expr, {
      displayMode,
      throwOnError: false,
      strict: 'warn',
      trust: false,
    });
  } catch {
    const safe = escapeHtml(expr);
    return `<span class="katex-error text-destructive font-mono text-xs">${safe}</span>`;
  }
}

/**
 * Pre-process Markdown text, replacing math delimiters with KaTeX HTML.
 *
 * Handles (in order):
 *   1. Display math: $$...$$
 *   2. Inline math:  $...$
 *
 * The replacement runs BEFORE marked.parse() so that marked doesn't
 * try to parse the math expressions as Markdown.
 */
function processMath(md: string): string {
  // Display math: $$...$$  (non-greedy, allow newlines)
  let result = md.replace(/\$\$([\s\S]+?)\$\$/g, (_, expr: string) => {
    return renderMath(expr.trim(), true);
  });
  // Inline math: $...$  (no newlines allowed inside)
  result = result.replace(/\$([^\n$]+?)\$/g, (_, expr: string) => {
    return renderMath(expr.trim(), false);
  });
  return result;
}

// ---------------------------------------------------------------------------
// Segment splitting (Mermaid blocks + markdown/math)
// ---------------------------------------------------------------------------

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
  const variables = useContext(DocVariableContext);

  // Apply {{var}} template substitution using the shared utility, then split into segments
  const segments = useMemo(() => {
    const processed = variables.size > 0 ? applyVariables(markdown, variables) : markdown;
    return splitSegments(processed);
  }, [markdown, variables]);

  const renderMarkdown = (md: string): string => {
    try {
      // Process math BEFORE markdown parsing to preserve LaTeX syntax
      const mathProcessed = processMath(md);
      const raw = marked.parse(mathProcessed, { async: false }) as string;
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
