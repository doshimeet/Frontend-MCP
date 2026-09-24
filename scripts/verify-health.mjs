#!/usr/bin/env node
/**
 * Universal Headless Application Health & Diagnostics Engine
 *
 * Verifies live frontend application health across candidate ports (3000, 3001, 4200, 5173).
 * Traps runtime console exceptions, unhandled page errors, HTTP 4xx/5xx network failures,
 * audits interactive focusable elements, and runs axe-core WCAG 2.1 AA audit.
 */

import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';
import net from 'net';
import http from 'http';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load axe-core bundle
let axeSource = '';
try {
  const axeSourcePath = require.resolve('axe-core/axe.min.js');
  axeSource = fs.readFileSync(axeSourcePath, 'utf8');
} catch (err) {
  // axe-core will be skipped if not installed
}

const CANDIDATE_PORTS = [3000, 3001, 4200, 5173];

/**
 * Test whether a TCP port is open locally
 */
function isPortOpen(port, host = '127.0.0.1', timeout = 400) {
  return new Promise((resolve) => {
    const socket = new net.Socket();
    let status = false;

    socket.setTimeout(timeout);
    socket.on('connect', () => {
      status = true;
      socket.destroy();
    });
    socket.on('timeout', () => {
      socket.destroy();
      resolve(false);
    });
    socket.on('error', () => {
      resolve(false);
    });
    socket.on('close', () => {
      resolve(status);
    });

    socket.connect(port, host);
  });
}

/**
 * Launch system browser with enterprise priority: msedge -> chrome -> bundled-chromium
 */
async function launchEnterpriseBrowser(preferredChannel = null, headless = true) {
  const channel = preferredChannel || process.env.PLAYWRIGHT_BROWSER_CHANNEL || 'msedge';
  const candidates = [channel, 'chrome', undefined];

  let lastError = null;
  for (const cand of candidates) {
    try {
      const launchOptions = { headless };
      if (cand) {
        launchOptions.channel = cand;
      }
      const browser = await chromium.launch(launchOptions);
      return { browser, activeChannel: cand || 'bundled-chromium' };
    } catch (err) {
      lastError = err;
    }
  }

  throw new Error(`Failed to launch browser with candidates [${candidates.join(', ')}]: ${lastError?.message}`);
}

/**
 * Resolve target URL: explicitly provided or auto-probed
 */
async function resolveTargetUrl(explicitUrl) {
  if (explicitUrl) {
    try {
      const parsed = new URL(explicitUrl);
      const port = parsed.port ? parseInt(parsed.port, 10) : (parsed.protocol === 'https:' ? 443 : 80);
      return { url: explicitUrl, port };
    } catch (err) {
      return { url: explicitUrl, port: 3000 };
    }
  }

  for (const port of CANDIDATE_PORTS) {
    const open = await isPortOpen(port);
    if (open) {
      return { url: `http://localhost:${port}`, port };
    }
  }

  return { url: 'http://localhost:3000', port: 3000, unreachable: true };
}

/**
 * Run comprehensive health audit on application URL
 */
export async function verifyApplicationHealth(targetUrl = null) {
  const timestamp = new Date().toISOString();
  const { url, port, unreachable } = await resolveTargetUrl(targetUrl);

  if (unreachable) {
    return {
      url,
      detected_port: port,
      timestamp,
      http_status: 0,
      is_healthy: false,
      console_errors: ['Server unreachable: No process listening on candidate dev ports [3000, 3001, 4200, 5173]'],
      failing_requests: [],
      interactive_elements_tested: 0,
      a11y_violations_count: 0,
      a11y_critical_count: 0,
      remediations: [
        `Dev server not running. Start application via 'npm run dev' on port 3000, 3001, 4200, or 5173.`,
        `Ensure firewall allows localhost loopback connections.`,
      ],
    };
  }

  let browser;
  const consoleErrors = [];
  const failingRequests = [];

  try {
    const launched = await launchEnterpriseBrowser();
    browser = launched.browser;
    const page = await browser.newPage();

    // Trap console errors & uncaught exceptions
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });

    page.on('pageerror', (err) => {
      consoleErrors.push(`Uncaught Exception: ${err.message}`);
    });

    // Trap failed network requests (excluding optional favicon/manifest)
    page.on('response', (response) => {
      const status = response.status();
      const reqUrl = response.url();
      if (status >= 400 && !reqUrl.includes('favicon.ico') && !reqUrl.includes('robots.txt')) {
        failingRequests.push(`${status} ${reqUrl}`);
      }
    });

    // Navigate to page
    let httpStatus = 200;
    try {
      const navResp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 15000 });
      if (navResp) {
        httpStatus = navResp.status();
      }
    } catch (navErr) {
      httpStatus = 504;
      consoleErrors.push(`Navigation failed: ${navErr.message}`);
    }

    // Interactive elements count
    let interactiveCount = 0;
    try {
      const interactiveElements = await page.locator(
        'button, a[href], input, select, textarea, [tabindex="0"], [role="button"], [role="tab"]'
      ).all();
      interactiveCount = interactiveElements.length;
    } catch (e) {
      interactiveCount = 0;
    }

    // Run axe-core accessibility check if available
    let a11yViolationsCount = 0;
    let a11yCriticalCount = 0;
    const remediations = [];

    if (axeSource && httpStatus < 400) {
      try {
        await page.evaluate(axeSource);
        const axeResults = await page.evaluate(async () => {
          // @ts-ignore
          return await window.axe.run(document, {
            runOnly: {
              type: 'tag',
              values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa'],
            },
          });
        });

        a11yViolationsCount = axeResults.violations.length;
        a11yCriticalCount = axeResults.violations.filter((v) => v.impact === 'critical').length;

        for (const v of axeResults.violations) {
          if (v.impact === 'critical' || v.impact === 'serious') {
            remediations.push(`[A11y ${v.impact.toUpperCase()}] ${v.id}: ${v.help} (${v.nodes.length} occurrences)`);
          }
        }
      } catch (axeErr) {
        // Soft fail on axe if page unmounted
      }
    }

    // Gate 2: Programmatic Anti-Slop Audit
    let designSlopViolations = [];
    let designQualityScore = 100;
    try {
      const slopResults = await page.evaluate(() => {
        const issues = [];
        const h1s = document.querySelectorAll('h1');
        if (h1s.length > 1) {
          issues.push(`[Hierarchy Slop] Multiple <h1> headings detected (${h1s.length}). Exactly one <h1> is permitted.`);
        }
        const headings = Array.from(document.querySelectorAll('h1, h2, h3'));
        for (let i = 0; i < headings.length - 1; i++) {
          const t1 = headings[i].innerText.toLowerCase();
          const t2 = headings[i + 1].innerText.toLowerCase();
          const w1 = t1.match(/\w{4,}/g) || [];
          const w2 = t2.match(/\w{4,}/g) || [];
          const overlap = w1.filter((w) => w2.includes(w));
          if (overlap.length >= 2) {
            issues.push(`[Hierarchy Slop] Stacked redundant headings: <${headings[i].tagName.toLowerCase()}> '${headings[i].innerText.trim()}' followed by <${headings[i + 1].tagName.toLowerCase()}> '${headings[i + 1].innerText.trim()}'.`);
          }
        }
        const styledEls = Array.from(document.querySelectorAll('[style]'));
        const complexStyles = styledEls.filter((el) => {
          const s = el.getAttribute('style').toLowerCase();
          return s.includes('display:') || s.includes('border:') || s.includes('padding:');
        });
        if (complexStyles.length > 5) {
          issues.push(`[Styling Slop] Excessive raw inline styles (${complexStyles.length} elements). Use Nexus utility classes.`);
        }
        const yellowBanner = styledEls.some((el) => {
          const s = el.getAttribute('style').toLowerCase();
          return s.includes('#ffcc00') || s.includes('rgb(255, 204, 0)');
        });
        if (yellowBanner) {
          issues.push(`[Brand Slop] Unrefined full-width yellow banner detected (#ffcc00). Use .nexus-classification-pill.`);
        }
        const allBadges = Array.from(document.querySelectorAll('.cds--tag, [class*="badge"], [class*="chip"]'));
        const nonTableBadges = allBadges.filter((el) => !el.closest('td, th'));
        const cells = Array.from(document.querySelectorAll('td, th'));
        const overpackedCell = cells.find((cell) => cell.querySelectorAll('.cds--tag, [class*="badge"], [class*="chip"]').length > 3);

        if (nonTableBadges.length > 4) {
          issues.push(`[Badge Overload] Excessive non-tabular badges detected (${nonTableBadges.length} in cards/headers). Limit badges to operational state transitions.`);
        } else if (overpackedCell) {
          const count = overpackedCell.querySelectorAll('.cds--tag, [class*="badge"], [class*="chip"]').length;
          issues.push(`[Badge Overload] Clustered status chips detected inside a single table cell (${count} badges in one cell). Limit cell metadata density.`);
        }
        return issues;
      });
      designSlopViolations = slopResults;
      designQualityScore = Math.max(0, 100 - designSlopViolations.length * 15);
      remediations.push(...designSlopViolations);
    } catch (e) {
      // Soft fail
    }

    if (consoleErrors.length > 0) {
      remediations.push(`Fix ${consoleErrors.length} client console error(s) detected during page render.`);
    }
    if (failingRequests.length > 0) {
      remediations.push(`Resolve ${failingRequests.length} failing network request(s) (HTTP 4xx/5xx).`);
    }

    const isHealthy = httpStatus === 200 && consoleErrors.length === 0 && a11yCriticalCount === 0 && designSlopViolations.length === 0;

    return {
      url,
      detected_port: port,
      timestamp,
      http_status: httpStatus,
      is_healthy: isHealthy,
      console_errors: consoleErrors,
      failing_requests: failingRequests,
      interactive_elements_tested: interactiveCount,
      a11y_violations_count: a11yViolationsCount,
      a11y_critical_count: a11yCriticalCount,
      design_slop_violations: designSlopViolations,
      design_quality_score: designQualityScore,
      remediations,
    };
  } catch (err) {
    return {
      url,
      detected_port: port,
      timestamp,
      http_status: 500,
      is_healthy: false,
      console_errors: [err.message],
      failing_requests: [],
      interactive_elements_tested: 0,
      a11y_violations_count: 0,
      a11y_critical_count: 0,
      remediations: [`Ensure browser engine is available and dev server is running.`],
    };
  } finally {
    if (browser) {
      await browser.close().catch(() => {});
    }
  }
}

// CLI entry point
if (process.argv[1] && process.argv[1].endsWith('verify-health.mjs')) {
  const args = process.argv.slice(2);
  let explicitUrl = null;
  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--url' && args[i + 1]) {
      explicitUrl = args[i + 1];
    }
  }

  verifyApplicationHealth(explicitUrl)
    .then((report) => {
      console.log(JSON.stringify(report, null, 2));
      process.exit(0);
    })
    .catch((err) => {
      console.error(JSON.stringify({ error: err.message }));
      process.exit(1);
    });
}
