import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

const checks = [
  {
    file: 'components/FieldWorkflowPanel.tsx',
    markers: ['field-summary-ledger', 'Shared field evidence settings', 'workbench-panel-disclosure', 'controlled-sample-disclosure', 'Load controlled sample', 'live-intake-disclosure'],
    forbidden: ['Load pilot sample'],
  },
  {
    file: 'components/PublicationOperationsPanel.tsx',
    markers: ['Open simulation form', 'Create publication pack', 'Create migration or intake job manually', 'publication-release-disclosure', 'Open locked publication action'],
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
  for (const forbidden of check.forbidden ?? []) {
    if (source.includes(forbidden)) {
      throw new Error(`${check.file} contains forbidden clutter marker: ${forbidden}`);
    }
  }
}

console.log('density-guard passed');
