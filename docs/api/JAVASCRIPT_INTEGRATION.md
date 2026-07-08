# JavaScript/TypeScript Integration Guide

Complete guide for integrating the Codex API with JavaScript/TypeScript.

## Installation

```bash
# Install dependencies
npm install axios dotenv
# or
npm install fetch-retry dotenv
```

## Table of Contents

1. [Basic Setup](#basic-setup)
2. [Text Generation](#text-generation)
3. [Authentication](#authentication)
4. [RAG Operations](#rag-operations)
5. [Advanced Patterns](#advanced-patterns)
6. [Error Handling](#error-handling)
7. [React Integration](#react-integration)

---

## Basic Setup

### API Client Class

```typescript
import axios, { AxiosInstance, AxiosError } from 'axios';

interface ClientConfig {
  apiUrl?: string;
  ragUrl?: string;
  timeout?: number;
}

class CodexAPIClient {
  private apiUrl: string;
  private ragUrl: string;
  private axiosInstance: AxiosInstance;
  private token: string | null = null;

  constructor(config: ClientConfig = {}) {
    this.apiUrl = config.apiUrl || 'http://localhost:8000';
    this.ragUrl = config.ragUrl || 'http://localhost:8001';

    this.axiosInstance = axios.create({
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }

  setToken(token: string): void {
    this.token = token;
    this.axiosInstance.defaults.headers.common['Authorization'] = `******;
  }

  clearToken(): void {
    this.token = null;
    delete this.axiosInstance.defaults.headers.common['Authorization'];
  }

  async request(method: string, url: string, data?: any) {
    try {
      const response = await this.axiosInstance({
        method,
        url,
        data,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  private handleError(error: any): Error {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status;
      const detail = error.response?.data?.detail || error.message;

      switch (status) {
        case 401:
          return new AuthenticationError(detail);
        case 429:
          return new RateLimitError(detail);
        case 422:
          return new ValidationError(detail);
        case 404:
          return new NotFoundError(detail);
        default:
          return new APIError(`HTTP ${status}: ${detail}`);
      }
    }
    throw error;
  }
}

// Custom Error Classes
class APIError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'APIError';
  }
}

class AuthenticationError extends APIError {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

class RateLimitError extends APIError {
  constructor(message: string) {
    super(message);
    this.name = 'RateLimitError';
  }
}

class ValidationError extends APIError {
  constructor(message: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

class NotFoundError extends APIError {
  constructor(message: string) {
    super(message);
    this.name = 'NotFoundError';
  }
}

export default CodexAPIClient;
```

---

## Text Generation

### Simple Prediction

```typescript
async function predict(client: CodexAPIClient, prompt: string): Promise<string> {
  const response = await client.request(
    'POST',
    'http://localhost:8000/predict',
    { prompt }
  );
  return response.output;
}

// Usage
const client = new CodexAPIClient();
const result = await predict(client, 'What is machine learning?');
console.log(result);
```

### Batch Predictions

```typescript
async function batchPredict(
  client: CodexAPIClient,
  prompts: string[]
): Promise<(string | null)[]> {
  const results = await Promise.all(
    prompts.map(async (prompt) => {
      try {
        return await predict(client, prompt);
      } catch (error) {
        console.error(`Error for prompt "${prompt}":`, error);
        return null;
      }
    })
  );
  return results;
}

// Usage
const prompts = [
  'What is AI?',
  'Explain machine learning',
  'What are neural networks?',
];
const results = await batchPredict(client, prompts);
results.forEach((result, i) => {
  console.log(`Q: ${prompts[i]}\nA: ${result}\n`);
});
```

---

## Authentication

### Register User

```typescript
interface User {
  user_id: string;
  email: string;
  name: string;
  created_at: string;
}

async function register(
  client: CodexAPIClient,
  email: string,
  password: string,
  name: string
): Promise<User> {
  return await client.request(
    'POST',
    `${client['apiUrl']}/api/auth/register`,
    { email, password, name }
  );
}

// Usage
const user = await register(
  client,
  'newuser@example.com',
  'SecurePass123!',
  'John Doe'
);
console.log(`Registered: ${user.user_id}`);
```

### Login

```typescript
interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: {
    id: string;
    email: string;
    name: string;
  };
}

async function login(
  client: CodexAPIClient,
  email: string,
  password: string
): Promise<string> {
  const response = await client.request(
    'POST',
    `http://localhost:8000/api/auth/login`,
    { email, password }
  ) as LoginResponse;

  client.setToken(response.access_token);
  return response.access_token;
}

// Usage
const token = await login(client, 'user@example.com', 'password');
console.log(`Logged in! Token: ${token.substring(0, 20)}...`);
```

### Token Management

```typescript
async function refreshToken(client: CodexAPIClient): Promise<string> {
  const response = await client.request(
    'POST',
    'http://localhost:8000/api/auth/refresh'
  ) as LoginResponse;

  client.setToken(response.access_token);
  return response.access_token;
}

async function logout(client: CodexAPIClient): Promise<void> {
  await client.request('POST', 'http://localhost:8000/api/auth/logout');
  client.clearToken();
}

// Usage
const newToken = await refreshToken(client);
await logout(client);
```

---

## RAG Operations

### Build Index

```typescript
interface Document {
  id: string;
  content: string;
  metadata?: Record<string, string>;
}

interface BuildIndexResponse {
  index_name: string;
  document_count: number;
  size_bytes: number;
  created_at: string;
}

async function buildRagIndex(
  client: CodexAPIClient,
  indexName: string,
  documents: Document[]
): Promise<BuildIndexResponse> {
  return await client.request(
    'POST',
    'http://localhost:8001/rag/build',
    { index_name: indexName, documents }
  );
}

// Usage
const documents: Document[] = [
  {
    id: 'doc_001',
    content: 'Machine learning is a subset of AI...',
    metadata: { source: 'guide.txt' },
  },
  {
    id: 'doc_002',
    content: 'Neural networks are inspired by brains...',
    metadata: { source: 'guide.txt' },
  },
];

const result = await buildRagIndex(client, 'my_knowledge_base', documents);
console.log(`Built index with ${result.document_count} documents`);
```

### Query Index

```typescript
interface QueryResult {
  document_id: string;
  content: string;
  score: number;
  metadata?: Record<string, string>;
}

interface QueryResponse {
  query: string;
  results: QueryResult[];
  total_results: number;
  query_time_ms: number;
}

async function queryRagIndex(
  client: CodexAPIClient,
  indexName: string,
  query: string,
  topK: number = 5,
  threshold: number = 0.0
): Promise<QueryResponse> {
  return await client.request(
    'POST',
    'http://localhost:8001/rag/query',
    { index_name: indexName, query, top_k: topK, threshold }
  );
}

// Usage
const results = await queryRagIndex(client, 'my_knowledge_base', 'machine learning', 3);
console.log(`Found ${results.total_results} results in ${results.query_time_ms}ms`);
results.results.forEach((result, i) => {
  console.log(`${i + 1}. Score: ${result.score.toFixed(2)}`);
  console.log(`   Content: ${result.content.substring(0, 100)}...`);
});
```

### List & Manage Indices

```typescript
interface IndexInfo {
  name: string;
  document_count: number;
  size_bytes: number;
  created_at: string;
  updated_at: string;
}

interface ListIndicesResponse {
  indices: IndexInfo[];
  total_count: number;
}

async function listIndices(client: CodexAPIClient): Promise<IndexInfo[]> {
  const response = await client.request(
    'GET',
    'http://localhost:8001/rag/indices'
  ) as ListIndicesResponse;
  return response.indices;
}

async function getIndexStats(
  client: CodexAPIClient,
  indexName: string
): Promise<any> {
  return await client.request(
    'GET',
    `http://localhost:8001/rag/stats/${indexName}`
  );
}

async function deleteIndex(
  client: CodexAPIClient,
  indexName: string
): Promise<any> {
  return await client.request(
    'DELETE',
    `http://localhost:8001/rag/indices/${indexName}`
  );
}

// Usage
const indices = await listIndices(client);
indices.forEach((index) => {
  console.log(`${index.name}: ${index.document_count} documents`);
});
```

---

## Advanced Patterns

### Async/Await Pattern

```typescript
async function completeWorkflow(): Promise<void> {
  const client = new CodexAPIClient();

  try {
    // Login
    const token = await login(client, 'user@example.com', 'password');
    console.log('Logged in');

    // Generate prediction
    const result = await predict(client, 'What is AI?');
    console.log('Prediction:', result);

    // Logout
    await logout(client);
    console.log('Logged out');
  } catch (error) {
    console.error('Error:', error);
  }
}

completeWorkflow();
```

### Retry with Exponential Backoff

```typescript
async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  maxAttempts: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (
        error instanceof RateLimitError ||
        (error instanceof APIError && error.message.includes('503'))
      ) {
        const delay = baseDelay * Math.pow(2, attempt);
        console.log(`Retrying in ${delay}ms... (attempt ${attempt + 1}/${maxAttempts})`);
        await new Promise((resolve) => setTimeout(resolve, delay));
      } else {
        throw error;
      }
    }
  }
  throw new Error(`Failed after ${maxAttempts} attempts`);
}

// Usage
const result = await retryWithBackoff(() => predict(client, 'test'));
```

### Promise.all for Parallel Operations

```typescript
async function parallelQueries(
  client: CodexAPIClient,
  indexName: string,
  queries: string[]
): Promise<QueryResponse[]> {
  const results = await Promise.all(
    queries.map((query) => queryRagIndex(client, indexName, query))
  );
  return results;
}

// Usage
const queries = ['machine learning', 'neural networks', 'deep learning'];
const results = await parallelQueries(client, 'kb', queries);
```

---

## Error Handling

### Try-Catch Pattern

```typescript
async function safePredict(
  client: CodexAPIClient,
  prompt: string
): Promise<string | null> {
  try {
    return await predict(client, prompt);
  } catch (error) {
    if (error instanceof ValidationError) {
      console.error('Invalid prompt:', error.message);
    } else if (error instanceof RateLimitError) {
      console.error('Rate limited. Please wait before retrying');
    } else if (error instanceof AuthenticationError) {
      console.error('Authentication failed');
    } else {
      console.error('Unexpected error:', error);
    }
    return null;
  }
}
```

### Error Handler Utility

```typescript
function handleAPIError(error: unknown): void {
  if (error instanceof AuthenticationError) {
    // Redirect to login
    window.location.href = '/login';
  } else if (error instanceof RateLimitError) {
    // Show rate limit message
    console.warn('Rate limit exceeded. Please wait before retrying.');
  } else if (error instanceof ValidationError) {
    // Show validation error
    console.error('Validation error:', error.message);
  } else if (error instanceof NotFoundError) {
    // Show not found message
    console.error('Resource not found');
  } else {
    // Generic error
    console.error('An unexpected error occurred:', error);
  }
}
```

---

## React Integration

### Custom Hook

```typescript
import { useState, useCallback } from 'react';

interface UsePredictOptions {
  onSuccess?: (result: string) => void;
  onError?: (error: Error) => void;
}

function usePredict(client: CodexAPIClient, options: UsePredictOptions = {}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<string | null>(null);

  const predict = useCallback(
    async (prompt: string) => {
      setLoading(true);
      setError(null);

      try {
        const result = await predict(client, prompt);
        setData(result);
        options.onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error(String(err));
        setError(error);
        options.onError?.(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [client, options]
  );

  return { predict, loading, error, data };
}

// Usage in Component
function TextGeneratorComponent() {
  const client = new CodexAPIClient();
  const { predict, loading, error, data } = usePredict(client);

  return (
    <div>
      <input
        type="text"
        onKeyPress={(e) => {
          if (e.key === 'Enter') predict(e.currentTarget.value);
        }}
      />
      {loading && <p>Loading...</p>}
      {error && <p style={{ color: 'red' }}>Error: {error.message}</p>}
      {data && <p>{data}</p>}
    </div>
  );
}
```

### Context Provider

```typescript
import { createContext, useContext, ReactNode } from 'react';

interface CodexContextType {
  client: CodexAPIClient;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const CodexContext = createContext<CodexContextType | undefined>(undefined);

export function CodexProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const client = new CodexAPIClient();

  const handleLogin = async (email: string, password: string) => {
    const newToken = await login(client, email, password);
    setToken(newToken);
  };

  const handleLogout = async () => {
    await logout(client);
    setToken(null);
  };

  return (
    <CodexContext.Provider
      value={{
        client,
        token,
        login: handleLogin,
        logout: handleLogout,
      }}
    >
      {children}
    </CodexContext.Provider>
  );
}

export function useCodex(): CodexContextType {
  const context = useContext(CodexContext);
  if (!context) {
    throw new Error('useCodex must be used within CodexProvider');
  }
  return context;
}
```

---

## Testing

### Jest Tests

```typescript
import axios from 'axios';
jest.mock('axios');

describe('CodexAPIClient', () => {
  let client: CodexAPIClient;
  const mockAxios = axios as jest.Mocked<typeof axios>;

  beforeEach(() => {
    client = new CodexAPIClient();
  });

  it('should predict text', async () => {
    const mockResponse = { output: 'Test output' };
    mockAxios.create().request.mockResolvedValueOnce({
      data: mockResponse,
    });

    const result = await predict(client, 'test');
    expect(result).toBe('Test output');
  });

  it('should handle authentication errors', async () => {
    mockAxios.create().request.mockRejectedValueOnce(
      new Error('Unauthorized')
    );

    await expect(login(client, 'user', 'pass')).rejects.toThrow();
  });
});
```

---

**Last Updated:** 2026-07-08
