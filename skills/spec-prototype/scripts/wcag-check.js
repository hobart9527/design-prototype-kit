#!/usr/bin/env node
/**
 * contrast-preflight.js (Zero-dependency contrast ratio preflight calculator).
 *
 * NOTE: This is a static contrast preflight tool, NOT a complete automated WCAG audit.
 * Complete accessibility verification requires full semantic audit, keyboard operability,
 * screen reader landmark inspection, focus management, and touch target tests.
 *
 * Usage:
 *   node contrast-preflight.js "#ffffff" "#000000"
 *   node contrast-preflight.js tokens.json [--level AAA]
 */
const fs = require('fs');

function parseHex(hex) {
  let c = hex.replace(/^#/, '');
  if (c.length === 3) c = c.split('').map(x => x + x).join('');
  const num = parseInt(c, 16);
  return [(num >> 16) & 255, (num >> 8) & 255, num & 255];
}

function srgbToLinear(val) {
  const v = val / 255;
  return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
}

function getLuminance(hex) {
  const [r, g, b] = parseHex(hex).map(srgbToLinear);
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
}

function getContrast(hex1, hex2) {
  const l1 = getLuminance(hex1);
  const l2 = getLuminance(hex2);
  const brightest = Math.max(l1, l2);
  const darkest = Math.min(l1, l2);
  return (brightest + 0.05) / (darkest + 0.05);
}

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error("Usage:\n  node wcag-check.js <color1-hex> <color2-hex>\n  node wcag-check.js <tokens.json> [--level AAA]");
  process.exit(1);
}

/**
 * Resolve the color group across the two incompatible token schemas that write
 * the same repository path.
 *
 * - `compile_tokens.py` writes a flat top-level `color` group plus a 3-tier
 *   `primitives.color` mirror.
 * - `export-tokens.py` (CSS path) groups tokens by CSS custom-property prefix,
 *   so `--bg-void` becomes group `bg`, never `color`.
 *
 * Both are adapted explicitly. Neither is inferred: a schema this tool does not
 * recognize yields no colors, which is a failure below rather than a pass.
 */
function isHex(v) {
  return typeof v === 'string' && v.startsWith('#');
}

/**
 * Walk a token tree, adopting every `$value`-bearing leaf whose value is a hex
 * color. Literal hexes and DTCG aliases (`{primitives.color.surface.$value}`) are
 * both kept; alias resolution happens against the flattened name map.
 */
function walkColors(node, colors, path) {
  if (!node || typeof node !== 'object') return;
  const value = node.$value;
  if (typeof value === 'string' && (isHex(value) || value.startsWith('{'))) {
    const name = node.$type === 'color'
      ? (path.filter(seg => seg !== 'color').join('-') || path.join('-'))
      : path.join('-');
    if (name && !(name in colors)) colors[name] = node;
  }
  for (const [key, child] of Object.entries(node)) {
    if (key.startsWith('$')) continue;
    if (child && typeof child === 'object' && !Array.isArray(child)) {
      walkColors(child, colors, [...path, key]);
    }
  }
}

function collectColors(content) {
  const colors = {};
  if (!content || typeof content !== 'object') return colors;
  // `compile_tokens.py` owns a flat top-level `color` group; it is the effective
  // contrast target set (its 3-tier mirror aliases the same hexes). Prefer it.
  if (content.color && typeof content.color === 'object' && !Array.isArray(content.color)) {
    walkColors(content.color, colors, ['color']);
    return colors;
  }
  // Fallback for the CSS-prefix schema (`bg`, `text`, `accent`, `status`, …)
  // emitted by export-tokens.py. Non-color groups yield no hex leaf and are
  // simply not adopted.
  for (const [key, value] of Object.entries(content)) {
    if (key.startsWith('$')) continue;
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      walkColors(value, colors, [key]);
    }
  }
  return colors;
}

/** Follow one `{a.b.c.$value}` alias to the literal hex it points at, or null. */
function resolveAlias(value, colors, seen = new Set()) {
  if (typeof value !== 'string') return null;
  const m = /^\{(.+?)\}$/.exec(value.trim());
  if (!m || seen.has(value)) return null;
  seen.add(value);
  const parts = m[1].split('.').filter(p => p !== '$value' && p !== 'color');
  const candidate = colors[parts.join('-')];
  if (candidate && isHex(candidate.$value)) return candidate.$value;
  if (candidate && typeof candidate.$value === 'string') return resolveAlias(candidate.$value, colors, seen);
  return null;
}

/** The literal hex a token resolves to: itself, or its alias target. */
function tokenHex(def, colors) {
  if (isHex(def?.$value)) return def.$value;
  return resolveAlias(def?.$value, colors);
}

/** The backdrop every other color is measured against, or an explicit null. */
function resolveSurface(colors) {
  // `surface` is the compiled name in `color`; `bg` is the compiled name in the
  // 3-tier mirror. Both describe the same backdrop token, so pick the one that
  // actually resolves to a hex rather than merging distinct names.
  for (const name of ['surface', 'background', 'bg-base', 'bg-void', 'bg', 'canvas']) {
    const def = colors[name];
    if (!def) continue;
    const hex = tokenHex(def, colors);
    if (hex) return hex;
  }
  return null;
}

if (args[0].endsWith('.json') || fs.existsSync(args[0])) {
  const content = JSON.parse(fs.readFileSync(args[0], 'utf-8'));
  const colors = collectColors(content);
  const surface = resolveSurface(colors);
  const targetLevel = args.includes('--level') ? args[args.indexOf('--level') + 1] : 'AA';
  const threshold = targetLevel === 'AAA' ? 7.0 : 4.5;
  const results = [];
  let allPass = true;

  const SURFACE_NAMES = new Set(['surface', 'background', 'bg-base', 'bg-void', 'bg', 'canvas']);
  for (const [name, def] of Object.entries(colors)) {
    if (SURFACE_NAMES.has(name)) continue;
    const val = tokenHex(def, colors);
    if (!val || !surface) continue;
    const ratio = getContrast(val, surface);
    const pass = ratio >= threshold;
    if (!pass) allPass = false;
    results.push({ token: name, value: val, surface, ratio: Number(ratio.toFixed(2)), pass });
  }

  // "No colors to check" is not "passed accessibility". A token file this tool
  // cannot measure is refused (non-zero exit) so an empty or unfamiliar schema
  // can never masquerade as a WCAG AA/AAA pass.
  if (!surface || results.length === 0) {
    allPass = false;
    console.log(JSON.stringify({
      targetLevel,
      threshold,
      surface,
      allPass,
      results,
      error: surface
        ? 'No color tokens with a hex `$value` were found to contrast against the surface.'
        : 'No surface/background color token was found; contrast cannot be measured.',
    }, null, 2));
    process.exit(1);
  }

  console.log(JSON.stringify({ targetLevel, threshold, surface, allPass, results }, null, 2));
  process.exit(allPass ? 0 : 1);
}

const [c1, c2] = args;
if (!c1 || !c2) {
  console.error("Usage: node wcag-check.js <color1-hex> <color2-hex>");
  process.exit(1);
}

const ratio = getContrast(c1, c2);
const passAA = ratio >= 4.5;
const passAALarge = ratio >= 3.0;
const passAAA = ratio >= 7.0;

console.log(JSON.stringify({
  color1: c1,
  color2: c2,
  ratio: Number(ratio.toFixed(2)),
  passAA,
  passAALarge,
  passAAA
}, null, 2));
