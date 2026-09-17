#!/usr/bin/env node
// Headless multi-viewport and multi-state screenshot capture for spec-prototype evidence.
// Uses local Playwright/Puppeteer or system Chrome/Edge. Zero extra dependencies.
//
// Usage: node capture.mjs <url> --output <dir> [--viewports 320,390,768,1280] [--states ideal,error,skeleton]

import fs from "node:fs";
import path from "node:path";
import { execFile, execFileSync, spawnSync } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

const pExecFile = promisify(execFile);
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const VIEWPORT_PRESETS = {
  "320": { width: 320, height: 640 },
  "390": { width: 390, height: 844 },
  "768": { width: 768, height: 1024 },
  "1280": { width: 1280, height: 800 },
};

async function mapConcurrent(items, concurrency, fn) {
  const results = [];
  let index = 0;
  async function worker() {
    while (index < items.length) {
      const i = index++;
      results[i] = await fn(items[i], i);
    }
  }
  const workers = Array.from({ length: Math.min(concurrency, items.length) }, () => worker());
  await Promise.all(workers);
  return results;
}

function findSystemBrowser() {
  const candidates = [
    // macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    // Linux
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/usr/bin/microsoft-edge",
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  // Try PATH
  for (const bin of ["google-chrome", "chromium", "chromium-browser", "msedge"]) {
    const res = spawnSync("which", [bin], { encoding: "utf-8" });
    if (res.status === 0 && res.stdout.trim()) {
      return res.stdout.trim();
    }
  }
  return null;
}

function buildStateUrl(baseUrl, state) {
  if (!state || state === "default") return baseUrl;
  const hashIdx = baseUrl.indexOf("#");
  if (hashIdx !== -1) {
    return baseUrl.slice(0, hashIdx) + `#state=${state}`;
  }
  return baseUrl + `#state=${state}`;
}

async function captureWithPlaywright(baseUrl, outputDir, viewports, states, concurrency = 4) {
  try {
    const { chromium } = await import("playwright");
    const browser = await chromium.launch({ headless: true });
    const captured = {};
    const failures = [];
    const runtimeErrors = [];

    const tasks = [];
    for (const state of states) {
      const stateUrl = buildStateUrl(baseUrl, state);
      for (const vp of viewports) {
        const prefix = states.length > 1 ? `${state}-${vp}` : `${vp}`;
        const targetFile = path.join(outputDir, `${prefix}.png`);
        const dim = VIEWPORT_PRESETS[vp] || { width: parseInt(vp, 10) || 1280, height: 800 };
        tasks.push({ state, vp, prefix, targetFile, dim, stateUrl });
      }
    }

    await mapConcurrent(tasks, concurrency, async ({ state, vp, prefix, targetFile, dim, stateUrl }) => {
      try {
        const page = await browser.newPage({ viewport: dim });
        page.on("pageerror", (err) => runtimeErrors.push(`[${prefix}] ${err.message}`));
        await page.goto(stateUrl, { waitUntil: "networkidle", timeout: 15000 });
        await page.screenshot({ path: targetFile, fullPage: false });
        await page.close();
        if (states.length > 1 && (state === "ideal" || state === states[0])) {
          const defaultTarget = path.join(outputDir, `${vp}.png`);
          if (!fs.existsSync(defaultTarget)) fs.copyFileSync(targetFile, defaultTarget);
        }
        captured[prefix] = targetFile;
      } catch (error) {
        failures.push({ state, viewport: vp, error: error instanceof Error ? error.message : String(error) });
      }
    });

    await browser.close();
    const vps = {};
    for (const [k, v] of Object.entries(captured)) {
      const vp = k.split("-").pop();
      if (!vps[vp]) vps[vp] = v;
    }
    return {
      status: failures.length ? "capture_failed" : "captured",
      runner: "playwright-concurrent",
      viewports: vps,
      captures: captured,
      runtime_errors: runtimeErrors,
      failures,
    };
  } catch {
    return null;
  }
}

async function captureWithCli(browserBin, baseUrl, outputDir, viewports, states, concurrency = 4) {
  const captured = {};
  const tasks = [];

  for (const state of states) {
    const stateUrl = buildStateUrl(baseUrl, state);
    for (const vp of viewports) {
      const dim = VIEWPORT_PRESETS[vp] || { width: parseInt(vp, 10) || 1280, height: 800 };
      const prefix = states.length > 1 ? `${state}-${vp}` : `${vp}`;
      const targetFile = path.join(outputDir, `${prefix}.png`);
      tasks.push({ state, vp, dim, prefix, targetFile, stateUrl });
    }
  }

  await mapConcurrent(tasks, concurrency, async ({ state, vp, dim, prefix, targetFile, stateUrl }) => {
    try {
      await pExecFile(
        browserBin,
        [
          "--headless",
          "--disable-gpu",
          "--disable-extensions",
          "--no-first-run",
          "--no-default-browser-check",
          "--disable-background-networking",
          "--disable-sync",
          "--hide-scrollbars",
          "--mute-audio",
          `--window-size=${dim.width},${dim.height}`,
          `--screenshot=${targetFile}`,
          stateUrl,
        ],
        { timeout: 15000 }
      );
      if (fs.existsSync(targetFile)) {
        captured[prefix] = targetFile;
        if (states.length > 1 && (state === "ideal" || state === states[0])) {
          const defaultTarget = path.join(outputDir, `${vp}.png`);
          if (!fs.existsSync(defaultTarget)) {
            try { fs.copyFileSync(targetFile, defaultTarget); } catch {}
          }
        }
      }
    } catch {
      // continue with remaining tasks
    }
  });

  if (Object.keys(captured).length > 0) {
    const vps = {};
    for (const [k, v] of Object.entries(captured)) {
      const vp = k.split("-").pop();
      if (!vps[vp]) vps[vp] = v;
    }
    return { status: "captured", runner: "system-browser-cli-concurrent", viewports: vps, captures: captured };
  }
  return null;
}

function syncReviewPortal(autoOpen = true) {
  try {
    const portalScript = path.join(__dirname, "generate_review_portal.py");
    if (fs.existsSync(portalScript)) {
      const pArgs = [portalScript];
      if (autoOpen) pArgs.push("--open");
      execFileSync("python3", pArgs, { stdio: "ignore" });
    }
  } catch {}
}

async function main() {
  const args = process.argv.slice(2);
  let url = null;
  let outputDir = null;
  let viewports = ["320", "390", "1280"];
  let states = ["default"];
  let autoOpen = true;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--no-open") {
      autoOpen = false;
    } else if (args[i] === "--open") {
      autoOpen = true;
    } else if (args[i] === "--slice") {
      const sliceId = args[++i];
      const repoRoot = path.resolve(__dirname, "../../..");
      const candidatePaths = [
        path.join(repoRoot, `prototype/experiments/${sliceId}/anchor/index.html`),
        path.join(repoRoot, `prototype/experiments/${sliceId}/hero-anchor/index.html`),
        path.join(repoRoot, `prototype/surfaces/${sliceId}/index.html`),
      ];
      const matched = candidatePaths.find((p) => fs.existsSync(p)) || candidatePaths[0];
      url = `file://${matched}`;
      outputDir = path.join(repoRoot, `prototype/evidence/probes/${sliceId}/`);
      states = ["ideal", "empty", "error"];
      viewports = ["320", "390", "768", "1280"];
    } else if (args[i] === "--output" || args[i] === "-o") {
      outputDir = args[++i];
    } else if (args[i] === "--target" || args[i] === "-t") {
      url = args[++i];
    } else if (args[i] === "--viewports" || args[i] === "-v") {
      viewports = (args[++i] || "").split(",").map((s) => s.trim()).filter(Boolean);
    } else if (args[i] === "--states" || args[i] === "-s") {
      states = (args[++i] || "").split(",").map((s) => s.trim()).filter(Boolean);
    } else if (!url && !args[i].startsWith("-")) {
      url = args[i];
    }
  }

  if (!url || !outputDir) {
    process.stderr.write("Usage: node capture.mjs <url> --output <dir> [--viewports 320,390,1280] [--states ideal,error]\n");
    process.exit(1);
  }

  fs.mkdirSync(outputDir, { recursive: true });

  // 1. Try Playwright
  let result = await captureWithPlaywright(url, outputDir, viewports, states);

  // 2. Try System Browser CLI if Playwright unavailable
  if (!result) {
    const browserBin = findSystemBrowser();
    if (browserBin) {
      result = await captureWithCli(browserBin, url, outputDir, viewports, states);
    }
  }

  if (result) {
    syncReviewPortal(autoOpen);
    process.stdout.write(JSON.stringify(result, null, 2) + "\n");
    process.exit(0);
  } else {
    const failure = {
      status: "browser_unavailable",
      reason: "No browser runner found (Playwright package or system Chrome/Chromium/Edge)",
    };
    process.stdout.write(JSON.stringify(failure, null, 2) + "\n");
    process.exit(2);
  }
}

main();
