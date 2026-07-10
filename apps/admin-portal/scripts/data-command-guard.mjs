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
assert(reporting.includes("sessionStatus !== 'ready'"), 'Reports must refresh protected data after cookie-session auth resolves, not only when a bearer token exists.');
assert(reporting.includes('loadReadiness(token)'), 'Reports must refresh readiness evidence after session resolution.');
assert(reporting.includes('Readiness gates') && reporting.includes('Recent audit events') && reporting.includes('Governance boundary'), 'Reports must expose readiness gates, recent audit events, and governance boundaries.');
assert(reporting.includes('auditEntityLabel') && reporting.includes('session: [protected]'), 'Reports must mask protected audit entity identifiers such as session IDs.');
assert(reporting.includes('formatEvidence'), 'Reports must format readiness evidence instead of rendering raw backend dictionaries.');
assert(reporting.includes('national-addressing-report-audit.csv') && reporting.includes('Governance boundaries') && reporting.includes('Recent audit events'), 'Report export must include audit/readiness/governance evidence, not only top-line metrics.');
assert(reporting.includes('/^[=+\\-@\\t\\r]/'), 'Report export must neutralize spreadsheet formula injection prefixes in CSV cells.');
assert(css.includes('.metric-row-list') && css.includes('.report-row-list'), 'Reports must use row-based metric styling.');
assert(css.includes('html body main.page-shell .reports-readiness-panel') && css.includes('html body main.page-shell .reports-audit-panel') && css.includes('html body main.page-shell .reports-boundary-panel'), 'Reports readiness, audit, and governance evidence must stay full-width on desktop.');

console.log('data-command-guard passed');
