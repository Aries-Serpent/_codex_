# MCP Package.json Integration Recipe

> **Generated**: 2026-02-17T11:23:00Z
> **Repository**: Aries-Serpent/_codex_
> **Purpose**: Complete package.json configuration for MCP-enabled projects
> **Status**: Production-Ready Template

---

## Complete package.json Template

### Location: `cognitive_app/package.json`

```json
{
  "name": "@codex/cognitive-app",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "description": "Cognitive App with MCP integration for E2E testing and automation",
  "author": "Aries-Serpent",
  "license": "MIT",
  "repository": {
    "type": "git",
    "url": "https://github.com/Aries-Serpent/_codex_.git",
    "directory": "cognitive_app"
  },

  "scripts": {
    "dev": "vite",
    "build": "tsc -b --noCheck && vite build",
    "lint": "eslint .",
    "preview": "vite preview",
    "optimize": "vite optimize",

    "test": "vitest run",
    "test:watch": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest run --coverage",

    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:chromium": "playwright test --project=chromium",
    "test:e2e:firefox": "playwright test --project=firefox",
    "test:e2e:webkit": "playwright test --project=webkit",
    "test:e2e:mobile": "playwright test --project='Mobile Chrome' --project='Mobile Safari'",
    "test:e2e:report": "playwright show-report",
    "test:e2e:trace": "playwright show-trace",
    "test:e2e:codegen": "playwright codegen http://localhost:5173",
    "test:e2e:install": "playwright install --with-deps",
    "test:e2e:update-snapshots": "playwright test --update-snapshots",
    "test:e2e:ci": "playwright test --reporter=github --reporter=html --reporter=json",
    "test:e2e:smoke": "GREP='@smoke' playwright test",
    "test:e2e:regression": "GREP='@regression' playwright test",

    "mcp:setup": "npm run mcp:install && npm run mcp:configure",
    "mcp:install": "npm install -D @modelcontextprotocol/sdk @playwright/test",
    "mcp:configure": "node scripts/setup-mcp.js",
    "mcp:validate": "node scripts/validate-mcp.js",
    "mcp:context": "node scripts/generate-mcp-context.js",

    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,js,jsx,json,css,md}\"",
    "typecheck": "tsc --noEmit",
    "validate": "npm run lint && npm run typecheck && npm run test && npm run test:e2e",

    "ci": "npm run lint && npm run typecheck && npm run test && npm run build",
    "ci:e2e": "npm run test:e2e:ci",

    "clean": "rimraf dist playwright-report test-results .vite node_modules/.vite",
    "clean:all": "npm run clean && rimraf node_modules",

    "preinstall": "npx only-allow npm",
    "postinstall": "playwright install chromium --with-deps || echo 'Playwright install skipped (CI or missing deps)'"
  },

  "dependencies": {
    "@github/spark": ">=0.43.1 <1",
    "@phosphor-icons/react": "^2.1.10",
    "@radix-ui/colors": "^3.0.0",
    "@radix-ui/react-accordion": "^1.2.3",
    "@radix-ui/react-alert-dialog": "^1.1.6",
    "@radix-ui/react-aspect-ratio": "^1.1.2",
    "@radix-ui/react-avatar": "^1.1.3",
    "@radix-ui/react-checkbox": "^1.1.4",
    "@radix-ui/react-collapsible": "^1.1.3",
    "@radix-ui/react-context-menu": "^2.2.6",
    "@radix-ui/react-dialog": "^1.1.6",
    "@radix-ui/react-dropdown-menu": "^2.1.6",
    "@radix-ui/react-hover-card": "^1.1.6",
    "@radix-ui/react-label": "^2.1.2",
    "@radix-ui/react-menubar": "^1.1.6",
    "@radix-ui/react-navigation-menu": "^1.2.5",
    "@radix-ui/react-popover": "^1.1.6",
    "@radix-ui/react-progress": "^1.1.2",
    "@radix-ui/react-radio-group": "^1.2.3",
    "@radix-ui/react-scroll-area": "^1.2.9",
    "@radix-ui/react-select": "^2.1.6",
    "@radix-ui/react-separator": "^1.1.2",
    "@radix-ui/react-slider": "^1.3.6",
    "@radix-ui/react-slot": "^1.1.2",
    "@radix-ui/react-switch": "^1.1.3",
    "@radix-ui/react-tabs": "^1.1.3",
    "@radix-ui/react-toggle": "^1.1.2",
    "@radix-ui/react-toggle-group": "^1.1.2",
    "@radix-ui/react-tooltip": "^1.1.8",
    "@tailwindcss/vite": "^4.1.11",
    "class-variance-authority": "^0.7.1",
    "clsx": "^2.1.1",
    "cmdk": "^1.1.1",
    "date-fns": "^3.6.0",
    "embla-carousel-react": "^8.5.2",
    "framer-motion": "^12.24.0",
    "input-otp": "^1.4.2",
    "lucide-react": "^0.484.0",
    "next-themes": "^0.4.6",
    "react": "^19.0.0",
    "react-day-picker": "^9.6.7",
    "react-dom": "^19.0.0",
    "react-error-boundary": "^6.0.0",
    "react-hook-form": "^7.54.2",
    "react-resizable-panels": "^2.1.7",
    "recharts": "^2.15.4",
    "sonner": "^2.0.1",
    "tailwind-merge": "^3.0.2",
    "vaul": "^1.1.2",
    "zod": "^3.25.76"
  },

  "devDependencies": {
    "@eslint/js": "^9.21.0",
    "@playwright/test": "^1.57.0",
    "@tailwindcss/postcss": "^4.1.18",
    "@testing-library/jest-dom": "^6.9.1",
    "@testing-library/react": "^16.3.1",
    "@testing-library/user-event": "^14.6.1",
    "@types/node": "^22.10.0",
    "@types/react": "^19.0.10",
    "@types/react-dom": "^19.0.4",
    "@vitejs/plugin-react-swc": "^4.2.2",
    "@vitest/coverage-v8": "^4.0.16",
    "@vitest/ui": "^4.0.16",
    "eslint": "^9.28.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.19",
    "globals": "^16.0.0",
    "jsdom": "^27.4.0",
    "prettier": "^3.2.5",
    "rimraf": "^5.0.5",
    "tailwindcss": "^4.1.18",
    "typescript": "~5.7.2",
    "typescript-eslint": "^8.38.0",
    "vite": "^7.2.6",
    "vitest": "^4.0.16"
  },

  "optionalDependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  },

  "engines": {
    "node": ">=22.0.0",
    "npm": ">=9.0.0"
  },

  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },

  "workspaces": {
    "packages": [
      "packages/*"
    ]
  }
}
```

---

## MCP-Specific Scripts

### Script: `scripts/setup-mcp.js`

**Purpose**: Configure MCP integration automatically

```javascript
#!/usr/bin/env node

/**
 * MCP Setup Script
 *
 * Configures MCP integration for the project:
 * - Verifies Playwright installation
 * - Creates MCP configuration files
 * - Sets up environment variables
 * - Validates MCP server connectivity
 */

import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

async function main() {
  console.log('🔧 Setting up MCP integration...\n');

  // Step 1: Verify Playwright installation
  console.log('1️⃣ Verifying Playwright installation...');
  try {
    await import('@playwright/test');
    console.log('   ✅ Playwright installed\n');
  } catch (error) {
    console.error('   ❌ Playwright not found. Run: npm install -D @playwright/test');
    process.exit(1);
  }

  // Step 2: Create .mcp directory
  console.log('2️⃣ Creating .mcp directory...');
  const mcpDir = path.join(rootDir, '.mcp');
  await fs.mkdir(mcpDir, { recursive: true });
  console.log(`   ✅ Created: ${mcpDir}\n`);

  // Step 3: Create MCP configuration template
  console.log('3️⃣ Creating MCP configuration...');
  const mcpConfig = {
    version: '1.0.0',
    servers: {
      github: {
        enabled: true,
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-github'],
        env: {
          GITHUB_TOKEN: '${GITHUB_TOKEN}'
        }
      },
      playwright: {
        enabled: true,
        command: 'npx',
        args: ['-y', '@playwright/mcp-server']
      }
    }
  };

  const configPath = path.join(mcpDir, 'config.json');
  await fs.writeFile(configPath, JSON.stringify(mcpConfig, null, 2));
  console.log(`   ✅ Created: ${configPath}\n`);

  // Step 4: Create .env.example
  console.log('4️⃣ Creating .env.example...');
  const envExample = `# GitHub MCP Server
GITHUB_TOKEN=your_github_personal_access_token_here

# Playwright Configuration
BASE_URL=http://localhost:5173
HEADED=false

# Test Configuration
TEST_USERNAME=testuser
TEST_PASSWORD=testpass
`;

  const envExamplePath = path.join(rootDir, '.env.example');
  await fs.writeFile(envExamplePath, envExample);
  console.log(`   ✅ Created: ${envExamplePath}\n`);

  // Step 5: Create gitignore entries
  console.log('5️⃣ Updating .gitignore...');
  const gitignorePath = path.join(rootDir, '.gitignore');
  const gitignoreEntries = `
# MCP
.mcp/cache/
.mcp/*.log

# Playwright
playwright-report/
test-results/
playwright/.cache/

# Environment
.env
.env.local
`;

  try {
    const existing = await fs.readFile(gitignorePath, 'utf-8');
    if (!existing.includes('.mcp/cache/')) {
      await fs.appendFile(gitignorePath, gitignoreEntries);
      console.log('   ✅ Updated .gitignore\n');
    } else {
      console.log('   ℹ️  .gitignore already configured\n');
    }
  } catch (error) {
    await fs.writeFile(gitignorePath, gitignoreEntries);
    console.log('   ✅ Created .gitignore\n');
  }

  // Step 6: Summary
  console.log('✅ MCP setup complete!\n');
  console.log('📝 Next steps:');
  console.log('   1. Copy .env.example to .env');
  console.log('   2. Add your GITHUB_TOKEN to .env');
  console.log('   3. Run: npm run test:e2e:install');
  console.log('   4. Run: npm run test:e2e\n');
}

main().catch((error) => {
  console.error('❌ Setup failed:', error);
  process.exit(1);
});
```

---

### Script: `scripts/generate-mcp-context.js`

**Purpose**: Generate MCP context manifest for CI/CD

```javascript
#!/usr/bin/env node

/**
 * MCP Context Generator
 *
 * Generates MCP context manifest with repository, PR, and CI metadata
 * Output: .mcp/context.json
 */

import fs from 'fs/promises';
import path from 'path';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, '..');

function runGitCommand(command) {
  try {
    return execSync(command, { encoding: 'utf-8', cwd: rootDir }).trim();
  } catch (error) {
    return null;
  }
}

async function generateContext() {
  console.log('📊 Generating MCP context...\n');

  const context = {
    generated_at: new Date().toISOString(),
    repository: {
      name: process.env.GITHUB_REPOSITORY || runGitCommand('git config --get remote.origin.url'),
      id: process.env.GITHUB_REPOSITORY_ID || null,
      default_branch: runGitCommand('git symbolic-ref refs/remotes/origin/HEAD | sed "s@^refs/remotes/origin/@@"'),
      current_branch: runGitCommand('git rev-parse --abbrev-ref HEAD'),
      total_commits: runGitCommand('git rev-list --count HEAD'),
      latest_commit: {
        sha: runGitCommand('git rev-parse HEAD'),
        message: runGitCommand('git log -1 --pretty=%B'),
        author: runGitCommand('git log -1 --pretty=%an'),
        date: runGitCommand('git log -1 --pretty=%aI'),
      }
    },
    recent_commits: runGitCommand('git log --oneline -10').split('\n').map(line => {
      const [sha, ...messageParts] = line.split(' ');
      return {
        sha,
        message: messageParts.join(' ')
      };
    }),
    languages: {
      python: execSync('find . -name "*.py" | wc -l', { cwd: rootDir, encoding: 'utf-8' }).trim(),
      typescript: execSync('find . -name "*.ts" | wc -l', { cwd: rootDir, encoding: 'utf-8' }).trim(),
      javascript: execSync('find . -name "*.js" | wc -l', { cwd: rootDir, encoding: 'utf-8' }).trim(),
    },
    ci: process.env.CI ? {
      workflow: process.env.GITHUB_WORKFLOW,
      run_id: process.env.GITHUB_RUN_ID,
      run_number: process.env.GITHUB_RUN_NUMBER,
      actor: process.env.GITHUB_ACTOR,
      event_name: process.env.GITHUB_EVENT_NAME,
    } : null,
    pr: process.env.GITHUB_EVENT_NAME === 'pull_request' ? {
      number: process.env.GITHUB_REF.split('/')[2],
      head_sha: process.env.GITHUB_SHA,
    } : null
  };

  const mcpDir = path.join(rootDir, '.mcp');
  await fs.mkdir(mcpDir, { recursive: true });

  const contextPath = path.join(mcpDir, 'context.json');
  await fs.writeFile(contextPath, JSON.stringify(context, null, 2));

  console.log(`✅ Context generated: ${contextPath}`);
  console.log(`   Size: ${JSON.stringify(context).length} bytes`);
  console.log(`   Repository: ${context.repository.name}`);
  console.log(`   Branch: ${context.repository.current_branch}`);
  console.log(`   Commits: ${context.repository.total_commits}\n`);
}

generateContext().catch((error) => {
  console.error('❌ Context generation failed:', error);
  process.exit(1);
});
```

---

## Environment Variables

### File: `.env.example`

```bash
# ===================================
# MCP Configuration
# ===================================

# GitHub MCP Server
# Get token from: https://github.com/settings/tokens
# Required scopes: repo, workflow, read:org
GITHUB_TOKEN=ghp_your_token_here

# GitHub Repository (auto-detected in CI)
GITHUB_REPOSITORY=Aries-Serpent/_codex_
GITHUB_REPOSITORY_ID=R_kgDOPjJ9Hg

# ===================================
# Playwright Configuration
# ===================================

# Base URL for E2E tests
BASE_URL=http://localhost:5173

# Run tests in headed mode (visible browser)
HEADED=false

# Browser to use (chromium, firefox, webkit)
BROWSER=chromium

# Slow motion (milliseconds) - useful for debugging
SLOW_MO=0

# ===================================
# Test Configuration
# ===================================

# Test user credentials (for authenticated tests)
TEST_USERNAME=testuser@example.com
TEST_PASSWORD=SecureTestPassword123!

# Test API key (for API tests)
TEST_API_KEY=test-key-12345

# Test API URL (defaults to BASE_URL/api)
TEST_API_URL=http://localhost:8000/api

# ===================================
# CI/CD Configuration
# ===================================

# CI environment (set automatically in GitHub Actions)
CI=false

# Enable debug logging
DEBUG=pw:api

# Test parallelism (number of workers)
# CI: 1 (sequential), Local: undefined (parallel)
WORKERS=

# Test retries on failure
RETRIES=0

# ===================================
# MCP Server Configuration
# ===================================

# MCP endpoint (for MCP server integration)
MCP_ENDPOINT=http://localhost:8080

# MCP cache directory
MCP_CACHE_DIR=.mcp/cache

# MCP log level (debug, info, warn, error)
MCP_LOG_LEVEL=info
```

---

## Installation Commands

### Quick Start

```bash
# 1. Clone repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_/cognitive_app

# 2. Install dependencies
npm install

# 3. Setup MCP integration
npm run mcp:setup

# 4. Configure environment
cp .env.example .env
# Edit .env and add your GITHUB_TOKEN

# 5. Install Playwright browsers
npm run test:e2e:install

# 6. Run E2E tests
npm run test:e2e
```

### Detailed Setup

```bash
# Install all dependencies
npm install

# Install Playwright browsers (all)
npx playwright install --with-deps

# Install specific browser only
npx playwright install chromium --with-deps

# Verify installation
npx playwright --version

# Run setup script
npm run mcp:setup

# Validate MCP configuration
npm run mcp:validate

# Generate MCP context
npm run mcp:context
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
- name: Setup Node.js and dependencies
  run: |
    cd cognitive_app
    npm ci

- name: Setup MCP integration
  run: |
    cd cognitive_app
    npm run mcp:setup
    npm run mcp:context

- name: Run E2E tests
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    BASE_URL: http://localhost:5173
  run: |
    cd cognitive_app
    npm run test:e2e:ci
```

---

## Troubleshooting

### Issue: "Playwright executable doesn't exist"

**Solution**:
```bash
npx playwright install --with-deps chromium
```

---

### Issue: "GITHUB_TOKEN not set"

**Solution**:
1. Create token at https://github.com/settings/tokens
2. Add to .env file
3. Ensure scopes: `repo`, `workflow`, `read:org`

---

### Issue: "Module not found: @modelcontextprotocol/sdk"

**Solution**:
```bash
npm install -D @modelcontextprotocol/sdk
```

---

## Best Practices

**DO ✅**:
1. Use `npm ci` in CI/CD (deterministic installs)
2. Cache `node_modules` and Playwright browsers
3. Version lock important dependencies
4. Run `npm audit` regularly
5. Keep Playwright version up-to-date

**DON'T ❌**:
1. Don't commit `node_modules` or `.env`
2. Don't use `npm install` in CI (use `npm ci`)
3. Don't skip `postinstall` hooks
4. Don't ignore security vulnerabilities
5. Don't use outdated Node.js versions

---

**Status**: ✅ Production-Ready
**Version**: 1.0.0
**Last Updated**: 2026-02-17T11:23:00Z
