# ✨ Welcome to Your Spark Template!
You've just launched your brand-new Spark Template Codespace — everything’s fired up and ready for you to explore, build, and create with Spark!

This template is your blank canvas. It comes with a minimal setup to help you get started quickly with Spark development.

🚀 What's Inside?
- A clean, minimal Spark environment
- Pre-configured for local development
- Ready to scale with your ideas

🧠 What Can You Do?

Right now, this is just a starting point — the perfect place to begin building and testing your Spark applications.

🧹 Just Exploring?
No problem! If you were just checking things out and don’t need to keep this code:

- Simply delete your Spark.
- Everything will be cleaned up — no traces left behind.

📄 License For Spark Template Resources

The Spark Template files and resources from GitHub are licensed under the terms of the MIT license, Copyright GitHub, Inc.

## Dependency regression checks

From this directory, run `npm ci`, `npm ls --all`, `npm run lint`,
`node node_modules/typescript/bin/tsc --noEmit`, `npm test`,
`npm run test:coverage`, and `npm run build`. The build uses `--noCheck` and is
not a type-check gate. The direct compiler command fails without installing
anything if TypeScript is absent.

The browser fixture imports the actual resizable/documentation components and
Framer Motion. It checks real panel dimensions, pointer/keyboard resizing,
focus, Markdown safety, Mermaid SVG/error recovery, reduced motion and generated
Tailwind styles in all three configured engines:

```bash
E2E_PORT=5187 node node_modules/@playwright/test/cli.js test e2e/dependency-behavior.spec.ts
```

Only when the installed CLI reports missing browsers or host prerequisites, use
its matching `install chromium firefox webkit` / `install-deps chromium firefox
webkit` commands. The test server refuses occupied ports and disables Spark's
backend proxies; the fixture rejects external requests.

Production tests must build the fixture and serve that output, not start Vite's
development server. Run both ordinary and GitHub Actions base-path builds:

```bash
GITHUB_ACTIONS='' npm run build -- --config e2e/vite.config.ts
GITHUB_ACTIONS='' E2E_PRODUCTION=1 E2E_PORT=5187 \
  node node_modules/@playwright/test/cli.js test e2e/dependency-behavior.spec.ts
GITHUB_ACTIONS=true npm run build -- --config e2e/vite.config.ts
GITHUB_ACTIONS=true E2E_PRODUCTION=1 E2E_PORT=5187 \
  BASE_URL=http://127.0.0.1:5187/_codex_/cognitive_app/ \
  node node_modules/@playwright/test/cli.js test e2e/dependency-behavior.spec.ts
```

### Lazy initialization browser regression matrix

Run the app suite with its **dedicated** configuration, not the main Playwright
configuration. Each of ten loopback servers compiles its own key, API URL and
cascade timing constants; browser scripts never pretend to mutate Vite's
`import.meta.env`. `LAZY_PORT` selects the first of ten consecutive ports
(default 5410–5419). Occupied ports fail rather than attaching to another server.
The config owns startup/shutdown, blocks service workers, has no retries/skips,
and runs all 28 cases in Chromium, Firefox and WebKit:

```bash
GITHUB_ACTIONS='' node node_modules/@playwright/test/cli.js test \
  --config e2e/lazy-init.playwright.config.ts
GITHUB_ACTIONS='' E2E_PRODUCTION=1 node node_modules/@playwright/test/cli.js test \
  --config e2e/lazy-init.playwright.config.ts
GITHUB_ACTIONS=true E2E_PRODUCTION=1 node node_modules/@playwright/test/cli.js test \
  --config e2e/lazy-init.playwright.config.ts
```

Production commands build each variant into `dist/lazy-init/<variant>` before
serving it with Vite preview. The final command verifies the real
`/_codex_/cognitive_app/` base path. The default/keyless builds leave timing
unset; fast/slow use 200/2000ms; zero/negative/excessive/invalid/nan compile
`0`, `-500`, `20000`, `invalid`, `NaN`. API builds cover the unset
`http://localhost:8000` default, explicit loopback, HTTPS and a custom host/port
with `/v1` prefix. `.env` loading is disabled and credentials are synthetic.

Install only missing browsers/prerequisites using the installed CLI as above.
If using a repository-local browser cache, export
`PLAYWRIGHT_BROWSERS_PATH="$PWD/.cache/ms-playwright"` for both installation and
tests; `TMPDIR="$PWD/.cache/installer"` can keep installer/browser scratch local
after creating that directory.

The suite loads the real application and selects its **Code** tab. Exact
`Status:` selectors scope the indicator. Only exact `/status` and `/infer`
URLs for the active build receive synthetic responses satisfying the actual
client schemas. Dashboard startup's three state endpoints, the exact font CSS
URL (empty offline CSS), and Spark's exact loaded-telemetry URL (204) are also
mocked. Everything else external/backend is aborted and fails teardown; no live
API is required. Clipboard tests verify exact `writeText` bytes via an explicit
cross-engine boundary stub, not native OS clipboard permissions. Downloads use
the browser's real download event and verify file contents. The timing fixture
mounts the production `CascadingExecutionMonitor` with one two-stage token and
observes real stage transitions/callbacks under Playwright's controlled clock;
it does not duplicate its timer implementation.

#### Historical 25-case intent mapping

Names below refer to the original lazy-init suite. IDs are stable test title
prefixes. Missing keys now intentionally mean **connected demo mode**, not the
obsolete hard error/disabled-valid-input expectation; production behavior is
unchanged.

| Original case / functional intent | Retained assertion |
| --- | --- |
| Missing-key error/guidance | L01: explicit demo explanation, no configuration error or live calls |
| Missing-key red indicator | L02: exact green demo-connected indicator, never red error |
| Missing-key disabled Generate | L03: empty input disabled; valid demo generation actually succeeds |
| Missing-key prompt submission | L04: entry/count work, valid demo input enabled, no live submission |
| Initial checking state | L05: hold actual status response; yellow Checking then green Connected |
| Transition after status check | L06: exact authenticated default `/status` and Connected, no fallback |
| Enable Generate after initialization | L07: empty remains disabled; valid prompt enabled |
| Periodic status check | L08: no recheck at 29999ms, one at 30000ms; unmount cancels interval |
| Keyed prompt entry | L09: actual string length, valid ARIA state and no error-border token |
| Valid minimum prompt | L10: short invalid styling/disabled state; ten characters valid |
| Progressive character counts | L11: correct counts and disappearance of minimum warning |
| Invalid-key/API fallback | L12: actual `/infer` 401, fallback code, explicit failure explanation |
| Demo Mode toast | L13: `/infer` 500, failure plus successful Demo Mode/k₁ description |
| Copy/download controls | L14: controls visible after completed fallback |
| Cache Hit badge | L15: schema-valid API code; badge present for true, absent for false |
| Default cascade timing | L16: two actual 800ms stages, no early completion |
| Fast cascade timing | L17: two actual 200ms stages, no early completion |
| Slow cascade timing | L18: two actual 2000ms stages, no early completion |
| Invalid timing fallback | L19: all five separately compiled invalid values execute 800ms stages |
| API URL configurations | L20: each compiled URL receives exact status/infer requests and returns API code |
| Generate/copy workflow | L21: exact generated code bytes passed to clipboard; success toast |
| Generate/download workflow | L22: real download, Python filename, exact bytes and toast |
| Short-prompt recovery | L23: no premature infer; corrected prompt generates actual expected code |
| ARIA roles/labels | L24: textbox/button/switch accessible names and invalid ARIA state |
| Keyboard submission | L25: explicit prompt focus, Tab focus on Generate, Enter generates exactly once |

Additional cases assert that **429 rejects without demo success**, 5001
characters cannot submit while 5000 can, and failed keyed status explicitly
connects in demo mode. Development/production fixture success never waives
existing lint, type or unit gates.
