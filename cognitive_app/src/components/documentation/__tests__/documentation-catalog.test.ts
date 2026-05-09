/**
 * Tests for documentation-data catalog helpers and documentation-search.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  DOC_CATALOG,
  DOC_CATEGORIES,
  getDocById,
  getDocsByCategory,
} from '../documentation-data';
import { searchDocs, invalidateSearchCache } from '../documentation-search';

// ---------------------------------------------------------------------------
// documentation-data
// ---------------------------------------------------------------------------

describe('DOC_CATALOG', () => {
  it('is a non-empty array', () => {
    expect(DOC_CATALOG.length).toBeGreaterThan(0);
  });

  it('each entry has required fields', () => {
    for (const entry of DOC_CATALOG) {
      expect(typeof entry.id).toBe('string');
      expect(entry.id.length).toBeGreaterThan(0);
      expect(typeof entry.title).toBe('string');
      expect(typeof entry.path).toBe('string');
      expect(typeof entry.category).toBe('string');
      expect(Array.isArray(entry.tags)).toBe(true);
    }
  });

  it('all IDs are unique', () => {
    const ids = DOC_CATALOG.map((e) => e.id);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

describe('DOC_CATEGORIES', () => {
  it('contains unique categories', () => {
    expect(new Set(DOC_CATEGORIES).size).toBe(DOC_CATEGORIES.length);
  });

  it('every catalog entry category is in DOC_CATEGORIES', () => {
    for (const entry of DOC_CATALOG) {
      expect(DOC_CATEGORIES).toContain(entry.category);
    }
  });
});

describe('getDocById', () => {
  it('returns the correct entry for a known id', () => {
    const first = DOC_CATALOG[0];
    const result = getDocById(first.id);
    expect(result).toEqual(first);
  });

  it('returns undefined for an unknown id', () => {
    expect(getDocById('non-existent-id-xyz')).toBeUndefined();
  });
});

describe('getDocsByCategory', () => {
  it('returns only entries matching the category', () => {
    const cat = DOC_CATALOG[0].category;
    const results = getDocsByCategory(cat);
    expect(results.length).toBeGreaterThan(0);
    for (const e of results) {
      expect(e.category).toBe(cat);
    }
  });

  it('returns empty array for an unknown category', () => {
    expect(getDocsByCategory('NonExistentCategory')).toHaveLength(0);
  });
});

// ---------------------------------------------------------------------------
// documentation-search
// ---------------------------------------------------------------------------

describe('searchDocs', () => {
  beforeEach(() => {
    invalidateSearchCache();
  });

  it('returns an empty array for an empty query', async () => {
    const results = await searchDocs('');
    expect(results).toHaveLength(0);
  });

  it('returns an empty array for a whitespace-only query', async () => {
    const results = await searchDocs('   ');
    expect(results).toHaveLength(0);
  });

  it('returns results for a known title word', async () => {
    // "AGENTS" is the title of the first catalog entry
    const results = await searchDocs('agents');
    expect(results.length).toBeGreaterThan(0);
    expect(results[0].score).toBeGreaterThan(0);
    expect(results[0].matchedFields.length).toBeGreaterThan(0);
  });

  it('results are sorted by score descending', async () => {
    const results = await searchDocs('agents');
    for (let i = 1; i < results.length; i++) {
      expect(results[i - 1].score).toBeGreaterThanOrEqual(results[i].score);
    }
  });

  it('returns cached results on repeated calls', async () => {
    const r1 = await searchDocs('readme');
    const r2 = await searchDocs('readme');
    expect(r1).toBe(r2); // same array reference from cache
  });

  it('cache is cleared after invalidateSearchCache', async () => {
    const r1 = await searchDocs('readme');
    invalidateSearchCache();
    const r2 = await searchDocs('readme');
    // Different array references since cache was cleared
    expect(r1).not.toBe(r2);
    // But same content
    expect(r1.map((e) => e.entry.id)).toEqual(r2.map((e) => e.entry.id));
  });

  it('returns no results for a completely unknown term', async () => {
    const results = await searchDocs('zzz_no_match_xyz_abc_999');
    expect(results).toHaveLength(0);
  });
});
