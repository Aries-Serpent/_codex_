/**
 * Client-side full-text search for the documentation catalog.
 *
 * Builds an inverted index over titles, tags, descriptions and (optionally)
 * loaded content.  Results are sorted by tf-idf-like score.
 * Query results are memoised with a SHA-256-keyed cache (TTL 5 min).
 */

import { DOC_CATALOG, DocEntry } from './documentation-data';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface SearchResult {
  entry: DocEntry;
  score: number;
  matchedFields: string[];
}

// ---------------------------------------------------------------------------
// SHA-256 utility (Web Crypto — available in secure contexts + Vite env)
// Falls back to a fast djb2 hash string when crypto.subtle is unavailable.
// ---------------------------------------------------------------------------

async function sha256(text: string): Promise<string> {
  try {
    const encoder = new TextEncoder();
    const data = encoder.encode(text);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map((b) => b.toString(16).padStart(2, '0')).join('');
  } catch {
    // Fallback: djb2 hash (non-cryptographic but sufficient for cache keying)
    let h = 5381;
    for (let i = 0; i < text.length; i++) {
      h = ((h << 5) + h) ^ text.charCodeAt(i);
    }
    return `djb2-${(h >>> 0).toString(16)}`;
  }
}

// ---------------------------------------------------------------------------
// In-memory cache
// ---------------------------------------------------------------------------

interface CacheEntry {
  results: SearchResult[];
  timestamp: number;
}

const CACHE_TTL_MS = 5 * 60 * 1000; // 5 minutes
const queryCache = new Map<string, CacheEntry>();

function cacheGet(key: string): SearchResult[] | null {
  const entry = queryCache.get(key);
  if (!entry) return null;
  if (Date.now() - entry.timestamp > CACHE_TTL_MS) {
    queryCache.delete(key);
    return null;
  }
  return entry.results;
}

function cachePut(key: string, results: SearchResult[]): void {
  queryCache.set(key, { results, timestamp: Date.now() });
}

// ---------------------------------------------------------------------------
// Inverted index
// ---------------------------------------------------------------------------

interface IndexEntry {
  entryId: string;
  field: string;
  terms: string[];
}

let _index: IndexEntry[] | null = null;

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, ' ')
    .split(/\s+/)
    .filter((t) => t.length > 1);
}

function buildIndex(): IndexEntry[] {
  return DOC_CATALOG.flatMap((entry) => [
    { entryId: entry.id, field: 'title', terms: tokenize(entry.title) },
    { entryId: entry.id, field: 'category', terms: tokenize(entry.category) },
    { entryId: entry.id, field: 'tags', terms: entry.tags.flatMap(tokenize) },
    {
      entryId: entry.id,
      field: 'description',
      terms: tokenize(entry.description ?? ''),
    },
    { entryId: entry.id, field: 'path', terms: tokenize(entry.path) },
  ]);
}

function getIndex(): IndexEntry[] {
  if (!_index) _index = buildIndex();
  return _index;
}

// Field score weights
const FIELD_WEIGHTS: Record<string, number> = {
  title: 10,
  tags: 6,
  category: 4,
  description: 2,
  path: 1,
};

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Search the documentation catalog.
 *
 * @param rawQuery - User-supplied query string
 * @returns Ranked list of matching DocEntry results
 */
export async function searchDocs(rawQuery: string): Promise<SearchResult[]> {
  const query = rawQuery.trim();
  if (!query) return [];

  const cacheKey = await sha256(query.toLowerCase());
  const cached = cacheGet(cacheKey);
  if (cached) return cached;

  const queryTerms = tokenize(query);
  const index = getIndex();

  // Accumulate scores per entry
  const scores: Record<string, { score: number; matchedFields: Set<string> }> =
    {};

  for (const entry of DOC_CATALOG) {
    scores[entry.id] = { score: 0, matchedFields: new Set() };
  }

  for (const indexEntry of index) {
    const weight = FIELD_WEIGHTS[indexEntry.field] ?? 1;
    for (const term of queryTerms) {
      const exactMatches = indexEntry.terms.filter((t) => t === term).length;
      const partialMatches = indexEntry.terms.filter(
        (t) => t !== term && t.includes(term),
      ).length;

      if (exactMatches > 0) {
        scores[indexEntry.entryId].score += weight * exactMatches * 2;
        scores[indexEntry.entryId].matchedFields.add(indexEntry.field);
      }
      if (partialMatches > 0) {
        scores[indexEntry.entryId].score += weight * partialMatches;
        scores[indexEntry.entryId].matchedFields.add(indexEntry.field);
      }
    }
  }

  const results: SearchResult[] = DOC_CATALOG.filter(
    (e) => scores[e.id].score > 0,
  )
    .map((e) => ({
      entry: e,
      score: scores[e.id].score,
      matchedFields: [...scores[e.id].matchedFields],
    }))
    .sort((a, b) => b.score - a.score);

  cachePut(cacheKey, results);
  return results;
}

/** Invalidate the entire query cache (e.g. after loading new content). */
export function invalidateSearchCache(): void {
  queryCache.clear();
  _index = null;
}
