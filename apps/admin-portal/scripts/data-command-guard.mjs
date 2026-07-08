import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const registry = await readFile(path.join(portalRoot, 'components/RegistryCorePanel.tsx'), 'utf8');
const reporting = await readFile(path.join(portalRoot, 'components/ReportingPanel.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

assert(registry.includes('Search, update, and manage official address records.'), 'Registry must be search-first and explain its purpose.');
assert(registry.includes('Addresses') && registry.includes('Roads') && registry.includes('Buildings'), 'Registry must expose address, road, and building sections.');
assert(reporting.includes('Reports are read-only'), 'Reports must be read-only.');
assert(reporting.includes('Province') && reporting.includes('Date from') && reporting.includes('Status'), 'Reports must provide filter controls.');
assert(reporting.includes('Export report'), 'Reports must provide export report action.');
assert(css.includes('.metric-row-list') && css.includes('.report-row-list'), 'Reports must use row-based metric styling.');

console.log('data-command-guard passed');
