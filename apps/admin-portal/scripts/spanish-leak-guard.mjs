import { readFileSync } from 'node:fs';

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const siteChrome = readFileSync(new URL('../components/SiteChrome.tsx', import.meta.url), 'utf8');
const roleChrome = readFileSync(new URL('../components/RoleAwareChrome.tsx', import.meta.url), 'utf8');
const reporting = readFileSync(new URL('../components/ReportingPanel.tsx', import.meta.url), 'utf8');
const registry = readFileSync(new URL('../components/RegistryCorePanel.tsx', import.meta.url), 'utf8');
const field = readFileSync(new URL('../components/FieldWorkflowPanel.tsx', import.meta.url), 'utf8');
const signage = readFileSync(new URL('../components/SignageOperationsPanel.tsx', import.meta.url), 'utf8');

const combined = [siteChrome, roleChrome, reporting, registry, field, signage].join('\n');

assert(!siteChrome.includes('LanguageSwitcher'), 'English-only build must not render a language switcher.');
assert(!siteChrome.includes('SpanishUiTextPatcher'), 'English-only build must not run Spanish UI patcher.');

for (const forbidden of ['command center', 'mission control', 'operational cockpit', 'smart review', 'AI dashboard']) {
  assert(!combined.toLowerCase().includes(forbidden), `Forbidden government-service wording found: ${forbidden}`);
}

assert(reporting.includes('Reports are read-only'), 'Reports page must state that reports are read-only.');
assert(reporting.includes('Province') && reporting.includes('Date from') && reporting.includes('Status'), 'Reports page must expose province/date/status filters.');
assert(registry.includes('Search, update, and manage official address records.'), 'Registry page must state the government-service purpose.');
assert(field.includes('Today summary') && field.includes('Assigned checks') && field.includes('Evidence submitted') && field.includes('Returned for correction'), 'Field work must expose the required Today summary rows.');

console.log('english-service-guard passed');
