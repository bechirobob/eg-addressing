import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function fail(message) {
  throw new Error(`desktop-workbench-guard failed: ${message}`);
}

const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');
const workbenchFiles = [
  {
    path: 'components/PublicationOperationsPanel.tsx',
    required: ['desktop-workbench-grid', 'publication-operations-grid', 'publication-summary-list', 'publication-release-head'],
    forbidden: ['review-glance-chips" aria-label="Release desk summary', '<span className="status-chip">Intake jobs'],
  },
  {
    path: 'components/VerificationWorkflowPanel.tsx',
    required: ['verification-workspace'],
    forbidden: [],
  },
  {
    path: 'components/FieldWorkflowPanel.tsx',
    required: ['field-workspace'],
    forbidden: [],
  },
];

for (const item of workbenchFiles) {
  const source = await readFile(path.join(portalRoot, item.path), 'utf8');
  if (source.includes('territory-admin-grid')) {
    const hasSpecificWorkspace = item.required.some((marker) => source.includes(marker));
    if (!hasSpecificWorkspace) {
      fail(`${item.path} uses territory-admin-grid without an explicit desktop workspace/workbench class`);
    }
  }
  for (const marker of item.required) {
    if (!source.includes(marker)) fail(`${item.path} missing required workbench marker ${marker}`);
  }
  for (const marker of item.forbidden) {
    if (source.includes(marker)) fail(`${item.path} contains forbidden desktop drift marker ${marker}`);
  }
}

const requiredCssMarkers = [
  'Permanent desktop workbench contract',
  'html body main.page-shell .desktop-workbench-grid.desktop-workbench-grid',
  'html body main.page-shell .publication-operations-grid.publication-operations-grid',
  '.publication-operations-grid .publication-release-head',
  '.publication-summary-list',
  'grid-template-columns: 1fr !important;',
  'grid-row: auto !important;',
  'order: 0 !important;',
  'grid-template-columns: repeat(4, minmax(0, 1fr)) !important;',
];

for (const marker of requiredCssMarkers) {
  if (!css.includes(marker)) fail(`globals.css missing desktop workbench marker ${marker}`);
}

const permanentSection = css.slice(css.indexOf('/* Permanent desktop workbench contract'));
const forbiddenPermanentMarkers = [
  '.publication-glance-panel .review-glance-head > .operator-summary-row',
  '.publication-glance-panel .status-chip.warn',
  'review-glance-chips .status-chip::after',
];

for (const marker of forbiddenPermanentMarkers) {
  if (permanentSection.includes(marker)) fail(`permanent desktop workbench section includes stale chip/card marker ${marker}`);
}

console.log('desktop-workbench-guard passed');
