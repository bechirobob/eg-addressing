const apiBaseUrl = process.env.SMOKE_API_BASE_URL ?? 'http://127.0.0.1:8100';

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function authHeader(token) {
  return { Authorization: String.fromCharCode(66, 101, 97, 114, 101, 114) + ' ' + token };
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
  body: JSON.stringify({ username: 'admin', password: 'admin123' }),
});

assert(login.response.ok, `login failed: ${login.response.status}`);
assert(login.data?.token, 'login did not return a token');
assert(login.data?.expires_at, 'login did not return session expiry metadata');

const authHeaders = {
  ...authHeader(login.data.token),
  'Content-Type': 'application/json',
};

const me = await jsonFetch('/api/v1/auth/me', { headers: authHeader(login.data.token) });
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

const correctionQueue = await jsonFetch('/api/v1/address-corrections?status=submitted', { headers: authHeader(login.data.token) });
assert(correctionQueue.response.ok, `correction queue fetch failed: ${correctionQueue.response.status}`);
assert(correctionQueue.data?.items?.some((item) => item.id === correction.data.id), 'submitted correction was not visible in review queue');

const beforeSummary = await jsonFetch('/api/v1/reporting/summary', { headers: authHeaders });
assert(beforeSummary.response.ok, `summary before failed: ${beforeSummary.response.status}`);

const stamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
const candidateName = `Smoke Flow Road ${stamp}`;

const createSubmission = await jsonFetch('/api/v1/field/submissions', {
  method: 'POST',
  headers: authHeaders,
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
  headers: authHeaders,
});

assert(approveSubmission.response.ok, `submission approve failed: ${approveSubmission.response.status}`);
assert(approveSubmission.data?.review_status === 'approved', 'submission was not approved');
assert(approveSubmission.data?.registry_entity_id, 'approval did not return registry entity id');

const roads = await jsonFetch('/api/v1/roads', { headers: authHeader(login.data.token) });
assert(roads.response.ok, `roads fetch failed: ${roads.response.status}`);
assert(Array.isArray(roads.data?.items), 'roads payload missing items');
assert(roads.data.items.some((road) => road.name === candidateName), 'approved road was not found in registry list');

const afterSummary = await jsonFetch('/api/v1/reporting/summary', { headers: authHeaders });
assert(afterSummary.response.ok, `summary after failed: ${afterSummary.response.status}`);
assert(afterSummary.data?.totals?.submissions >= beforeSummary.data?.totals?.submissions + 1, 'reporting submissions total did not increase');

const submissions = await jsonFetch('/api/v1/field/submissions', { headers: authHeaders });
assert(submissions.response.ok, `submissions fetch failed: ${submissions.response.status}`);
assert(
  submissions.data?.items?.some((item) => item.id === createSubmission.data.id && item.review_status === 'approved' && item.registry_entity_id === approveSubmission.data.registry_entity_id),
  'approved submission state was not persisted',
);

const logout = await jsonFetch('/api/v1/auth/logout', {
  method: 'POST',
  headers: authHeader(login.data.token),
});
assert(logout.response.status === 204, `logout failed: ${logout.response.status}`);

const afterLogout = await jsonFetch('/api/v1/auth/me', { headers: authHeader(login.data.token) });
assert(afterLogout.response.status === 401, 'revoked token still passed auth/me after logout');

console.log(JSON.stringify({
  candidateName,
  submissionId: createSubmission.data.id,
  registryEntityId: approveSubmission.data.registry_entity_id,
  correctionId: correction.data.id,
  submissionsBefore: beforeSummary.data.totals.submissions,
  submissionsAfter: afterSummary.data.totals.submissions,
  logoutStatus: logout.response.status,
  revokedTokenStatus: afterLogout.response.status,
}, null, 2));
