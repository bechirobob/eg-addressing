import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const reporting = await readFile(path.join(portalRoot, 'components/ReportingDashboardPanel.tsx'), 'utf8');
const i18n = await readFile(path.join(portalRoot, 'components/i18n.tsx'), 'utf8');

assert(!reporting.includes('translateUiText(`Next:'), 'Reports readiness details must not construct an English `Next:` prefix before translation.');
assert(i18n.includes("'Next:'") || i18n.includes("'Next action'"), 'Spanish dictionary must include next-action wording used in operational panels.');
assert(!/Listo for signage\/export/.test(i18n), 'Spanish dictionary must not contain mixed-language signage/export output.');
assert(!/operator vía review/.test(i18n), 'Spanish dictionary must not contain mixed-language operator road-review output.');
assert(reporting.includes("translateUiText('Ready for signage/export'"), 'Reports automation labels must translate Ready for signage/export before the runtime patcher sees it.');
assert(reporting.includes('localizedAutomationLabel(row.bucket, locale)'), 'Reports automation bucket labels must be localized before rendering.');

console.log('spanish-leak-guard passed');
