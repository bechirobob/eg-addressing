import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const source = readFileSync(join(here, '../app/operations-runbook/page.tsx'), 'utf8');

const required = [
  'Benji — BeCoreOps',
  'Pending ministry appointment',
  'Operations Runbook',
  'Internal services remain private',
];

const forbidden = [
  /C-0\d/,
  /\/home\//,
  /artifacts\//,
  /backup-readability/,
  /\b20\d{2}-\d{2}-\d{2}\b/,
  /\b20\d{6}T\d{6}Z\b/,
  /\b\d{1,2}:\d{2}\b/,
  /localhost/,
  /127\.0\.0\.1/,
  /\.enc\b/,
  /\.pdf\b/,
  /\.txt\b/,
  /file path/i,
  /timestamp/i,
];

for (const text of required) {
  if (!source.includes(text)) {
    throw new Error(`operations runbook missing required public text: ${text}`);
  }
}

for (const pattern of forbidden) {
  if (pattern.test(source)) {
    throw new Error(`operations runbook contains government-grade leak pattern: ${pattern}`);
  }
}

console.log('operations-runbook-guard passed');
