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

`code-generator-lazy-init.spec.ts` is a separate existing app suite; fixture
success does not establish that suite's success or waive lint/type failures.
