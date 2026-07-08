const baseUrl = process.env.SMOKE_APP_BASE_URL ?? 'http://127.0.0.1:3100';

const forbiddenEverywhere = [
  'command center',
  'mission control',
  'ai dashboard',
  'smart review',
  'Operational Reporting Dashboard',
  'Field Submission Workflow',
  'Location Review and Registry Readiness',
  'Registry Administration',
  'Language selection',
  'pilot-mvp',
  'demo access',
  'Rows JSON',
  'http://localhost:8100',
  'http://api:8100',
];

const pages = [
  {
    path: '/',
    required: [
      'National Addressing Platform',
      'Use this service to register a location, check an official address code, or track a submitted request.',
      'Register a location',
      'Check address code',
      'Track a request',
      'How a location becomes official',
      'Staff sign-in',
    ],
  },
  {
    path: '/geotag',
    required: ['Register location', 'Submit location for review'],
  },
  {
    path: '/issue',
    required: ['Check address code', 'Search the public registry'],
  },
  {
    path: '/track',
    required: ['Track request', 'Tracking code'],
    forbidden: ['citizen_contact', 'dip_last4', 'admin123'],
  },
  {
    path: '/field',
    required: ['Field work', 'Complete assigned location checks and submit field evidence for review.'],
  },
  {
    path: '/registry',
    required: ['Address registry', 'Search, update, and manage official address records.', 'Official address records'],
  },
  {
    path: '/signage',
    required: ['Publication & signage', 'Review approved address records before public release and physical signage.'],
  },
  {
    path: '/reports',
    required: ['Reports', 'Reports are read-only', 'Track workload, review progress, field activity, and publication readiness.'],
  },
  {
    path: '/login',
    required: ['Staff sign-in', 'Sign in to perform protected registry actions'],
    forbidden: ['Pilot Admin Sign-In', 'admin123', 'editor123', 'viewer123'],
  },
];

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

for (const page of pages) {
  const response = await fetch(`${baseUrl}${page.path}`, { redirect: 'follow' });
  assert(response.ok, `${page.path} returned ${response.status}`);
  const html = (await response.text()).toLowerCase().replaceAll('&amp;', '&');
  for (const phrase of page.required) {
    assert(html.includes(phrase.toLowerCase()), `${page.path} missing required phrase: ${phrase}`);
  }
  for (const phrase of [...forbiddenEverywhere, ...(page.forbidden ?? [])]) {
    assert(!html.includes(phrase.toLowerCase()), `${page.path} contains forbidden phrase: ${phrase}`);
  }
  console.log(`ok ${page.path}`);
}

console.log('page copy guard passed');
