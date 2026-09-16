#!/usr/bin/env node
/**
 * Zero-dependency WCAG 2.1 AA/AAA contrast calculator.
 * Usage: node wcag-check.js "#ffffff" "#000000"
 */

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

const [,, c1, c2] = process.argv;
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
