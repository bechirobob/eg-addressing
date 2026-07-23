import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();

const files = {
  tokens: path.join(root, 'app', 'government-design-tokens.css'),
  layout: path.join(root, 'app', 'layout.tsx'),
  page: path.join(root, 'app', 'design-lab', 'page.tsx'),
  styles: path.join(root, 'app', 'design-lab', 'page.module.css'),
  standard: path.resolve(root, '..', '..', 'docs', 'design-system', 'becoreops-government-enterprise-design-standard.md'),
  phase: path.resolve(root, '..', '..', 'docs', 'design-system', 'eg-addressing-staff-platform-redesign-phase-1.md'),
};

const failures = [];

function readRequired(name, filePath) {
  if (!fs.existsSync(filePath)) {
    failures.push(`${name}: missing ${path.relative(root, filePath)}`);
    return '';
  }
  return fs.readFileSync(filePath, 'utf8');
}

const tokens = readRequired('tokens', files.tokens);
const layout = readRequired('layout', files.layout);
const page = readRequired('design-lab page', files.page);
const styles = readRequired('design-lab styles', files.styles);
const standard = readRequired('BGEDS standard', files.standard);
const phase = readRequired('phase foundation', files.phase);

const requiredTokens = [
  '--bge-color-canvas',
  '--bge-color-surface',
  '--bge-color-text',
  '--bge-color-divider',
  '--bge-color-institution',
  '--bge-color-action',
  '--bge-color-focus',
  '--bge-color-success',
  '--bge-color-warning',
  '--bge-color-danger',
  '--bge-font-sans',
  '--bge-font-size-page-title',
  '--bge-space-4',
  '--bge-rail-width',
  '--bge-topbar-height',
  '--bge-inspector-width',
  '--bge-duration-standard',
];

for (const token of requiredTokens) {
  if (!tokens.includes(token)) failures.push(`tokens: missing ${token}`);
}

if (!layout.includes("import './government-design-tokens.css';")) {
  failures.push('layout: government design tokens are not imported');
}

const requiredPageMarkers = [
  'DESIGN LAB — NOT AN OFFICIAL PRODUCTION RECORD',
  "process.env.NEXT_PUBLIC_APP_ENV === 'production'",
  'Today&apos;s national addressing work',
  'Assigned queue',
  'Decision inspector',
  'Staff administration target',
  'Personnel, teams, scope, equipment, and access',
];

for (const marker of requiredPageMarkers) {
  if (!page.includes(marker)) failures.push(`design-lab page: missing marker ${marker}`);
}

const requiredStyleMarkers = [
  'grid-template-columns: var(--bge-rail-width) minmax(0, 1fr)',
  'grid-template-columns: minmax(220px, 0.72fr) minmax(520px, 1.75fr) minmax(280px, 0.9fr)',
  '@media (max-width: 860px)',
  '@media (max-width: 600px)',
];

for (const marker of requiredStyleMarkers) {
  if (!styles.includes(marker)) failures.push(`design-lab styles: missing ${marker}`);
}

const prohibitedStylePatterns = [
  /linear-gradient\s*\(/i,
  /radial-gradient\s*\(/i,
  /border-radius:\s*(?:999|9999)px/i,
  /backdrop-filter\s*:/i,
];

for (const pattern of prohibitedStylePatterns) {
  if (pattern.test(styles)) failures.push(`design-lab styles: prohibited pattern ${pattern}`);
}

if (!standard.includes('BeCoreOps Government & Enterprise Design Standard')) {
  failures.push('standard: expected BGEDS title is missing');
}
if (!standard.includes('Five-minute rule')) {
  failures.push('standard: Five-minute rule is missing');
}
if (!phase.includes('The correct response is a controlled frontend reconstruction')) {
  failures.push('phase foundation: reconstruction boundary is missing');
}
if (!phase.includes('Preserved without redesign')) {
  failures.push('phase foundation: preserved-system boundary is missing');
}

const result = {
  checked: Object.keys(files).length,
  required_tokens: requiredTokens.length,
  failures,
  passed: failures.length === 0,
};

console.log(JSON.stringify(result, null, 2));

if (failures.length > 0) process.exit(1);
