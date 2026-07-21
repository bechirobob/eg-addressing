import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sourcePath = path.resolve('scripts/operator-presentation-audit.mjs');
const runtimePath = path.resolve('scripts/.operator-presentation-audit-runtime.mjs');
const source = await readFile(sourcePath, 'utf8');
const corrected = source.replace("'/territories': '.territory-admin-grid'", "'/territories': '.territory-workspace'");
if (corrected === source) {
  throw new Error('presentation audit territory selector correction was not applied');
}
await writeFile(runtimePath, corrected, 'utf8');
await import(pathToFileURL(runtimePath).href);
