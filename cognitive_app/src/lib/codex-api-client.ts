import { z } from 'zod';

const CodexRequestSchema = z.object({
  prompt: z.string().min(10).max(5000),
  context: z.object({
    language: z.enum(['python', 'javascript', 'typescript', 'rust', 'go']).optional(),
    framework: z.string().optional(),
    tier: z.enum(['A', 'B', 'C']).optional(),
  }).optional(),
});

const CodexResponseSchema = z.object({
  code: z.string(),
  metadata: z.object({
    k1_factor: z.number(),
    coherence: z.number(),
    cache_hit: z.boolean(),
    processing_time_ms: z.number(),
  }),
  quantum_metrics: z.object({
    superposition_states: z.number(),
    entanglement_score: z.number(),
  }),
});

const StatusResponseSchema = z.object({
  healthy: z.boolean(),
  metrics: z.record(z.number()),
});

const SuperpositionScenarioSchema = z.object({
  state: z.string(),
  probability: z.number(),
  energy: z.number(),
  bell_state: z.string().optional(),
});

const QuantumStateResponseSchema = z.object({
  k1_factor: z.number(),
  accuracy: z.number(),
  coherence: z.number(),
  quantum_advantage: z.number(),
  superposition_states: z.array(SuperpositionScenarioSchema),
});

const MemoryEntrySchema = z.object({
  id: z.string(),
  type: z.enum(['decision', 'fact', 'pattern', 'lesson']),
  category: z.string(),
  content: z.string(),
  confidence: z.number(),
  timestamp: z.string(),
});

const MemoryStateResponseSchema = z.object({
  stm_count: z.number(),
  ltm_count: z.number(),
  capacity: z.number(),
  cache_hit_rate: z.number(),
  compression_rate: z.number(),
  patterns: z.array(z.any()),
  recent_operations: z.array(z.any()).optional(),
});

const AgentSchema = z.object({
  id: z.string(),
  name: z.string(),
  status: z.enum(['idle', 'active', 'thinking', 'error']),
  paradigm: z.enum(['chaos', 'fractal', 'fluid', 'electromagnetic', 'wave', 'relativity']),
  current_task: z.string().nullable(),
});

const TaskSchema = z.object({
  id: z.string(),
  description: z.string(),
  assigned_agent: z.string().nullable(),
  status: z.enum(['pending', 'running', 'completed', 'failed']),
  started_at: z.string().nullable(),
  completed_at: z.string().nullable(),
});

const AgentStateResponseSchema = z.object({
  agents: z.array(AgentSchema),
  tasks: z.array(TaskSchema),
});

const DashboardMetricsSchema = z.object({
  quantum: z.object({
    k1_factor: z.number(),
    quantum_advantage: z.number(),
    coherence: z.number(),
    accuracy: z.number(),
  }),
  agents: z.object({
    active_count: z.number(),
    task_count: z.number(),
    success_rate: z.number(),
    avg_response_time: z.number(),
  }),
  memory: z.object({
    cache_hit_rate: z.number(),
    pattern_count: z.number(),
    compression_rate: z.number(),
    stm_usage: z.number(),
  }),
  system: z.object({
    api_latency_p50: z.number(),
    api_latency_p95: z.number(),
    error_rate: z.number(),
    uptime: z.number(),
  }),
});

const ConsolidateResponseSchema = z.object({
  consolidated: z.number(),
  pruned: z.number(),
  stm_count: z.number(),
  ltm_count: z.number(),
  timestamp: z.string(),
  error: z.string().optional(),
});

export type CodexRequest = z.infer<typeof CodexRequestSchema>;
export type CodexResponse = z.infer<typeof CodexResponseSchema>;
export type StatusResponse = z.infer<typeof StatusResponseSchema>;
export type QuantumStateResponse = z.infer<typeof QuantumStateResponseSchema>;
export type SuperpositionScenario = z.infer<typeof SuperpositionScenarioSchema>;
export type MemoryEntry = z.infer<typeof MemoryEntrySchema>;
export type MemoryStateResponse = z.infer<typeof MemoryStateResponseSchema>;
export type Agent = z.infer<typeof AgentSchema>;
export type Task = z.infer<typeof TaskSchema>;
export type AgentStateResponse = z.infer<typeof AgentStateResponseSchema>;
export type DashboardMetrics = z.infer<typeof DashboardMetricsSchema>;
export type ConsolidateResponse = z.infer<typeof ConsolidateResponseSchema>;

export class CodexAPIError extends Error {
  constructor(public statusCode: number, message: string) {
    super(message);
    this.name = 'CodexAPIError';
  }
}

export class CodexAPIClient {
  private static __mockFactory: ((baseURL: string, apiKey: string) => Record<string, unknown>) | null = null;

  static mockImplementation(factory: (baseURL: string, apiKey: string) => Record<string, unknown>) {
    this.__mockFactory = factory;
    return this;
  }

  private baseURL: string;
  private apiKey: string;

  constructor(baseURL: string, apiKey: string) {
    const factory = (this.constructor as typeof CodexAPIClient).__mockFactory;
    if (factory) {
      const mockInstance = factory(baseURL, apiKey);
      Object.assign(this, mockInstance);
      return;
    }

    this.baseURL = baseURL;
    this.apiKey = apiKey;
  }

  async generateCode(request: CodexRequest): Promise<CodexResponse> {
    const validated = CodexRequestSchema.parse(request);

    const response = await fetch(`${this.baseURL}/infer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
        'X-Client-Version': '1.0.0',
      },
      body: JSON.stringify(validated),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'API request failed' }));
      throw new CodexAPIError(response.status, error.message || `HTTP ${response.status}`);
    }

    const data = await response.json();
    return CodexResponseSchema.parse(data);
  }

  async getStatus(): Promise<StatusResponse> {
    const response = await fetch(`${this.baseURL}/status`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to fetch status');
    }

    const data = await response.json();
    return StatusResponseSchema.parse(data);
  }

  async getQuantumState(): Promise<QuantumStateResponse> {
    const response = await fetch(`${this.baseURL}/api/cognitive/state`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to fetch quantum state');
    }

    const data = await response.json();
    return QuantumStateResponseSchema.parse(data);
  }

  async evaluateScenario(scenarios: unknown[]): Promise<unknown> {
    const response = await fetch(`${this.baseURL}/api/cognitive/evaluate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({ scenarios }),
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to evaluate scenario');
    }

    return await response.json();
  }

  async collapseWaveFunction(scenarioId: string): Promise<unknown> {
    const response = await fetch(`${this.baseURL}/api/cognitive/collapse`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({ scenario_id: scenarioId }),
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to collapse wave function');
    }

    return await response.json();
  }

  async getMemoryState(): Promise<MemoryStateResponse> {
    const response = await fetch(`${this.baseURL}/api/memory/state`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to fetch memory state');
    }

    const data = await response.json();
    return MemoryStateResponseSchema.parse(data);
  }

  async searchMemories(query: string): Promise<MemoryEntry[]> {
    const response = await fetch(`${this.baseURL}/api/memory/search?q=${encodeURIComponent(query)}`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to search memories');
    }

    const data = await response.json();
    return z.array(MemoryEntrySchema).parse(data);
  }

  async getAgentState(): Promise<AgentStateResponse> {
    const response = await fetch(`${this.baseURL}/api/agents/state`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to fetch agent state');
    }

    const data = await response.json();
    return AgentStateResponseSchema.parse(data);
  }

  async orchestrateTask(taskDescription: string, workflowToken?: string): Promise<unknown> {
    const response = await fetch(`${this.baseURL}/api/agents/orchestrate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        task_description: taskDescription,
        workflow_token: workflowToken
      }),
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to orchestrate task');
    }

    return await response.json();
  }

  async getDashboardMetrics(): Promise<DashboardMetrics> {
    const response = await fetch(`${this.baseURL}/api/metrics/dashboard`, {
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to fetch dashboard metrics');
    }

    const data = await response.json();
    return DashboardMetricsSchema.parse(data);
  }

  async consolidateMemory(): Promise<ConsolidateResponse> {
    const response = await fetch(`${this.baseURL}/api/memory/consolidate`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${this.apiKey}` },
    });

    if (!response.ok) {
      throw new CodexAPIError(response.status, 'Failed to consolidate memory');
    }

    const data = await response.json();
    return ConsolidateResponseSchema.parse(data);
  }
}
