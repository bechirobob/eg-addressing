const baseUrl = process.env.SMOKE_APP_BASE_URL ?? 'http://127.0.0.1:3100';

const pages = [
  {
    path: '/',
    required: ['National Addressing Platform', 'Choose the correct service before starting', 'From citizen capture to official registry'],
    forbidden: ['pilot-mvp', 'demo access', 'Rows JSON', 'http://localhost:8100', 'http://api:8100'],
  },
  {
    path: '/geotag',
    required: ['Register a Location', 'Use GPS to capture the property point', 'Submit location for review'],
    forbidden: ['pilot-mvp', 'demo access', 'Rows JSON', 'http://localhost:8100', 'http://api:8100'],
  },
  {
    path: '/issue',
    required: ['Check Address Code', 'Search the public registry', 'Example official code'],
    forbidden: ['Published sample record', 'pilot-mvp', 'demo access', 'Rows JSON', 'http://localhost:8100', 'http://api:8100'],
  },
  {
    path: '/track',
    required: ['Track a Location Request', 'Check the public-safe status', 'Tracking code'],
    forbidden: ['citizen_contact', 'dip_last4', 'admin123', 'http://localhost:8100', 'http://api:8100'],
  },
  {
    path: '/records',
    required: ['Address Case Files', 'Search canonical government address records', 'Evidence is grouped as a case file'],
    forbidden: ['pilot-mvp', 'Rows JSON', 'demo access'],
  },
  {
    path: '/login',
    required: ['Administrative Sign-In', 'Sign in to perform protected registry actions'],
    forbidden: ['Pilot Admin Sign-In', 'admin123', 'editor123', 'viewer123'],
  },
  {
    path: '/verify',
    required: ['Evidence Review Workflow'],
    forbidden: ['pilot', 'demo', 'bootstrap'],
  },
  {
    path: '/reports',
    required: ['Operational Reporting Dashboard'],
    forbidden: ['pilot', 'demo', 'bootstrap'],
  },
  {
    path: '/exports',
    required: ['Publication and Intake Operations'],
    forbidden: ['Rows JSON', 'sample import', 'demo', 'pilot'],
  },
  {
    path: '/territories',
    required: ['Territory Registry Management'],
    forbidden: ['pilot territory', 'demo role'],
  },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const page of pages) {
  const response = await fetch(`${baseUrl}${page.path}`, { redirect: 'follow' });
  assert(response.ok, `${page.path} returned ${response.status}`);
  const html = (await response.text()).toLowerCase();
  for (const phrase of page.required) {
    assert(html.includes(phrase.toLowerCase()), `${page.path} missing required phrase: ${phrase}`);
  }
  for (const phrase of page.forbidden) {
    assert(!html.includes(phrase.toLowerCase()), `${page.path} contains forbidden phrase: ${phrase}`);
  }
  console.log(`ok ${page.path}`);
}

console.log('page copy guard passed');
