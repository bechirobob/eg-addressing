import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = process.cwd();
const files = {
  qr: resolve(root, 'lib/qr.ts'),
  proof: resolve(root, 'components/PublicProofPanel.tsx'),
  route: resolve(root, 'app/proof/[code]/page.tsx'),
  profile: resolve(root, 'components/PublicCodeLookupPanel.tsx'),
};

function assert(condition, message) {
  if (!condition) {
    console.error(`Public proof guard failed: ${message}`);
    process.exit(1);
  }
}

const qr = readFileSync(files.qr, 'utf8');
const proof = readFileSync(files.proof, 'utf8');
const route = readFileSync(files.route, 'utf8');
const profile = readFileSync(files.profile, 'utf8');

assert(/function reedSolomonRemainder/.test(qr), 'QR generator must include local Reed-Solomon error correction, not a decorative SVG placeholder.');
assert(/createQrSvg\(profileUrl/.test(proof), 'Public proof page must generate QR from the official public profile URL.');
assert(/\/code\/\$\{encodeURIComponent\(code\)\}/.test(proof), 'QR proof must point to the official /code/[code] public profile, not a private/admin URL.');
assert(/Print \/ save PDF/.test(proof), 'Proof route must expose browser-native print/save-PDF action.');
assert(/not proof of ownership, private title, property rights/.test(proof), 'Proof route must include public-safe ownership/title disclaimer.');
assert(!/proof of ownership[^,]/i.test(proof.replace(/not proof of ownership/g, '')), 'Proof route must not imply ownership proof.');
assert(/PublicProofPanel/.test(route), 'Proof route must render the public proof panel.');
assert(/\/proof\/\$\{encodeURIComponent\(code\)\}/.test(profile), 'Public code profile must link to /proof/[code].');

console.log('Public proof QR guard passed');
