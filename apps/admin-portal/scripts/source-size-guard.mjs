import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../../..');

const budgets = [
  {
    file: 'apps/admin-portal/app/globals.css',
    maxLines: 16000,
    note: 'Global CSS is capped while route/domain styles are split into smaller modules.',
  },
  {
    file: 'services/api/app/db.py',
    maxLines: 4700,
    note: 'Database access should be split by domain before adding large new workflow blocks.',
  },
  {
    file: 'services/api/app/main.py',
    maxLines: 2600,
    note: 'API routes should move toward domain routers instead of one large app module.',
  },
  {
    file: 'services/api/tests/test_app.py',
    maxLines: 3100,
    note: 'Tests should be split by auth, public workflow, official record, and admin domains.',
  },
  {
    file: 'apps/admin-portal/components/FieldWorkflowPanel.tsx',
    maxLines: 1000,
    note: 'Field workflow UI should stay compact and avoid absorbing unrelated operations.',
  },
  {
    file: 'apps/admin-portal/components/SignageOperationsPanel.tsx',
    maxLines: 930,
    note: 'Location review/signage UI should split if additional workflow sections are added.',
  },
  {
    file: 'apps/admin-portal/components/PublicationOperationsPanel.tsx',
    maxLines: 720,
    note: 'Publication operations should stay behind disclosures and avoid route sprawl.',
  },
];

function countLines(source) {
  if (!source) return 0;
  return source.endsWith('\n') ? source.split('\n').length - 1 : source.split('\n').length;
}

const failures = [];
const rows = [];

for (const budget of budgets) {
  const filePath = path.join(repoRoot, budget.file);
  const source = await readFile(filePath, 'utf8');
  const lines = countLines(source);
  const size = await stat(filePath);
  const status = lines <= budget.maxLines ? 'pass' : 'fail';
  rows.push({ file: budget.file, lines, maxLines: budget.maxLines, bytes: size.size, status, note: budget.note });
  if (status === 'fail') {
    failures.push(`${budget.file}: ${lines} lines exceeds budget ${budget.maxLines}. ${budget.note}`);
  }
}

if (failures.length) {
  console.error(JSON.stringify({ status: 'fail', failures, rows }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({ status: 'pass', files: rows.length, rows }, null, 2));
