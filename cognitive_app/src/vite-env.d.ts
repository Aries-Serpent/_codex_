interface ImportMetaEnv {
  readonly VITE_CODEX_API?: string;
  readonly VITE_CODEX_KEY?: string;
  readonly VITE_OPENAI_API_KEY?: string;
  readonly VITE_OPENAI_BASE_URL?: string;
  readonly VITE_OPENAI_MODEL?: string;
  readonly VITE_SPARK_API_KEY?: string;
}

declare global {
  var spark: {
    llm: (prompt: string | TemplateStringsArray, model?: string, options?: Record<string, unknown>) => Promise<string>;
    llmPrompt: (strings: TemplateStringsArray, ...values: unknown[]) => string;
  };
}

export {};
