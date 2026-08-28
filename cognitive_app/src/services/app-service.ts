import {
  CodexAPIClient,
  CodexAPIError,
  type CodexRequest,
  type CodexResponse,
} from '@/lib/codex-api-client';
import { MockCodexAPIClient } from '@/lib/mock-api-client';
import { SparkLLMClient } from '@/lib/spark-llm-client';

export const DEFAULT_LANGUAGE = 'python' as const;
export const DEFAULT_MODEL = 'gpt-4o-mini' as const;

export const SUPPORTED_LANGUAGES = [
  'python',
  'javascript',
  'typescript',
  'rust',
  'go',
  'bash',
] as const;

export const SUPPORTED_MODELS = [
  'gpt-4o-mini',
  'gpt-4o',
  'claude-sonnet-4',
  'codex-mini',
] as const;

export type AppGenerationLanguage = (typeof SUPPORTED_LANGUAGES)[number];
export type AppGenerationModel = (typeof SUPPORTED_MODELS)[number];

export interface AppGenerationRequest {
  prompt: string;
  language: AppGenerationLanguage;
  model?: AppGenerationModel;
  aiMode?: boolean;
}

export interface AppGenerationResult {
  source: 'spark' | 'api' | 'mock';
  response: CodexResponse;
}

export interface AppStatusResult {
  status: 'connected' | 'error' | 'checking';
  error: string | null;
  message: string | null;
}

export class AppService {
  private clientRef: CodexAPIClient | null = null;
  private mockClientRef: MockCodexAPIClient | null = null;
  private sparkClientRef: SparkLLMClient | null = null;

  private createClient(): CodexAPIClient | null {
    const apiKey = import.meta.env.VITE_CODEX_KEY;
    return apiKey ? new CodexAPIClient(import.meta.env.VITE_CODEX_API || 'http://localhost:8000', apiKey) : null;
  }

  private getClient(): CodexAPIClient | null {
    if (!this.clientRef) {
      this.clientRef = this.createClient();
    }
    return this.clientRef;
  }

  private getMockClient(): MockCodexAPIClient {
    if (!this.mockClientRef) {
      this.mockClientRef = new MockCodexAPIClient();
    }
    return this.mockClientRef;
  }

  private getSparkClient(): SparkLLMClient {
    if (!this.sparkClientRef) {
      this.sparkClientRef = new SparkLLMClient();
    }
    return this.sparkClientRef;
  }

  private mapModelTier(model: AppGenerationModel): 'A' | 'B' | 'C' {
    switch (model) {
      case 'gpt-4o':
        return 'A';
      case 'claude-sonnet-4':
        return 'A';
      case 'codex-mini':
        return 'B';
      case 'gpt-4o-mini':
      default:
        return 'B';
    }
  }

  private buildRequest(prompt: string, language: AppGenerationLanguage, model: AppGenerationModel): CodexRequest {
    return {
      prompt,
      context: {
        language,
        tier: this.mapModelTier(model),
      },
    };
  }

  async getStatus(aiMode: boolean): Promise<AppStatusResult> {
    if (aiMode) {
      try {
        const status = await this.getSparkClient().getStatus();
        return {
          status: 'connected',
          error: null,
          message: `AI Mode: ${status.model}`,
        };
      } catch (error) {
        console.error('Spark status check failed:', error);
        return {
          status: 'error',
          error: 'Spark LLM client unavailable',
          message: null,
        };
      }
    }

    const client = this.getClient();
    if (!client) {
      try {
        await this.getMockClient().getStatus();
        return {
          status: 'connected',
          error: null,
          message: 'Using demo mode (API key not configured)',
        };
      } catch (error) {
        console.error('Mock client status check failed:', error);
        return {
          status: 'error',
          error: 'Demo mode unavailable',
          message: null,
        };
      }
    }

    try {
      await client.getStatus();
      return {
        status: 'connected',
        error: null,
        message: null,
      };
    } catch (error) {
      console.error('Primary API status check failed:', error);
      try {
        await this.getMockClient().getStatus();
        return {
          status: 'connected',
          error: null,
          message: 'API connection failed, using demo mode',
        };
      } catch (mockError) {
        console.error('Mock client status check failed:', mockError);
        return {
          status: 'error',
          error: 'Unable to connect to API or demo mode',
          message: null,
        };
      }
    }
  }

  async generateCode(request: AppGenerationRequest): Promise<AppGenerationResult> {
    const model = request.model ?? DEFAULT_MODEL;
    const language = request.language ?? DEFAULT_LANGUAGE;

    if (request.aiMode) {
      try {
        const response = await this.getSparkClient().generateCode(
          this.buildRequest(request.prompt, language, model),
        );
        return { source: 'spark', response };
      } catch (error) {
        console.error('Spark code generation failed, falling back to app service generation.', error);
      }
    }

    const client = this.getClient();
    if (client) {
      try {
        const response = await client.generateCode(this.buildRequest(request.prompt, language, model));
        return { source: 'api', response };
      } catch (error) {
        if (error instanceof CodexAPIError && error.statusCode === 429) {
          throw error;
        }
      }
    }

    const mockResponse = await this.getMockClient().generateCode(
      this.buildRequest(request.prompt, language, model),
    );
    return { source: 'mock', response: mockResponse };
  }
}

export const appService = new AppService();
