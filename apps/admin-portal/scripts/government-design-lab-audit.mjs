import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

import { chromium } from 'playwright';

const baseUrl = (process.env.OPERATOR_UI_BASE_URL || 'http://127.0.0.1:3100').replace(/\/$/, '');
const outputDir = path.resolve(process.env.OPERATOR_UI_EVIDENCE_DIR || 'artifacts/operator-ui-browser-evidence');
const commitSha = process.env.GITHUB_SHA || process.env.OPERATOR_UI_COMMIT || 'unknown';

const scenarios = [
  { name: 'government-design-lab-desktop', viewport: { width: 1440, height: 1000 }, mode: 'desktop' },
  { name: 'government-design-lab-tablet', viewport: { width: 1024, height: 900 }, mode: 'tablet' },
  { name: 'government-design-lab-mobile', viewport: { width: 390, height: 844 }, mode: 'mobile' },
];

await mkdir(outputDir, { recursive: true });

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const browser = await chromium.launch({ headless: true });
const evidence = [];

try {
  for (const scenario of scenarios) {
    const context = await browser.newContext({ viewport: scenario.viewport });
    const page = await context.newPage();

    await page.goto(`${baseUrl}/design-lab`, { waitUntil: 'networkidle' });
    await page.getByRole('heading', { name: "Today's national addressing work" }).waitFor();

    const measurements = await page.evaluate(() => {
      const body = document.body;
      const rail = document.querySelector('aside[aria-label="Government workspace navigation"]');
      const workbench = document.querySelector('section[aria-label="Queue, authoritative record, and decision workbench"]');
      const queue = workbench?.children.item(0) ?? null;
      const record = workbench?.children.item(1) ?? null;
      const inspector = document.querySelector('aside[aria-label="Evidence and valid actions"]');
      const nav = document.querySelector('nav');

      const rect = (node) => node instanceof HTMLElement
        ? {
            x: node.getBoundingClientRect().x,
            y: node.getBoundingClientRect().y,
            width: node.getBoundingClientRect().width,
            height: node.getBoundingClientRect().height,
          }
        : null;

      return {
        viewportWidth: window.innerWidth,
        bodyScrollWidth: body.scrollWidth,
        bodyClientWidth: body.clientWidth,
        rail: rect(rail),
        workbench: rect(workbench),
        queue: rect(queue),
        record: rect(record),
        inspector: rect(inspector),
        navScrollWidth: nav instanceof HTMLElement ? nav.scrollWidth : 0,
        navClientWidth: nav instanceof HTMLElement ? nav.clientWidth : 0,
        workbenchDisplay: workbench instanceof HTMLElement ? getComputedStyle(workbench).display : null,
      };
    });

    assert(measurements.bodyScrollWidth <= measurements.viewportWidth + 1, `${scenario.name}: body-level horizontal overflow`);
    assert(measurements.rail, `${scenario.name}: institutional rail missing`);
    assert(measurements.workbench, `${scenario.name}: workbench missing`);
    assert(measurements.queue && measurements.record && measurements.inspector, `${scenario.name}: queue/record/inspector structure incomplete`);

    if (scenario.mode === 'desktop') {
      assert(measurements.rail.width >= 230, 'desktop: institutional rail is too narrow');
      assert(measurements.workbenchDisplay === 'grid', 'desktop: workbench must use grid layout');
      assert(measurements.queue.x < measurements.record.x, 'desktop: queue must precede record horizontally');
      assert(measurements.record.x < measurements.inspector.x, 'desktop: inspector must remain beside the record');
      assert(Math.abs(measurements.queue.y - measurements.record.y) < 2, 'desktop: queue and record must share a workbench row');
      assert(Math.abs(measurements.record.y - measurements.inspector.y) < 2, 'desktop: inspector must share the desktop workbench row');
      assert(measurements.record.width > measurements.queue.width, 'desktop: record surface must dominate queue width');
    }

    if (scenario.mode === 'tablet') {
      assert(measurements.workbenchDisplay === 'grid', 'tablet: workbench should retain structured grid layout');
      assert(measurements.queue.x < measurements.record.x, 'tablet: queue must remain beside record');
      assert(measurements.inspector.y > measurements.record.y, 'tablet: inspector should move below the primary work row');
    }

    if (scenario.mode === 'mobile') {
      assert(measurements.workbenchDisplay === 'block', 'mobile: workbench must become a sequential task flow');
      assert(measurements.record.y > measurements.queue.y, 'mobile: record must follow queue vertically');
      assert(measurements.inspector.y > measurements.record.y, 'mobile: inspector must follow record vertically');
      assert(measurements.navScrollWidth >= measurements.navClientWidth, 'mobile: horizontal role navigation measurement invalid');
    }

    const screenshot = `${scenario.name}.png`;
    await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: true });

    evidence.push({
      name: scenario.name,
      route: '/design-lab',
      viewport: scenario.viewport,
      mode: scenario.mode,
      screenshot,
      measurements,
      passed: true,
    });

    await context.close();
  }
} finally {
  await browser.close();
}

const result = {
  commit: commitSha,
  route: '/design-lab',
  scenarios: evidence,
  passed: evidence.length === scenarios.length && evidence.every((item) => item.passed),
};

await writeFile(path.join(outputDir, 'government-design-lab-evidence.json'), `${JSON.stringify(result, null, 2)}\n`, 'utf8');
console.log(JSON.stringify(result, null, 2));
