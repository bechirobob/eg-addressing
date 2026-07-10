import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const registry = await readFile(path.join(portalRoot, 'components/RegistryCorePanel.tsx'), 'utf8');
const publication = await readFile(path.join(portalRoot, 'components/PublicationOperationsPanel.tsx'), 'utf8');

assert(!registry.includes('Quick update'), 'Registry must not expose fake Quick update actions');
assert(registry.includes('disabled={!canWrite || isSubmitting}'), 'Registry create controls should be role-gated');
assert(registry.includes('disabled={!canArchive || isSubmitting}'), 'Registry archive controls should be admin-gated');
assert(registry.includes('Editor or admin access required'), 'Registry should explain editor/admin role gating');
assert(registry.includes('Admin access required to archive'), 'Registry should explain archive gating');
assert(publication.includes('commitDisabledReason'), 'Publication commit actions should show disabled reasons');
assert(publication.includes('publishDisabledReason'), 'Publication publish actions should show disabled reasons');
assert(publication.includes('publicationReleaseEnabled'), 'Publication release controls must be guarded by an explicit release gate flag');
assert(publication.includes('Institutional release gate locked'), 'Publication UI must tell operators when the release gate is locked');
assert(publication.includes('disabled={Boolean(commitDisabledReason(job))}'), 'Commit buttons must be disabled when not actionable');
assert(publication.includes('disabled={Boolean(publishDisabledReason(pack))}'), 'Publish buttons must be disabled when not actionable');

console.log('registry-action-guard passed');
