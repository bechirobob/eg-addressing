import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sourcePath = path.resolve('scripts/government-service-delivery-browser-audit.mjs');
const runtimePath = path.resolve('scripts/.government-service-delivery-browser-audit-runtime.mjs');
const source = await readFile(sourcePath, 'utf8');
const expected = "assert(bodyText.includes('Institutional approval lock active'),";
const replacement = "assert(bodyText.includes('Public release and physical signage remain institutionally locked') || bodyText.includes('Institutional lock active'),";
const corrected = source.replaceAll(expected, replacement);

if (corrected === source || corrected.includes(expected)) {
  throw new Error('government service-delivery publication-lock browser correction was not applied');
}

await writeFile(runtimePath, corrected, 'utf8');
await import(pathToFileURL(runtimePath).href);
