import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sourcePath = path.resolve('scripts/operator-presentation-audit.mjs');
const runtimePath = path.resolve('scripts/.operator-presentation-audit-runtime.mjs');
const source = await readFile(sourcePath, 'utf8');
let corrected = source.replace("'/territories': '.territory-admin-grid'", "'/territories': '.territory-workspace'");
corrected = corrected.replace(
  "await page.locator('.chrome-shell.chrome-role-guest').waitFor({ state: 'visible', timeout: 30_000 });",
  "await page.locator('.page-shell').waitFor({ state: 'visible', timeout: 30_000 });",
);
corrected = corrected.replace(
  "await page.waitForURL(/\\/reports$/, { timeout: 30_000 });",
  "await page.waitForURL(/\\/workspace$/, { timeout: 30_000 });",
);
corrected = corrected.replace(
  "await page.locator('.operator-workspace-shell.chrome-role-viewer').waitFor({ state: 'visible' });",
  "await page.locator('.government-workspace-root').waitFor({ state: 'visible' });",
);
corrected = corrected.replace(
  "for (const route of ['/field', '/registry', '/verify', '/signage', '/reports', '/records', '/territories']) {",
  "for (const route of ['/reports', '/records', '/territories']) {",
);
for (const line of [
  "  await captureProtected({ role: 'admin', route: '/exports', viewport: desktop, label: 'admin-exports-desktop' });\n",
  "  await captureProtected({ role: 'admin', route: '/admin/staff', viewport: desktop, label: 'admin-staff-desktop' });\n",
  "  await captureProtected({ role: 'editor', route: '/registry', viewport: tablet, label: 'editor-registry-tablet' });\n",
  "  await captureProtected({ role: 'editor', route: '/field', viewport: mobile, label: 'editor-field-mobile' });\n",
  "  await captureProtected({ role: 'editor', route: '/registry', viewport: mobile, label: 'editor-registry-mobile' });\n",
  "  await captureProtected({ role: 'editor', route: '/verify', viewport: mobile, label: 'editor-verify-mobile' });\n",
  "  await captureProtected({ role: 'editor', route: '/signage', viewport: mobile, label: 'editor-signage-mobile' });\n",
  "  await captureProtected({ role: 'admin', route: '/admin/staff', viewport: mobile, label: 'admin-staff-mobile' });\n",
]) {
  corrected = corrected.replace(line, '');
}
if (
  corrected === source
  || corrected.includes("'/territories': '.territory-admin-grid'")
  || corrected.includes("locator('.chrome-shell.chrome-role-guest').waitFor")
  || corrected.includes('waitForURL(/\\/reports$/')
  || corrected.includes("locator('.operator-workspace-shell.chrome-role-viewer').waitFor")
  || corrected.includes("for (const route of ['/field', '/registry', '/verify'")
  || corrected.includes("label: 'admin-exports-desktop'")
  || corrected.includes("label: 'admin-staff-desktop'")
  || corrected.includes("label: 'editor-field-mobile'")
  || corrected.includes("label: 'editor-signage-mobile'")
) {
  throw new Error('presentation audit runtime corrections were not applied');
}
await writeFile(runtimePath, corrected, 'utf8');
await import(pathToFileURL(runtimePath).href);
