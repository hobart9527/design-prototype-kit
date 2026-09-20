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

// ---- Revision-specific evidence binding (pure seam) ----------------------
// Binds captured pixels to the environment, target and dependency identity that
// produced them. Native-platform validation is never inferred from the runner,
// the requested viewport list or a target-platform label: only an actual run on
// that platform may claim it.

const BROWSER_EXECUTION_BY_RUNNER = {
  "playwright-concurrent": "html-browser",
  "system-browser-cli-concurrent": "html-browser",
};

function normalizeDependencies(dependencies) {
  return (Array.isArray(dependencies) ? dependencies : [])
    .map((entry) => (typeof entry === "string" ? { ref: entry, digest: null } : entry || {}))
    .filter((entry) => typeof entry.ref === "string" && entry.ref.length > 0)
    .map((entry) => ({ ref: entry.ref, digest: entry.digest == null ? null : String(entry.digest) }))
    .sort((a, b) => (a.ref < b.ref ? -1 : a.ref > b.ref ? 1 : 0));
}

export function buildCaptureMetadata(result, options = {}) {
  const capture = result && typeof result === "object" ? result : {};
  const {
    targetPath = null,
    targetUri = null,
    targetPlatform = "web",
    runtime = "unknown",
    sourceRevision = "unversioned",
    dependencies = [],
  } = options;

  const captures = capture.captures || {};
  const failures = Array.isArray(capture.failures) ? capture.failures : [];
  const runtimeErrors = Array.isArray(capture.runtime_errors) ? capture.runtime_errors : [];
  const screenshotCount = Object.keys(captures).length;
  const browserExecution = BROWSER_EXECUTION_BY_RUNNER[capture.runner] || "unavailable";
  const status = typeof capture.status === "string" ? capture.status : "browser_unavailable";
  const captured = status === "captured" && screenshotCount > 0;

  let evidenceKind;
  if (screenshotCount === 0) evidenceKind = "none";
  else if (captured && runtimeErrors.length === 0 && failures.length === 0) evidenceKind = "rendered";
  else evidenceKind = "screenshot-only";

  const depList = normalizeDependencies(dependencies);
  const dependencySignature = depList.map((d) => `${d.ref}=${d.digest ?? "-"}`).join(",");
  const identity = [
    `target:${targetPath ?? targetUri ?? "unknown"}`,
    `source:${sourceRevision}`,
    `deps:${dependencySignature}`,
  ].join("|");

  return {
    schema: "loom.capture-metadata.v1",
    status,
    identity,
    environment: {
      runtime,
      browser_execution: browserExecution,
      runner: capture.runner || null,
    },
    target: { platform: targetPlatform, path: targetPath, uri: targetUri },
    source: { revision: sourceRevision },
    evidence: {
      kind: evidenceKind,
      screenshots: screenshotCount,
      paths: Object.values(captures),
      runtime_errors: runtimeErrors,
      failures,
    },
    validation: {
      kind: "renderer_capture",
      claim: captured ? "renderer_screenshots_pending_review" : "capture_failed",
      // Hard-coded false: a browser render can never be native-platform validation.
      native_platform_validation: false,
      human: "pending_review",
      visual: "pending_review",
    },
    dependencies: depList,
  };
}

export function mergeVerification(previous, metadata) {
  const prev = previous && typeof previous === "object" ? previous : {};
  // Inherited human/visual status survives only while the bound identity is
  // unchanged; any target, source or dependency change resets it to pending.
  const sameIdentity = typeof prev.identity === "string" && prev.identity === metadata.identity;
  const carried = (field) => (sameIdentity ? prev[field] || "pending_review" : "pending_review");
  const vpKeys = Object.keys(metadata.environment ? metadata.environment.viewports || {} : {});
  return {
    status: "captured_pending_review",
    renderer: "captured",
    browser: "captured",
    visual: carried("visual"),
    human: carried("human"),
    identity: metadata.identity,
    identity_changed: !sameIdentity,
    evidence: `Capture ${metadata.status} (${metadata.evidence.kind}; ${metadata.evidence.screenshots} screenshot(s)${
      vpKeys.length > 0 ? `, ${vpKeys.join(", ")}px` : ""
    }) on ${metadata.environment.browser_execution}/${metadata.environment.runtime}; pending visual & experience critique`,
    timestamp: new Date().toISOString(),
    runner: metadata.environment.runner || "browser-capture",
    metadata,
  };
}

// The script may live anywhere; evidence is written only into a repository that
// actually carries the spec-prototype Skill, never into whatever tree happens to
// contain this file.
export function resolveEvidenceRoot(explicit) {
  const primary = typeof explicit === "string" && explicit.length > 0 ? explicit : null;
  // An explicit root is authoritative: if it is not a spec-prototype repository we
  // refuse rather than silently writing into the current working tree.
  const candidates = primary ? [primary] : [process.env.LOOM_REPO_ROOT, process.cwd()];
  for (const candidate of candidates) {
    if (typeof candidate !== "string" || candidate.length === 0) continue;
    const abs = path.resolve(candidate);
    if (fs.existsSync(path.join(abs, "skills", "spec-prototype"))) return abs;
  }
  return null;
}

function recordHandoffEvidence(outputDir, result, metadata, options = {}) {
  try {
    const repoRoot = resolveEvidenceRoot(options.repoRoot);
    if (!repoRoot) return { written: false, reason: "no_repository_root" };
    const manifestPath = path.join(repoRoot, "prototype/evidence/handoff-manifest.json");
    if (!fs.existsSync(path.dirname(manifestPath))) {
      fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
    }
    let existing = {};
    if (fs.existsSync(manifestPath)) {
      try {
        existing = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
      } catch {}
    }
    existing.verification = mergeVerification(existing.verification, metadata);
    fs.writeFileSync(manifestPath, JSON.stringify(existing, null, 2), "utf-8");
    return { written: true, path: manifestPath };
  } catch (error) {
    // best-effort evidence recording
    return { written: false, reason: error instanceof Error ? error.message : String(error) };
  }
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
  let targetPath = null;
  let targetPlatform = "web";
  let runtime = "unknown";
  let sourceRevision = "unversioned";
  let repoRoot = null;
  const dependencies = [];

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--no-open") {
      autoOpen = false;
    } else if (args[i] === "--open") {
      autoOpen = true;
    } else if (args[i] === "--target-path") {
      targetPath = args[++i] || null;
    } else if (args[i] === "--target-platform") {
      targetPlatform = args[++i] || "web";
    } else if (args[i] === "--runtime") {
      runtime = args[++i] || "unknown";
    } else if (args[i] === "--source-revision") {
      sourceRevision = args[++i] || "unversioned";
    } else if (args[i] === "--dep") {
      const raw = args[++i] || "";
      const eq = raw.indexOf("=");
      if (eq > 0) dependencies.push({ ref: raw.slice(0, eq), digest: raw.slice(eq + 1) });
      else if (raw) dependencies.push({ ref: raw, digest: null });
    } else if (args[i] === "--repo-root") {
      repoRoot = args[++i] || null;
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

  const metadataOptions = {
    targetPath,
    targetUri: url,
    targetPlatform,
    runtime,
    sourceRevision,
    dependencies,
    repoRoot,
  };

  if (result) {
    const metadata = buildCaptureMetadata(result, metadataOptions);
    const recording = recordHandoffEvidence(outputDir, result, metadata, { repoRoot });
    syncReviewPortal(autoOpen);
    process.stdout.write(JSON.stringify({ ...result, metadata, evidence_record: recording }, null, 2) + "\n");
    process.exit(0);
  } else {
    // A failed capture is a result, not silence: emit explicit metadata and never
    // record it as usable evidence.
    const failure = {
      status: "browser_unavailable",
      reason: "No browser runner found (Playwright package or system Chrome/Chromium/Edge)",
      metadata: buildCaptureMetadata({ status: "browser_unavailable" }, metadataOptions),
    };
    process.stdout.write(JSON.stringify(failure, null, 2) + "\n");
    process.exit(2);
  }
}

// Importable seam: the module is inert unless executed directly (`node capture.mjs`).
if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(fileURLToPath(import.meta.url))) {
  main();
}
