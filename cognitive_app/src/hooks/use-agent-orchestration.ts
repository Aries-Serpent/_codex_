import { useState, useEffect, useCallback } from 'react';
import { CodexAPIClient, AgentStateResponse } from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';

const API_URL = import.meta.env.VITE_CODEX_API || 'http://localhost:8000';
const API_KEY = import.meta.env.VITE_CODEX_KEY || 'demo-key';

const client = new CodexAPIClient(API_URL, API_KEY);
const mockClient = new MockCodexAPIClient();

export function useAgentOrchestration(autoRefresh = false, intervalMs = 5000) {
  const [state, setState] = useState<AgentStateResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [orchestrating, setOrchestrating] = useState(false);

  const fetchState = useCallback(async () => {
    try {
      setError(null);
      const data = await client.getAgentState();
      setState(data);
    } catch (err) {
      try {
        const mockData = await mockClient.getAgentState();
        setState(mockData);
        setError(null);
      } catch (mockErr) {
        setError(err instanceof Error ? err.message : 'Failed to fetch agent state');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  const orchestrateTask = useCallback(async (taskDescription: string, workflowToken?: string) => {
    try {
      setOrchestrating(true);
      setError(null);
      await client.orchestrateTask(taskDescription, workflowToken);
      await fetchState();
      return true;
    } catch (err) {
      try {
        await mockClient.orchestrateTask(taskDescription, workflowToken);
        await fetchState();
        setError(null);
        return true;
      } catch (mockErr) {
        setError(err instanceof Error ? err.message : 'Failed to orchestrate task');
        return false;
      }
    } finally {
      setOrchestrating(false);
    }
  }, [fetchState]);

  useEffect(() => {
    fetchState();

    if (autoRefresh) {
      const interval = setInterval(fetchState, intervalMs);
      return () => clearInterval(interval);
    }
  }, [fetchState, autoRefresh, intervalMs]);

  return { 
    state, 
    loading, 
    error, 
    orchestrating, 
    orchestrateTask, 
    refetch: fetchState 
  };
}
