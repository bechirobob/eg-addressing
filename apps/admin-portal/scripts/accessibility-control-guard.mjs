import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function readComponent(name) {
  return readFile(path.join(portalRoot, 'components', name), 'utf8');
}

const checks = [
  {
    file: 'ReportingDashboardPanel.tsx',
    required: [
      'aria-label={`Open ministry walkthrough route',
      'aria-label={`Show correction queue filter',
      'htmlFor={`reviewer-note-${item.id}`',
      'id={`reviewer-note-${item.id}`',
    ],
  },
  {
    file: 'PublicationOperationsPanel.tsx',
    required: [
      'aria-label={`Remove intake row',
      'htmlFor={`intake-row-type-${row.id}`',
      'id={`intake-row-type-${row.id}`',
    ],
  },
  {
    file: 'TerritoryAdminPanel.tsx',
    required: [
      'id="include-archived-territories"',
      'htmlFor="include-archived-territories"',
    ],
  },
  {
    file: 'RegistryCorePanel.tsx',
    required: [
      'id="include-archived-registry"',
      'htmlFor="include-archived-registry"',
    ],
  },
];

for (const check of checks) {
  const source = await readComponent(check.file);
  for (const needle of check.required) {
    assert(source.includes(needle), `${check.file} missing accessibility marker: ${needle}`);
  }
}

console.log('accessibility-control-guard passed');
