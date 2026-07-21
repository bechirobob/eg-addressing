import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const layout = await readFile(path.join(portalRoot, 'app/layout.tsx'), 'utf8');
const chrome = await readFile(path.join(portalRoot, 'components/RoleAwareChrome.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/operator-shell.css'), 'utf8');

assert(layout.includes("import './operator-shell.css';"), 'layout must load the operator workspace stylesheet after globals.css');

for (const marker of [
  'operator-workspace-shell',
  'operator-sidebar',
  'operator-utility-bar',
  'operator-mobile-menu',
  'operator-navigation-scrim',
  'operator-sidebar-mobile',
  'hidden={!mobileNavigationOpen}',
  'mobile-control-nav',
  'normalizedRoute',
  'routeIsActive',
  'humanizeRole',
  "document.body.style.overflow = 'hidden'",
  "event.key !== 'Tab'",
  "labelKey: 'navFieldWork'",
  'gridTemplateColumns',
]) {
  assert(chrome.includes(marker), `RoleAwareChrome missing operator shell marker: ${marker}`);
}

for (const selector of [
  '.operator-workspace-shell',
  '.operator-sidebar',
  '.operator-utility-bar',
  '.operator-mobile-menu',
  'body:has(.operator-workspace-shell) .data-table',
  '@media (max-width: 860px)',
  '@media (prefers-reduced-motion: reduce)',
]) {
  assert(css.includes(selector), `operator-shell.css missing required responsive selector: ${selector}`);
}

for (const forbidden of [
  /linear-gradient/i,
  /radial-gradient/i,
  /backdrop-filter/i,
  /border-radius\s*:\s*999/i,
  /command center/i,
  /mission control/i,
]) {
  assert(!forbidden.test(css), `operator-shell.css contains forbidden presentation pattern: ${forbidden}`);
}

assert(css.includes('grid-template-columns: 246px minmax(0, 1fr);'), 'desktop operator layout must retain a stable navigation rail');
assert(css.includes('.operator-sidebar-mobile:not([hidden])') && css.includes('position: fixed;') && css.includes('@keyframes operator-drawer-in'), 'mobile operator navigation must use a hidden, keyboard-safe off-canvas drawer');
assert(css.includes('.desktop-table-wrap') && css.includes('.mobile-card-list'), 'responsive table and mobile record alternatives must remain explicit');

console.log('operator-shell-guard passed');
