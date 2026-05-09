/**
 * Documentation catalog and metadata.
 *
 * Each entry maps a human-readable title to a file path relative to the
 * repository root.  Content is fetched lazily via the GitHub API (live mode)
 * or returned from the mock catalog (offline / HAR-replay modes).
 */

export interface DocEntry {
  id: string;
  title: string;
  path: string;
  category: string;
  tags: string[];
  description?: string;
}

export const DOC_CATALOG: DocEntry[] = [
  {
    id: 'agents-md',
    title: 'AGENTS.md',
    path: 'AGENTS.md',
    category: 'Core',
    tags: ['agents', 'overview', 'onboarding'],
    description: 'AI agent entry point and operational guidelines.',
  },
  {
    id: 'readme',
    title: 'README',
    path: 'README.md',
    category: 'Core',
    tags: ['overview', 'getting-started'],
    description: 'Repository overview and quick-start guide.',
  },
  {
    id: 'changelog',
    title: 'CHANGELOG',
    path: 'CHANGELOG.md',
    category: 'Core',
    tags: ['changelog', 'releases', 'history'],
    description: 'Full release and change history.',
  },
  {
    id: 'codebase-agency-policy',
    title: 'Codebase Agency Policy',
    path: '.codex/CODEBASE_AGENCY_POLICY.md',
    category: 'Policy',
    tags: ['policy', 'agents', 'mandatory'],
    description: 'Mandatory rules governing all agent actions.',
  },
  {
    id: 'agentic-repo-state',
    title: 'Agentic Repo State',
    path: '.codex/AGENTIC_REPO_STATE.md',
    category: 'Policy',
    tags: ['auth', 'state', 'agents'],
    description: 'Current authorization state for the agentic repo.',
  },
  {
    id: 'agent-accountability',
    title: 'Agent Accountability Report',
    path: 'docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md',
    category: 'Reports',
    tags: ['accountability', 'sessions', 'audit'],
    description: 'Agent session accountability and audit trail.',
  },
  {
    id: 'cognitive-brain-docs',
    title: 'Cognitive Brain Complete Docs',
    path: '.codex/docs/COGNITIVE_BRAIN_COMPLETE_DOCS.md',
    category: 'Architecture',
    tags: ['cognitive-brain', 'architecture', 'design'],
    description: 'Complete Cognitive Brain System documentation.',
  },
  {
    id: 'ci-auto-fix-system',
    title: 'CI Auto-Fix System',
    path: '.codex/docs/CI_AUTO_FIX_SYSTEM.md',
    category: 'CI/CD',
    tags: ['ci', 'auto-fix', 'patterns'],
    description: 'CI/CD automation and auto-fix pattern library.',
  },
  {
    id: 'mcp-tool-reference',
    title: 'Copilot MCP Tool Reference',
    path: '.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md',
    category: 'Reference',
    tags: ['mcp', 'tools', 'copilot', 'reference'],
    description: 'Live MCP tool inventory: Playwright + GitHub MCP tools.',
  },
  {
    id: 'github-variables-secrets',
    title: 'GitHub Variables & Secrets Reference',
    path: 'docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md',
    category: 'Reference',
    tags: ['github', 'variables', 'secrets', 'api'],
    description: 'Complete REST API endpoint tables for secrets and variables.',
  },
];

export const DOC_CATEGORIES = [...new Set(DOC_CATALOG.map((d) => d.category))];

export function getDocById(id: string): DocEntry | undefined {
  return DOC_CATALOG.find((d) => d.id === id);
}

export function getDocsByCategory(category: string): DocEntry[] {
  return DOC_CATALOG.filter((d) => d.category === category);
}
