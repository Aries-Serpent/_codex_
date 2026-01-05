import { useState, useEffect, useCallback } from 'react';
import { CodexAPIClient, MemoryStateResponse, MemoryEntry } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';

const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_CODEX_KEY || 'demo-key';

const client = new CodexAPIClient(API_URL, API_KEY);
const mockClient = new MockCodexAPIClient();

export function useMemorySystem(autoRefresh = false, intervalMs = 10000) {
  const [state, setState] = useState<MemoryStateResponse | null>(null);
  const [searchResults, setSearchResults] = useState<MemoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchState = useCallback(async () => {
    try {
      setError(null);
      const data = await client.getMemoryState();
      setState(data);
    } catch (err) {
      try {
        const mockData = await mockClient.getMemoryState();
        setState(mockData);
        setError(null);
      } catch (mockErr) {
        setError(err instanceof Error ? err.message : 'Failed to fetch memory state');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const searchMemories = useCallback(async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    try {
      setSearching(true);
      setError(null);
      const results = await client.searchMemories(query);
      setSearchResults(results);
    } catch (err) {
      try {
        const mockResults = await mockClient.searchMemories(query);
        setSearchResults(mockResults);
        setError(null);
      } catch (mockErr) {
        setError(err instanceof Error ? err.message : 'Failed to search memories');
      }
    } finally {
      setSearching(false);
    }
  }, []);

  useEffect(() => {
    fetchState();

    if (autoRefresh) {
      const interval = setInterval(fetchState, intervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchState, autoRefresh, intervalMs]);

  return { 
    state, 
    searchResults, 
    loading, 
    searching, 
    error, 
    searchMemories, 
    refetch: fetchState 
  };
}
