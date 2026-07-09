import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');
const fieldSource = await readFile(path.join(portalRoot, 'components/FieldWorkflowPanel.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

function fail(message) {
  throw new Error(`field-desktop-workbench-guard failed: ${message}`);
}

const requiredSourceMarkers = [
  'field-summary-ledger',
  'field-upload-workbench',
  'controlled-file-upload',
  'selectedEvidenceUploadId',
  'Select a row with an evidence reference before uploading.',
];

for (const marker of requiredSourceMarkers) {
  if (!fieldSource.includes(marker)) fail(`missing source marker ${marker}`);
}

const liveTableMatch = fieldSource.match(/<div className="table-wrap desktop-table-wrap live-intake-table-wrap"[\s\S]*?<\/table>/);
if (!liveTableMatch) fail('live intake desktop table not found');
const liveTable = liveTableMatch[0];
if (liveTable.includes('type="file"')) fail('native file input is inside the desktop live-intake table');
if (liveTable.includes('table-file-upload')) fail('table-file-upload control is inside the desktop live-intake table');
if (!liveTable.includes('Select')) fail('desktop live-intake table must select a record, not upload inline');

const forbiddenSourceMarkers = ['step-chip', 'readiness-pill', 'status-pill', 'status-chip'];
for (const marker of forbiddenSourceMarkers) {
  if (fieldSource.includes(marker)) fail(`forbidden field source marker ${marker}`);
}

const requiredCssMarkers = [
  'Permanent /field desktop workbench contract',
  'main.page-shell:has(.field-workspace) .desktop-main-content',
  '.field-workspace .field-assignments-panel',
  'grid-column: 1 / -1 !important;',
  '.field-workspace .field-location-checks-panel',
  'grid-column: 1 / span 4 !important;',
  '.field-workspace .field-intake-panel',
  'grid-column: 5 / -1 !important;',
  '.field-workspace .live-intake-panel',
  '.field-workspace .controlled-file-upload input[type=\'file\']',
  '.field-workspace .table-file-upload',
];

for (const marker of requiredCssMarkers) {
  if (!css.includes(marker)) fail(`missing CSS desktop contract marker ${marker}`);
}

const permanentSection = css.slice(css.indexOf('/* Permanent /field desktop workbench contract'));
const requiredPermanentRules = [
  'background: transparent !important;',
  'border: 0 !important;',
  'border-radius: 0 !important;',
  'box-shadow: none !important;',
  'display: none !important;',
];
for (const rule of requiredPermanentRules) {
  if (!permanentSection.includes(rule)) fail(`permanent desktop contract missing ${rule}`);
}

console.log('field-desktop-workbench-guard passed');
