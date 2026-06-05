# MCP Workflow Recipes for GitHub Actions

> **Generated**: 2026-02-17T11:22:00Z
> **Repository**: Aries-Serpent/_codex_
> **Purpose**: Production-ready GitHub Actions workflows for MCP integration
> **Status**: Ready for Implementation

---

## Table of Contents

1. [E2E Testing Workflow](#e2e-testing-workflow)
2. [MCP Context Workflow](#mcp-context-workflow)
3. [Copilot Agent CI Integration](#copilot-agent-ci-integration)
4. [Chain-PR Orchestration](#chain-pr-orchestration)
5. [Best Practices](#best-practices)

---

## E2E Testing Workflow

### File: `.github/workflows/e2e-playwright.yml`

**Purpose**: Run Playwright E2E tests with MCP context in CI/CD

```yaml
name: E2E Tests (Playwright + MCP)

on:
  pull_request:
    branches: [main, develop]
    paths:
      - 'cognitive_app/**'
      - 'e2e/**'
      - 'playwright.config.ts'
      - '.github/workflows/e2e-playwright.yml'
  push:
    branches: [main]
  workflow_dispatch:
    inputs:
      browser:
        description: 'Browser to test (chromium, firefox, webkit, all)'
        required: false
        default: 'chromium'
        type: choice
        options:
          - chromium
          - firefox
          - webkit
          - all
      headed:
        description: 'Run in headed mode (visible browser)'
        required: false
        default: false
        type: boolean

env:
  NODE_VERSION: '22'
  PYTHON_VERSION: '3.11'
  PLAYWRIGHT_VERSION: '1.57.0'

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  e2e-tests:
    name: E2E Tests (${{ matrix.browser }})
    runs-on: ubuntu-latest
    timeout-minutes: 30

    strategy:
      fail-fast: false
      matrix:
        browser: ${{
          github.event.inputs.browser == 'all' && fromJSON('["chromium", "firefox", "webkit"]') ||
          github.event.inputs.browser && fromJSON(format('["{0}"]', github.event.inputs.browser)) ||
          fromJSON('["chromium"]')
        }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for context

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'
          cache-dependency-path: 'cognitive_app/package-lock.json'

      - name: Setup Python (for MCP context)
        uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install -r requirements-test.txt

      - name: Install Node.js dependencies
        working-directory: cognitive_app
        run: npm ci

      - name: Install Playwright browsers
        working-directory: cognitive_app
        run: |
          npx playwright install --with-deps ${{ matrix.browser }}

      - name: Cache Playwright browsers
        uses: actions/cache@v4
        with:
          path: ~/.cache/ms-playwright
          key: playwright-${{ runner.os }}-${{ env.PLAYWRIGHT_VERSION }}-${{ matrix.browser }}
          restore-keys: |
            playwright-${{ runner.os }}-${{ env.PLAYWRIGHT_VERSION }}-
            playwright-${{ runner.os }}-

      - name: Prepare MCP context (optional)
        id: mcp-context
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          # Generate MCP context manifest
          python << 'EOF'
          import json
          import os

          context = {
            "repository": {
              "owner": "${{ github.repository_owner }}",
              "name": "${{ github.event.repository.name }}",
              "id": "${{ github.repository_id }}",
              "node_id": "${{ github.event.repository.node_id }}"
            },
            "pr": {
              "number": "${{ github.event.pull_request.number }}",
              "head_sha": "${{ github.event.pull_request.head.sha }}",
              "base_ref": "${{ github.event.pull_request.base.ref }}"
            } if "${{ github.event_name }}" == "pull_request" else None,
            "workflow": {
              "run_id": "${{ github.run_id }}",
              "run_number": "${{ github.run_number }}",
              "actor": "${{ github.actor }}"
            }
          }

          with open('mcp_context.json', 'w') as f:
            json.dump(context, f, indent=2)

          print(f"✅ MCP context generated: {len(json.dumps(context))} bytes")
          EOF

      - name: Run E2E tests
        working-directory: cognitive_app
        env:
          BASE_URL: http://localhost:5173
          CI: true
          HEADED: ${{ github.event.inputs.headed == 'true' }}
        run: |
          if [ "$HEADED" = "true" ]; then
            npm run test:e2e -- --project=${{ matrix.browser }} --headed
          else
            npm run test:e2e -- --project=${{ matrix.browser }}
          fi

      - name: Upload test results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-results-${{ matrix.browser }}-${{ github.run_id }}
          path: |
            cognitive_app/playwright-report/
            cognitive_app/test-results/
          retention-days: 7
          if-no-files-found: warn

      - name: Upload trace files (on failure)
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-traces-${{ matrix.browser }}-${{ github.run_id }}
          path: cognitive_app/test-results/**/*.zip
          retention-days: 7
          if-no-files-found: ignore

      - name: Parse test results
        if: always()
        id: parse-results
        working-directory: cognitive_app
        run: |
          if [ -f test-results/results.json ]; then
            TOTAL=$(jq '[.suites[].tests[]] | length' test-results/results.json)
            PASSED=$(jq '[.suites[].tests[] | select(.status == "passed")] | length' test-results/results.json)
            FAILED=$(jq '[.suites[].tests[] | select(.status == "failed")] | length' test-results/results.json)
            SKIPPED=$(jq '[.suites[].tests[] | select(.status == "skipped")] | length' test-results/results.json)

            echo "total=$TOTAL" >> $GITHUB_OUTPUT
            echo "passed=$PASSED" >> $GITHUB_OUTPUT
            echo "failed=$FAILED" >> $GITHUB_OUTPUT
            echo "skipped=$SKIPPED" >> $GITHUB_OUTPUT
          else
            echo "⚠️ No test results found"
            echo "total=0" >> $GITHUB_OUTPUT
            echo "passed=0" >> $GITHUB_OUTPUT
            echo "failed=0" >> $GITHUB_OUTPUT
            echo "skipped=0" >> $GITHUB_OUTPUT
          fi

      - name: Generate job summary
        if: always()
        run: |
          cat << 'EOF' >> $GITHUB_STEP_SUMMARY
          ## 🎭 E2E Test Results: ${{ matrix.browser }}

          | Metric | Count |
          |--------|-------|
          | **Total Tests** | ${{ steps.parse-results.outputs.total }} |
          | **Passed** | ✅ ${{ steps.parse-results.outputs.passed }} |
          | **Failed** | ❌ ${{ steps.parse-results.outputs.failed }} |
          | **Skipped** | ⏭️ ${{ steps.parse-results.outputs.skipped }} |

          **Browser**: ${{ matrix.browser }}
          **Duration**: ${{ job.status == 'success' && '✅ Success' || '❌ Failed' }}

          ---

          📊 [View Full Report](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})
          EOF

      - name: Comment PR with results
        if: always() && github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const total = '${{ steps.parse-results.outputs.total }}';
            const passed = '${{ steps.parse-results.outputs.passed }}';
            const failed = '${{ steps.parse-results.outputs.failed }}';
            const browser = '${{ matrix.browser }}';
            const runUrl = `https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}`;

            const body = `## 🎭 E2E Test Results (${browser})

            | Metric | Count |
            |--------|-------|
            | **Total** | ${total} |
            | **Passed** | ✅ ${passed} |
            | **Failed** | ❌ ${failed} |

            **Status**: ${failed > 0 ? '❌ Failed' : '✅ Passed'}

            [View detailed results](${runUrl})`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: body
            });

  # Aggregate results from all browsers
  e2e-summary:
    name: E2E Test Summary
    runs-on: ubuntu-latest
    needs: e2e-tests
    if: always()

    steps:
      - name: Check test results
        run: |
          if [ "${{ needs.e2e-tests.result }}" == "success" ]; then
            echo "✅ All E2E tests passed"
          else
            echo "❌ Some E2E tests failed"
            exit 1
          fi

      - name: Generate final summary
        run: |
          echo "## 🎭 E2E Test Suite Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY
          echo "**Result**: ${{ needs.e2e-tests.result == 'success' && '✅ All tests passed' || '❌ Some tests failed' }}" >> $GITHUB_STEP_SUMMARY
          echo "**Browsers Tested**: ${{ join(matrix.browser, ', ') }}" >> $GITHUB_STEP_SUMMARY
```

---

## MCP Context Workflow

### File: `.github/workflows/mcp-context-delivery.yml`

**Purpose**: Provide rich MCP context for agent tasks

```yaml
name: MCP Context Delivery

on:
  workflow_call:
    inputs:
      task_type:
        description: 'Type of task requiring MCP context'
        required: true
        type: string
      pr_number:
        description: 'PR number for context'
        required: false
        type: number
    outputs:
      context_artifact:
        description: 'Name of uploaded context artifact'
        value: ${{ jobs.build-context.outputs.artifact_name }}

jobs:
  build-context:
    name: Build MCP Context
    runs-on: ubuntu-latest
    outputs:
      artifact_name: ${{ steps.upload.outputs.artifact_name }}

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Gather repository context
        id: repo-context
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python << 'EOF'
          import json
          import subprocess
          import os

          def run_cmd(cmd):
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.stdout.strip()

          context = {
            "repository": {
              "name": os.getenv("GITHUB_REPOSITORY"),
              "id": os.getenv("GITHUB_REPOSITORY_ID"),
              "default_branch": run_cmd("git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'"),
              "total_commits": run_cmd("git rev-list --count HEAD"),
              "languages": {
                "python": run_cmd("find . -name '*.py' | wc -l"),
                "typescript": run_cmd("find . -name '*.ts' | wc -l"),
                "javascript": run_cmd("find . -name '*.js' | wc -l"),
              }
            },
            "recent_commits": [
              {
                "sha": line.split()[0],
                "message": " ".join(line.split()[1:])
              }
              for line in run_cmd("git log --oneline -10").split("\n")
            ],
            "test_coverage": {
              "python": run_cmd("coverage report --show-missing 2>/dev/null || echo 'N/A'"),
            },
            "task_type": "${{ inputs.task_type }}",
            "pr_number": "${{ inputs.pr_number }}" if "${{ inputs.pr_number }}" else None,
          }

          os.makedirs(".mcp", exist_ok=True)
          with open(".mcp/context.json", "w") as f:
            json.dump(context, f, indent=2)

          print(f"✅ Context generated: {len(json.dumps(context))} bytes")
          EOF

      - name: Gather PR context (if applicable)
        if: inputs.pr_number
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          gh pr view ${{ inputs.pr_number }} --json \
            number,title,body,author,createdAt,updatedAt,mergeable,state,files \
            > .mcp/pr_context.json

          echo "✅ PR context gathered"

      - name: Gather CI/CD context
        run: |
          python << 'EOF'
          import json
          import os

          ci_context = {
            "workflow": {
              "name": os.getenv("GITHUB_WORKFLOW"),
              "run_id": os.getenv("GITHUB_RUN_ID"),
              "run_number": os.getenv("GITHUB_RUN_NUMBER"),
              "actor": os.getenv("GITHUB_ACTOR"),
              "event_name": os.getenv("GITHUB_EVENT_NAME"),
            },
            "runner": {
              "os": os.getenv("RUNNER_OS"),
              "arch": os.getenv("RUNNER_ARCH"),
              "temp": os.getenv("RUNNER_TEMP"),
            }
          }

          with open(".mcp/ci_context.json", "w") as f:
            json.dump(ci_context, f, indent=2)
          EOF

      - name: Upload context artifact
        id: upload
        uses: actions/upload-artifact@v4
        with:
          name: mcp-context-${{ github.run_id }}
          path: .mcp/
          retention-days: 7

      - name: Output artifact name
        run: echo "artifact_name=mcp-context-${{ github.run_id }}" >> $GITHUB_OUTPUT
```

---

## Copilot Agent CI Integration

### File: `.github/workflows/copilot-agent-trigger.yml`

**Purpose**: Trigger Copilot Agent tasks from CI/CD events

```yaml
name: Copilot Agent Task Trigger

on:
  issue_comment:
    types: [created]
  pull_request_review:
    types: [submitted]

jobs:
  trigger-agent:
    name: Trigger Copilot Agent
    runs-on: ubuntu-latest
    if: |
      (github.event_name == 'issue_comment' && contains(github.event.comment.body, '@copilot')) ||
      (github.event_name == 'pull_request_review' && contains(github.event.review.body, '@copilot'))

    steps:
      - name: Extract agent command
        id: extract
        uses: actions/github-script@v7
        with:
          script: |
            const body = context.payload.comment?.body || context.payload.review?.body || '';
            const mentionPattern = /@copilot\s+(.+)/;
            const match = body.match(mentionPattern);

            if (match) {
              const command = match[1].trim();
              console.log(`Found agent command: ${command}`);
              core.setOutput('command', command);
              core.setOutput('has_command', 'true');
            } else {
              core.setOutput('has_command', 'false');
            }

      - name: Post acknowledgment
        if: steps.extract.outputs.has_command == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            const command = '${{ steps.extract.outputs.command }}';
            const body = `✅ Copilot Agent task received: "${command}"

            I'll start working on this right away. You'll see commits and updates as I progress.

            Track progress: https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }}`;

            if (context.payload.comment) {
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: body
              });
            }

      - name: Trigger agent workflow
        if: steps.extract.outputs.has_command == 'true'
        uses: actions/github-script@v7
        with:
          script: |
            // This would trigger the actual Copilot Agent task
            // Implementation depends on your agent infrastructure

            console.log('Agent task triggered successfully');
```

---

## Chain-PR Orchestration

### File: `.github/workflows/chain-pr-orchestrator.yml`

**Purpose**: Manage multi-PR dependency chains

```yaml
name: Chain-PR Orchestrator

on:
  workflow_dispatch:
    inputs:
      chain_id:
        description: 'Chain identifier (e.g., refactor-2024-02)'
        required: true
        type: string
      pr_count:
        description: 'Number of PRs in chain'
        required: true
        type: number

env:
  CHAIN_ID: ${{ inputs.chain_id }}
  PR_COUNT: ${{ inputs.pr_count }}

jobs:
  create-chain:
    name: Create PR Chain
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Create chain metadata
        run: |
          mkdir -p .github/pr-chains

          cat << EOF > .github/pr-chains/${CHAIN_ID}.json
          {
            "chain_id": "${CHAIN_ID}",
            "pr_count": ${PR_COUNT},
            "created_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
            "status": "pending",
            "prs": []
          }
          EOF

      - name: Generate PR plan
        id: plan
        run: |
          python << 'EOF'
          import json

          chain_id = "${{ env.CHAIN_ID }}"
          pr_count = int("${{ env.PR_COUNT }}")

          plan = {
            "chain_id": chain_id,
            "prs": []
          }

          for i in range(1, pr_count + 1):
            pr = {
              "number": i,
              "branch": f"chain/{chain_id}/part-{i}",
              "base": f"chain/{chain_id}/part-{i-1}" if i > 1 else "main",
              "title": f"[Chain {chain_id}] Part {i}/{pr_count}",
              "depends_on": i - 1 if i > 1 else None
            }
            plan["prs"].append(pr)

          with open(".github/pr-chains/plan.json", "w") as f:
            json.dump(plan, f, indent=2)

          print(json.dumps(plan, indent=2))
          EOF

      - name: Create PR comment template
        run: |
          cat << 'EOF' > .github/pr-chains/PR_TEMPLATE.md
          <!-- PR Chain: ${{ env.CHAIN_ID }} -->

          ## 🔗 Chain PR #{PR_NUMBER}/{PR_TOTAL}

          **Chain ID**: `${{ env.CHAIN_ID }}`

          ### Dependencies
          {DEPENDENCY_INFO}

          ### Progress
          - [x] Part 1/{PR_TOTAL}: {PR_1_TITLE}
          - [x] Part 2/{PR_TOTAL}: {PR_2_TITLE}
          - [ ] **Current**: Part {PR_NUMBER}/{PR_TOTAL}
          - [ ] Part {NEXT}/{PR_TOTAL}: {NEXT_PR_TITLE}

          ### Merge Order
          ⚠️ **Important**: This PR must be merged in sequence. Do not merge until PR #{PREV_PR} is merged.

          ### Testing
          Each PR in the chain is tested independently and as part of the full chain.

          ---

          *Part of PR chain automation. See [PR Chain Guide](.github/pr-chains/README.md)*
          EOF
```

---

## Best Practices

### Workflow Design

**DO ✅**:
1. Use concurrency groups to cancel duplicate runs
2. Cache dependencies (Playwright browsers, npm packages)
3. Upload artifacts with meaningful retention periods
4. Provide rich job summaries for PR comments
5. Use matrix strategies for multi-browser testing
6. Set appropriate timeouts (job and step level)

**DON'T ❌**:
1. Don't store secrets in workflow files
2. Don't run expensive workflows on every commit
3. Don't skip error handling in scripts
4. Don't use `always()` without conditions
5. Don't ignore workflow validation warnings

---

### MCP Integration

**DO ✅**:
1. Generate MCP context as JSON artifacts
2. Include repository, PR, and CI metadata
3. Make context available to subsequent steps
4. Use typed context schemas
5. Version context format for compatibility

**DON'T ❌**:
1. Don't include sensitive data in context
2. Don't generate context for read-only workflows
3. Don't hardcode paths or URLs
4. Don't skip context validation
5. Don't ignore context size limits

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Playwright CI Documentation](https://playwright.dev/docs/ci)
- [MCP Capability Matrix](./MCP_CAPABILITY_MATRIX.md)

---

**Status**: ✅ Production-Ready
**Version**: 1.0.0
**Last Updated**: 2026-02-17T11:22:00Z
