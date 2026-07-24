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

function userForRole(role) {
  return {
    id: `service-delivery-${role}`,
    username: `service_delivery_${role}`,
    full_name: role === 'admin' ? 'National Platform Administrator' : role === 'editor' ? 'National Operations Officer' : 'Read-only Institutional Officer',
    role,
  };
}

const territories = [
  { id: 'territory-malabo', name: 'Malabo', province_code: 'BN', province: 'Bioko Norte', type: 'municipality', readiness: 'active', is_archived: false },
  { id: 'territory-bata', name: 'Bata', province_code: 'LI', province: 'Litoral', type: 'municipality', readiness: 'active', is_archived: false },
];

const assignments = [
  { assignment_id: 'ASSIGN-BN-041', territory_id: 'territory-malabo', territory: 'Malabo', task: 'Confirm ministerial services corridor', team: 'Field Team 04', priority: 'high' },
  { assignment_id: 'ASSIGN-LI-018', territory_id: 'territory-bata', territory: 'Bata', task: 'Trace northern service road', team: 'Field Team 11', priority: 'standard' },
];

const fieldTasks = [
  { id: 'TASK-BN-0021', address_label: 'National Records Annex', territory_name: 'Malabo', territory_id: 'territory-malabo', grid_code: 'BN-MAL-1842', status: 'needs-field-check', field_status: 'visited', field_note: 'Front entrance located; final frontage image pending.', latitude: 3.75041, longitude: 8.78321, accuracy_meters: 4.1, landmark: 'Avenida de la Independencia' },
  { id: 'TASK-LI-0014', address_label: 'Bata North Operations Depot', territory_name: 'Bata', territory_id: 'territory-bata', grid_code: 'LI-BAT-7721', status: 'needs-field-check', field_status: 'needs-recapture', field_note: 'GNSS accuracy exceeded operational threshold.', latitude: 1.8651, longitude: 9.7692, accuracy_meters: 43.8, landmark: 'Northern service road' },
];

const fieldSubmissions = [
  {
    id: 'SUB-BN-000421',
    assignment_id: 'ASSIGN-BN-041',
    territory_id: 'territory-malabo',
    territory_name: 'Malabo',
    submission_type: 'building',
    candidate_name: 'National Records Annex',
    candidate_status: 'candidate',
    notes: 'Entrance, frontage, and GNSS observation synchronized.',
    submitted_by: 'Field Team 04',
    review_status: 'submitted',
    reviewer_note: '',
    registry_entity_id: null,
    spatial_evidence: {
      geometry_type: 'Point',
      latitude: 3.75041,
      longitude: 8.78321,
      accuracy_meters: 4.1,
      road_reference: 'Avenida de la Independencia',
      capture_method: 'GNSS',
      evidence_source: 'field-capture',
      grid_cells: [{ grid_code: 'BN-MAL-1842' }],
      evidence_attachments: [{
        type: 'field-photograph',
        reference: 'Entrance and frontage photographs',
        note: 'Device and capture time verified.',
        captured_by: 'Field Team 04',
        files: [{ file_id: 'field-evidence-001', file_name: 'records-annex-frontage.jpg', content_type: 'image/jpeg', size_bytes: 184320, access: 'protected' }],
      }],
    },
  },
  {
    id: 'SUB-LI-000318',
    assignment_id: 'ASSIGN-LI-018',
    territory_id: 'territory-bata',
    territory_name: 'Bata',
    submission_type: 'road',
    candidate_name: 'Bata North Service Road',
    candidate_status: 'candidate',
    notes: 'Road end point requires recapture.',
    submitted_by: 'Field Team 11',
    review_status: 'under-review',
    reviewer_note: 'Field recapture requested.',
    registry_entity_id: null,
    spatial_evidence: {
      geometry_type: 'LineString',
      points: [{ latitude: 1.8651, longitude: 9.7692, accuracy_meters: 5.2, role: 'start' }],
      evidence_attachments: [],
    },
  },
];

const geotagSubmissions = [
  {
    id: 'GEO-BN-000184',
    territory_id: 'territory-malabo',
    territory_name: 'Malabo',
    address_label: 'Ministerial Services Building, Avenida de la Independencia',
    citizen_name: 'Controlled presentation record',
    dip_masked: '•••• 2841',
    identity_verification_status: 'verified',
    identity_document_verified: true,
    landmark: 'Government administrative corridor',
    latitude: 3.7521,
    longitude: 8.7731,
    accuracy_meters: 5.4,
    capture_method: 'device-gps',
    grid_code: 'BN-MAL-1842',
    status: 'registry-ready',
    duplicate_hint: 'none',
    quality_flags: { accuracy_level: 'high-accuracy', accuracy_label: 'High accuracy', requires_field_check: false, duplicate_code: false, possible_duplicate: false, recommended_action: 'Place in release hold' },
    reviewer_note: 'Identity, road, and location review complete.',
    field_submission_id: 'SUB-BN-000421',
    signage_batch: null,
    suggested_road_name: 'Avenida de la Independencia',
    road_suggestion_attribution: 'Controlled map reference',
    road_suggestion_status: 'accepted',
    reviewed_road_name: 'Avenida de la Independencia',
    automation: {
      quality_score: 96,
      triage_bucket: 'registry-ready',
      process_stage: 'release-hold',
      next_best_action: 'publication-simulation',
      next_best_action_label: 'Run controlled release simulation',
      reasons: ['Identity verified', 'GNSS accuracy within threshold', 'No unresolved duplicate'],
      field_work: { required: false, status: 'complete', field_submission_id: 'SUB-BN-000421' },
      signage: { ready: false, batch: null, export_status: 'locked-until-publication' },
      integration: { api_record_state: 'protected-registry', partner_api_ready: false },
    },
  },
  {
    id: 'GEO-LI-000207',
    territory_id: 'territory-bata',
    territory_name: 'Bata',
    address_label: 'Bata North Operations Depot',
    citizen_name: 'Controlled presentation record',
    dip_masked: null,
    identity_verification_status: 'pending',
    identity_document_verified: false,
    landmark: 'Northern service road',
    latitude: 1.8651,
    longitude: 9.7692,
    accuracy_meters: 43.8,
    capture_method: 'device-gps',
    grid_code: 'LI-BAT-7721',
    status: 'needs-field-check',
    duplicate_hint: 'possible-same-cell',
    quality_flags: { accuracy_level: 'weak-gps', accuracy_label: 'Weak GNSS', requires_field_check: true, duplicate_code: false, possible_duplicate: true, recommended_action: 'Send to field confirmation' },
    reviewer_note: 'Recapture required.',
    field_submission_id: 'SUB-LI-000318',
    signage_batch: null,
    suggested_road_name: 'Bata North Service Road',
    road_suggestion_attribution: 'Controlled map reference',
    road_suggestion_status: 'pending',
    reviewed_road_name: null,
    automation: {
      quality_score: 48,
      triage_bucket: 'field-verification',
      process_stage: 'exception-review',
      next_best_action: 'send-field-verification',
      next_best_action_label: 'Complete field recapture',
      reasons: ['GNSS accuracy exceeds threshold', 'Possible same grid cell'],
      field_work: { required: true, status: 'needs-recapture', field_submission_id: 'SUB-LI-000318' },
      signage: { ready: false, batch: null, export_status: 'blocked' },
      integration: { api_record_state: 'candidate', partner_api_ready: false },
    },
  },
];

const addresses = [
  { id: 'EG-BN-MAL-000184', formatted: 'Ministerial Services Building, Avenida de la Independencia', territory_name: 'Malabo', status: 'registry-ready', publication_state: 'internal-registry', is_archived: false },
  { id: 'EG-LI-BAT-000207', formatted: 'Bata Regional Office, Carretera del Litoral', territory_name: 'Bata', status: 'active', publication_state: 'published', is_archived: false },
];

const importJobs = [
  { id: 'IMPORT-2026-014', name: 'Authorized Bioko Norte intake', source_name: 'bioko_norte_authorized_registry.csv', status: 'validated', imported_count: 0, total_rows: 12, valid_rows: 11 },
];

const publicationPacks = [
  { id: 'PACK-2026-008', name: 'Official institutional address release 008', status: 'draft', audience: 'Government and approved institutional partners', address_count: 2 },
  { id: 'PACK-2026-005', name: 'Published municipal address release 005', status: 'published', audience: 'Public registry', address_count: 14 },
];

const signageRows = [
  { grid_code: 'LI-BAT-000207', signage_text: 'EG-LI-BAT-000207', address_label: 'Bata Regional Office, Carretera del Litoral', territory_name: 'Bata', latitude: 1.8563, longitude: 9.7658, accuracy_meters: 4.2, batch: 'SIGN-2026-005', status: 'published' },
];

const staffUsers = [
  { ...userForRole('admin'), is_active: true, active_sessions: 2, created_at: '2026-06-01T08:00:00Z' },
  { ...userForRole('editor'), is_active: true, active_sessions: 1, created_at: '2026-06-03T08:00:00Z' },
  { ...userForRole('viewer'), is_active: true, active_sessions: 0, created_at: '2026-06-05T08:00:00Z' },
  { ...userForRole('agency_viewer'), is_active: true, active_sessions: 0, created_at: '2026-06-07T08:00:00Z' },
  { id: 'disabled-editor', username: 'former_field_editor', full_name: 'Former Field Officer', role: 'editor', is_active: false, active_sessions: 0, created_at: '2026-05-12T08:00:00Z' },
];

function reportingSummary() {
  return {
    totals: { territories: 2, submissions: 4, review_queue: 2, published_addresses: 15, import_jobs: 1, public_corrections: 1, correction_queue: 1, citizen_geotags: 2, geotag_queue: 1 },
    territories_by_province: [{ province_code: 'BN', territory_count: 1 }, { province_code: 'LI', territory_count: 1 }],
    review_breakdown: [{ review_status: 'submitted', count: 1 }, { review_status: 'under-review', count: 1 }],
    publication_breakdown: [{ status: 'published', count: 15 }, { status: 'internal-registry', count: 1 }],
    correction_breakdown: [{ status: 'submitted', count: 1 }],
    geotag_breakdown: [{ status: 'needs-field-check', count: 1 }, { status: 'registry-ready', count: 1 }],
    filters: { province: null, territory: null, status: null, date_from: null, date_to: null },
  };
}

function readinessSummary() {
  return {
    readiness_status: 'pilot-prep',
    passed_gates: 6,
    total_gates: 8,
    gates: [
      { name: 'Operator access', status: 'passed', evidence: 'Role checks active', next_step: 'Maintain access control' },
      { name: 'Field synchronization', status: 'attention', evidence: 'One device-held item requires synchronization', next_step: 'Synchronize when connectivity is restored' },
      { name: 'Publication release', status: 'attention', evidence: 'Institutional release remains locked', next_step: 'Formal approval required' },
    ],
    totals: { addresses: 16 },
    recent_audit_events: [],
    boundaries: ['Review environment only. Public release remains disabled.'],
  };
}

function automationSummary() {
  return {
    sla: { items_tracked: 2, on_time: 1, approaching: 0, overdue: 1, unknown: 0, oldest_overdue: null, items: [] },
    publication_hold: { registry_ready: 1, public_release_locked: true, oldest_days: 1, oldest_hours: 24, note: 'Institutional release lock is active in this review environment.' },
  };
}

async function installFixtures(page, role) {
  const user = role ? userForRole(role) : null;
  await page.addInitScript(({ activeRole }) => {
    if (activeRole) window.localStorage.setItem('egAddressingToken', `service-delivery-token-${activeRole}`);
    else window.localStorage.removeItem('egAddressingToken');
  }, { activeRole: role });

  await page.route('**/api/v1/**', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    const pathname = url.pathname;

    if (pathname.endsWith('/api/v1/auth/me')) {
      await route.fulfill(user ? response({ user, auth_mode: 'bearer_token', session_ttl_hours: 6 }) : response({ detail: 'Not authenticated' }, 401));
      return;
    }
    if (pathname.endsWith('/api/v1/auth/logout')) {
      await route.fulfill(response({ status: 'signed-out' }));
      return;
    }
    if (pathname.endsWith('/api/v1/reporting/summary')) {
      await route.fulfill(response(reportingSummary()));
      return;
    }
    if (pathname.endsWith('/api/v1/pilot-readiness/summary')) {
      await route.fulfill(response(readinessSummary()));
      return;
    }
    if (pathname.endsWith('/api/v1/admin/users')) {
      await route.fulfill(response({ items: staffUsers }));
      return;
    }
    if (pathname.endsWith('/api/v1/field/assignments')) {
      await route.fulfill(response({ items: assignments }));
      return;
    }
    if (pathname.endsWith('/api/v1/field/geotag-tasks')) {
      await route.fulfill(response({ items: fieldTasks }));
      return;
    }
    if (pathname.endsWith('/api/v1/field/submissions')) {
      await route.fulfill(response({ items: fieldSubmissions }));
      return;
    }
    if (pathname.endsWith('/api/v1/territories')) {
      await route.fulfill(response({ items: territories }));
      return;
    }
    if (pathname.endsWith('/api/v1/geotag-submissions')) {
      await route.fulfill(response({ items: geotagSubmissions }));
      return;
    }
    if (pathname.endsWith('/api/v1/addresses')) {
      await route.fulfill(response({ items: addresses }));
      return;
    }
    if (pathname.endsWith('/api/v1/imports/jobs')) {
      await route.fulfill(response({ items: importJobs }));
      return;
    }
    if (pathname.endsWith('/api/v1/publication/packs')) {
      await route.fulfill(response({ items: publicationPacks }));
      return;
    }
    if (pathname.endsWith('/api/v1/signage/export')) {
      await route.fulfill(response({ items: signageRows, count: signageRows.length }));
      return;
    }
    if (pathname.endsWith('/api/v1/geotag-submissions/duplicates/summary')) {
      await route.fulfill(response({ groups: [{ grid_code: 'LI-BAT-7721', count: 2, active_count: 2, resolved_count: 0 }] }));
      return;
    }
    if (pathname.endsWith('/api/v1/geotag-submissions/automation/summary')) {
      await route.fulfill(response(automationSummary()));
      return;
    }
    if (pathname.includes('/api/v1/geotag-submissions/automation/sla-drilldown')) {
      await route.fulfill(response({ items: [], count: 0 }));
      return;
    }
    if (pathname.endsWith('/api/v1/signage/pack')) {
      await route.fulfill(response({ batch_id: 'SIGN-2026-005', record_count: signageRows.length, records: signageRows }));
      return;
    }
    if (pathname.includes('/certificate')) {
      await route.fulfill(response({ certificate_id: 'CERT-2026-001', address_code: 'EG-BN-MAL-000184', address_label: 'Ministerial Services Building', status: 'published', qr_payload: 'EG-BN-MAL-000184', html: '<!doctype html><title>Controlled certificate</title>' }));
      return;
    }
    if (request.method() === 'GET') {
      await route.fulfill(response({ items: [], total: 0 }));
      return;
    }
    await route.fulfill(response({ id: 'controlled-action-result', status: 'accepted-for-browser-evidence', address_label: 'Controlled action result', candidate_name: 'Controlled action result' }));
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

async function auditAllowed(browser, { role, route, viewport, label, title, routeClass }) {
  const context = await browser.newContext({ viewport, colorScheme: 'light', reducedMotion: 'reduce' });
  const page = await context.newPage();
  const consoleErrors = [];
  page.on('pageerror', (error) => consoleErrors.push(`pageerror: ${error.message}`));
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(`console: ${message.text()}`);
  });
  await installFixtures(page, role);
  await page.goto(`${baseUrl}${route}`, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.locator('.government-workspace-root').waitFor({ state: 'visible', timeout: 30_000 });
  await page.locator(routeClass).waitFor({ state: 'visible', timeout: 30_000 });
  await page.getByRole('heading', { level: 1, name: title }).waitFor({ state: 'visible', timeout: 30_000 });
  await page.locator('.government-three-pane-workbench').waitFor({ state: 'visible', timeout: 30_000 });
  await page.waitForTimeout(550);

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
  assert((await page.locator('.government-three-pane-workbench > *').count()) === 3, `${label}: queue-record-decision workbench must contain exactly three panes`);
  assert((await page.getByText('Valid next actions', { exact: true }).count()) >= 1, `${label}: decision inspector heading is missing`);

  if (viewport.width >= 1360) {
    const boxes = await page.locator('.government-three-pane-workbench > *').evaluateAll((elements) => elements.map((element) => {
      const box = element.getBoundingClientRect();
      return { x: box.x, y: box.y, width: box.width };
    }));
    assert(boxes.every((box) => box.width >= 235), `${label}: one or more desktop workbench panes are too narrow`);
    assert(Math.max(...boxes.map((box) => box.y)) - Math.min(...boxes.map((box) => box.y)) <= 4, `${label}: desktop panes are not aligned`);
  }

  if (route === '/field') {
    assert(bodyText.includes('Device sync'), `${label}: device synchronization state is missing`);
    assert(bodyText.includes('Field capture does not create a public address'), `${label}: field authority boundary is missing`);
    assert(bodyText.includes('Confirm ministerial services corridor'), `${label}: assignment fixture is not represented`);
  }
  if (route === '/admin/staff') {
    assert(bodyText.includes('Current administrator cannot disable this session account'), `${label}: current-admin safeguard is missing`);
    assert(bodyText.includes('Least privilege remains the default'), `${label}: least-privilege guidance is missing`);
    assert(bodyText.includes('National Platform Administrator'), `${label}: personnel fixture is not represented`);
  }
  if (route === '/signage') {
    assert(bodyText.includes('Institutional approval lock active'), `${label}: publication release lock is not explicit`);
    assert(bodyText.includes('Preparation, approval, publication, and signage are separate states'), `${label}: publication lifecycle separation is missing`);
    assert(bodyText.includes('Ministerial Services Building'), `${label}: publication case fixture is not represented`);
  }
  if (route === '/exports') {
    assert(bodyText.includes('Official publication pack'), `${label}: official pack inspector is missing`);
    assert(bodyText.includes('Institutional approval lock active'), `${label}: pack publication lock is not explicit`);
    assert(bodyText.includes('Official institutional address release 008'), `${label}: publication pack fixture is not represented`);
  }

  assert(consoleErrors.length === 0, `${label}: browser console errors: ${consoleErrors.join(' | ')}`);
  const screenshot = `${label}.png`;
  await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: true });
  await context.close();
  return { label, role, route, viewport, dimensions: measured, screenshot, status: 'passed' };
}

async function auditDenied(browser, { role, route, label }) {
  const viewport = { width: 390, height: 844 };
  const context = await browser.newContext({ viewport, colorScheme: 'light', reducedMotion: 'reduce' });
  const page = await context.newPage();
  await installFixtures(page, role);
  await page.goto(`${baseUrl}${route}`, { waitUntil: 'domcontentloaded', timeout: 45_000 });
  await page.waitForURL(/\/workspace$/, { timeout: 30_000 });
  await page.locator('.government-workspace-root').waitFor({ state: 'visible', timeout: 30_000 });
  const measured = await dimensions(page);
  assert(Math.max(measured.scrollWidth, measured.bodyWidth) <= measured.clientWidth + 2, `${label}: redirect target overflows`);
  assert(page.url().endsWith('/workspace'), `${label}: unauthorized route did not redirect to the role-owned workspace`);
  const screenshot = `${label}.png`;
  await page.screenshot({ path: path.join(outputDir, screenshot), fullPage: true });
  await context.close();
  return { label, role, route, finalUrl: `${baseUrl}/workspace`, viewport, dimensions: measured, screenshot, status: 'passed' };
}

const browser = await chromium.launch({ headless: true });
const evidence = [];
try {
  const desktop = { width: 1440, height: 900 };
  const tablet = { width: 1024, height: 768 };
  const mobile = { width: 390, height: 844 };

  evidence.push(await auditAllowed(browser, { role: 'editor', route: '/field', viewport: desktop, label: 'government-field-editor-desktop', title: 'Field Operations', routeClass: '.government-field-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'editor', route: '/field', viewport: tablet, label: 'government-field-editor-tablet', title: 'Field Operations', routeClass: '.government-field-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'editor', route: '/field', viewport: mobile, label: 'government-field-editor-mobile', title: 'Field Operations', routeClass: '.government-field-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'admin', route: '/admin/staff', viewport: desktop, label: 'government-administration-admin-desktop', title: 'Administration', routeClass: '.government-administration-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'admin', route: '/admin/staff', viewport: mobile, label: 'government-administration-admin-mobile', title: 'Administration', routeClass: '.government-administration-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'editor', route: '/signage', viewport: desktop, label: 'government-publication-editor-desktop', title: 'Publication', routeClass: '.government-publication-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'editor', route: '/signage', viewport: tablet, label: 'government-publication-editor-tablet', title: 'Publication', routeClass: '.government-publication-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'editor', route: '/signage', viewport: mobile, label: 'government-publication-editor-mobile', title: 'Publication', routeClass: '.government-publication-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'admin', route: '/exports', viewport: desktop, label: 'government-publication-outputs-admin-desktop', title: 'Publication', routeClass: '.government-publication-workbench' }));
  evidence.push(await auditAllowed(browser, { role: 'admin', route: '/exports', viewport: mobile, label: 'government-publication-outputs-admin-mobile', title: 'Publication', routeClass: '.government-publication-workbench' }));

  evidence.push(await auditDenied(browser, { role: 'viewer', route: '/field', label: 'government-field-viewer-denied-mobile' }));
  evidence.push(await auditDenied(browser, { role: 'viewer', route: '/signage', label: 'government-publication-viewer-denied-mobile' }));
  evidence.push(await auditDenied(browser, { role: 'editor', route: '/admin/staff', label: 'government-administration-editor-denied-mobile' }));
  evidence.push(await auditDenied(browser, { role: 'editor', route: '/exports', label: 'government-publication-outputs-editor-denied-mobile' }));

  const result = {
    commitSha,
    generatedAt: new Date().toISOString(),
    baseUrl,
    authorityBoundary: 'Presentation, responsive, route-authority, and release-lock evidence only. This is not publication authorization.',
    evidence,
  };
  await writeFile(path.join(outputDir, 'government-service-delivery-evidence.json'), `${JSON.stringify(result, null, 2)}\n`, 'utf8');
  await writeFile(
    path.join(outputDir, 'government-service-delivery-README.md'),
    `# Government service-delivery browser audit\n\n- Exact commit: \`${commitSha}\`\n- Field Operations, Administration, Publication, and Publication Outputs audited independently.\n- Desktop, tablet, and mobile layouts audited where operationally relevant.\n- Official coat of arms and BeCoreOps delivery attribution verified.\n- Route denial verified for viewer/editor roles.\n- Institutional publication lock verified.\n- Body-level horizontal overflow: none.\n- AI/ChatGPT attribution: none.\n- Checks passed: ${evidence.length}.\n`,
    'utf8',
  );
  console.log(`government service-delivery browser audit passed: ${evidence.length} checks`);
} finally {
  await browser.close();
}
