import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sourcePath = path.resolve('scripts/government-operational-workbench-browser-audit.mjs');
const runtimePath = path.resolve('scripts/.government-operational-workbench-browser-audit-runtime.mjs');
const source = await readFile(sourcePath, 'utf8');
const original = "await page.getByRole('heading', { level: 1, name: expectedTitle }).waitFor({ state: 'visible', timeout: 30_000 });";
const replacement = "await page.locator('.government-operation-page').getByRole('heading', { level: 1, name: expectedTitle }).waitFor({ state: 'visible', timeout: 30_000 });";
const corrected = source.replace(original, replacement);

if (corrected === source || corrected.includes(original)) {
  throw new Error('government operational workbench browser audit title scoping was not applied');
}

await writeFile(runtimePath, corrected, 'utf8');
await import(pathToFileURL(runtimePath).href);
