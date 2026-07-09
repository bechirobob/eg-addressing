const apiBaseUrl = process.env.SMOKE_API_BASE_URL ?? 'http://127.0.0.1:8100';
const smokeAdminUsername = process.env.SMOKE_ADMIN_USERNAME ?? 'admin';
const smokeAdminPassword = process.env.SMOKE_ADMIN_PASSWORD;

if (!smokeAdminPassword) {
  throw new Error('SMOKE_ADMIN_PASSWORD is required for admin smoke tests');
}

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function authHeader(token) {
  return { Authorization: `Bearer ${token}` };
}

function parseSetCookies(headers) {
  const raw = typeof headers.getSetCookie === 'function' ? headers.getSetCookie() : [];
  const fallback = headers.get('set-cookie');
  const values = raw.length ? raw : fallback ? [fallback] : [];
  const pairs = [];
  for (const value of values) {
    for (const part of value.split(/,(?=\s*[^;,]+=)/)) {
      const pair = part.split(';', 1)[0]?.trim();
      if (pair) pairs.push(pair);
    }
  }
  return pairs;
}

function cookieValue(cookieHeader, name) {
  const match = cookieHeader.match(new RegExp(`(?:^|;\\s*)${name}=([^;]+)`));
  return match ? decodeURIComponent(match[1]) : '';
}

async function jsonFetch(path, init = {}) {
  const response = await fetch(`${apiBaseUrl}${path}`, init);
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  return { response, data };
}

const login = await jsonFetch('/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: smokeAdminUsername, password: smokeAdminPassword }),
});

assert(login.response.ok, `login failed: ${login.response.status}`);
assert(login.data?.expires_at, 'login did not return session expiry metadata');

const cookieHeader = parseSetCookies(login.response.headers).join('; ');
const csrfToken = cookieValue(cookieHeader, 'eg_addressing_csrf');
const authMode = login.data?.auth_mode ?? (login.data?.token ? 'bearer_token' : 'cookie_session');
const sessionHeaders = login.data?.token
  ? authHeader(login.data.token)
  : { Cookie: cookieHeader, ...(csrfToken ? { 'X-CSRF-Token': csrfToken } : {}) };

if (authMode === 'cookie_session') {
  assert(cookieHeader.includes('eg_addressing_session='), 'cookie session login did not set a session cookie');
  assert(csrfToken, 'cookie session login did not set a CSRF cookie');
} else {
  assert(login.data?.token, 'bearer login did not return a token');
}

const jsonSessionHeaders = {
  ...sessionHeaders,
  'Content-Type': 'application/json',
};

const me = await jsonFetch('/api/v1/auth/me', { headers: sessionHeaders });
assert(me.response.ok, `auth/me failed: ${me.response.status}`);
assert(me.data?.user?.role === 'admin', 'admin login did not resolve an admin session');

const issuance = await jsonFetch('/api/v1/public/issuance/EG-BN-MALABO-001A');
assert(issuance.response.ok, `public issuance lookup failed: ${issuance.response.status}`);
assert(issuance.data?.extract_status === 'ready', 'public issuance did not return a ready extract');

const correction = await jsonFetch('/api/v1/public/corrections', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'EG-BN-MALABO-001A',
    public_code: 'EG-BN-MALABO-001A',
    correction_type: 'record-update',
    reason: 'smoke-test-review',
    note: 'Automated smoke correction report for public correction flow.',
    reporter_name: 'Smoke automation',
    reporter_contact: 'smoke@example.invalid',
  }),
});
assert(correction.response.status === 201, `public correction submit failed: ${correction.response.status}`);
assert(correction.data?.status === 'submitted', 'public correction did not enter submitted state');

const correctionQueue = await jsonFetch('/api/v1/address-corrections?status=submitted', { headers: sessionHeaders });
assert(correctionQueue.response.ok, `correction queue fetch failed: ${correctionQueue.response.status}`);
assert(correctionQueue.data?.items?.some((item) => item.id === correction.data.id), 'submitted correction was not visible in review queue');

const beforeSummary = await jsonFetch('/api/v1/reporting/summary', { headers: jsonSessionHeaders });
assert(beforeSummary.response.ok, `summary before failed: ${beforeSummary.response.status}`);

const stamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
const candidateName = `Smoke Flow Road ${stamp}`;

const createSubmission = await jsonFetch('/api/v1/field/submissions', {
  method: 'POST',
  headers: jsonSessionHeaders,
  body: JSON.stringify({
    assignment_id: 'field-malabo-001',
    territory_id: 'territory-malabo-urban-core',
    submission_type: 'road',
    candidate_name: candidateName,
    candidate_status: 'submitted',
    notes: 'Automated smoke flow submission with captured geometry evidence.',
    submitted_by: 'Smoke automation',
    spatial_evidence: {
      geometry_type: 'LineString',
      capture_method: 'automated-smoke-gps-fixture',
      evidence_source: 'smoke-test-fixture',
      points: [
        { role: 'start', latitude: 3.7521, longitude: 8.7731 },
        { role: 'end', latitude: 3.7534, longitude: 8.7759 },
      ],
      calculated_length_km: 0.34,
      accuracy_note: 'Disposable smoke fixture geometry; backend recalculates official length.',
    },
  }),
});

assert(createSubmission.response.status === 201, `submission create failed: ${createSubmission.response.status}`);
assert(createSubmission.data?.id, 'submission create did not return an id');

const approveSubmission = await jsonFetch(`/api/v1/field/submissions/${createSubmission.data.id}/approve`, {
  method: 'POST',
  headers: sessionHeaders,
});

assert(approveSubmission.response.ok, `submission approve failed: ${approveSubmission.response.status}`);
assert(approveSubmission.data?.review_status === 'approved', 'submission was not approved');
assert(approveSubmission.data?.registry_entity_id, 'approval did not return registry entity id');

const roads = await jsonFetch('/api/v1/roads', { headers: sessionHeaders });
assert(roads.response.ok, `roads fetch failed: ${roads.response.status}`);
assert(Array.isArray(roads.data?.items), 'roads payload missing items');
assert(roads.data.items.some((road) => road.name === candidateName), 'approved road was not found in registry list');

const afterSummary = await jsonFetch('/api/v1/reporting/summary', { headers: jsonSessionHeaders });
assert(afterSummary.response.ok, `summary after failed: ${afterSummary.response.status}`);
assert(afterSummary.data?.totals?.submissions >= beforeSummary.data?.totals?.submissions + 1, 'reporting submissions total did not increase');

const submissions = await jsonFetch('/api/v1/field/submissions', { headers: jsonSessionHeaders });
assert(submissions.response.ok, `submissions fetch failed: ${submissions.response.status}`);
assert(
  submissions.data?.items?.some((item) => item.id === createSubmission.data.id && item.review_status === 'approved' && item.registry_entity_id === approveSubmission.data.registry_entity_id),
  'approved submission state was not persisted',
);

const logout = await jsonFetch('/api/v1/auth/logout', {
  method: 'POST',
  headers: sessionHeaders,
});
assert(logout.response.status === 204, `logout failed: ${logout.response.status}`);

const afterLogout = await jsonFetch('/api/v1/auth/me', { headers: sessionHeaders });
assert(afterLogout.response.status === 401, 'revoked session still passed auth/me after logout');

console.log(JSON.stringify({
  authMode,
  candidateName,
  submissionId: createSubmission.data.id,
  registryEntityId: approveSubmission.data.registry_entity_id,
  correctionId: correction.data.id,
  submissionsBefore: beforeSummary.data.totals.submissions,
  submissionsAfter: afterSummary.data.totals.submissions,
  logoutStatus: logout.response.status,
  revokedSessionStatus: afterLogout.response.status,
}, null, 2));
