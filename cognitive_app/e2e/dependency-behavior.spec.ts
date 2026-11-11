import { test, expect } from '@playwright/test';

test.beforeEach(async ({ page, baseURL }) => {
  const origin = new URL(baseURL!).origin;
  await page.route('**/*', async (route) => {
    const url = new URL(route.request().url());
    if (url.origin === origin) {
      await route.continue();
    } else {
      await route.abort('blockedbyclient');
      throw new Error(`Unexpected external request: ${url.origin}${url.pathname}`);
    }
  });
});

for (const variant of ['horizontal', 'vertical', 'legacy', 'precedence']) {
  test(`${variant} panels resize by pointer and keyboard with real layout`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
    await page.goto('e2e/fixtures/dependencies.html');
    const section = page.getByRole('region', { name: `${variant} panels` });
    const group = section.locator('[data-slot="resizable-panel-group"]');
    const first = section.locator('[data-slot="resizable-panel"]').first();
    const handle = section.getByRole('separator');
    const vertical = variant === 'vertical' || variant === 'legacy';
    const dimension = vertical ? 'height' : 'width';
    await expect(group).toHaveCSS('flex-direction', vertical ? 'column' : 'row');
    await expect(handle).toHaveAttribute('aria-orientation', vertical ? 'horizontal' : 'vertical');
    await expect(handle).toHaveAttribute('tabindex', '0');
    await handle.scrollIntoViewIfNeeded();
    await expect.poll(async () => (await first.boundingBox())![dimension]).toBeGreaterThan(50);
    const before = (await first.boundingBox())![dimension];
    expect(before).toBeCloseTo((vertical ? 240 : 600) * 0.4, -1);
    const box = (await handle.boundingBox())!;
    const x = box.x + box.width / 2;
    const y = box.y + box.height / 2;
    await page.mouse.move(x, y);
    await page.mouse.down();
    await page.mouse.move(x + (vertical ? 0 : 50), y + (vertical ? 50 : 0), { steps: 10 });
    await page.mouse.up();
    await expect.poll(async () => (await first.boundingBox())![dimension]).toBeGreaterThan(before + 25);
    const dragged = (await first.boundingBox())![dimension];
    await handle.focus();
    await expect(handle).toBeFocused();
    await page.keyboard.press(vertical ? 'ArrowUp' : 'ArrowLeft');
    await expect.poll(async () => (await first.boundingBox())![dimension]).toBeLessThan(dragged - 1);
    await test.info().attach('layout-evidence.json', {
      body: JSON.stringify({
        variant, dimension, before, dragged,
        keyboard: (await first.boundingBox())![dimension],
        flexDirection: await group.evaluate((element) => getComputedStyle(element).flexDirection),
      }),
      contentType: 'application/json',
    });
    expect(errors).toEqual([]);
  });
}

test('real Markdown, strict Mermaid rendering, rerender and visible errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (error) => errors.push(error.message));
  page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
  await page.goto('e2e/fixtures/dependencies.html');
  await expect(page.getByRole('heading', { name: 'Synthetic documentation' })).toBeVisible();
  await expect(page.getByRole('table')).toContainText('marked');
  await expect(page.locator('.katex')).toBeVisible();
  await expect(page.getByText('synthetic code', { exact: true })).toHaveJSProperty('tagName', 'CODE');
  await expect(page.getByText('unsafe', { exact: true })).not.toHaveAttribute('href');
  expect(await page.locator('.doc-content script, .doc-content [onclick]').count()).toBe(0);
  expect(await page.evaluate(() => 'fixtureUnsafe' in window)).toBe(false);
  const mermaid = page.getByRole('region', { name: 'Mermaid fixture' });
  const diagram = mermaid.locator('svg.flowchart');
  await expect(diagram).toBeVisible();
  await expect(diagram).toContainText('Alpha');
  await mermaid.getByRole('button', { name: 'Change chart' }).click();
  await expect(diagram).toContainText('Gamma');
  await expect(diagram).not.toContainText('Alpha');
  await mermaid.getByRole('button', { name: 'Invalid chart' }).click();
  await expect(mermaid.getByText('Diagram render error')).toBeVisible();
  await expect(mermaid.locator('pre')).toHaveText('not a valid diagram');
  await mermaid.getByRole('button', { name: 'Change chart' }).click();
  await expect(diagram).toContainText('Gamma');
  expect(errors).toEqual([]);
});

for (const reducedMotion of ['no-preference', 'reduce'] as const) {
  test(`animation and Tailwind styles with reduced motion ${reducedMotion}`, async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (error) => errors.push(error.message));
    page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
    await page.emulateMedia({ reducedMotion });
    await page.goto('e2e/fixtures/dependencies.html');
    const square = page.getByTestId('motion-fixture');
    await expect(square).toHaveCSS('width', '16px');
    await expect(square).toHaveCSS('height', '16px');
    await expect(square).not.toHaveCSS('background-color', 'rgba(0, 0, 0, 0)');
    await expect(page.locator('svg.flowchart')).toBeVisible();
    await square.scrollIntoViewIfNeeded();
    const before = (await square.boundingBox())!.x;
    await page.getByRole('button', { name: 'Animate fixture' }).click();
    const samples = await square.evaluate(async (element) => {
      const positions: number[] = [];
      for (let frame = 0; frame < 60; frame++) {
        await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
        positions.push(new DOMMatrixReadOnly(getComputedStyle(element).transform).m41);
        if (positions.at(-1)! >= 119.5) break;
      }
      return positions;
    });
    await test.info().attach('animation-samples.json', {
      body: JSON.stringify({ reducedMotion, samples }),
      contentType: 'application/json',
    });
    const interpolated = samples.some((position) => position > 0.5 && position < 119.5);
    expect(interpolated).toBe(reducedMotion !== 'reduce');
    await expect(square).toHaveCSS('opacity', '0.5');
    const after = (await square.boundingBox())!.x;
    expect(after - before).toBeCloseTo(120, 0);
    await test.info().attach('motion-evidence.json', {
      body: JSON.stringify({ reducedMotion, samples, before, after }),
      contentType: 'application/json',
    });
    expect(errors).toEqual([]);
  });
}
