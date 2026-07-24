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
const fieldPage = await read('app/field/page.tsx');
const adminPage = await read('app/admin/staff/page.tsx');
const publicationPage = await read('app/signage/page.tsx');
const outputsPage = await read('app/exports/page.tsx');
const field = await read('components/GovernmentFieldOperationsWorkbench.tsx');
const administration = await read('components/GovernmentAdministrationWorkbench.tsx');
const publication = await read('components/GovernmentPublicationWorkbench.tsx');
const shell = await read('components/GovernmentWorkspaceShell.tsx');
const styles = await read('app/government-service-delivery-workbenches.css');
const workOrder = await read('../../docs/design-system/NLI-WO-007-field-administration-publication-workspaces.md');

assert(/import '\.\/government-service-delivery-workbenches\.css';/.test(layout), 'root layout must load service-delivery workbench styles');
for (const [name, page, component] of [
  ['field', fieldPage, 'GovernmentFieldOperationsWorkbench'],
  ['administration', adminPage, 'GovernmentAdministrationWorkbench'],
  ['publication', publicationPage, 'GovernmentPublicationWorkbench'],
  ['publication outputs', outputsPage, 'GovernmentPublicationWorkbench'],
]) {
  assert(/GovernmentWorkspaceShell/.test(page) && new RegExp(component).test(page), `${name} route must compose the government shell and controlled workbench`);
  assert(/getGovernmentWorkspaceData/.test(page), `${name} route must use shared current workspace data`);
  assert(/robots:[\s\S]*index: false/.test(page), `${name} route must prevent indexing`);
}
assert(/initialSection="outputs"/.test(outputsPage), 'administrator output route must open the consolidated publication output section');

for (const endpoint of ['/api/v1/field/assignments', '/api/v1/field/geotag-tasks', '/api/v1/field/submissions', '/api/v1/territories', '/evidence-files']) {
  assert(field.includes(endpoint), `field workbench must use ${endpoint}`);
}
assert(/SYNC_STORAGE_KEY/.test(field) && /localStorage/.test(field) && /navigator\.onLine/.test(field), 'field workbench must preserve device-held synchronization state');
assert(/It has not entered the national registry yet/.test(field), 'field sync queue must disclose that device-held work is not a national record');
assert(/Submit to verification/.test(field) && /href="\/verify"/.test(field), 'field workbench must hand work to Verification');
assert(!/method:\s*'PATCH'[\s\S]*field\/assignments/.test(field), 'field workbench must not invent assignment mutation authority');
assert(/credentials: 'include'/.test(field) && /authorizationHeader\(token\)/.test(field) && /csrfHeader\(\)/.test(field), 'field workbench must support cookie and bearer sessions');

for (const endpoint of ['/api/v1/admin/users', '/disable', '/revoke-sessions']) {
  assert(administration.includes(endpoint), `administration workbench must use ${endpoint}`);
}
assert(/method: 'PATCH'/.test(administration), 'administration workbench must preserve controlled account update');
assert(/Current administrator cannot disable this session account/.test(administration), 'administration must expose current-admin safeguard');
assert(/Last active administrator cannot be disabled/.test(administration), 'administration must expose last-active-admin safeguard');
assert(/Least privilege remains the default/.test(administration), 'administration must state least-privilege posture');

for (const endpoint of [
  '/api/v1/geotag-submissions',
  '/api/v1/addresses',
  '/api/v1/imports/jobs',
  '/api/v1/publication/packs',
  '/api/v1/signage/export',
  '/api/v1/signage/pack',
  '/publication-simulation',
  '/publish',
  '/duplicate-decision',
  '/road-suggestion',
  '/identity',
  '/certificate',
]) {
  assert(publication.includes(endpoint), `publication workbench must use ${endpoint}`);
}
assert(/NEXT_PUBLIC_PUBLICATION_RELEASE_ENABLED/.test(publication), 'publication release must remain guarded by the institutional flag');
assert(/sessionUser\?\.role === 'admin' && publicationReleaseEnabled/.test(publication), 'public release must require administrator authority and institutional flag');
assert(/Institutional approval lock active/.test(publication), 'publication UI must explain the release lock');
assert(/Preparation, approval, publication, and signage are separate states/.test(publication), 'publication workbench must preserve lifecycle separation');
assert(/Run simulation only/.test(publication), 'publication workbench must expose non-publishing release simulation');

assert(/src="\/eg-coat-of-arms\.svg"/.test(shell), 'official coat of arms must remain in the government shell');
assert(/Developed by BeCoreOps for the Government of the Republic of Equatorial Guinea/.test(shell), 'approved BeCoreOps attribution must remain present');
assert(/GovernmentIcon/.test(shell) && /government-navigation-icon/.test(shell), 'icon-led navigation must remain present');

assert(/@media \(max-width: 920px\)/.test(styles) && /@media \(max-width: 700px\)/.test(styles), 'service-delivery workbenches must define tablet and mobile behavior');
assert(/prefers-reduced-motion/.test(styles), 'service-delivery workbenches must respect reduced-motion preferences');
assert(!/linear-gradient\s*\(|radial-gradient\s*\(|backdrop-filter\s*:/i.test(styles), 'service-delivery styles must not use decorative gradients or glass effects');
assert(!/border-radius:\s*(?:999|9999)px/i.test(styles), 'service-delivery styles must not use decorative pill controls');

const combined = `${fieldPage}\n${adminPage}\n${publicationPage}\n${outputsPage}\n${field}\n${administration}\n${publication}\n${styles}`;
assert(!/ChatGPT|OpenAI|AI[- ]generated|generated by AI/i.test(combined), 'migrated government workbenches must not contain AI attribution');
assert(/Complete the protected operational redesign through Publication/.test(workOrder), 'work order must preserve the approved completion boundary');
assert(/does not expose it/.test(workOrder), 'work order must prohibit invented field dispatch authority');
assert(/administrator-only public release protected by/.test(workOrder), 'work order must preserve controlled publication authority');

console.log('government-service-delivery-workbench-guard passed');
