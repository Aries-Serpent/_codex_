/**
 * github-public-api.ts
 *
 * Live data client for the GitHub REST API.
 *
 * Since Aries-Serpent/_codex_ is a PUBLIC repository, all read endpoints
 * work without authentication from any browser on GitHub Pages.
 *
 * Browser requests intentionally use unauthenticated public reads. Codespace
 * authenticated operations are routed through the Cognitive Brain middleware;
 * GitHub credentials must never be embedded in Vite environment variables.
 */

const REPO   = (import.meta.env.VITE_GITHUB_REPO as string | undefined)
             ?? 'Aries-Serpent/_codex_';
const BASE   = 'https://api.github.com';

function headers(): HeadersInit {
  const h: Record<string, string> = {
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
  };
  return h;
}

async function ghFetch<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    credentials: 'omit',
    headers: headers(),
  });
  if (!res.ok) throw new Error(`GitHub API ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

// ---------------------------------------------------------------------------
// Public API surface
// ---------------------------------------------------------------------------

export interface RepoStats {
  stars: number;
  forks: number;
  open_issues: number;
  language: string;
  pushed_at: string;
  default_branch: string;
}

export interface WorkflowRun {
  id: number;
  name: string;
  status: string;
  conclusion: string | null;
  html_url: string;
  created_at: string;
  updated_at: string;
}

export interface Release {
  tag_name: string;
  name: string;
  published_at: string;
  html_url: string;
  prerelease: boolean;
}

export interface BranchInfo {
  name: string;
  commit_sha: string;
}

export async function fetchRepoStats(): Promise<RepoStats> {
  const d = await ghFetch<Record<string, unknown>>(`/repos/${REPO}`);
  return {
    stars:          d.stargazers_count as number,
    forks:          d.forks_count as number,
    open_issues:    d.open_issues_count as number,
    language:       d.language as string,
    pushed_at:      d.pushed_at as string,
    default_branch: d.default_branch as string,
  };
}

export async function fetchLatestWorkflowRuns(limit = 5): Promise<WorkflowRun[]> {
  const d = await ghFetch<{ workflow_runs: WorkflowRun[] }>(
    `/repos/${REPO}/actions/runs?per_page=${limit}`,
  );
  return d.workflow_runs;
}

export async function fetchPagesWorkflowStatus(): Promise<WorkflowRun | null> {
  // Specifically fetch the MkDocs Pages deploy status
  try {
    const d = await ghFetch<{ workflow_runs: WorkflowRun[] }>(
      `/repos/${REPO}/actions/workflows/pages-mkdocs.yml/runs?per_page=1&branch=main`,
    );
    return d.workflow_runs[0] ?? null;
  } catch {
    return null;
  }
}

export async function fetchLatestRelease(): Promise<Release | null> {
  try {
    return await ghFetch<Release>(`/repos/${REPO}/releases/latest`);
  } catch {
    return null;
  }
}

export async function fetchMainBranch(): Promise<BranchInfo | null> {
  try {
    const d = await ghFetch<{ commit: { sha: string } }>(
      `/repos/${REPO}/branches/main`,
    );
    return { name: 'main', commit_sha: d.commit.sha };
  } catch {
    return null;
  }
}

/** Rate limit info — useful to surface in UI when approaching limits */
export async function fetchRateLimit(): Promise<{ remaining: number; limit: number }> {
  try {
    const d = await ghFetch<{ rate: { remaining: number; limit: number } }>('/rate_limit');
    return d.rate;
  } catch {
    return { remaining: 0, limit: 60 };
  }
}
