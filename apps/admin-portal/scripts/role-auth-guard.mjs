import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(portalRoot, '..', '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function read(relativePath, base = portalRoot) {
  return readFile(path.resolve(base, relativePath), 'utf8');
}

const gitignore = await read('.gitignore', repoRoot);
const composeConfig = await read('infra/docker/docker-compose.yml', repoRoot);
const siteData = await read('components/site-data.ts');
const roleAwareChrome = await read('components/RoleAwareChrome.tsx');
const governmentWorkspaceShell = await read('components/GovernmentWorkspaceShell.tsx');
const loginPanel = await read('components/LoginPanel.tsx');
const homePage = await read('app/page.tsx');
const administrationPage = await read('app/admin/staff/page.tsx');
const governmentAdministration = await read('components/GovernmentAdministrationWorkbench.tsx');

assert(/(^|\n)knowledge\//.test(gitignore), 'knowledge/ must stay ignored so mission logs never ride into git by accident');
assert(/(^|\n)\.hermes\//.test(gitignore), 'local tooling state should stay ignored');
assert(!/NEXT_PUBLIC_API_BASE_URL:\s*http:\/\/localhost/.test(composeConfig), 'public browser API base must not be wired to localhost in docker compose');

assert(/if \(role === 'admin' \|\| role === 'editor' \|\| role === 'viewer' \|\| role === 'agency_viewer'\) return '\/workspace';/.test(siteData), 'every authenticated staff role must land on the actionable government workspace');
assert(/return '\/';/.test(siteData), 'guest default route must return to the public service start page');
assert(/href: '\/workspace',[\s\S]*visibleTo: \['viewer', 'editor', 'admin', 'agency_viewer'\]/.test(siteData), 'workspace Home navigation must be visible to every authenticated staff role');
assert(/\{ path: '\/workspace', allowedRoles: \['viewer', 'editor', 'admin', 'agency_viewer'\] \}/.test(siteData), 'workspace route must explicitly deny guest access');
assert(/\{ path: '\/operations-runbook', allowedRoles: \['guest', 'viewer', 'editor', 'admin', 'agency_viewer'\] \}/.test(siteData), 'operations runbook must have explicit public route ownership instead of relying on unknown-route fallback');
assert(/const PUBLIC_PREFIXES = \['\/code\/', '\/proof\/'\];/.test(siteData), 'public dynamic code/proof routes must be explicitly whitelisted');
assert(/const PROTECTED_PREFIXES = \['\/workspace', '\/admin', '\/reports', '\/exports', '\/registry', '\/verify', '\/field', '\/signage', '\/records', '\/territories'\];/.test(siteData), 'staff and admin route prefixes must be deny-by-default governed');
assert(/normalized\.startsWith\(`\$\{prefix\}\/`\)/.test(siteData), 'nested staff routes must inherit base route permissions');
assert(/return Boolean\(baseRule\?\.allowedRoles\.includes\(role\)\);/.test(siteData), 'unknown nested staff routes must not default open');
assert(/routeNeedsResolvedSession\(pathname: string\)/.test(siteData) && /return Boolean\(baseRule && !baseRule\.allowedRoles\.includes\('guest'\)\);/.test(siteData), 'nested staff routes must wait for session resolution');

assert(/\{ path: '\/reports', allowedRoles: \['viewer', 'editor', 'admin', 'agency_viewer'\] \}/.test(siteData), 'reports route must allow read-only agency reviewers');
assert(/\{ path: '\/exports', allowedRoles: \['admin'\] \}/.test(siteData), 'exports route must stay admin-only');
assert(/\{ path: '\/admin', allowedRoles: \['admin'\] \}/.test(siteData), 'admin route prefix must stay admin-only');
assert(/\{ path: '\/admin\/staff', allowedRoles: \['admin'\] \}/.test(siteData), 'staff account UI must stay under an admin-only route');
assert(/href: '\/admin\/staff',[\s\S]*visibleTo: \['admin'\][\s\S]*group: 'admin'/.test(siteData), 'staff account navigation must only be visible inside the admin group for admin users');
assert(/\(role === 'guest' \? item\.group === 'public' : item\.group !== 'public'\)/.test(roleAwareChrome), 'signed-in admins can see staff and admin navigation while guests only see public navigation');
assert(/navAdmin/.test(roleAwareChrome) && /navStaffAccounts/.test(roleAwareChrome), 'admin navigation group and staff account link must have explicit label keys');
assert(/GovernmentWorkspaceShell/.test(administrationPage) && /GovernmentAdministrationWorkbench/.test(administrationPage), 'staff account route must use the protected government administration workbench');
assert(/\/api\/v1\/admin\/users/.test(governmentAdministration) && /\/revoke-sessions/.test(governmentAdministration) && /\/disable/.test(governmentAdministration), 'administration workbench must preserve protected personnel and session endpoints');
assert(/Current administrator cannot disable this session account/.test(governmentAdministration), 'current administrator lockout protection must be visible');
assert(/Last active administrator cannot be disabled/.test(governmentAdministration), 'last active administrator lockout protection must be visible');
assert(!/System readiness dashboard|Audit dashboard|Route inventory/.test(governmentAdministration), 'administration readiness must stay operationally focused, not become a generic dashboard');
assert(!/GovernmentAdministrationWorkbench/.test(roleAwareChrome), 'shared staff chrome must not import or load the administration workbench');
assert(/\{ path: '\/verify', allowedRoles: \['editor', 'admin'\] \}/.test(siteData), 'verify route must stay editor/admin only');
assert(/\{\s*href: '\/login',[\s\S]*visibleTo: \[\]/.test(siteData), 'login must not appear in shared public navigation');
assert(/className="service-start-staff"/.test(homePage) && /href="\/login"/.test(homePage), 'the only public sign-in affordance must be the homepage Staff services block');
assert(/STAFF_SESSION_ROUTES/.test(roleAwareChrome), 'legacy protected routes must retain their scoped sign-out utility during migration');
assert(!/currentRoute !== '\/login' \? \(\s*<Link href="\/login"/.test(roleAwareChrome), 'shared chrome must not render a public Sign in fallback');

assert(/clearStoredToken\(\);/.test(governmentWorkspaceShell), 'new government workspace logout must clear the stored token');
assert(/sessionRequestInit\(storedToken\)/.test(governmentWorkspaceShell), 'new government workspace logout must revoke cookie or bearer sessions through the authoritative endpoint');
assert(/router\.replace\('\/login'\);/.test(governmentWorkspaceShell), 'new government workspace logout must return the operator to login');
assert(/isRouteAccessible\(item\.href, role\)/.test(governmentWorkspaceShell), 'new government workspace navigation must be filtered by centralized route authority');
assert(/src="\/eg-coat-of-arms\.svg"/.test(governmentWorkspaceShell), 'government workspace must display the official Equatorial Guinea coat of arms');
assert(/Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea/.test(governmentWorkspaceShell), 'government workspace must carry the approved BeCoreOps delivery attribution');

assert(/setForcedGuest\(true\);/.test(roleAwareChrome), 'legacy logout must force guest mode immediately to avoid stale signed-in chrome');
assert(/clearStoredToken\(\);/.test(roleAwareChrome), 'legacy logout must clear the stored token');
assert(/router\.replace\('\/login'\);/.test(roleAwareChrome), 'legacy logout must send the operator back to /login');
assert(/routeNeedsResolvedSession\(currentRoute\)/.test(roleAwareChrome), 'protected routes must wait for resolved session state before rendering');
assert(/isRouteAccessible\(currentRoute, role\)/.test(roleAwareChrome), 'route accessibility must stay centralized through site-data rules');

assert(/defaultRouteForRole\(/.test(loginPanel), 'login success redirect must stay centralized through defaultRouteForRole');
assert(/router\.push\(nextRoute\);/.test(loginPanel), 'login must navigate to the role-owned workspace');
assert(!/!payload\.token/.test(loginPanel), 'cookie-session login must not require a bearer token in the JSON payload');
assert(/auth_mode\?: string/.test(loginPanel), 'login payload typing must include auth_mode for cookie-session handling');
assert(/sessionRequestInit/.test(roleAwareChrome), 'legacy logout must use sessionRequestInit so cookie-only sessions can revoke server-side');
assert(!/if \(storedToken\) \{[\s\S]*auth\/logout[\s\S]*\}/.test(roleAwareChrome), 'legacy logout must not skip server revoke when localStorage token is absent');

assert(!/\/records': 'navCaseFiles'/.test(roleAwareChrome), 'Case files must not be added back to crowded legacy global staff navigation.');
assert(!/\{ href: '\/records', label: 'Case Files'/.test(roleAwareChrome), 'Case files must not be added back to legacy mobile bottom navigation. Keep it inside Address registry.');
assert(/role: 'viewer' \| 'editor' \| 'admin' \| 'agency_viewer';/.test(await read('components/demoAuth.ts')), 'session user typing must include agency_viewer');

console.log('role-auth-guard passed');
