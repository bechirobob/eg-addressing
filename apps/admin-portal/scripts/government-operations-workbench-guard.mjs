import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

async function read(relativePath) {
  return readFile(path.resolve(portalRoot, relativePath), 'utf8');
}

const layout = await read('app/layout.tsx');
const registryPage = await read('app/registry/page.tsx');
const verificationPage = await read('app/verify/page.tsx');
const registry = await read('components/GovernmentRegistryWorkbench.tsx');
const verification = await read('components/GovernmentVerificationWorkbench.tsx');
const shell = await read('components/GovernmentWorkspaceShell.tsx');
const styles = await read('app/government-operations-workbench.css');
const sharedData = await read('lib/governmentWorkspaceData.ts');
const workOrder = await read('../../docs/design-system/NLI-WO-006-registry-verification-workbench.md');

assert(/import '\.\/government-operations-workbench\.css';/.test(layout), 'root layout must load the government operations workbench stylesheet');
assert(/GovernmentWorkspaceShell/.test(registryPage) && /GovernmentRegistryWorkbench/.test(registryPage), 'registry route must use the protected government shell and registry workbench');
assert(/GovernmentWorkspaceShell/.test(verificationPage) && /GovernmentVerificationWorkbench/.test(verificationPage), 'verification route must use the protected government shell and verification workbench');
assert(/robots:[\s\S]*index: false/.test(registryPage) && /robots:[\s\S]*index: false/.test(verificationPage), 'protected operational workbenches must prevent indexing');
assert(/getGovernmentWorkspaceData/.test(registryPage) && /getGovernmentWorkspaceData/.test(verificationPage), 'operational routes must use shared current summary data for the shell');
assert(/\/api\/v1\/reporting\/summary/.test(sharedData) && /\/api\/v1\/pilot-readiness\/summary/.test(sharedData), 'shared workspace data must use current reporting and readiness services');

for (const endpoint of ['/api/v1/territories', '/api/v1/roads', '/api/v1/buildings', '/api/v1/addresses']) {
  assert(registry.includes(endpoint), `registry workbench must use ${endpoint}`);
}
assert(/method: 'PATCH'/.test(registry), 'registry workbench must preserve controlled updates');
assert(/method: 'DELETE'/.test(registry), 'registry workbench must preserve administrator archive actions');
assert(/Editor or administrator authority is required/.test(registry), 'registry workbench must explain write authority');
assert(/Administrator authority is required to archive/.test(registry), 'registry workbench must explain archive authority');
assert(/Publication authority remains separate/.test(registry), 'registry workbench must distinguish registry state from publication authority');
assert(/credentials: 'include'/.test(registry) && /authorizationHeader\(token\)/.test(registry) && /csrfHeader\(\)/.test(registry), 'registry workbench must support cookie and bearer sessions');

assert(/\['submitted', 'under-review'\]\.includes\(submission\.review_status\)/.test(verification), 'verification workbench must keep only active submitted and under-review cases');
for (const endpoint of ['/api/v1/field/submissions', '/evidence-history', '/evidence-review', '/evidence-files/', '/api/v1/verification/lookup']) {
  assert(verification.includes(endpoint), `verification workbench must use ${endpoint}`);
}
for (const action of ["'approve'", "'rework'", "'under-review'", "'reject'"]) {
  assert(verification.includes(action), `verification workbench must expose ${action} through existing authority endpoints`);
}
assert(/Protected evidence must be accepted first/.test(verification), 'verification approval must explain evidence-decision prerequisites');
assert(/Approval is not publication/.test(verification), 'verification workbench must distinguish approval from publication');
assert(/credentials: 'include'/.test(verification) && /authorizationHeader\(token\)/.test(verification) && /csrfHeader\(\)/.test(verification), 'verification workbench must support cookie and bearer sessions');

assert(/sectionLabel\?: string/.test(shell) && /workspaceTitle\?: string/.test(shell) && /workContext\?: string\[\]/.test(shell), 'government shell must support route-specific workbench context');
assert(/src="\/eg-coat-of-arms\.svg"/.test(shell), 'official coat of arms must remain in the protected shell');
assert(/GovernmentIcon/.test(shell) && /government-navigation-icon/.test(shell), 'icon-led government navigation must remain present');
assert(/Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea/.test(shell), 'approved BeCoreOps attribution must remain present');

assert(/\.government-three-pane-workbench[\s\S]*grid-template-columns: minmax\(250px, 0\.72fr\) minmax\(520px, 1\.55fr\) minmax\(300px, 0\.86fr\)/.test(styles), 'desktop workbench must define queue, record, and decision panes');
assert(/@media \(max-width: 920px\)/.test(styles) && /@media \(max-width: 700px\)/.test(styles), 'workbenches must define purpose-built tablet and mobile behavior');
assert(/prefers-reduced-motion/.test(styles), 'workbenches must respect reduced-motion preferences');
assert(!/linear-gradient\s*\(|radial-gradient\s*\(|backdrop-filter\s*:/i.test(styles), 'workbench styles must not use decorative gradients or glass effects');
assert(!/border-radius:\s*(?:999|9999)px/i.test(styles), 'workbench styles must not use decorative pill controls');

const combinedVisibleProduct = `${registryPage}\n${verificationPage}\n${registry}\n${verification}\n${shell}\n${styles}`;
assert(!/ChatGPT|OpenAI|AI[- ]generated|generated by AI/i.test(combinedVisibleProduct), 'protected government workbenches must not contain AI attribution');
assert(/continuous queue–record–evidence–decision workflow/.test(workOrder), 'work order must preserve the approved workflow objective');
assert(/does not change database schema/.test(workOrder), 'work order must preserve the implementation authority boundary');

console.log('government-operations-workbench-guard passed');
