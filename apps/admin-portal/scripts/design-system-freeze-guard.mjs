import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const design = await readFile(path.join(portalRoot, 'DESIGN.md'), 'utf8');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');
const sourceFiles = [
  'app/page.tsx',
  'app/geotag/page.tsx',
  'app/track/page.tsx',
  'app/issue/page.tsx',
  'components/CitizenGeotagPanel.tsx',
  'components/TrackingLookupPanel.tsx',
  'components/PublicIssuancePanel.tsx',
  'components/PublicCodeLookupPanel.tsx',
  'components/FieldWorkflowPanel.tsx',
  'components/RegistryCorePanel.tsx',
  'components/SignageOperationsPanel.tsx',
  'components/ReportingPanel.tsx',
];

const requiredDesignPhrases = [
  'Phase 0 freeze',
  'one clear purpose',
  'one primary action',
  'clear data fields',
  'Public/staff boundary',
  'Verification rule',
];

for (const phrase of requiredDesignPhrases) {
  assert(design.includes(phrase), `DESIGN.md missing required contract phrase: ${phrase}`);
}

const requiredTokens = [
  '--gov-bg',
  '--gov-surface',
  '--gov-surface-raised',
  '--gov-ink',
  '--gov-ink-strong',
  '--gov-muted',
  '--gov-line',
  '--gov-blue',
  '--gov-green',
  '--gov-gold',
  '--gov-red',
  '--gov-radius',
  '--gov-radius-sm',
  '--gov-control-height',
  '--gov-shadow',
];

for (const token of requiredTokens) {
  assert(css.includes(`${token}:`), `globals.css missing shared design token: ${token}`);
  assert(design.includes(token), `DESIGN.md missing shared design token: ${token}`);
}

const forbiddenVisiblePhrases = [
  /AI dashboard/i,
  /command center/i,
  /mission control/i,
  /smart civic platform/i,
  /autonomous platform/i,
  /futuristic admin panel/i,
];

for (const relativePath of sourceFiles) {
  const source = await readFile(path.join(portalRoot, relativePath), 'utf8');
  for (const pattern of forbiddenVisiblePhrases) {
    assert(!pattern.test(source), `${relativePath} contains forbidden design-language phrase: ${pattern}`);
  }
}

console.log('design-system-freeze-guard passed');
