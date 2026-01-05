import { useState, useEffect, useCallback } from 'react';
import { CodexAPIClient, QuantumStateResponse } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';

const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_CODEX_KEY || 'demo-key';

const client = new CodexAPIClient(API_URL, API_KEY);
const mockClient = new MockCodexAPIClient();

export function useQuantumState(autoRefresh = false, intervalMs = 10000) {
  const [state, setState] = useState<QuantumStateResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchState = useCallback(async () => {
    try {
      setError(null);
      const data = await client.getQuantumState();
      setState(data);
    } catch (err) {
      try {
        const mockData = await mockClient.getQuantumState();
        setState(mockData);
        setError(null);
      } catch (mockErr) {
        setError(err instanceof Error ? err.message : 'Failed to fetch quantum state');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchState();

    if (autoRefresh) {
      const interval = setInterval(fetchState, intervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchState, autoRefresh, intervalMs]);

  return { state, loading, error, refetch: fetchState };
}
