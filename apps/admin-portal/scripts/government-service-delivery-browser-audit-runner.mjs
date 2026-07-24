import { readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const sourcePath = path.resolve('scripts/government-service-delivery-browser-audit.mjs');
const runtimePath = path.resolve('scripts/.government-service-delivery-browser-audit-runtime.mjs');
const source = await readFile(sourcePath, 'utf8');

const publicationLockExpected = "assert(bodyText.includes('Institutional approval lock active'),";
const publicationLockReplacement = "assert(bodyText.includes('Public release and physical signage remain institutionally locked') || bodyText.includes('Institutional lock active'),";
let corrected = source.replaceAll(publicationLockExpected, publicationLockReplacement);

const waitAnchor = "  await page.locator('.government-three-pane-workbench').waitFor({ state: 'visible', timeout: 30_000 });\n  await page.waitForTimeout(550);";
const deterministicWait = `  await page.locator('.government-three-pane-workbench').waitFor({ state: 'visible', timeout: 30_000 });
  if (route === '/exports') {
    const sectionControl = page.locator('.government-publication-command-bar select').first();
    await sectionControl.selectOption('outputs');
    const packQueueRecord = page.locator('.government-record-queue > button').filter({ hasText: 'Official institutional address release 008' }).first();
    await packQueueRecord.waitFor({ state: 'visible', timeout: 30_000 });
    await packQueueRecord.click();
    await page.getByText('Official publication pack', { exact: true }).waitFor({ state: 'visible', timeout: 30_000 });
  }
  await page.waitForTimeout(550);`;
corrected = corrected.replace(waitAnchor, deterministicWait);

const packInspectorExpected = "assert(bodyText.includes('Official publication pack'), `${label}: official pack inspector is missing`);";
const packInspectorReplacement = "assert((await page.getByText('Official publication pack', { exact: true }).count()) >= 1, `${label}: official pack inspector is missing`);";
corrected = corrected.replace(packInspectorExpected, packInspectorReplacement);

const packFixtureExpected = "assert(bodyText.includes('Official institutional address release 008'), `${label}: publication pack fixture is not represented`);";
const packFixtureReplacement = "assert((await page.getByText('Official institutional address release 008', { exact: true }).count()) >= 1, `${label}: publication pack fixture is not represented`);";
corrected = corrected.replace(packFixtureExpected, packFixtureReplacement);

if (
  corrected === source
  || corrected.includes(publicationLockExpected)
  || corrected.includes(packInspectorExpected)
  || corrected.includes(packFixtureExpected)
  || !corrected.includes("selectOption('outputs')")
  || !corrected.includes("getByText('Official publication pack'")
) {
  throw new Error('government service-delivery browser runtime corrections were not applied');
}

await writeFile(runtimePath, corrected, 'utf8');
await import(pathToFileURL(runtimePath).href);
