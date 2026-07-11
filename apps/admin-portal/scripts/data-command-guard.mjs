import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const registry = await readFile(path.join(portalRoot, 'components/RegistryCorePanel.tsx'), 'utf8');
const records = await readFile(path.join(portalRoot, 'components/AddressRecordSearchPanel.tsx'), 'utf8');
const reporting = await readFile(path.join(portalRoot, 'components/ReportingPanel.tsx'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

assert(registry.includes('Search, update, and manage official address records.'), 'Registry must be search-first and explain its purpose.');
assert(registry.includes('Addresses') && registry.includes('Roads') && registry.includes('Buildings'), 'Registry must expose address, road, and building sections.');
assert(registry.includes('registry-secondary-action') && registry.includes('Open case files') && registry.includes('href="/records"'), 'Case files must live as a secondary Address Registry action, not as a global nav item.');
assert(records.includes('protected-evidence-ledger') && records.includes('downloadProtectedEvidenceFile') && records.includes('/evidence-files/'), 'Case files must show protected field evidence with authenticated download actions.');
assert(!records.includes('object_key'), 'Case file UI must not reference private storage object keys.');
assert(css.includes('.registry-secondary-action'), 'Registry secondary case-file action must have restrained row styling.');
assert(css.includes('.protected-evidence-ledger') && css.includes('.protected-evidence-row'), 'Protected evidence files must use compact row ledger styling.');
assert(reporting.includes('Reports are read-only'), 'Reports must be read-only.');
assert(reporting.includes('Province') && reporting.includes('Date from') && reporting.includes('Status'), 'Reports must provide filter controls.');
assert(reporting.includes('Export report'), 'Reports must provide export report action.');
assert(reporting.includes("sessionStatus !== 'ready'"), 'Reports must refresh protected data after cookie-session auth resolves, not only when a bearer token exists.');
assert(reporting.includes('loadReadiness(token)'), 'Reports must refresh readiness evidence after session resolution.');
assert(reporting.includes('Readiness gates') && reporting.includes('Recent audit events') && reporting.includes('Governance boundary'), 'Reports must expose readiness gates, recent audit events, and governance boundaries.');
assert(reporting.includes('auditEntityLabel') && reporting.includes('session: [protected]') && reporting.includes('[protected-id]'), 'Reports must mask protected audit entity identifiers and long stable IDs.');
assert(reporting.includes('formatEvidence'), 'Reports must format readiness evidence instead of rendering raw backend dictionaries.');
assert(reporting.includes('safeIsoDate'), 'Report export must safely format audit timestamps without throwing on malformed values.');
assert(reporting.includes('summary.filters ?? {}') && reporting.includes('filterDisplayValue'), 'Report export must describe the applied report filters, not stale edited input fields.');
assert(reporting.includes('Promise.all([loadSummary(token ?? null), loadReadiness(token ?? null)]'), 'Applying report filters must refresh summary and readiness/audit evidence together.');
assert(reporting.includes('national-addressing-report-audit.csv') && reporting.includes('Governance boundaries') && reporting.includes('Recent audit events'), 'Report export must include audit/readiness/governance evidence, not only top-line metrics.');
assert(reporting.includes('/^[=+\\-@\\t\\r]/'), 'Report export must neutralize spreadsheet formula injection prefixes in CSV cells.');
assert(css.includes('.metric-row-list') && css.includes('.report-row-list'), 'Reports must use row-based metric styling.');
assert(css.includes('html body main.page-shell .reports-readiness-panel') && css.includes('html body main.page-shell .reports-audit-panel') && css.includes('html body main.page-shell .reports-boundary-panel'), 'Reports readiness, audit, and governance evidence must stay full-width on desktop.');

console.log('data-command-guard passed');
