#!/usr/bin/env node
/**
 * Deterministic craft & accessibility pre-check for spec-prototype.
 * Runs four static checks (reduced-motion, narrow media query, overlay inert
 * isolation, chart scale/gridlines). It is NOT a design-quality or Grade
 * verdict and must not be reported as one.
 * Exits with code 0 when all four checks pass, code 1 otherwise.
 */
import fs from "node:fs";
import path from "node:path";

const targetHtml = process.argv[2] || "index.html";
if (!fs.existsSync(targetHtml)) {
  console.error(`Target HTML not found: ${targetHtml}`);
  process.exit(1);
}

const htmlDir = path.dirname(path.resolve(targetHtml));
const htmlContent = fs.readFileSync(targetHtml, "utf-8");

// Discover associated CSS and JS files
const cssFiles = [];
const cssMatches = htmlContent.matchAll(/href=["']([^"']+\.css)["']/g);
for (const match of cssMatches) {
  const cssPath = path.resolve(htmlDir, match[1]);
  if (fs.existsSync(cssPath)) cssFiles.push(fs.readFileSync(cssPath, "utf-8"));
}

const jsFiles = [];
const jsMatches = htmlContent.matchAll(/src=["']([^"']+\.js)["']/g);
for (const match of jsMatches) {
  const jsPath = path.resolve(htmlDir, match[1]);
  if (fs.existsSync(jsPath)) jsFiles.push(fs.readFileSync(jsPath, "utf-8"));
}

const allCss = cssFiles.join("\n");
const allJs = jsFiles.join("\n");

const deltas = [];

// 1. Accessibility: Reduced-Motion Equivalence
if (!allCss.includes("prefers-reduced-motion")) {
  deltas.push("CSS missing '@media (prefers-reduced-motion)' block for motion reduction.");
}

// 2. Responsiveness: Narrow Viewport Stacking
if (!allCss.includes("@media") || !allCss.includes("max-width")) {
  deltas.push("CSS missing responsive '@media (max-width: ...)' queries for narrow viewports (390px).");
}

// 3. Modal / Overlay: Inert Focus Isolation
const hasModalOrDrawer = htmlContent.includes("modal") || htmlContent.includes("drawer") || htmlContent.includes("dialog");
if (hasModalOrDrawer && !htmlContent.includes("inert") && !allJs.includes("inert")) {
  deltas.push("Interactive overlay detected, but neither HTML nor JS applies 'inert' focus isolation to background.");
}

// 4. Anti-Toy Craft: SVG Sparklines must carry scale / gridlines
if (htmlContent.includes("<svg") && (htmlContent.includes("sparkline") || htmlContent.includes("timeline"))) {
  const hasGridOrAxis = htmlContent.includes("grid-line") || htmlContent.includes("axis") || allCss.includes("grid-line");
  if (!hasGridOrAxis) {
    deltas.push("SVG timeline/sparkline detected without scale benchmarks or reference gridlines.");
  }
}

if (deltas.length > 0) {
  console.error("❌ Deterministic craft/accessibility checks failed:");
  for (const delta of deltas) {
    console.error(`  - ${delta}`);
  }
  process.exit(1);
} else {
  console.log("✓ Deterministic craft/accessibility checks passed (4/4: reduced-motion, narrow media query, overlay inert isolation, chart scale/gridlines).");
  console.log("  Mechanical check only — this is not a design-quality, accessibility-conformance, or Grade 4 (A+) verdict.");
  process.exit(0);
}
