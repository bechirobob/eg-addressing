import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

import { chromium } from 'playwright';

const baseUrl = (process.env.OPERATOR_UI_BASE_URL || 'http://127.0.0.1:3100').replace(/\/$/, '');
const outputDir = path.resolve(
  process.env.OPERATOR_UI_EVIDENCE_DIR || 'artifacts/operator-ui-browser-evidence',
);
const commitSha = process.env.GITHUB_SHA || process.env.OPERATOR_UI_COMMIT || 'unknown';

await mkdir(outputDir, { recursive: true });

const evidence = [];
const browser = await chromium.launch({ headless: true });

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function userForRole(role) {
  return {
    id: `ci-${role}`,
    username: `ci_${role}`,
    full_name: `CI ${role.replaceAll('_', ' ')}`,
    role,
  };
}

function jsonResponse(body, status = 200) {
  return {
    status,
    contentType: 'application/json',
    body: JSON.stringify(body),
  };
}

const emptyReportingSummary = {
  totals: {
    territories: 0,
    submissions: 0,
    review_queue: 0,
    published_addresses: 0,
    import_jobs: 0,
    public_corrections: 0,
    correction_queue: 0,
    citizen_geotags: 0,
    geotag_queue: 0,
  },
  territories_by_province: [],
  review_breakdown: [],
  publication_breakdown: [],
  correction_breakdown: [],
  geotag_breakdown: [],
  filters: {
    province: null,
    territory: null,
    status: null,
    date_from: null,
    date_to: null,
  },
};

const emptyReadinessSummary = {
  readiness_status: 'pilot-prep',
  passed_gates: 0,
  total_gates: 0,
  gates: [],
  recent_audit_events: [],
  boundaries: ['Automated browser evidence only — not an operational readiness claim.'],
};

async function installApiFixtures(page, role) {
  const user = role ? userForRole(role) : null;

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;

    if (pathname.endsWith('/api/v1/auth/me')) {
      if (!user) {
        await route.fulfill(jsonResponse({ detail: 'Not authenticated' }, 401));
        return;
      }
      await route.fulfill(jsonResponse({ user }));
      return;
    }

    if (pathname.endsWith('/api/v1/auth/logout')) {
      await route.fulfill(jsonResponse({ status: 'signed-out' }));
      return;
    }

    if (pathname.endsWith('/api/v1/admin/users')) {
      await route.fulfill(
        jsonResponse({
          items: user
            ? [
                {
                  ...user,
                  is_active: true,
                  active_sessions: 1,
                  created_at: '2026-07-21T00:00:00Z',
                },
              ]
            : [],
        }),
      );
      return;
    }

    if (pathname.endsWith('/api/v1/reporting/summary')) {
      await route.fulfill(jsonResponse(emptyReportingSummary));
      return;
    }

    if (pathname.endsWith('/api/v1/pilot-readiness/summary')) {
      await route.fulfill(jsonResponse(emptyReadinessSummary));
      return;
    }

    if (request.method() === 'GET') {
      await route.fulfill(jsonResponse({ items: [], total: 0 }));
      return;
    }

    await route.fulfill(jsonResponse({ status: 'accepted-for-ci-fixture' }));
  });
}

async function assertNoHorizontalOverflow(page, label) {
  const dimensions = await page.evaluate(() => ({
    viewportWidth: window.innerWidth,
    documentWidth: document.documentElement.scrollWidth,
    bodyWidth: document.body.scrollWidth,
  }));
  const widest = Math.max(dimensions.documentWidth, dimensions.bodyWidth);
  assert(
    widest <= dimensions.viewportWidth + 1,
    `${label}: horizontal overflow detected (${widest}px > ${dimensions.viewportWidth}px)`,
  );
  return dimensions;
}

async function assertMobileDrawer(page, label) {
  const menu = page.locator('.operator-mobile-menu');
  await menu.waitFor({ state: 'visible' });
  assert(!(await page.locator('.operator-sidebar-desktop').isVisible()), `${label}: desktop rail visible on mobile`);

  await menu.click();
  const drawer = page.locator('#operator-primary-navigation');
  await drawer.waitFor({ state: 'visible' });
  await page.waitForFunction(() => {
    const active = document.activeElement;
    return active instanceof HTMLAnchorElement && Boolean(active.closest('#operator-primary-navigation'));
  });

  await page.keyboard.press('Escape');
  await drawer.waitFor({ state: 'hidden' });
  const focusReturned = await menu.evaluate((element) => document.activeElement === element);
  assert(focusReturned, `${label}: focus did not return to the mobile menu button after Escape`);
}

async function captureProtected({ role, route, viewport, label, screenshot = true }) {
  const context = await browser.newContext({
    viewport,
    colorScheme: 'light',
    reducedMotion: 'reduce',
  });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('pageerror', (error) => consoleErrors.push(`pageerror: ${error.message}`));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(`console: ${message.text()}`);
  });

  await installApiFixtures(page, role);
  await page.goto(`${baseUrl}${route}`, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.locator('.operator-workspace-shell').waitFor({ state: 'visible', timeout: 30_000 });
  await page.locator('.operator-utility-bar').waitFor({ state: 'visible' });

  const dimensions = await assertNoHorizontalOverflow(page, label);
  const shellRole = await page.locator('.operator-workspace-shell').getAttribute('class');
  assert(shellRole?.includes(`chrome-role-${role}`), `${label}: shell role class does not match ${role}`);
  await page.getByText('National Addressing Platform', { exact: true }).first().waitFor({ state: 'visible' });

  if (viewport.width <= 860) {
    await assertMobileDrawer(page, label);
  } else {
    await page.locator('.operator-sidebar-desktop').waitFor({ state: 'visible' });
    assert(!(await page.locator('.operator-mobile-menu').isVisible()), `${label}: mobile menu visible on desktop`);
  }

  const screenshotPath = path.join(outputDir, `${label}.png`);
  if (screenshot) {
    await page.screenshot({ path: screenshotPath, fullPage: true });
  }

  evidence.push({
    label,
    role,
    route,
    finalUrl: page.url(),
    viewport,
    dimensions,
    screenshot: screenshot ? path.basename(screenshotPath) : null,
    consoleErrors,
    status: 'passed',
  });
  await context.close();
}

async function captureDeniedRedirect() {
  const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
  const page = await context.newPage();
  await installApiFixtures(page, 'viewer');
  await page.goto(`${baseUrl}/field`, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.waitForURL(/\/reports$/, { timeout: 30_000 });
  await page.locator('.operator-workspace-shell.chrome-role-viewer').waitFor({ state: 'visible' });
  const dimensions = await assertNoHorizontalOverflow(page, 'viewer-denied-redirect-mobile');
  const screenshotPath = path.join(outputDir, 'viewer-denied-redirect-mobile.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  evidence.push({
    label: 'viewer-denied-redirect-mobile',
    role: 'viewer',
    route: '/field',
    finalUrl: page.url(),
    viewport: { width: 390, height: 844 },
    dimensions,
    screenshot: path.basename(screenshotPath),
    status: 'passed',
  });
  await context.close();
}

async function capturePublic(viewport, label) {
  const context = await browser.newContext({ viewport, colorScheme: 'light', reducedMotion: 'reduce' });
  const page = await context.newPage();
  await installApiFixtures(page, null);
  await page.goto(baseUrl, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.locator('.chrome-shell.chrome-role-guest').waitFor({ state: 'visible', timeout: 30_000 });
  assert((await page.locator('.operator-workspace-shell').count()) === 0, `${label}: protected shell leaked onto public home`);
  const dimensions = await assertNoHorizontalOverflow(page, label);
  const screenshotPath = path.join(outputDir, `${label}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });
  evidence.push({
    label,
    role: 'guest',
    route: '/',
    finalUrl: page.url(),
    viewport,
    dimensions,
    screenshot: path.basename(screenshotPath),
    status: 'passed',
  });
  await context.close();
}

try {
  const desktop = { width: 1440, height: 900 };
  const tablet = { width: 1024, height: 768 };
  const mobile = { width: 390, height: 844 };

  for (const route of ['/field', '/registry', '/verify', '/signage', '/reports']) {
    await captureProtected({
      role: 'editor',
      route,
      viewport: desktop,
      label: `editor-${route.slice(1)}-desktop`,
    });
  }

  await captureProtected({ role: 'admin', route: '/admin/staff', viewport: desktop, label: 'admin-staff-desktop' });
  await captureProtected({ role: 'viewer', route: '/reports', viewport: desktop, label: 'viewer-reports-desktop' });
  await captureProtected({ role: 'agency_viewer', route: '/reports', viewport: desktop, label: 'agency-viewer-reports-desktop' });
  await captureProtected({ role: 'editor', route: '/registry', viewport: tablet, label: 'editor-registry-tablet' });
  await captureProtected({ role: 'editor', route: '/field', viewport: mobile, label: 'editor-field-mobile' });
  await captureProtected({ role: 'admin', route: '/admin/staff', viewport: mobile, label: 'admin-staff-mobile' });
  await captureProtected({ role: 'agency_viewer', route: '/reports', viewport: mobile, label: 'agency-viewer-reports-mobile' });
  await captureDeniedRedirect();
  await capturePublic(desktop, 'public-home-desktop');
  await capturePublic(mobile, 'public-home-mobile');

  await writeFile(
    path.join(outputDir, 'evidence.json'),
    `${JSON.stringify({ commitSha, generatedAt: new Date().toISOString(), baseUrl, evidence }, null, 2)}\n`,
    'utf8',
  );
  await writeFile(
    path.join(outputDir, 'README.md'),
    `# NLI-WO-003 browser evidence\n\n- Exact commit: \`${commitSha}\`\n- Environment: GitHub-hosted CI browser fixture\n- Authority boundary: presentation/accessibility evidence only; not deployment or publication approval.\n- Checks: ${evidence.length} passed.\n`,
    'utf8',
  );
  console.log(`operator-shell browser evidence passed: ${evidence.length} checks`);
} finally {
  await browser.close();
}
