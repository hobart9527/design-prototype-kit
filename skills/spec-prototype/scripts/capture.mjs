#!/usr/bin/env node
// Headless multi-viewport and multi-state screenshot capture for spec-prototype evidence.
// Uses local Playwright/Puppeteer or system Chrome/Edge. Zero extra dependencies.
//
// Usage: node capture.mjs <url> --output <dir> [--viewports 320,390,768,1280] [--states ideal,error,skeleton]

import fs from "node:fs";
import path from "node:path";
import { execFileSync, spawnSync } from "node:child_process";

const VIEWPORT_PRESETS = {
  "320": { width: 320, height: 640 },
  "390": { width: 390, height: 844 },
  "768": { width: 768, height: 1024 },
  "1280": { width: 1280, height: 800 },
};

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

async function captureWithPlaywright(baseUrl, outputDir, viewports, states) {
  try {
    const { chromium } = await import("playwright");
    const browser = await chromium.launch({ headless: true });
    const captured = {};
    for (const state of states) {
      const stateUrl = buildStateUrl(baseUrl, state);
      for (const vp of viewports) {
        const dim = VIEWPORT_PRESETS[vp] || { width: parseInt(vp, 10) || 1280, height: 800 };
        const page = await browser.newPage({ viewport: dim });
        await page.goto(stateUrl, { waitUntil: "networkidle", timeout: 15000 });
        const prefix = states.length > 1 ? `${state}-${vp}` : `${vp}`;
        const targetFile = path.join(outputDir, `${prefix}.png`);
        await page.screenshot({ path: targetFile, fullPage: false });
        if (states.length > 1 && (state === "ideal" || state === states[0])) {
          const defaultTarget = path.join(outputDir, `${vp}.png`);
          if (!fs.existsSync(defaultTarget)) {
            try { fs.copyFileSync(targetFile, defaultTarget); } catch {}
          }
        }
        await page.close();
        captured[prefix] = targetFile;
      }
    }
    await browser.close();
    const vps = {}; for (const [k, v] of Object.entries(captured)) { const vp = k.split("-").pop(); if (!vps[vp]) vps[vp] = v; }
    return { status: "captured", runner: "playwright", viewports: vps, captures: captured };
  } catch {
    return null;
  }
}

function captureWithCli(browserBin, baseUrl, outputDir, viewports, states) {
  const captured = {};
  for (const state of states) {
    const stateUrl = buildStateUrl(baseUrl, state);
    for (const vp of viewports) {
      const dim = VIEWPORT_PRESETS[vp] || { width: parseInt(vp, 10) || 1280, height: 800 };
      const prefix = states.length > 1 ? `${state}-${vp}` : `${vp}`;
      const targetFile = path.join(outputDir, `${prefix}.png`);
      try {
        execFileSync(
          browserBin,
          [
            "--headless",
            "--disable-gpu",
            `--window-size=${dim.width},${dim.height}`,
            `--screenshot=${targetFile}`,
            stateUrl,
          ],
          { timeout: 15000, stdio: "ignore" }
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
        // continue with remaining viewports/states
      }
    }
  }
  if (Object.keys(captured).length > 0) {
    const vps = {}; for (const [k, v] of Object.entries(captured)) { const vp = k.split("-").pop(); if (!vps[vp]) vps[vp] = v; }
    return { status: "captured", runner: "system-browser-cli", viewports: vps, captures: captured };
  }
  return null;
}

async function main() {
  const args = process.argv.slice(2);
  let url = null;
  let outputDir = null;
  let viewports = ["320", "390", "1280"];
  let states = ["default"];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--output" || args[i] === "-o") {
      outputDir = args[++i];
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
      result = captureWithCli(browserBin, url, outputDir, viewports, states);
    }
  }

  if (result) {
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
