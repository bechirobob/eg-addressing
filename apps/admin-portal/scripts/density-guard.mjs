import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

const checks = [
  {
    file: 'components/FieldWorkflowPanel.tsx',
    markers: ['field-summary-ledger', 'Shared field evidence settings', 'workbench-panel-disclosure', 'live-intake-panel'],
  },
  {
    file: 'components/PublicationOperationsPanel.tsx',
    markers: ['Open simulation form', 'Create publication pack', 'Create migration or intake job manually'],
  },
  {
    file: 'components/TerritoryAdminPanel.tsx',
    markers: ['Create new territory', 'Edit selected territory details', 'territory-command-panel'],
  },
  {
    file: 'components/AddressRecordSearchPanel.tsx',
    markers: ['registry-hold-workbench', 'hold-risk-ledger', 'Hold register', 'const canSearch = sessionStatus === \'ready\';', 'sessionRequestInit(token)'],
  },
];

for (const check of checks) {
  const source = await readFile(path.join(portalRoot, check.file), 'utf8');
  for (const marker of check.markers) {
    if (!source.includes(marker)) {
      throw new Error(`${check.file} missing density guard marker: ${marker}`);
    }
  }
}

console.log('density-guard passed');
