import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const verification = await readFile(path.join(portalRoot, 'components/VerificationWorkflowPanel.tsx'), 'utf8');

assert(
  verification.includes("['submitted', 'under-review'].includes(submission.review_status)"),
  'Verification queue must only show submitted / under-review records as active actions',
);
assert(
  !verification.includes("submission.review_status !== 'approved'"),
  'Verification queue must not keep rejected/rework records active by filtering only approved records',
);

console.log('verification-queue-guard passed');
