import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function read(relativePath) {
  return readFile(path.resolve(portalRoot, relativePath), 'utf8');
}

const layout = await read('app/layout.tsx');
const page = await read('app/workspace/page.tsx');
const shell = await read('components/GovernmentWorkspaceShell.tsx');
const home = await read('components/GovernmentOperatorHome.tsx');
const icons = await read('components/GovernmentIcon.tsx');
const styles = await read('app/government-workspace.css');
const accessStyles = await read('app/government-access-gate.css');
const siteData = await read('components/site-data.ts');
const sharedData = await read('lib/governmentWorkspaceData.ts');

assert(/import '\.\/government-workspace\.css';/.test(layout), 'root layout must load the isolated government workspace stylesheet');
assert(/import '\.\/government-access-gate\.css';/.test(layout), 'root layout must load the protected route access state');
assert(/GovernmentWorkspaceShell/.test(page) && /GovernmentOperatorHome/.test(page), 'workspace route must compose the protected shell and actionable home');
assert(!/SiteChrome/.test(page), 'government workspace must not be nested inside the legacy public or operator presentation shell');
assert(/getGovernmentWorkspaceData/.test(page), 'operator home must use the shared government workspace data service');
assert(/\/api\/v1\/reporting\/summary/.test(sharedData), 'government workspace data must use the current reporting summary rather than illustrative operational totals');
assert(/\/api\/v1\/pilot-readiness\/summary/.test(sharedData), 'government workspace data must use the protected readiness summary');
assert(/robots:[\s\S]*index: false/.test(page), 'protected workspace metadata must prevent indexing');

assert(/src="\/eg-coat-of-arms\.svg"/.test(shell), 'official coat of arms must remain in the institutional identity');
assert(/alt="Coat of arms of the Republic of Equatorial Guinea"/.test(shell), 'coat of arms must have meaningful alternative text');
assert(/Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea/.test(shell), 'approved BeCoreOps delivery attribution must remain visible');
assert(/GovernmentIcon/.test(shell) && /government-navigation-icon/.test(shell), 'workspace navigation must use the approved government icon system');
assert(/isRouteAccessible\(item\.href, role\)/.test(shell), 'workspace destinations must be filtered by authoritative route rules');
assert(/routeAccessible[\s\S]*isRouteAccessible\(pathname, sessionUser\.role\)/.test(shell), 'the government shell must resolve active-route authority before showing protected content');
assert(/sessionStatus === 'guest'[\s\S]*router\.replace\('\/login'\)/.test(shell), 'guest sessions must be redirected to staff sign-in');
assert(/!routeAccessible[\s\S]*router\.replace\('\/workspace'\)/.test(shell), 'authenticated users without route authority must return to the role-owned workspace');
assert(/sessionStatus !== 'ready' \|\| !sessionUser \|\| !routeAccessible/.test(shell), 'protected children must remain behind the resolved access boundary');
assert(/sessionRequestInit\(storedToken\)/.test(shell) && /clearStoredToken\(\)/.test(shell), 'workspace logout must revoke and clear sessions');
assert(/BECOREOPS INTERNAL REVIEW ENVIRONMENT/.test(shell), 'non-production notice must identify BeCoreOps without AI references');

assert(/GovernmentIconName/.test(icons), 'government icon component must expose a controlled icon-name contract');
for (const icon of ['home', 'registry', 'mapping', 'field', 'verification', 'publication', 'analytics', 'administration', 'search', 'signout']) {
  assert(new RegExp(`'${icon}'`).test(icons), `government icon system must include ${icon}`);
}

assert(/Routine processing remains automated; operators handle exceptions/.test(home), 'operator home must state the automation-first operating model');
assert(/Values are read from current platform summaries/.test(home), 'operator home must disclose the source of displayed workload values');
assert(/Only destinations permitted by the active role are shown/.test(home), 'operator home must explain role-filtered workspaces');
assert(/firstAccessibleRoute/.test(home) && /isRouteAccessible/.test(home), 'operator-home actions must resolve to permitted routes');

assert(/\.government-workspace-layout[\s\S]*grid-template-columns: 256px minmax\(0, 1fr\)/.test(styles), 'desktop workspace must use an explicit institutional rail and work area');
assert(/\.government-coat-of-arms/.test(styles), 'workspace stylesheet must size and contain the national emblem');
assert(/\.government-navigation-link[\s\S]*grid-template-columns: 22px minmax\(0, 1fr\)/.test(styles), 'navigation must reserve a stable icon column');
assert(/\.government-home-grid[\s\S]*grid-template-columns: minmax\(0, 1\.6fr\) minmax\(300px, 0\.72fr\)/.test(styles), 'desktop home must use a real operational workbench layout');
assert(/@media \(max-width: 920px\)/.test(styles) && /@media \(max-width: 700px\)/.test(styles), 'workspace must define independent tablet and mobile behavior');
assert(/prefers-reduced-motion/.test(styles), 'workspace must respect reduced-motion preferences');
assert(/\.government-access-gate[\s\S]*min-height: 100vh/.test(accessStyles), 'protected-route transition must occupy the viewport without rendering legacy chrome');
assert(!/border-radius:\s*(?:[1-9]\d*|0?\.[1-9])(?:px|rem|em)/.test(`${styles}\n${accessStyles}`.replace(/border-radius:\s*50%/g, '')), 'workspace must not introduce decorative rounded containers or pill controls');

const combined = `${page}\n${shell}\n${home}\n${icons}\n${styles}\n${accessStyles}\n${sharedData}`;
assert(!/ChatGPT|OpenAI|AI[- ]generated|generated by AI/i.test(combined), 'government workspace must not contain AI or ChatGPT attribution');
assert(/href: '\/workspace'/.test(siteData) && /path: '\/workspace'/.test(siteData), 'workspace must remain explicitly navigable and route-owned');

console.log('government-workspace-shell-guard passed');
