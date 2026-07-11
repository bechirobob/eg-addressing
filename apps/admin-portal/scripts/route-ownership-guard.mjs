import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');
const appRoot = path.join(portalRoot, 'app');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function read(relativePath) {
  return readFile(path.resolve(portalRoot, relativePath), 'utf8');
}

async function discoverPageRoutes(dir = appRoot) {
  const entries = await readdir(dir, { withFileTypes: true });
  const routes = [];
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      routes.push(...await discoverPageRoutes(fullPath));
      continue;
    }
    if (entry.name !== 'page.tsx') continue;
    const relativeDir = path.relative(appRoot, path.dirname(fullPath));
    const route = relativeDir === '' ? '/' : `/${relativeDir.replaceAll(path.sep, '/')}`;
    routes.push(route);
  }
  return routes.sort();
}

const allRoles = ['guest', 'viewer', 'editor', 'admin', 'agency_viewer'];
const ownership = {
  '/': { layer: 'public primary', owner: 'public service directory', roles: allRoles, nav: 'home-link', decision: 'keep' },
  '/geotag': { layer: 'public primary', owner: 'citizen GPS/location registration', roles: allRoles, nav: 'public', decision: 'keep-summary-first' },
  '/issue': { layer: 'public primary', owner: 'public address-code lookup/correction', roles: allRoles, nav: 'public', decision: 'keep' },
  '/track': { layer: 'public primary', owner: 'public request tracking', roles: allRoles, nav: 'public', decision: 'keep' },
  '/login': { layer: 'public utility', owner: 'staff sign-in via homepage staff block', roles: allRoles, nav: 'hidden', decision: 'keep-hidden' },
  '/operations-runbook': { layer: 'public hidden', owner: 'controlled pilot operations guidance', roles: allRoles, nav: 'hidden', decision: 'keep-hidden-explicit' },
  '/code/[code]': { layer: 'public dynamic', owner: 'public address profile', roles: allRoles, nav: 'hidden-dynamic', decision: 'keep' },
  '/proof/[code]': { layer: 'public dynamic', owner: 'public proof/QR validation', roles: allRoles, nav: 'hidden-dynamic', decision: 'keep' },
  '/field': { layer: 'staff primary', owner: 'field work / geometry evidence', roles: ['editor', 'admin'], nav: 'staff', decision: 'keep-primary' },
  '/registry': { layer: 'staff primary', owner: 'address registry', roles: ['editor', 'admin'], nav: 'staff', decision: 'keep-primary' },
  '/reports': { layer: 'staff primary read-only', owner: 'readiness/reporting/audit summary', roles: ['viewer', 'editor', 'admin', 'agency_viewer'], nav: 'staff', decision: 'keep-summary-first' },
  '/signage': { layer: 'staff primary gated', owner: 'publication/signage preparation', roles: ['editor', 'admin'], nav: 'staff', decision: 'keep-primary-gated' },
  '/records': { layer: 'staff secondary', owner: 'case files under address registry', roles: ['viewer', 'editor', 'admin'], nav: 'hidden-owner-registry', decision: 'keep-secondary' },
  '/verify': { layer: 'staff secondary', owner: 'evidence/review queue', roles: ['editor', 'admin'], nav: 'hidden-owner-field-registry', decision: 'keep-secondary' },
  '/territories': { layer: 'staff secondary', owner: 'territory/admin unit maintenance', roles: ['editor', 'admin'], nav: 'hidden-owner-registry-admin', decision: 'keep-secondary' },
  '/exports': { layer: 'admin internal secondary', owner: 'publication/intake operations', roles: ['admin'], nav: 'hidden-owner-signage', decision: 'keep-internal-or-consolidate-later' },
  '/admin/staff': { layer: 'admin primary', owner: 'staff account control + tiny readiness summary', roles: ['admin'], nav: 'admin', decision: 'keep-primary-admin' },
};

const siteData = await read('components/site-data.ts');
const registryCorePanel = await read('components/RegistryCorePanel.tsx');
const fieldWorkflowPanel = await read('components/FieldWorkflowPanel.tsx');
const signageOperationsPanel = await read('components/SignageOperationsPanel.tsx');
const packageJson = JSON.parse(await read('package.json'));
const discoveredRoutes = await discoverPageRoutes();
const ownershipRoutes = Object.keys(ownership).sort();

const missingOwnership = discoveredRoutes.filter((route) => !ownership[route]);
const staleOwnership = ownershipRoutes.filter((route) => !discoveredRoutes.includes(route));

assert(missingOwnership.length === 0, `Routes missing ownership: ${missingOwnership.join(', ')}`);
assert(staleOwnership.length === 0, `Ownership table has stale routes: ${staleOwnership.join(', ')}`);

for (const [route, spec] of Object.entries(ownership)) {
  assert(spec.layer && spec.owner && spec.decision, `${route} ownership must include layer, owner, and decision`);
  if (route.includes('[')) continue;
  const rolePattern = spec.roles.map((role) => `'${role}'`).join(', ');
  assert(siteData.includes(`{ path: '${route}', allowedRoles: [${rolePattern}] }`), `${route} route rule must match declared ownership roles`);
}

assert(/const PUBLIC_PREFIXES = \['\/code\/', '\/proof\/'\];/.test(siteData), 'public dynamic code/proof ownership must stay explicit');
assert(/const PROTECTED_PREFIXES = \['\/admin', '\/reports', '\/exports', '\/registry', '\/verify', '\/field', '\/signage', '\/records', '\/territories'\];/.test(siteData), 'protected route prefixes must stay centralized');

for (const route of ['/records', '/verify', '/territories', '/exports']) {
  assert(new RegExp(`href: '${route}',[\\s\\S]*visibleTo: \\[\\]`).test(siteData), `${route} must remain hidden from global/mobile nav and be reached through its owner workflow`);
}

for (const route of ['/geotag', '/issue', '/track', '/field', '/registry', '/reports', '/signage']) {
  assert(new RegExp(`href: '${route}',[\\s\\S]*visibleTo: \\[[^\\]]+'`).test(siteData), `${route} primary workflow must remain intentionally discoverable`);
}

assert(/href: '\/login',[\s\S]*visibleTo: \[\]/.test(siteData), 'login must remain hidden from shared nav');
assert(!siteData.includes("href: '/operations-runbook'"), 'operations runbook must stay hidden from nav');
assert(/<Link href="\/records">Open case files<\/Link>/.test(registryCorePanel), 'registry must keep an in-layer Case Files handoff');
assert(/<Link href="\/verify">Review evidence queue<\/Link>/.test(registryCorePanel), 'registry must keep an in-layer review queue handoff');
assert(/<Link href="\/territories">Maintain territories<\/Link>/.test(registryCorePanel), 'registry must keep an in-layer territories maintenance handoff');
assert(/<Link href="\/verify">Review submitted evidence<\/Link>/.test(fieldWorkflowPanel), 'field workflow must keep an in-layer review queue handoff');
assert(/sessionUser\?\.role === 'admin'[\s\S]*<Link href="\/exports">Open publication operations<\/Link>/.test(signageOperationsPanel), 'signage must keep an admin-only publication operations handoff');
assert(packageJson.scripts['test:route-ownership'] === 'node scripts/route-ownership-guard.mjs', 'package script test:route-ownership must run this guard');

console.log(`route-ownership-guard passed (${discoveredRoutes.length} routes declared)`);
