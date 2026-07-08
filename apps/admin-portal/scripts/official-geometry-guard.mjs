import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const portalRoot = path.resolve(__dirname, '..');
const css = await readFile(path.join(portalRoot, 'app/globals.css'), 'utf8');

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function tokenValue(name) {
  return css.match(new RegExp(`${name}:\\s*([^;]+);`))?.[1]?.trim() ?? null;
}

function resolveRadius(value) {
  if (value === 'var(--gov-radius)') return tokenValue('--radius-card');
  if (value === 'var(--gov-radius-sm)') return tokenValue('--radius-control');
  if (value === 'var(--radius-card)') return tokenValue('--radius-card');
  if (value === 'var(--radius-control)') return tokenValue('--radius-control');
  if (value === 'var(--registry-radius)') return tokenValue('--radius-card');
  return value;
}

const radiusValues = [...css.matchAll(/border-radius:\s*([^;]+);/g)].map((match) => match[1].trim());
for (const original of radiusValues) {
  const value = resolveRadius(original);
  if (!value || value === '0' || value === '0px' || value === '50%' || value.includes('999px') || value.includes('circle') || value.startsWith('var(--ref-radius') || value.startsWith('var(--radius')) continue;
  const px = Number.parseFloat(value);
  assert(Number.isFinite(px) && px <= 12, `Visual guide allows only restrained radii up to 12px except status badges, found: ${original}`);
}
assert(css.includes('--radius-xl:'), 'Radius XL token must exist');
assert(css.includes('--radius-lg:'), 'Radius LG token must exist');
assert(css.includes('--radius-md:'), 'Radius MD token must exist');
assert(tokenValue('--radius-card') === '12px', 'Visual guide card radius token must stay at 12px');
assert(tokenValue('--radius-control') === '8px', 'Visual guide control radius token must stay at 8px');
const egShadow = (css.match(/--eg-shadow:\s*([^;]+);/)?.[1]?.trim() ?? 'none').replace(/\s*!important$/, '');
const govShadow = (tokenValue('--gov-shadow') ?? 'none').replace(/\s*!important$/, '');
const boxShadowValues = [...css.matchAll(/box-shadow:\s*([^;]+);/g)].map((match) =>
  match[1].trim().replace(/\s*!important$/, '').replace('var(--eg-shadow)', egShadow).replace('var(--gov-shadow)', govShadow),
);
for (const value of boxShadowValues) {
  if (value === 'none' || value === 'var(--ref-shadow)') continue;
  const isHardOffset = /\b0\s+rgba?\(/.test(value);
  const isInputInset = /^inset\s+\d+px\s+0\s+0\s+(?:rgba?\(|var\(--eg-blue\))/.test(value);
  assert(isHardOffset || isInputInset, `Reference civic UI may use only restrained offset/inset shadows, found: ${value}`);
  assert(!/\b(1[8-9]|[2-9]\d)px\s+rgba?\(/.test(value), `Reference civic UI must avoid heavy blur shadows, found: ${value}`);
}
assert(!/transform:\s*translate/i.test(css), 'Official UI must not use button/card translate motion');
assert(!/transition:\s*(?!none\s*!important;)/.test(css.replace(/transition:\s+none/g, 'transition:none')), 'Official UI must not rely on animated interaction styling');
const bodyBlocks = [...css.matchAll(/(?:^|\n)(?:html,\s*\n)?body\s*\{[\s\S]*?\}/g)].map((match) => match[0]);
assert(bodyBlocks.some((block) => block.includes('background-image: none !important')), 'Visual guide requires no decorative grid background on body');
assert(css.includes('--page-bg: #f7f4ec'), 'Visual guide page background token must exist');
assert(css.includes('--surface: #fffef9'), 'Visual guide surface token must exist');
assert(!/linear-gradient\(135deg/.test(css), 'Official UI must not use diagonal SaaS background gradients');
console.log('official-geometry-guard passed');
