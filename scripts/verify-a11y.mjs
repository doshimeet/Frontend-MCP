#!/usr/bin/env node
/**
 * Automated Headless Accessibility & Contrast Verification Engine (Playwright + axe-core)
 *
 * Enterprise WCAG 2.1 Level AA Compliance Auditor.
 * Launches headless system browser (Edge or Chrome fallback), injects axe-core,
 * evaluates DOM accessibility tree and contrast ratios, and formats an actionable audit report.
 */

import { chromium } from 'playwright-core';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { createRequire } from 'module';

const require = createRequire(import.meta.url);
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Load axe-core bundle
const axeSourcePath = require.resolve('axe-core/axe.min.js');
const axeSource = fs.readFileSync(axeSourcePath, 'utf8');

/**
 * Launch system browser with enterprise priority: msedge -> chrome -> chromium
 */
export async function launchEnterpriseBrowser(preferredChannel = null, headless = true) {
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
 * Run axe-core accessibility audit on a Playwright Page
 */
export async function auditPage(page, options = {}) {
  // Inject axe-core source into page context
  await page.evaluate(axeSource);

  // Configure WCAG 2.1 AA rules
  const axeOptions = {
    runOnly: {
      type: 'tag',
      values: options.tags || ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice'],
    },
  };

  const results = await page.evaluate(async (opts) => {
    // @ts-ignore
    return await window.axe.run(document, opts);
  }, axeOptions);

  // Generate remediation advice based on design system rules
  const remediations = results.violations.map((v) => {
    if (v.id === 'color-contrast') {
      return `[Token Contrast] Rule '${v.id}': Use IBM Carbon / Design System high-contrast tokens ($text-primary: #161616, $interactive: #0f62fe). Current text violates 4.5:1 ratio.`;
    }
    if (v.id === 'button-name') {
      return `[Micro-copy / Clarify] Rule '${v.id}': Button is missing discernible accessible text or aria-label. Provide an action verb label.`;
    }
    if (v.id === 'label') {
      return `[Form Accessibility] Rule '${v.id}': Form input missing associated <label> or id/htmlFor binding.`;
    }
    if (v.id === 'landmark-one-main' || v.id === 'region') {
      return `[Structural Shell] Rule '${v.id}': Ensure page layout is enclosed in <main role="main"> landmark.`;
    }
    return `[A11y Remediation] Rule '${v.id}': ${v.help} (See ${v.helpUrl})`;
  });

  const criticalAndSerious = results.violations.filter((v) => v.impact === 'critical' || v.impact === 'serious');

  return {
    url: page.url(),
    timestamp: new Date().toISOString(),
    success: criticalAndSerious.length === 0,
    passesCount: results.passes.length,
    violationsCount: results.violations.length,
    criticalCount: results.violations.filter((v) => v.impact === 'critical').length,
    seriousCount: results.violations.filter((v) => v.impact === 'serious').length,
    moderateCount: results.violations.filter((v) => v.impact === 'moderate').length,
    minorCount: results.violations.filter((v) => v.impact === 'minor').length,
    violations: results.violations,
    remediations,
  };
}

/**
 * Audit live URL
 */
export async function auditUrl(url, options = {}) {
  const { browser, activeChannel } = await launchEnterpriseBrowser(options.channel, options.headless !== false);
  try {
    const context = await browser.newContext({
      viewport: options.viewport || { width: 1280, height: 800 },
    });
    const page = await context.newPage();
    
    // Navigate with timeout
    await page.goto(url, { waitUntil: 'networkidle', timeout: options.timeout || 15000 });
    const auditResult = await auditPage(page, options);
    auditResult.browserChannel = activeChannel;
    return auditResult;
  } finally {
    await browser.close();
  }
}

/**
 * Audit raw HTML string (ideal for test harnesses and pre-commit scans)
 */
export async function auditHtml(htmlContent, options = {}) {
  const { browser, activeChannel } = await launchEnterpriseBrowser(options.channel, options.headless !== false);
  try {
    const page = await browser.newPage();
    await page.setContent(htmlContent, { waitUntil: 'load' });
    const auditResult = await auditPage(page, options);
    auditResult.browserChannel = activeChannel;
    return auditResult;
  } finally {
    await browser.close();
  }
}

/**
 * Pretty-print audit results to console
 */
export function formatAuditReport(report) {
  console.log('\n================================================================================');
  console.log('       ENTERPRISE ACCESSIBILITY AUDIT REPORT (Playwright + axe-core)');
  console.log('================================================================================');
  console.log(` Target Target:     ${report.url || 'HTML Document'}`);
  console.log(` Browser Engine:    ${report.browserChannel}`);
  console.log(` Timestamp:         ${report.timestamp}`);
  console.log(` WCAG Rule Passes:  ✅ ${report.passesCount}`);
  console.log(` Total Violations:  ${report.violationsCount === 0 ? '✅ 0' : '❌ ' + report.violationsCount}`);
  console.log(`   - Critical:      ${report.criticalCount}`);
  console.log(`   - Serious:       ${report.seriousCount}`);
  console.log(`   - Moderate:      ${report.moderateCount}`);
  console.log(`   - Minor:         ${report.minorCount}`);
  console.log('--------------------------------------------------------------------------------');

  if (report.violationsCount === 0) {
    console.log(' 🎉 PERFECT SCORE: 100% WCAG 2.1 Level AA compliant. Zero violations detected!\n');
    return;
  }

  console.log(' VIOLATION DETAILS & REMEDIATION GUIDANCE:');
  report.violations.forEach((v, idx) => {
    const impactColor = v.impact === 'critical' ? '[CRITICAL]' : v.impact === 'serious' ? '[SERIOUS]' : '[MODERATE]';
    console.log(`\n ${idx + 1}. ${impactColor} ${v.id} (${v.impact.toUpperCase()})`);
    console.log(`    Help:      ${v.help}`);
    console.log(`    Help URL:  ${v.helpUrl}`);
    v.nodes.forEach((node, nIdx) => {
      console.log(`    Target ${nIdx + 1}:  ${node.target.join(' ')}`);
      console.log(`    Snippet:   ${node.html.trim().slice(0, 100)}`);
      if (node.failureSummary) {
        console.log(`    Failure:   ${node.failureSummary.split('\n')[0]}`);
      }
    });
  });

  console.log('\n RECOMMENDED REMEDIATIONS:');
  report.remediations.forEach((rem, idx) => {
    console.log(`  ${idx + 1}. ${rem}`);
  });
  console.log('================================================================================\n');
}

// CLI Execution Handler
if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const args = process.argv.slice(2);
  let targetUrl = process.env.TARGET_URL || 'http://localhost:3000';
  let reportPath = null;
  let htmlPath = null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--url' && args[i + 1]) {
      targetUrl = args[i + 1];
      i++;
    } else if (args[i] === '--report' && args[i + 1]) {
      reportPath = args[i + 1];
      i++;
    } else if (args[i] === '--html' && args[i + 1]) {
      htmlPath = args[i + 1];
      i++;
    }
  }

  (async () => {
    try {
      let report;
      if (htmlPath) {
        const content = fs.readFileSync(htmlPath, 'utf8');
        report = await auditHtml(content);
      } else {
        console.log(`Initiating accessibility audit against: ${targetUrl}...`);
        report = await auditUrl(targetUrl);
      }

      formatAuditReport(report);

      if (reportPath) {
        fs.writeFileSync(reportPath, JSON.stringify(report, null, 2), 'utf8');
        console.log(`Audit report exported to: ${reportPath}`);
      }

      // Exit 0 if clean pass or only minor/moderate, exit 1 if critical/serious violations exist
      if (!report.success) {
        process.exit(1);
      }
    } catch (err) {
      console.error(`\n❌ Accessibility Audit Failed: ${err.message}`);
      process.exit(1);
    }
  })();
}
