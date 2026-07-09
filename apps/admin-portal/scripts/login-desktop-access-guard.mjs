import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');
const loginSource = await readFile(path.join(portalRoot, 'components/LoginPanel.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

function fail(message) {
  throw new Error(`login-desktop-access-guard failed: ${message}`);
}

const sourceMarkers = [
  'login-workspace section-grid single-column-grid',
  'login-access-panel public-task-panel civic-panel-blue',
  'id="login-username"',
  'id="login-password"',
];

for (const marker of sourceMarkers) {
  if (!loginSource.includes(marker)) fail(`missing LoginPanel marker ${marker}`);
}

const cssMarkers = [
  'Permanent /login desktop access contract',
  'main.page-shell-access .login-workspace.login-workspace',
  'grid-template-columns: minmax(420px, 620px) minmax(320px, 1fr) !important;',
  'main.page-shell-access .login-access-panel.login-access-panel',
  'min-width: 420px !important;',
  'writing-mode: horizontal-tb !important;',
  'grid-template-columns: max-content minmax(260px, 1fr) !important;',
  'white-space: nowrap !important;',
];

for (const marker of cssMarkers) {
  if (!css.includes(marker)) fail(`missing CSS marker ${marker}`);
}

const contract = css.slice(css.indexOf('/* Permanent /login desktop access contract'));
if (!contract.includes('@media (max-width: 760px)')) fail('mobile fallback missing');
if (/login-access-panel[\s\S]{0,500}grid-column:\s*auto/.test(contract)) fail('login panel may still auto-place into one desktop grid column');

console.log('login-desktop-access-guard passed');
