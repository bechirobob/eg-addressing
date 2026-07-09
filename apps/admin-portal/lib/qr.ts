const VERSION = 5;
const SIZE = 17 + VERSION * 4;
const DATA_CODEWORDS = 108;
const EC_CODEWORDS = 26;
const ALIGNMENT_PATTERN_POSITIONS = [6, 30];
const FORMAT_XOR_MASK = 0x5412;

const enum EccLevelBits {
  Low = 1,
}

type Cell = boolean | null;

type MatrixState = {
  modules: Cell[][];
  reserved: boolean[][];
};

function createMatrix(): MatrixState {
  return {
    modules: Array.from({ length: SIZE }, () => Array<Cell>(SIZE).fill(null)),
    reserved: Array.from({ length: SIZE }, () => Array<boolean>(SIZE).fill(false)),
  };
}

function setModule(state: MatrixState, x: number, y: number, value: boolean, reserve = true) {
  if (x < 0 || y < 0 || x >= SIZE || y >= SIZE) return;
  state.modules[y][x] = value;
  if (reserve) state.reserved[y][x] = true;
}

function setFinderPattern(state: MatrixState, x: number, y: number) {
  for (let dy = -1; dy <= 7; dy += 1) {
    for (let dx = -1; dx <= 7; dx += 1) {
      const xx = x + dx;
      const yy = y + dy;
      if (xx < 0 || yy < 0 || xx >= SIZE || yy >= SIZE) continue;
      const inPattern = dx >= 0 && dx <= 6 && dy >= 0 && dy <= 6;
      const dark = inPattern && (dx === 0 || dx === 6 || dy === 0 || dy === 6 || (dx >= 2 && dx <= 4 && dy >= 2 && dy <= 4));
      setModule(state, xx, yy, dark, true);
    }
  }
}

function setAlignmentPattern(state: MatrixState, cx: number, cy: number) {
  for (let dy = -2; dy <= 2; dy += 1) {
    for (let dx = -2; dx <= 2; dx += 1) {
      const xx = cx + dx;
      const yy = cy + dy;
      if (state.reserved[yy]?.[xx]) continue;
      const dark = Math.max(Math.abs(dx), Math.abs(dy)) !== 1;
      setModule(state, xx, yy, dark, true);
    }
  }
}

function reserveFormatAreas(state: MatrixState) {
  for (let i = 0; i < 9; i += 1) {
    if (i !== 6) {
      state.reserved[8][i] = true;
      state.reserved[i][8] = true;
    }
  }
  for (let i = 0; i < 8; i += 1) {
    state.reserved[8][SIZE - 1 - i] = true;
    state.reserved[SIZE - 1 - i][8] = true;
  }
}

function addFunctionPatterns(state: MatrixState) {
  setFinderPattern(state, 0, 0);
  setFinderPattern(state, SIZE - 7, 0);
  setFinderPattern(state, 0, SIZE - 7);

  for (let i = 8; i < SIZE - 8; i += 1) {
    const dark = i % 2 === 0;
    setModule(state, i, 6, dark, true);
    setModule(state, 6, i, dark, true);
  }

  for (const cx of ALIGNMENT_PATTERN_POSITIONS) {
    for (const cy of ALIGNMENT_PATTERN_POSITIONS) {
      const overlapsFinder = (cx === 6 && cy === 6) || (cx === 6 && cy === SIZE - 7) || (cx === SIZE - 7 && cy === 6);
      if (!overlapsFinder) setAlignmentPattern(state, cx, cy);
    }
  }

  // Fixed dark module for QR versions 2 and above.
  setModule(state, 8, SIZE - 8, true, true);
  reserveFormatAreas(state);
}

function appendBits(bits: number[], value: number, length: number) {
  for (let i = length - 1; i >= 0; i -= 1) bits.push((value >>> i) & 1);
}

function utf8Bytes(input: string) {
  return Array.from(new TextEncoder().encode(input));
}

function createDataCodewords(input: string) {
  const data = utf8Bytes(input);
  // Version 5-L byte mode capacity is enough for canonical public proof/profile URLs used by this pilot.
  if (data.length > 106) {
    throw new Error('QR payload is too long for the public proof QR version.');
  }

  const bits: number[] = [];
  appendBits(bits, 0b0100, 4); // byte mode
  appendBits(bits, data.length, 8); // version 1-9 byte count indicator
  for (const byte of data) appendBits(bits, byte, 8);
  const maxBits = DATA_CODEWORDS * 8;
  appendBits(bits, 0, Math.min(4, maxBits - bits.length));
  while (bits.length % 8 !== 0) bits.push(0);

  const codewords: number[] = [];
  for (let i = 0; i < bits.length; i += 8) {
    let byte = 0;
    for (let j = 0; j < 8; j += 1) byte = (byte << 1) | bits[i + j];
    codewords.push(byte);
  }
  for (let pad = 0; codewords.length < DATA_CODEWORDS; pad += 1) {
    codewords.push(pad % 2 === 0 ? 0xec : 0x11);
  }
  return codewords;
}

const gfExp = new Array<number>(512);
const gfLog = new Array<number>(256);
(function initGaloisField() {
  let x = 1;
  for (let i = 0; i < 255; i += 1) {
    gfExp[i] = x;
    gfLog[x] = i;
    x <<= 1;
    if (x & 0x100) x ^= 0x11d;
  }
  for (let i = 255; i < 512; i += 1) gfExp[i] = gfExp[i - 255];
})();

function gfMultiply(a: number, b: number) {
  if (a === 0 || b === 0) return 0;
  return gfExp[gfLog[a] + gfLog[b]];
}

function reedSolomonGenerator(degree: number) {
  let result = [1];
  for (let i = 0; i < degree; i += 1) {
    const next = new Array<number>(result.length + 1).fill(0);
    for (let j = 0; j < result.length; j += 1) {
      next[j] ^= gfMultiply(result[j], gfExp[i]);
      next[j + 1] ^= result[j];
    }
    result = next;
  }
  return result;
}

function reedSolomonRemainder(data: number[], degree: number) {
  const generator = reedSolomonGenerator(degree);
  const result = new Array<number>(degree).fill(0);
  for (const byte of data) {
    const factor = byte ^ result.shift()!;
    result.push(0);
    for (let i = 0; i < degree; i += 1) result[i] ^= gfMultiply(generator[i], factor);
  }
  return result;
}

function codewordsToBits(codewords: number[]) {
  const bits: number[] = [];
  for (const byte of codewords) appendBits(bits, byte, 8);
  return bits;
}

function placeDataBits(state: MatrixState, bits: number[]) {
  let bitIndex = 0;
  let upward = true;
  for (let right = SIZE - 1; right >= 1; right -= 2) {
    if (right === 6) right -= 1;
    for (let vert = 0; vert < SIZE; vert += 1) {
      const y = upward ? SIZE - 1 - vert : vert;
      for (let j = 0; j < 2; j += 1) {
        const x = right - j;
        if (state.reserved[y][x]) continue;
        state.modules[y][x] = bitIndex < bits.length ? bits[bitIndex] === 1 : false;
        bitIndex += 1;
      }
    }
    upward = !upward;
  }
}

function maskBit(mask: number, x: number, y: number) {
  switch (mask) {
    case 0: return (x + y) % 2 === 0;
    case 1: return y % 2 === 0;
    case 2: return x % 3 === 0;
    case 3: return (x + y) % 3 === 0;
    case 4: return (Math.floor(y / 2) + Math.floor(x / 3)) % 2 === 0;
    case 5: return ((x * y) % 2) + ((x * y) % 3) === 0;
    case 6: return (((x * y) % 2) + ((x * y) % 3)) % 2 === 0;
    case 7: return (((x + y) % 2) + ((x * y) % 3)) % 2 === 0;
    default: return false;
  }
}

function applyMask(source: MatrixState, mask: number): boolean[][] {
  return source.modules.map((row, y) => row.map((cell, x) => {
    const value = cell === true;
    if (source.reserved[y][x]) return value;
    return value !== maskBit(mask, x, y);
  }));
}

function penalty(matrix: boolean[][]) {
  let score = 0;
  for (let y = 0; y < SIZE; y += 1) {
    let runColor = matrix[y][0];
    let runLength = 1;
    for (let x = 1; x < SIZE; x += 1) {
      if (matrix[y][x] === runColor) runLength += 1;
      else {
        if (runLength >= 5) score += 3 + runLength - 5;
        runColor = matrix[y][x];
        runLength = 1;
      }
    }
    if (runLength >= 5) score += 3 + runLength - 5;
  }
  for (let x = 0; x < SIZE; x += 1) {
    let runColor = matrix[0][x];
    let runLength = 1;
    for (let y = 1; y < SIZE; y += 1) {
      if (matrix[y][x] === runColor) runLength += 1;
      else {
        if (runLength >= 5) score += 3 + runLength - 5;
        runColor = matrix[y][x];
        runLength = 1;
      }
    }
    if (runLength >= 5) score += 3 + runLength - 5;
  }
  for (let y = 0; y < SIZE - 1; y += 1) {
    for (let x = 0; x < SIZE - 1; x += 1) {
      const color = matrix[y][x];
      if (matrix[y][x + 1] === color && matrix[y + 1][x] === color && matrix[y + 1][x + 1] === color) score += 3;
    }
  }
  const pattern = [true, false, true, true, true, false, true, false, false, false, false];
  const reverse = [...pattern].reverse();
  for (let y = 0; y < SIZE; y += 1) {
    for (let x = 0; x <= SIZE - 11; x += 1) {
      const slice = matrix[y].slice(x, x + 11);
      if (pattern.every((v, i) => slice[i] === v) || reverse.every((v, i) => slice[i] === v)) score += 40;
    }
  }
  for (let x = 0; x < SIZE; x += 1) {
    for (let y = 0; y <= SIZE - 11; y += 1) {
      const slice = Array.from({ length: 11 }, (_, i) => matrix[y + i][x]);
      if (pattern.every((v, i) => slice[i] === v) || reverse.every((v, i) => slice[i] === v)) score += 40;
    }
  }
  const dark = matrix.flat().filter(Boolean).length;
  const percent = (dark * 100) / (SIZE * SIZE);
  score += Math.floor(Math.abs(percent - 50) / 5) * 10;
  return score;
}

function bchFormatBits(formatData: number) {
  let data = formatData << 10;
  const generator = 0x537;
  for (let i = 14; i >= 10; i -= 1) {
    if (((data >>> i) & 1) !== 0) data ^= generator << (i - 10);
  }
  return ((formatData << 10) | data) ^ FORMAT_XOR_MASK;
}

function addFormatBits(matrix: boolean[][], mask: number) {
  const bits = bchFormatBits((EccLevelBits.Low << 3) | mask);
  const bit = (i: number) => ((bits >>> i) & 1) !== 0;

  for (let i = 0; i <= 5; i += 1) matrix[8][i] = bit(i);
  matrix[8][7] = bit(6);
  matrix[8][8] = bit(7);
  matrix[7][8] = bit(8);
  for (let i = 9; i < 15; i += 1) matrix[14 - i][8] = bit(i);

  for (let i = 0; i < 8; i += 1) matrix[SIZE - 1 - i][8] = bit(i);
  for (let i = 8; i < 15; i += 1) matrix[8][SIZE - 15 + i] = bit(i);
  matrix[SIZE - 8][8] = true;
}

function buildMatrix(input: string) {
  const data = createDataCodewords(input);
  const ec = reedSolomonRemainder(data, EC_CODEWORDS);
  const state = createMatrix();
  addFunctionPatterns(state);
  placeDataBits(state, codewordsToBits([...data, ...ec]));

  let bestMask = 0;
  let bestMatrix = applyMask(state, 0);
  let bestPenalty = Number.POSITIVE_INFINITY;
  for (let mask = 0; mask < 8; mask += 1) {
    const candidate = applyMask(state, mask);
    addFormatBits(candidate, mask);
    const score = penalty(candidate);
    if (score < bestPenalty) {
      bestPenalty = score;
      bestMask = mask;
      bestMatrix = candidate;
    }
  }
  addFormatBits(bestMatrix, bestMask);
  return bestMatrix;
}

function escapeAttribute(value: string) {
  return value.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

export function createQrSvg(input: string, options: { moduleSize?: number; margin?: number; title?: string } = {}) {
  const moduleSize = options.moduleSize ?? 6;
  const margin = options.margin ?? 4;
  const matrix = buildMatrix(input);
  const dimension = (SIZE + margin * 2) * moduleSize;
  const paths: string[] = [];
  for (let y = 0; y < SIZE; y += 1) {
    for (let x = 0; x < SIZE; x += 1) {
      if (matrix[y][x]) paths.push(`M${(x + margin) * moduleSize} ${(y + margin) * moduleSize}h${moduleSize}v${moduleSize}h-${moduleSize}z`);
    }
  }
  const title = options.title ? `<title>${escapeAttribute(options.title)}</title>` : '';
  return `<svg xmlns="http://www.w3.org/2000/svg" role="img" aria-label="${escapeAttribute(options.title ?? 'QR code')}" viewBox="0 0 ${dimension} ${dimension}" width="${dimension}" height="${dimension}" shape-rendering="crispEdges">${title}<rect width="100%" height="100%" fill="#fff"/><path d="${paths.join(' ')}" fill="#0b2f4f"/></svg>`;
}

export function qrMetadata(input: string) {
  const matrix = buildMatrix(input);
  return {
    version: VERSION,
    size: SIZE,
    darkModules: matrix.flat().filter(Boolean).length,
    payloadBytes: utf8Bytes(input).length,
  };
}
