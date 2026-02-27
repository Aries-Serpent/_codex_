import { useState, useEffect, useCallback } from 'react';
import { CodexAPIClient } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';

const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_CODEX_KEY || 'demo-key';

const client = new CodexAPIClient(API_URL, API_KEY);
const mockClient = new MockCodexAPIClient();

export interface MSVMetrics {
  correctness_awareness: number;
  conflict_detection: number;
  importance_assessment: number;
  experience_matching: number;
  adaptive_response: number;
  composite_score: number;
  timestamp: string;
  phase: string;
}

/**
 * Hook for fetching Metacognitive State Vector (MSV) metrics from cognitive brain.
 *
 * MSV measures AI self-awareness across 5 cognitive dimensions:
 * - Correctness Awareness: Test coverage, CodeQL integration
 * - Conflict Detection: Split-brain elimination, config consolidation
 * - Importance Assessment: Priority-based plansets, phase-gating
 * - Experience Matching: Pattern detection, meta-learning
 * - Adaptive Response: CI auto-fix, self-healing iterations
 *
 * @param autoRefresh - Whether to automatically refresh metrics
 * @param intervalMs - Refresh interval in milliseconds (default: 10000)
 * @returns MSV metrics, loading state, error, and refetch function
 */
export function useMSVMetrics(autoRefresh = false, intervalMs = 10000) {
  const [metrics, setMetrics] = useState<MSVMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchMetrics = useCallback(async () => {
    try {
      setError(null);

      // Try to fetch from API endpoint
      const response = await client.get('/api/cognitive/msv-metrics');
      setMetrics(response as MSVMetrics);
    } catch (err) {
      try {
        // Fallback to mock data
        const mockData = await mockClient.getMSVMetrics();
        setMetrics(mockData);
        setError(null);
      } catch (mockErr) {
        const primaryMessage = err instanceof Error ? err.message : 'unknown primary error';
        const fallbackMessage = mockErr instanceof Error ? mockErr.message : 'unknown fallback error';
        setError(
          `Failed to fetch MSV metrics from both production and fallback sources. Primary error: ${primaryMessage}. Fallback error: ${fallbackMessage}.`
        );
      }
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
