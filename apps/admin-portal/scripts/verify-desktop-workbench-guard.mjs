import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');
const verifySource = await readFile(path.join(portalRoot, 'components/VerificationWorkflowPanel.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

function fail(message) {
  throw new Error(`verify-desktop-workbench-guard failed: ${message}`);
}

const requiredSourceMarkers = [
  'verification-workspace',
  'verification-queue-panel',
  'verification-trust-panel',
  'protected-file-actions',
  'evidence-history-summary',
  'Accept evidence first',
];

for (const marker of requiredSourceMarkers) {
  if (!verifySource.includes(marker)) fail(`missing source marker ${marker}`);
}

const requiredCssMarkers = [
  'Permanent /verify desktop workbench contract',
  'main.page-shell:has(.verification-workspace) .desktop-main-content',
  '.verification-workspace .verification-queue-panel.verification-queue-panel',
  '.verification-workspace .verification-trust-panel.verification-trust-panel',
  'grid-column: 1 / -1 !important;',
  'grid-template-columns: minmax(280px, 0.34fr) minmax(0, 0.66fr) !important;',
  '.verification-workspace .review-list',
  'grid-template-columns: repeat(2, minmax(420px, 1fr)) !important;',
  '.verification-workspace .review-card:has(.technical-evidence-disclosure[open])',
  'writing-mode: horizontal-tb !important;',
  'text-orientation: mixed !important;',
];

for (const marker of requiredCssMarkers) {
  if (!css.includes(marker)) fail(`missing CSS desktop contract marker ${marker}`);
}

const permanentSection = css.slice(css.indexOf('/* Permanent /verify desktop workbench contract'));
const forbiddenNarrowRules = [
  'grid-template-columns:minmax(620px,1.1fr) minmax(360px,.62fr)',
  '.verification-trust-panel {\n  order: -2;',
];
for (const rule of forbiddenNarrowRules) {
  if (permanentSection.includes(rule)) fail(`permanent section still contains old narrow rule ${rule}`);
}

console.log('verify-desktop-workbench-guard passed');
