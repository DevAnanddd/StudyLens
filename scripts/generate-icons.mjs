/**
 * Pure-Node PNG icon generator for the StudyLens PWA.
 * Draws the favicon design (indigo→purple gradient + white lightning bolt)
 * and writes 192x192 and 512x512 RGBA PNGs to public/icons/.
 *
 * Run: node scripts/generate-icons.mjs
 */
import { deflateSync } from "node:zlib";
import { mkdirSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const OUT_DIR = join(__dirname, "..", "public", "icons");
const BOLT_POLY = [
  [34, 8],
  [16, 38],
  [28, 38],
  [24, 56],
  [44, 26],
  [30, 26],
];

function crc32(buf) {
  let table = crc32.table;
  if (!table) {
    table = crc32.table = new Int32Array(256);
    for (let n = 0; n < 256; n++) {
      let c = n;
      for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
      table[n] = c;
    }
  }
  let crc = -1;
  for (let i = 0; i < buf.length; i++) crc = (crc >>> 8) ^ table[(crc ^ buf[i]) & 0xff];
  return (crc ^ -1) >>> 0;
}

function chunk(type, data) {
  const len = Buffer.alloc(4);
  len.writeUInt32BE(data.length, 0);
  const typeBuf = Buffer.from(type, "ascii");
  const crc = Buffer.alloc(4);
  crc.writeUInt32BE(crc32(Buffer.concat([typeBuf, data])), 0);
  return Buffer.concat([len, typeBuf, data, crc]);
}

/** Top-left color → bottom-right color vertical-ish gradient. */
function lerp(a, b, t) {
  return Math.round(a + (b - a) * t);
}
function colorAt(y, x, size) {
  const t = y / size;
  const s = x / size;
  // Indigo top-left → violet mid → pink bottom-right (subtle).
  const r1 = 79, g1 = 70, b1 = 229; // #4F46E5
  const r2 = 124, g2 = 58, b2 = 237; // #7C3AED
  const r3 = 236, g3 = 72, b3 = 153; // #EC4899
  const t2 = Math.min(1, t * 1.4);
  const r = lerp(lerp(r1, r2, t), r3, t2 * 0.25 + s * 0.1);
  const g = lerp(lerp(g1, g2, t), g3, t2 * 0.25 + s * 0.1);
  const b = lerp(lerp(b1, b2, t), b3, t2 * 0.25 + s * 0.1);
  return [r, g, b];
}

function pointInPoly(px, py, poly) {
  let inside = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i];
    const [xj, yj] = poly[j];
    const intersect =
      yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;
    if (intersect) inside = !inside;
  }
  return inside;
}

function renderIcon(size) {
  const scale = size / 64;
  const bkgRows = [];

  // Fill background (a vertical gradient per row).
  for (let y = 0; y < size; y++) {
    const row = Buffer.alloc(size * 4);
    for (let x = 0; x < size; x++) {
      const [r, g, b] = colorAt(y, x, size);
      row[x * 4] = r;
      row[x * 4 + 1] = g;
      row[x * 4 + 2] = b;
      row[x * 4 + 3] = 255;
    }
    bkgRows.push(row);
  }

  // Draw the white bolt over the background.
  const scaledPoly = BOLT_POLY.map(([px, py]) => [px * scale, py * scale]);
  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      if (pointInPoly(x + 0.5, y + 0.5, scaledPoly)) {
        const off = x * 4;
        bkgRows[y][off] = 255;
        bkgRows[y][off + 1] = 255;
        bkgRows[y][off + 2] = 255;
      }
    }
  }

  const raw = Buffer.concat(bkgRows);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(size, 0);
  ihdr.writeUInt32BE(size, 4);
  ihdr[8] = 8; // bit depth
  ihdr[9] = 6; // color type RGBA
  ihdr[10] = 0;
  ihdr[11] = 0;
  ihdr[12] = 0;

  // Add filter byte (0) per scanline.
  const filtered = Buffer.alloc(size * (size * 4 + 1));
  for (let y = 0; y < size; y++) {
    filtered[y * (size * 4 + 1)] = 0;
    bkgRows[y].copy(filtered, y * (size * 4 + 1) + 1);
  }

  const png = Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr),
    chunk("IDAT", deflateSync(filtered, { level: 9 })),
    chunk("IEND", Buffer.alloc(0)),
  ]);
  return png;
}

mkdirSync(OUT_DIR, { recursive: true });
for (const size of [192, 512]) {
  const png = renderIcon(size);
  const outPath = join(OUT_DIR, `icon-${size}.png`);
  writeFileSync(outPath, png);
  console.log(`Wrote ${outPath} (${png.length} bytes)`);
}