import { useState, useEffect, useCallback } from 'react';
import { CodexAPIClient, DashboardMetrics } from '@/lib/codex-api-client';

const client = new CodexAPIClient();

export function useDashboardMetrics(autoRefresh = true, intervalMs = 10000) {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setError(null);
      const data = await client.getDashboardMetrics();
      setMetrics(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch dashboard metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();

    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, intervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchMetrics, autoRefresh, intervalMs]);

  return { metrics, loading, error, refetch: fetchMetrics };
}
