import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

import { chromium } from 'playwright';

const baseUrl = (process.env.OPERATOR_UI_BASE_URL || 'http://127.0.0.1:3100').replace(/\/$/, '');
const outputDir = path.resolve(process.env.OPERATOR_UI_EVIDENCE_DIR || 'artifacts/operator-ui-browser-evidence');
const commitSha = process.env.OPERATOR_UI_COMMIT || process.env.GITHUB_SHA || 'unknown';

await mkdir(outputDir, { recursive: true });

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function response(body, status = 200, contentType = 'application/json') {
  return {
    status,
    contentType,
    body: contentType === 'application/json' ? JSON.stringify(body) : body,
  };
}

const editor = {
  id: 'government-workbench-editor',
  username: 'government_workbench_editor',
  full_name: 'National Registry and Verification Officer',
  role: 'editor',
};

const territories = [
  { id: 'territory-malabo', name: 'Malabo', province_code: 'BN', province: 'Bioko Norte', type: 'municipality', readiness: 'active', is_archived: false },
  { id: 'territory-bata', name: 'Bata', province_code: 'LI', province: 'Litoral', type: 'municipality', readiness: 'active', is_archived: false },
];

const roads = [
  { id: 'road-independencia', name: 'Avenida de la Independencia', territory_id: 'territory-malabo', territory_name: 'Malabo', status: 'active', length_km: '4.8', is_archived: false },
  { id: 'road-litoral', name: 'Carretera del Litoral', territory_id: 'territory-bata', territory_name: 'Bata', status: 'active', length_km: '11.2', is_archived: false },
];

const buildings = [
  { id: 'building-ministry', label: 'Ministerial Services Building', territory_id: 'territory-malabo', territory_name: 'Malabo', road_id: 'road-independencia', road_name: 'Avenida de la Independencia', status: 'active', usage: 'government', is_archived: false },
  { id: 'building-bata-office', label: 'Bata Regional Office', territory_id: 'territory-bata', territory_name: 'Bata', road_id: 'road-litoral', road_name: 'Carretera del Litoral', status: 'active', usage: 'government', is_archived: false },
];

const addresses = [
  { id: 'EG-BN-MAL-000184', formatted: 'Ministerial Services Building, Avenida de la Independencia', territory_id: 'territory-malabo', territory_name: 'Malabo', road_id: 'road-independencia', road_name: 'Avenida de la Independencia', building_id: 'building-ministry', building_label: 'Ministerial Services Building', province_code: 'BN', status: 'registry-ready', publication_state: 'internal-registry', is_archived: false },
  { id: 'EG-LI-BAT-000207', formatted: 'Bata Regional Office, Carretera del Litoral', territory_id: 'territory-bata', territory_name: 'Bata', road_id: 'road-litoral', road_name: 'Carretera del Litoral', building_id: 'building-bata-office', building_label: 'Bata Regional Office', province_code: 'LI', status: 'active', publication_state: 'published', is_archived: false },
];

const submissions = [
  {
    id: 'SUB-BN-000421',
    territory_name: 'Malabo',
    submission_type: 'building',
    candidate_name: 'National Records Annex',
    candidate_status: 'candidate',
    review_status: 'submitted',
    reviewer_note: '',
    registry_entity_id: null,
    submitted_by: 'Field Team 04',
    notes: 'Entrance, frontage, and GNSS observation synchronized.',
    spatial_evidence: {
      geometry_type: 'Point',
      latitude: 3.75041,
      longitude: 8.78321,
      accuracy_meters: 3.8,
      road_reference: 'Avenida de la Independencia',
      capture_method: 'GNSS',
      evidence_source: 'field-capture',
      grid_cells: [{ grid_code: 'BN-MAL-1842' }],
      review_confidence: 'high',
      evidence_review_status: 'accepted',
      evidence_attachments: [
        {
          type: 'field-photograph',
          reference: 'Entrance and frontage photographs',
          note: 'Device and capture time verified.',
          captured_by: 'Field Team 04',
          files: [
            { file_id: 'evidence-001', file_name: 'records-annex-frontage.jpg', content_type: 'image/jpeg', size_bytes: 184320, access: 'protected', review_status: 'accepted', reviewer_note: 'Entrance and road frontage visible.' },
          ],
        },
      ],
    },
  },
  {
    id: 'SUB-LI-000318',
    territory_name: 'Bata',
    submission_type: 'road',
    candidate_name: 'Bata North Service Road',
    candidate_status: 'candidate',
    review_status: 'under-review',
    reviewer_note: 'Field recapture requested.',
    registry_entity_id: null,
    submitted_by: 'Field Team 11',
    notes: 'End point and complete road trace are missing.',
    spatial_evidence: {
      geometry_type: 'LineString',
      points: [{ latitude: 1.8651, longitude: 9.7692, accuracy_meters: 5.2, role: 'start' }],
      calculated_length_km: 0.7,
      grid_cells: [{ grid_code: 'LI-BAT-7721' }],
      evidence_review_status: 'pending',
      evidence_attachments: [],
    },
  },
];

const evidenceHistory = [
  { id: 1, actor_username: 'field_team_04', action: 'evidence-uploaded', details: { file_name: 'records-annex-frontage.jpg' }, created_at: '2026-07-24T08:10:00Z' },
  { id: 2, actor_username: 'verification_officer', action: 'evidence-accepted', details: { file_name: 'records-annex-frontage.jpg' }, created_at: '2026-07-24T08:24:00Z' },
];

async function installFixtures(page) {
  await page.addInitScript(() => {
    window.localStorage.setItem('egAddressingToken', 'government-workbench-browser-token');
  });

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname;

    if (pathname.endsWith('/api/v1/auth/me')) {
      await route.fulfill(response({ user: editor, auth_mode: 'bearer_token', session_ttl_hours: 6 }));
      return;
    }
    if (pathname.endsWith('/api/v1/auth/logout')) {
      await route.fulfill(response({ status: 'signed-out' }));
      return;
    }
    if (pathname.endsWith('/api/v1/territories')) {
      await route.fulfill(response({ items: territories }));
      return;
    }
    if (pathname.endsWith('/api/v1/roads')) {
      await route.fulfill(response({ items: roads }));
      return;
    }
    if (pathname.endsWith('/api/v1/buildings')) {
      await route.fulfill(response({ items: buildings }));
      return;
    }
    if (pathname.endsWith('/api/v1/addresses')) {
      await route.fulfill(response({ items: addresses }));
      return;
    }
    if (pathname.endsWith('/api/v1/field/submissions')) {
      await route.fulfill(response({ items: submissions }));
      return;
    }
    if (pathname.includes('/evidence-history')) {
      await route.fulfill(response({ items: evidenceHistory }));
      return;
    }
    if (pathname.endsWith('/api/v1/geotag-submissions/automation/sla-drilldown')) {
      await route.fulfill(response({ items: [{ id: 'SUB-LI-000318', label: 'Bata North Service Road', age_hours: 31, due_hours: 24, territory_name: 'Bata', next_best_action_label: 'Complete field recapture' }] }));
      return;
    }
    if (pathname.endsWith('/api/v1/verification/lookup')) {
      await route.fulfill(response({ query: url.searchParams.get('query') ?? '', match_status: 'verified', address_label: 'Bata Regional Office, Carretera del Litoral', jurisdiction: 'Litoral · Bata', verification_note: 'Published registry record verified.', address_id: 'EG-LI-BAT-000207' }));
      return;
    }
    if (pathname.includes('/evidence-files/') && request.method() === 'GET') {
      await route.fulfill(response('controlled evidence fixture', 200, 'application/octet-stream'));
      return;
    }
    if (request.method() === 'GET') {
      await route.fulfill(response({ items: [] }));
      return;
    }
    await route.fulfill(response({ id: 'fixture-action-result', status: 'accepted-for-browser-evidence' }));
  });
}

async function dimensions(page) {
  return page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
    bodyWidth: document.body.scrollWidth,
    clientHeight: document.documentElement.clientHeight,
    scrollHeight: document.documentElement.scrollHeight,
  }));
}

async function auditRoute(browser, { route, viewport, label, expectedTitle }) {
  const context = await browser.newContext({ viewport, colorScheme: 'light', reducedMotion: 'reduce' });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('pageerror', (error) => consoleErrors.push(error.message));
  await installFixtures(page);

  await page.goto(`${baseUrl}${route}`, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.locator('.government-workspace-root').waitFor({ state: 'visible', timeout: 30_000 });
  await page.locator('.government-three-pane-workbench').waitFor({ state: 'visible', timeout: 30_000 });
  await page.getByRole('heading', { level: 1, name: expectedTitle }).waitFor({ state: 'visible', timeout: 30_000 });
  await page.waitForTimeout(500);

  const measured = await dimensions(page);
  assert(Math.max(measured.scrollWidth, measured.bodyWidth) <= measured.clientWidth + 2, `${label}: body-level horizontal overflow detected`);

  const emblemLoaded = await page.locator('.government-coat-of-arms').evaluate((image) => image instanceof HTMLImageElement && image.complete && image.naturalWidth > 0);
  assert(emblemLoaded, `${label}: official coat of arms did not load`);
  const attribution = await page.locator('.government-delivery-footer').innerText();
  assert(attribution.includes('Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea'), `${label}: approved BeCoreOps attribution is missing`);
  const bodyText = await page.locator('body').innerText();
  assert(!/ChatGPT|OpenAI|AI[- ]generated|generated by AI/i.test(bodyText), `${label}: prohibited AI attribution is visible`);
  assert((await page.locator('.government-navigation-link .government-navigation-icon').count()) >= 7, `${label}: icon-led government navigation is incomplete`);
  assert((await page.locator('.government-operation-summary > div').count()) === 5, `${label}: stable five-measure operational summary is missing`);

  const panes = page.locator('.government-three-pane-workbench > *');
  assert((await panes.count()) === 3, `${label}: queue-record-decision workbench must contain exactly three primary panes`);
  if (viewport.width >= 1100) {
    const paneBoxes = await panes.evaluateAll((elements) => elements.map((element) => {
      const box = element.getBoundingClientRect();
      return { x: box.x, y: box.y, width: box.width, height: box.height };
    }));
    assert(paneBoxes.every((box) => box.width >= 235), `${label}: one or more desktop workbench panes are too narrow`);
    assert(Math.max(...paneBoxes.map((box) => box.y)) - Math.min(...paneBoxes.map((box) => box.y)) <= 4, `${label}: desktop panes are not aligned as one workbench`);
  }

  if (route === '/registry') {
    await page.getByText('Ministerial Services Building, Avenida de la Independencia', { exact: true }).first().waitFor({ state: 'visible' });
    assert((await page.getByText('Valid next actions', { exact: true }).count()) >= 1, `${label}: registry decision inspector is missing`);
    const registerSelector = page.locator('.government-command-bar label').filter({ hasText: 'Register' }).locator('select');
    await registerSelector.selectOption('roads');
    await page.getByText('Avenida de la Independencia', { exact: true }).first().waitFor({ state: 'visible' });
    await registerSelector.selectOption('addresses');
  } else {
    await page.getByText('National Records Annex', { exact: true }).first().waitFor({ state: 'visible' });
    assert((await page.getByText('Decision inspector', { exact: true }).count()) >= 1, `${label}: verification decision inspector is missing`);
    assert((await page.getByText('records-annex-frontage.jpg', { exact: true }).count()) >= 1, `${label}: protected evidence file is not represented`);
    const approve = page.getByRole('button', { name: 'Approve and promote to registry' });
    assert(await approve.isEnabled(), `${label}: valid accepted-evidence case is not approvable`);
    await page.getByText('Bata North Service Road', { exact: true }).first().click();
    assert((await page.getByRole('button', { name: 'Required location evidence is missing' }).count()) === 1, `${label}: missing-evidence approval block is not explicit`);
  }

  assert(consoleErrors.length === 0, `${label}: browser console errors: ${consoleErrors.join(' | ')}`);
  const screenshot = `${label}.png`;
  await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: true });
  await context.close();

  return { label, route, viewport, dimensions: measured, screenshot, status: 'passed' };
}

const browser = await chromium.launch({ headless: true });
try {
  const evidence = [];
  evidence.push(await auditRoute(browser, { route: '/registry', viewport: { width: 1440, height: 900 }, label: 'government-registry-desktop', expectedTitle: 'Address Registry' }));
  evidence.push(await auditRoute(browser, { route: '/registry', viewport: { width: 390, height: 844 }, label: 'government-registry-mobile', expectedTitle: 'Address Registry' }));
  evidence.push(await auditRoute(browser, { route: '/verify', viewport: { width: 1440, height: 900 }, label: 'government-verification-desktop', expectedTitle: 'Verification' }));
  evidence.push(await auditRoute(browser, { route: '/verify', viewport: { width: 1024, height: 768 }, label: 'government-verification-tablet', expectedTitle: 'Verification' }));
  evidence.push(await auditRoute(browser, { route: '/verify', viewport: { width: 390, height: 844 }, label: 'government-verification-mobile', expectedTitle: 'Verification' }));

  const result = {
    commitSha,
    generatedAt: new Date().toISOString(),
    baseUrl,
    authorityBoundary: 'Presentation, responsive layout, evidence visibility, and permitted-action affordance evidence only. No publication authorization is implied.',
    evidence,
  };
  await writeFile(path.join(outputDir, 'government-operational-workbench-evidence.json'), `${JSON.stringify(result, null, 2)}\n`, 'utf8');
  await writeFile(
    path.join(outputDir, 'government-operational-workbench-README.md'),
    `# Registry and verification government-workbench audit\n\n- Exact commit: \`${commitSha}\`\n- Registry and Verification audited independently on desktop, tablet, and mobile.\n- Official coat of arms and approved BeCoreOps delivery attribution verified.\n- Icon-led navigation verified.\n- Queue, record, and decision panes verified.\n- Protected evidence and evidence-gated approval behavior verified.\n- Body-level horizontal overflow: none.\n- AI/ChatGPT attribution: none.\n- Checks passed: ${evidence.length}.\n`,
    'utf8',
  );
  console.log(`government operational workbench browser audit passed: ${evidence.length} checks`);
} finally {
  await browser.close();
}
