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
if (corrected === source || corrected.includes("'/territories': '.territory-admin-grid'") || corrected.includes("locator('.chrome-shell.chrome-role-guest').waitFor")) {
  throw new Error('presentation audit runtime corrections were not applied');
}
await writeFile(runtimePath, corrected, 'utf8');
await import(pathToFileURL(runtimePath).href);
