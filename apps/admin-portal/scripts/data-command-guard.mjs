import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const registry = await readFile(path.join(portalRoot, 'components/RegistryCorePanel.tsx'), 'utf8');
const reporting = await readFile(path.join(portalRoot, 'components/ReportingDashboardPanel.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

assert(registry.includes('data-command-deck'), 'Registry must expose a data command deck.');
assert(registry.includes('case-lane'), 'Registry must use case lanes instead of table-first navigation.');
assert(registry.toLowerCase().includes('information scent'), 'Registry lanes must explain information scent.');
assert(reporting.includes('data-command-deck'), 'Reporting must expose a risk-lane command deck.');
assert(reporting.toLowerCase().includes('risk lane'), 'Reporting lanes must identify operational risk lanes.');
assert(css.includes('.data-command-deck'), 'Data command deck must have responsive styling.');
assert(css.includes('.case-lane'), 'Case lanes must have dedicated styling.');

console.log('data-command-guard passed');
