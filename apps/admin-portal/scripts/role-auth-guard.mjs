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
const loginPanel = await read('components/LoginPanel.tsx');

assert(/(^|\n)knowledge\//.test(gitignore), 'knowledge/ must stay ignored so mission logs never ride into git by accident');
assert(/(^|\n)\.hermes\//.test(gitignore), 'local tooling state should stay ignored');
assert(!/NEXT_PUBLIC_API_BASE_URL:\s*http:\/\/localhost/.test(composeConfig), 'public browser API base must not be wired to localhost in docker compose');

assert(/if \(role === 'admin'\) return '\/verify';/.test(siteData), 'admin default route must remain /verify');
assert(/if \(role === 'editor'\) return '\/registry';/.test(siteData), 'editor default route must remain /registry');
assert(/return '\/reports';/.test(siteData), 'viewer\/guest default route must remain /reports');
assert(/\{ path: '\/exports', allowedRoles: \['admin'\] \}/.test(siteData), 'exports route must stay admin-only');
assert(/\{ path: '\/verify', allowedRoles: \['editor', 'admin'\] \}/.test(siteData), 'verify route must stay editor\/admin only');
assert(/\{\s*href: '\/login',[\s\S]*visibleTo: \['guest'\]/.test(siteData), 'login nav item must stay guest-only');

assert(/setForcedGuest\(true\);/.test(roleAwareChrome), 'logout must force guest mode immediately to avoid stale signed-in chrome');
assert(/clearStoredToken\(\);/.test(roleAwareChrome), 'logout must clear the stored token');
assert(/router\.replace\('\/login'\);/.test(roleAwareChrome), 'logout must send the operator back to /login');
assert(/routeNeedsResolvedSession\(currentRoute\)/.test(roleAwareChrome), 'protected routes must wait for resolved session state before rendering');
assert(/isRouteAccessible\(currentRoute, role\)/.test(roleAwareChrome), 'route accessibility must stay centralized through site-data rules');

assert(/defaultRouteForRole\(/.test(loginPanel), 'login success redirect must stay centralized through defaultRouteForRole');
assert(/router\.push\(nextRoute\);/.test(loginPanel), 'login must navigate to the role-owned workspace');

console.log('role-auth-guard passed');
