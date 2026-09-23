import { test, expect } from '@playwright/test';
import fs from 'fs';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const axeSourcePath = require.resolve('axe-core/axe.min.js');
const axeSource = fs.readFileSync(axeSourcePath, 'utf8');

test.describe('Enterprise Accessibility & Contrast Audits (WCAG 2.1 AA)', () => {
  const routesToAudit = ['/'];

  for (const route of routesToAudit) {
    test(`Route '${route}' should have 0 critical or serious WCAG 2.1 AA violations`, async ({ page }) => {
      await page.goto(route, { waitUntil: 'networkidle' });

      // Inject axe-core
      await page.evaluate(axeSource);

      // Run audit
      const results = await page.evaluate(async () => {
        // @ts-ignore
        return await window.axe.run(document, {
          runOnly: {
            type: 'tag',
            values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'],
          },
        });
      });

      const criticalAndSerious = results.violations.filter(
        (v: any) => v.impact === 'critical' || v.impact === 'serious'
      );

      if (criticalAndSerious.length > 0) {
        console.error(`A11y Violations on ${route}:`, JSON.stringify(criticalAndSerious, null, 2));
      }

      expect(criticalAndSerious.length).toBe(0);
    });
  }
});
