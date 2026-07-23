import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

import { chromium } from 'playwright';

const baseUrl = (process.env.OPERATOR_UI_BASE_URL || 'http://127.0.0.1:3100').replace(/\/$/, '');
const outputDir = path.resolve(process.env.OPERATOR_UI_EVIDENCE_DIR || 'artifacts/operator-ui-browser-evidence');
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

function emptyReportingSummary() {
  return {
    totals: {
      territories: 3,
      submissions: 8,
      review_queue: 3,
      published_addresses: 2,
      import_jobs: 1,
      public_corrections: 1,
      correction_queue: 1,
      citizen_geotags: 6,
      geotag_queue: 2,
    },
    territories_by_province: [
      { province_code: 'BN', territory_count: 2 },
      { province_code: 'LN', territory_count: 1 },
    ],
    review_breakdown: [
      { review_status: 'submitted', count: 2 },
      { review_status: 'under-review', count: 1 },
      { review_status: 'approved', count: 5 },
    ],
    publication_breakdown: [
      { status: 'published', count: 2 },
      { status: 'internal-registry', count: 3 },
    ],
    correction_breakdown: [
      { status: 'submitted', count: 1 },
      { status: 'resolved', count: 2 },
    ],
    geotag_breakdown: [
      { status: 'needs-field-check', count: 2 },
      { status: 'registry-ready', count: 4 },
    ],
    filters: {
      province: null,
      territory: null,
      status: null,
      date_from: null,
      date_to: null,
    },
  };
}

function readinessSummary() {
  return {
    readiness_status: 'pilot-prep',
    passed_gates: 5,
    total_gates: 7,
    gates: [
      { name: 'Operator access', status: 'passed', evidence: 'Role checks active', next_step: 'Maintain access control' },
      { name: 'Publication release', status: 'attention', evidence: 'Release remains locked', next_step: 'Institutional approval required' },
    ],
    totals: { addresses: 5 },
    recent_audit_events: [],
    boundaries: ['Presentation environment only. Publication remains disabled.'],
  };
}

function automationSummary() {
  return {
    sla: {
      items_tracked: 3,
      on_time: 2,
      approaching: 1,
      overdue: 0,
      unknown: 0,
      oldest_overdue: null,
      items: [],
    },
    publication_hold: {
      registry_ready: 2,
      public_release_locked: true,
      oldest_days: 1,
      oldest_hours: 24,
      note: 'Presentation fixture — public release remains locked.',
    },
  };
}

async function installApiFixtures(page, role) {
  const user = role ? userForRole(role) : null;

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request();
    const pathname = new URL(request.url()).pathname;

    if (pathname.endsWith('/api/v1/auth/me')) {
      await route.fulfill(user ? jsonResponse({ user, auth_mode: 'bearer_token', session_ttl_hours: 6 }) : jsonResponse({ detail: 'Not authenticated' }, 401));
      return;
    }

    if (pathname.endsWith('/api/v1/auth/login')) {
      await route.fulfill(user ? jsonResponse({ user, token: `ci-token-${role}`, auth_mode: 'bearer_token' }) : jsonResponse({ detail: 'Not authenticated' }, 401));
      return;
    }

    if (pathname.endsWith('/api/v1/auth/logout')) {
      await route.fulfill(jsonResponse({ status: 'signed-out' }));
      return;
    }

    if (pathname.endsWith('/api/v1/reporting/summary')) {
      await route.fulfill(jsonResponse(emptyReportingSummary()));
      return;
    }

    if (pathname.endsWith('/api/v1/pilot-readiness/summary')) {
      await route.fulfill(jsonResponse(readinessSummary()));
      return;
    }

    if (pathname.endsWith('/api/v1/admin/users')) {
      await route.fulfill(jsonResponse({
        items: [
          { ...userForRole('admin'), is_active: true, active_sessions: 1, created_at: '2026-07-21T00:00:00Z' },
          { ...userForRole('editor'), is_active: true, active_sessions: 1, created_at: '2026-07-21T00:00:00Z' },
          { ...userForRole('viewer'), is_active: true, active_sessions: 0, created_at: '2026-07-21T00:00:00Z' },
          { ...userForRole('agency_viewer'), is_active: true, active_sessions: 0, created_at: '2026-07-21T00:00:00Z' },
        ],
      }));
      return;
    }

    if (pathname.endsWith('/api/v1/geotag-submissions/automation/summary')) {
      await route.fulfill(jsonResponse(automationSummary()));
      return;
    }

    if (pathname.endsWith('/api/v1/geotag-submissions/duplicates/summary')) {
      await route.fulfill(jsonResponse({ groups: [] }));
      return;
    }

    if (pathname.includes('/api/v1/geotag-submissions/automation/sla-drilldown')) {
      await route.fulfill(jsonResponse({ items: [], count: 0 }));
      return;
    }

    if (pathname.endsWith('/api/v1/signage/export')) {
      await route.fulfill(jsonResponse({ items: [], count: 0 }));
      return;
    }

    if (pathname.endsWith('/api/v1/address-records/holds')) {
      await route.fulfill(jsonResponse({ source: 'ci-fixture', status: 'ok', count: 0, items: [] }));
      return;
    }

    if (pathname.endsWith('/api/v1/address-records/search')) {
      await route.fulfill(jsonResponse({ items: [] }));
      return;
    }

    if (pathname.endsWith('/api/v1/verification/lookup')) {
      await route.fulfill(jsonResponse({
        query: 'EG-BN-MALABO-001A',
        match_status: 'verified',
        address_label: 'Malabo Reference Building',
        jurisdiction: 'Bioko Norte',
        verification_note: 'Published registry fixture for presentation review.',
      }));
      return;
    }

    if (pathname.endsWith('/api/v1/public/territory-options') || pathname.endsWith('/api/v1/provinces') || pathname.endsWith('/api/v1/territories/provinces') || pathname.endsWith('/api/v1/admin-units')) {
      await route.fulfill(jsonResponse({ items: [] }));
      return;
    }

    if (pathname.endsWith('/api/v1/territories') || pathname.endsWith('/api/v1/roads') || pathname.endsWith('/api/v1/buildings') || pathname.endsWith('/api/v1/addresses') || pathname.endsWith('/api/v1/field/submissions') || pathname.endsWith('/api/v1/geotag-submissions') || pathname.endsWith('/api/v1/imports/jobs') || pathname.endsWith('/api/v1/publication/packs')) {
      await route.fulfill(jsonResponse({ items: [], total: 0 }));
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
  assert(widest <= dimensions.viewportWidth + 2, `${label}: horizontal overflow detected (${widest}px > ${dimensions.viewportWidth}px)`);
  return dimensions;
}

async function contrastMetrics(page) {
  return page.evaluate(() => {
    function rgb(value) {
      const match = value.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)/i);
      return match ? match.slice(1).map(Number) : [0, 0, 0];
    }
    function luminance(channelValues) {
      const channels = channelValues.map((value) => {
        const normalized = value / 255;
        return normalized <= 0.03928 ? normalized / 12.92 : ((normalized + 0.055) / 1.055) ** 2.4;
      });
      return (0.2126 * channels[0]) + (0.7152 * channels[1]) + (0.0722 * channels[2]);
    }
    const sidebar = document.querySelector('.operator-sidebar-desktop');
    const link = document.querySelector('.operator-sidebar-desktop .nav-link:not(.nav-link-active)') || document.querySelector('.operator-sidebar-desktop .nav-link');
    if (!(sidebar instanceof HTMLElement) || !(link instanceof HTMLElement)) return null;
    const foreground = rgb(getComputedStyle(link).color);
    const background = rgb(getComputedStyle(sidebar).backgroundColor);
    const l1 = luminance(foreground);
    const l2 = luminance(background);
    const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05);
    return { foreground, background, ratio: Number(ratio.toFixed(2)) };
  });
}

async function assertDesktop(page, label) {
  await page.locator('.operator-sidebar-desktop').waitFor({ state: 'visible' });
  assert(!(await page.locator('.operator-mobile-menu').isVisible()), `${label}: mobile menu visible at desktop width`);
  assert((await page.locator('.mobile-card-list:visible').count()) === 0, `${label}: mobile card layout visible on desktop`);
  const contentWidth = await page.locator('.operator-workspace-column').evaluate((element) => element.getBoundingClientRect().width);
  assert(contentWidth >= 760, `${label}: desktop content column is too narrow (${contentWidth}px)`);
  const contrast = await contrastMetrics(page);
  assert(contrast && contrast.ratio >= 4.5, `${label}: sidebar contrast is below 4.5:1 (${contrast?.ratio ?? 'missing'})`);
  return { contentWidth, contrast };
}

async function assertMobileDrawer(page, label) {
  const menu = page.locator('.operator-mobile-menu');
  await menu.waitFor({ state: 'visible' });
  assert(!(await page.locator('.operator-sidebar-desktop').isVisible()), `${label}: desktop sidebar visible on mobile`);
  assert((await page.locator('.desktop-table-wrap:visible').count()) === 0, `${label}: desktop table visible on mobile`);
  await menu.click();
  const drawer = page.locator('#operator-primary-navigation');
  await drawer.waitFor({ state: 'visible' });
  await page.waitForFunction(() => {
    const active = document.activeElement;
    return active instanceof HTMLAnchorElement && Boolean(active.closest('#operator-primary-navigation'));
  });
  await page.keyboard.press('Escape');
  await drawer.waitFor({ state: 'hidden' });
  assert(await menu.evaluate((element) => document.activeElement === element), `${label}: focus did not return to menu after Escape`);
}

async function layoutMetrics(page, route) {
  return page.evaluate((activeRoute) => {
    const selectors = {
      '/field': '.field-workspace',
      '/registry': '.registry-simple-shell',
      '/verify': '.verification-workspace',
      '/signage': '.operator-review-shell',
      '/reports': '.reports-service-grid',
      '/records': '.operations-panel',
      '/territories': '.territory-admin-grid',
      '/exports': '.publication-operations-grid',
      '/admin/staff': '.staff-admin-workspace',
    };
    const element = document.querySelector(selectors[activeRoute]);
    if (!(element instanceof HTMLElement)) return null;
    const rect = element.getBoundingClientRect();
    const style = getComputedStyle(element);
    return {
      width: Math.round(rect.width),
      display: style.display,
      gridTemplateColumns: style.gridTemplateColumns,
    };
  }, route);
}

async function captureProtected({ role, route, viewport, label }) {
  const context = await browser.newContext({ viewport, colorScheme: 'light', reducedMotion: 'reduce' });
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
  await page.waitForTimeout(450);

  const dimensions = await assertNoHorizontalOverflow(page, label);
  const shellRole = await page.locator('.operator-workspace-shell').getAttribute('class');
  assert(shellRole?.includes(`chrome-role-${role}`), `${label}: shell role class does not match ${role}`);

  let responsiveMetrics;
  if (viewport.width <= 860) {
    await assertMobileDrawer(page, label);
    responsiveMetrics = { mode: 'mobile' };
  } else {
    responsiveMetrics = { mode: 'desktop', ...(await assertDesktop(page, label)) };
  }

  const routeLayout = await layoutMetrics(page, route);
  assert(routeLayout && routeLayout.width > 0, `${label}: route layout was not found`);

  const screenshotPath = path.join(outputDir, `${label}.png`);
  await page.screenshot({ path: screenshotPath, fullPage: true });

  evidence.push({
    label,
    role,
    route,
    finalUrl: page.url(),
    viewport,
    dimensions,
    responsiveMetrics,
    routeLayout,
    screenshot: path.basename(screenshotPath),
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
  await assertNoHorizontalOverflow(page, 'viewer-denied-redirect-mobile');
  const screenshotPath = path.join(outputDir, 'viewer-denied-redirect-mobile.png');
  await page.screenshot({ path: screenshotPath, fullPage: true });
  evidence.push({
    label: 'viewer-denied-redirect-mobile',
    role: 'viewer',
    route: '/field',
    finalUrl: page.url(),
    viewport: { width: 390, height: 844 },
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
  evidence.push({ label, role: 'guest', route: '/', finalUrl: page.url(), viewport, dimensions, screenshot: path.basename(screenshotPath), status: 'passed' });
  await context.close();
}

try {
  const desktop = { width: 1440, height: 900 };
  const tablet = { width: 1024, height: 768 };
  const mobile = { width: 390, height: 844 };

  for (const route of ['/field', '/registry', '/verify', '/signage', '/reports', '/records', '/territories']) {
    await captureProtected({ role: 'editor', route, viewport: desktop, label: `editor-${route.slice(1)}-desktop` });
  }

  await captureProtected({ role: 'admin', route: '/exports', viewport: desktop, label: 'admin-exports-desktop' });
  await captureProtected({ role: 'admin', route: '/admin/staff', viewport: desktop, label: 'admin-staff-desktop' });
  await captureProtected({ role: 'viewer', route: '/reports', viewport: desktop, label: 'viewer-reports-desktop' });
  await captureProtected({ role: 'viewer', route: '/records', viewport: desktop, label: 'viewer-records-desktop' });
  await captureProtected({ role: 'agency_viewer', route: '/reports', viewport: desktop, label: 'agency-viewer-reports-desktop' });

  await captureProtected({ role: 'editor', route: '/registry', viewport: tablet, label: 'editor-registry-tablet' });
  await captureProtected({ role: 'editor', route: '/field', viewport: mobile, label: 'editor-field-mobile' });
  await captureProtected({ role: 'editor', route: '/registry', viewport: mobile, label: 'editor-registry-mobile' });
  await captureProtected({ role: 'editor', route: '/verify', viewport: mobile, label: 'editor-verify-mobile' });
  await captureProtected({ role: 'editor', route: '/signage', viewport: mobile, label: 'editor-signage-mobile' });
  await captureProtected({ role: 'admin', route: '/admin/staff', viewport: mobile, label: 'admin-staff-mobile' });
  await captureProtected({ role: 'agency_viewer', route: '/reports', viewport: mobile, label: 'agency-viewer-reports-mobile' });

  await captureDeniedRedirect();
  await capturePublic(desktop, 'public-home-desktop');
  await capturePublic(mobile, 'public-home-mobile');

  await writeFile(path.join(outputDir, 'evidence.json'), `${JSON.stringify({ commitSha, generatedAt: new Date().toISOString(), baseUrl, evidence }, null, 2)}\n`, 'utf8');
  await writeFile(path.join(outputDir, 'README.md'), `# Operator presentation audit\n\n- Exact commit: \`${commitSha}\`\n- Environment: GitHub-hosted Chromium fixture\n- Desktop and mobile layouts are audited independently.\n- Sidebar contrast threshold: 4.5:1 minimum.\n- Checks passed: ${evidence.length}.\n- Authority boundary: presentation/accessibility evidence only; not publication approval.\n`, 'utf8');
  console.log(`operator presentation audit passed: ${evidence.length} checks`);
} finally {
  await browser.close();
}
