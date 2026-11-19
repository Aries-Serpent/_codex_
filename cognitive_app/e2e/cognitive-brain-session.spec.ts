import { expect, test } from '@playwright/test';

const API = 'http://127.0.0.1:8765';

test('Cognitive Brain UI session authorizes protected HTTP operations', async ({ page }) => {
  await page.goto('/');
  const result = await page.evaluate(async (api) => {
    const session = await fetch(`${api}/api/session`, {
      method: 'POST',
      credentials: 'include',
    });
    const command = await fetch(`${api}/api/cli/run`, {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ command: 'git status --short', timeout: 10 }),
    });
    return {
      sessionStatus: session.status,
      sessionBody: await session.json(),
      commandStatus: command.status,
    };
  }, API);

  expect(result.sessionStatus).toBe(200);
  expect(result.sessionBody.credential_transport).toBe('httponly_cookie');
  expect(result.commandStatus).toBe(200);
});
