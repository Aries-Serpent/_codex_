/**
 * DocumentationViewer — full-featured documentation browser.
 *
 * Layout:
 *   ┌──────────────┬────────────────────────────┐
 *   │  Sidebar     │  Content pane              │
 *   │  (search +   │  (rendered Markdown)       │
 *   │   catalog)   │                            │
 *   └──────────────┴────────────────────────────┘
 *
 * State is synced to the URL as `?doc=<id>`.
 * Content is fetched from the GitHub raw API (live) or falls back to
 * a static placeholder (offline / demo mode).
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MagnifyingGlass, FileText, CaretRight, X } from '@phosphor-icons/react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { DocumentationContent } from './DocumentationContent';
import {
  DOC_CATALOG,
  DOC_CATEGORIES,
  DocEntry,
  getDocById,
} from './documentation-data';
import { searchDocs, SearchResult } from './documentation-search';

// ---------------------------------------------------------------------------
// Content fetching (GitHub raw — gracefully degrades to placeholder)
// ---------------------------------------------------------------------------

const REPO = 'Aries-Serpent/_codex_';
const BRANCH = '0D_base_';

async function fetchDocContent(path: string): Promise<string> {
  try {
    const url = `https://raw.githubusercontent.com/${REPO}/${BRANCH}/${path}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.text();
  } catch {
    // Escape backslashes first, then other Markdown special characters,
    // so that existing backslashes in the path cannot be used to escape
    // the surrounding backtick code-span delimiter.
    const safePath = path.replace(/\\/g, '\\\\').replace(/[`*_[\]()]/g, '\\$&');
    return `_Content for \`${safePath}\` is not available in offline/demo mode._\n\nConnect to GitHub to load live documentation.`;
  }
}

// ---------------------------------------------------------------------------
// Sidebar item component
// ---------------------------------------------------------------------------

const SidebarItem: React.FC<{
  entry: DocEntry;
  active: boolean;
  onSelect: (id: string) => void;
}> = ({ entry, active, onSelect }) => (
  <button
    className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors flex items-start gap-2 group ${
      active
        ? 'bg-accent/20 text-accent font-medium'
        : 'text-muted-foreground hover:bg-muted/60 hover:text-foreground'
    }`}
    onClick={() => onSelect(entry.id)}
  >
    <FileText
      weight={active ? 'fill' : 'regular'}
      className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${active ? 'text-accent' : 'text-muted-foreground group-hover:text-foreground'}`}
    />
    <span className="leading-tight">{entry.title}</span>
    {active && (
      <CaretRight className="ml-auto mt-0.5 h-3.5 w-3.5 shrink-0 text-accent" />
    )}
  </button>
);

// ---------------------------------------------------------------------------
// Main component
// ---------------------------------------------------------------------------

export const DocumentationViewer: React.FC = () => {
  // Sync active doc with URL ?doc= param
  const getInitialDocId = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get('doc') ?? DOC_CATALOG[0]?.id ?? '';
  };

  const [activeDocId, setActiveDocId] = useState<string>(getInitialDocId);
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Load content when active doc changes
  useEffect(() => {
    const entry = getDocById(activeDocId);
    if (!entry) return;

    setLoading(true);
    setContent('');

    fetchDocContent(entry.path).then((text) => {
      setContent(text);
      setLoading(false);
    });

    // Update URL
    const url = new URL(window.location.href);
    url.searchParams.set('doc', activeDocId);
    window.history.replaceState(null, '', url.toString());
  }, [activeDocId]);

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(async () => {
      if (!searchQuery.trim()) {
        setSearchResults([]);
        return;
      }
      const results = await searchDocs(searchQuery);
      setSearchResults(results);
    }, 250);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [searchQuery]);

  const handleSelect = useCallback((id: string) => {
    setActiveDocId(id);
    setSearchQuery('');
    setSearchResults([]);
  }, []);

  const handleNavigate = useCallback((pathOrId: string) => {
    // Try matching by path first, then by id
    const found =
      DOC_CATALOG.find((e) => e.path === pathOrId) ??
      DOC_CATALOG.find((e) => e.id === pathOrId);
    if (found) setActiveDocId(found.id);
  }, []);

  // Filtered catalog for sidebar
  const filteredCatalog =
    searchResults.length > 0
      ? searchResults.map((r) => r.entry)
      : activeCategory
        ? DOC_CATALOG.filter((e) => e.category === activeCategory)
        : DOC_CATALOG;

  const activeEntry = getDocById(activeDocId);

  return (
    <div className="flex h-[calc(100vh-14rem)] min-h-[500px] gap-0 rounded-xl border border-border overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 flex flex-col border-r border-border bg-muted/20">
        {/* Search */}
        <div className="p-3 border-b border-border">
          <div className="relative">
            <MagnifyingGlass className="absolute left-2.5 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Search docs…"
              className="pl-8 pr-8 h-8 text-sm bg-background"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                onClick={() => setSearchQuery('')}
              >
                <X className="h-3.5 w-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Category filter chips */}
        {!searchQuery && (
          <div className="flex flex-wrap gap-1.5 p-2 border-b border-border">
            <Button
              size="sm"
              variant={activeCategory === null ? 'secondary' : 'ghost'}
              className="h-6 text-xs px-2"
              onClick={() => setActiveCategory(null)}
            >
              All
            </Button>
            {DOC_CATEGORIES.map((cat) => (
              <Button
                key={cat}
                size="sm"
                variant={activeCategory === cat ? 'secondary' : 'ghost'}
                className="h-6 text-xs px-2"
                onClick={() =>
                  setActiveCategory(activeCategory === cat ? null : cat)
                }
              >
                {cat}
              </Button>
            ))}
          </div>
        )}

        {/* Document list */}
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-0.5">
            {searchResults.length > 0 && (
              <p className="text-xs text-muted-foreground px-2 py-1">
                {searchResults.length} result{searchResults.length !== 1 ? 's' : ''}
              </p>
            )}
            {filteredCatalog.map((entry) => (
              <SidebarItem
                key={entry.id}
                entry={entry}
                active={entry.id === activeDocId}
                onSelect={handleSelect}
              />
            ))}
          </div>
        </ScrollArea>
      </aside>

      {/* Content pane */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        {activeEntry && (
          <div className="flex items-center gap-3 px-5 py-3 border-b border-border bg-muted/10 shrink-0">
            <FileText weight="duotone" className="h-4 w-4 text-accent shrink-0" />
            <div className="flex-1 min-w-0">
              <h2 className="text-sm font-semibold truncate">{activeEntry.title}</h2>
              <p className="text-xs text-muted-foreground truncate">{activeEntry.path}</p>
            </div>
            <div className="flex items-center gap-1.5 shrink-0">
              <Badge variant="secondary" className="text-xs">{activeEntry.category}</Badge>
              {activeEntry.tags.slice(0, 2).map((tag) => (
                <Badge key={tag} variant="outline" className="text-xs">{tag}</Badge>
              ))}
            </div>
          </div>
        )}

        <Separator />

        {/* Scrollable content */}
        <ScrollArea className="flex-1 p-6">
          {loading ? (
            <div className="flex flex-col gap-3 animate-pulse">
              {[...Array(6)].map((_, i) => (
                <div
                  key={i}
                  className="h-4 rounded bg-muted"
                  style={{ width: `${60 + Math.random() * 40}%` }}
                />
              ))}
            </div>
          ) : (
            <DocumentationContent
              markdown={content}
              onNavigate={handleNavigate}
              className="max-w-4xl"
            />
          )}
        </ScrollArea>
      </div>
    </div>
  );
};
