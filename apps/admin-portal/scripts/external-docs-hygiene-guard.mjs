import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '../../..');

const scannedFiles = [
  'docs/source-proposals/openapi.yaml',
  'docs/source-proposals/build-roadmap.md',
  'docs/source-proposals/repo-scaffold-overview.md',
];

const forbiddenPatterns = [
  { pattern: /\bMVP\b/i, reason: 'External handoff docs should describe implementation scope, not MVP status.' },
  { pattern: /\bstarter\b/i, reason: 'Starter-language makes the handoff look unfinished.' },
  { pattern: /\bprototype\b/i, reason: 'Prototype-language is not appropriate in public handoff material.' },
  { pattern: /\bplaceholder\b/i, reason: 'Placeholder-language should not appear in handoff material.' },
  { pattern: /\bdummy\b/i, reason: 'Dummy-language should not appear in handoff material.' },
  { pattern: /\blorem\b/i, reason: 'Lorem text is never valid handoff content.' },
  { pattern: /Generated with|AI-assisted|ChatGPT|Claude|Hermes Agent/i, reason: 'No AI/tool attribution in tracked handoff docs.' },
  { pattern: /\/home\/ubuntu|artifacts\/|\.hermes\//i, reason: 'Internal paths/artifact locations should not leak into handoff docs.' },
  { pattern: /localhost|127\.0\.0\.1|http:\/\/api:8100/i, reason: 'Raw local origins should not appear in handoff docs.' },
];

const allowlist = [
  // File names may retain historical source folder names; this guard scans file content only.
];

const failures = [];

for (const file of scannedFiles) {
  const source = await readFile(path.join(repoRoot, file), 'utf8');
  const lines = source.split(/\r?\n/);
  lines.forEach((line, index) => {
    for (const item of forbiddenPatterns) {
      if (item.pattern.test(line) && !allowlist.some((allowed) => allowed.file === file && allowed.line === index + 1)) {
        failures.push({ file, line: index + 1, text: line.trim(), reason: item.reason });
      }
    }
  });
}

if (failures.length) {
  console.error(JSON.stringify({ status: 'fail', failures }, null, 2));
  process.exit(1);
}

console.log(JSON.stringify({ status: 'pass', scannedFiles }, null, 2));
