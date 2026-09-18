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

if (args[0].endsWith('.json') || fs.existsSync(args[0])) {
  const content = JSON.parse(fs.readFileSync(args[0], 'utf-8'));
  const colors = content.color || {};
  const surface = colors.surface?.$value || colors.background?.$value || '#ffffff';
  const targetLevel = args.includes('--level') ? args[args.indexOf('--level') + 1] : 'AA';
  const threshold = targetLevel === 'AAA' ? 7.0 : 4.5;
  const results = [];
  let allPass = true;

  for (const [name, def] of Object.entries(colors)) {
    if (name === 'surface' || name === 'background') continue;
    const val = def.$value;
    if (typeof val === 'string' && val.startsWith('#')) {
      const ratio = getContrast(val, surface);
      const pass = ratio >= threshold;
      if (!pass) allPass = false;
      results.push({ token: name, value: val, surface, ratio: Number(ratio.toFixed(2)), pass });
    }
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
