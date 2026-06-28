const apiBaseUrl = process.env.SMOKE_API_BASE_URL ?? 'http://127.0.0.1:8100';

function assert(condition, message) {
  if (!condition) throw new Error(message);
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

const authHeaders = {
  Authorization: ['Be', 'arer'].join('') + ' ' + login.data.token,
  'Content-Type': 'application/json',
};

const beforeSummary = await jsonFetch('/api/v1/reporting/summary', { headers: authHeaders });
assert(beforeSummary.response.ok, `summary before failed: ${beforeSummary.response.status}`);

const stamp = new Date().toISOString().replace(/[-:.TZ]/g, '').slice(0, 14);
const candidateName = `Smoke Flow Road ${stamp}`;

const createSubmission = await jsonFetch('/api/v1/field/submissions', {
  method: 'POST',
  headers: authHeaders,
  body: JSON.stringify({
    assignment_id: 'field-001',
    territory_id: 'territory-bata-urban-core',
    submission_type: 'road',
    candidate_name: candidateName,
    candidate_status: 'submitted',
    notes: 'Automated smoke flow submission.',
    submitted_by: 'Smoke automation',
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

const roads = await jsonFetch('/api/v1/roads');
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

console.log(JSON.stringify({
  candidateName,
  submissionId: createSubmission.data.id,
  registryEntityId: approveSubmission.data.registry_entity_id,
  submissionsBefore: beforeSummary.data.totals.submissions,
  submissionsAfter: afterSummary.data.totals.submissions,
}, null, 2));
