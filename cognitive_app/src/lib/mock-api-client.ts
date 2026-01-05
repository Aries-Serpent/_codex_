import { 
  CodexRequest, 
  CodexResponse, 
  StatusResponse, 
  QuantumStateResponse,
  MemoryStateResponse,
  MemoryEntry,
  AgentStateResponse,
  DashboardMetrics,
  Agent,
  Task
} from './codex-api-client';

export class MockCodexAPIClient {
  private mockDelay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

  async generateCode(request: CodexRequest): Promise<CodexResponse> {
    await this.mockDelay(800 + Math.random() * 400);

    const sampleCode = `def ${request.prompt.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 30)}():
    """
    ${request.prompt}
    
    Generated using quantum-enhanced cognitive brain
    - k₁ factor: 0.312 (target ≤0.35)
    - Coherence: 68.5% (target ≥65%)
    - Quantum advantage: 2.86x faster than classical
    """
    # Implementation using ${request.context?.framework || 'standard library'}
    result = perform_operation()
    
    # Validate output
    if not result:
        raise ValueError("Operation failed")
    
    return result


def perform_operation():
    """Core operation logic"""
    # ${request.context?.tier || 'B'}-tier transformation applied
    return {"status": "success", "data": []}


if __name__ == "__main__":
    print(${request.prompt.toLowerCase().replace(/[^a-z0-9]/g, '_').substring(0, 30)}())
`;

    return {
      code: sampleCode,
      metadata: {
        k1_factor: 0.312 + Math.random() * 0.03,
        coherence: 0.65 + Math.random() * 0.1,
        cache_hit: Math.random() > 0.7,
        processing_time_ms: 800 + Math.random() * 400,
      },
      quantum_metrics: {
        superposition_states: 3,
        entanglement_score: 0.75 + Math.random() * 0.2,
      },
    };
  }

  async getStatus(): Promise<StatusResponse> {
    await this.mockDelay(100);
    return {
      healthy: true,
      metrics: {
        k1_factor: 0.312,
        quantum_advantage: 2.86,
        coherence: 0.685,
        accuracy: 0.864,
      },
    };
  }

  async getQuantumState(): Promise<QuantumStateResponse> {
    await this.mockDelay(150);
    return {
      k1_factor: 0.312 + Math.random() * 0.02,
      accuracy: 0.864 + Math.random() * 0.02,
      coherence: 0.685 + Math.random() * 0.05,
      quantum_advantage: 2.86 + Math.random() * 0.1,
      superposition_states: [
        {
          state: "Refactor with Design Patterns",
          probability: 0.42,
          energy: 0.85,
          bell_state: "entangled",
        },
        {
          state: "Optimize Performance",
          probability: 0.35,
          energy: 0.72,
        },
        {
          state: "Add Error Handling",
          probability: 0.23,
          energy: 0.68,
        },
      ],
    };
  }

  async evaluateScenario(): Promise<unknown> {
    await this.mockDelay(300);
    return {
      results: [],
      coherence: 0.685,
      quantum_advantage: 2.86,
    };
  }

  async collapseWaveFunction(): Promise<unknown> {
    await this.mockDelay(200);
    return {
      selected_state: "option-1",
      collapsed: true,
      final_probability: 1.0,
    };
  }

  async getMemoryState(): Promise<MemoryStateResponse> {
    await this.mockDelay(150);
    return {
      stm_count: 5,
      ltm_count: 150,
      capacity: 1000,
      cache_hit_rate: 0.32 + Math.random() * 0.1,
      compression_rate: 0.60 + Math.random() * 0.05,
      patterns: [
        {
          id: "pattern-1",
          name: "Refactor Extract Method",
          usage_count: 15,
          compression_ratio: 0.62,
          last_accessed: new Date(Date.now() - 30 * 60000).toISOString(),
        },
        {
          id: "pattern-2",
          name: "Error Handling Best Practices",
          usage_count: 23,
          compression_ratio: 0.58,
          last_accessed: new Date(Date.now() - 60 * 60000).toISOString(),
        },
        {
          id: "pattern-3",
          name: "API Response Caching",
          usage_count: 18,
          compression_ratio: 0.65,
          last_accessed: new Date(Date.now() - 90 * 60000).toISOString(),
        },
      ],
      recent_operations: [],
    };
  }

  async searchMemories(query: string): Promise<MemoryEntry[]> {
    await this.mockDelay(200);
    
    if (!query.trim()) return [];

    const mockMemories: MemoryEntry[] = [
      {
        id: "mem-1",
        type: "pattern",
        category: "Code Quality",
        content: `Pattern matching for "${query}": Extract Method refactoring applied to reduce function complexity`,
        confidence: 0.85,
        timestamp: new Date(Date.now() - 120 * 60000).toISOString(),
      },
      {
        id: "mem-2",
        type: "decision",
        category: "Architecture",
        content: `Decision related to "${query}": Use dependency injection for better testability`,
        confidence: 0.92,
        timestamp: new Date(Date.now() - 240 * 60000).toISOString(),
      },
      {
        id: "mem-3",
        type: "lesson",
        category: "Performance",
        content: `Lesson learned about "${query}": Caching reduces API calls by 60% on average`,
        confidence: 0.78,
        timestamp: new Date(Date.now() - 360 * 60000).toISOString(),
      },
    ];

    return mockMemories;
  }

  async getAgentState(): Promise<AgentStateResponse> {
    await this.mockDelay(150);

    const agents: Agent[] = [
      {
        id: "agent-1",
        name: "Workflow Navigator",
        status: Math.random() > 0.5 ? "idle" : "active",
        paradigm: "chaos",
        current_task: Math.random() > 0.5 ? "Analyzing code complexity patterns" : null,
      },
      {
        id: "agent-2",
        name: "Quantum Decision",
        status: "active",
        paradigm: "wave",
        current_task: "Evaluating architectural decisions",
      },
      {
        id: "agent-3",
        name: "Physics Optimizer",
        status: "idle",
        paradigm: "fluid",
        current_task: null,
      },
      {
        id: "agent-4",
        name: "Pattern Recognizer",
        status: Math.random() > 0.7 ? "thinking" : "idle",
        paradigm: "fractal",
        current_task: Math.random() > 0.7 ? "Detecting code patterns" : null,
      },
      {
        id: "agent-5",
        name: "Field Analyzer",
        status: "idle",
        paradigm: "electromagnetic",
        current_task: null,
      },
      {
        id: "agent-6",
        name: "Causal Coordinator",
        status: "idle",
        paradigm: "relativity",
        current_task: null,
      },
    ];

    const tasks: Task[] = [
      {
        id: "task-1",
        description: "Audit code quality metrics",
        assigned_agent: "agent-2",
        status: "running",
        started_at: new Date(Date.now() - 300000).toISOString(),
        completed_at: null,
      },
      {
        id: "task-2",
        description: "Generate API documentation",
        assigned_agent: null,
        status: "pending",
        started_at: null,
        completed_at: null,
      },
    ];

    return { agents, tasks };
  }

  async orchestrateTask(taskDescription: string, workflowToken?: string): Promise<unknown> {
    await this.mockDelay(1500);
    return {
      task_id: `task-${Date.now()}`,
      status: "running",
      assigned_agent: "agent-1",
      estimated_duration: 30,
      workflow_token: workflowToken,
      description: taskDescription,
    };
  }

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    await this.mockDelay(150);
    return {
      quantum: {
        k1_factor: 0.312,
        quantum_advantage: 2.86,
        coherence: 0.685,
        accuracy: 0.864,
      },
      agents: {
        active_count: 2,
        task_count: 5,
        success_rate: 0.92,
        avg_response_time: 850,
      },
      memory: {
        cache_hit_rate: 0.32,
        pattern_count: 150,
        compression_rate: 0.60,
        stm_usage: 0.5,
      },
      system: {
        api_latency_p50: 120,
        api_latency_p95: 450,
        error_rate: 0.02,
        uptime: 0.998,
      },
    };
  }
}
