#!/usr/bin/env node
// verify.mjs — the one-command verification loop for spec-prototype.
//
//   node verify.mjs <url> --out <evidence-dir> --artifact <html-file>
//     [--viewports 320,390,768,1280] [--states ideal,error,skeleton]
//     [--records truth.md,world.md,briefs/<slice>.md] [--portal] [--turn 2|3] [--root <repo-root>]
//
// One invocation = one bounded verification trip: capture -> detect -> optional
// divergence presence check -> portal sync -> per-turn budget circuit breaker.
// The execution-boundary hook admits this as a single installed helper; the
// sub-steps never pass through the hook.
//
// Budgets (deliberately visible, matching stage-3/stage-4 discipline):
//   turn 2 (Make):  2 verify trips, 2 detect runs each
//   turn 3 (Look):  2 inspection rounds
// Exceeding the budget exits 42 with BUDGET_EXCEEDED: record the residue as
// PARTIAL and stop instead of opening another round.
//
// Detect missing or unreadable artifacts is recorded, never fatal. Capture
// failure is fatal only when capture itself fails.

import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SKILL_ROOT = path.resolve(__dirname, "..");

const BUDGETS = { 2: 2, 3: 2 };

function parseArgs(argv) {
  const opts = {
    url: null, out: null, artifact: null, portal: false, turn: null,
    viewports: "390,1280", states: "ideal", records: null,
    root: process.cwd(),
  };
  const rest = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) { if (!opts.url) opts.url = a; else rest.push(a); continue; }
    const key = a.slice(2);
    const next = () => { const v = argv[++i]; if (v === undefined) throw new Error(`--${key} needs a value`); return v; };
    switch (key) {
      case "out": opts.out = next(); break;
      case "artifact": opts.artifact = next(); break;
      case "viewports": opts.viewports = next(); break;
      case "states": opts.states = next(); break;
      case "records": opts.records = next(); break;
      case "turn": opts.turn = Number(next()); break;
      case "root": opts.root = next(); break;
      case "portal": opts.portal = true; break;
      default: throw new Error(`unknown flag --${key}`);
    }
  }
  if (!opts.url || !opts.out) {
    throw new Error("usage: node verify.mjs <url> --out <evidence-dir> [--artifact <file>] [--records a,b] [--portal] [--turn 2|3]");
  }
  return opts;
}

function run(cmd, args, label) {
  const started = Date.now();
  try {
    const stdout = execFileSync(cmd, args, { encoding: "utf-8", cwd: process.cwd(), maxBuffer: 64 * 1024 * 1024 });
    return { ok: true, stdout, ms: Date.now() - started };
  } catch (err) {
    return { ok: false, stdout: err.stdout?.toString() || "", stderr: err.stderr?.toString() || String(err), status: err.status ?? 1, ms: Date.now() - started };
  }
}

function budgetCheck(turn, outDir) {
  if (!turn || !BUDGETS[turn]) return { status: "unbudgeted" };
  const counter = path.join(outDir, ".verify-count");
  fs.mkdirSync(outDir, { recursive: true });
  let counts = {};
  if (fs.existsSync(counter)) {
    try { counts = JSON.parse(fs.readFileSync(counter, "utf-8")); } catch { counts = {}; }
  }
  const n = (counts[String(turn)] || 0) + 1;
  counts[String(turn)] = n;
  fs.writeFileSync(counter, JSON.stringify(counts));
  const budget = BUDGETS[turn];
  return n <= budget
    ? { status: "within", trip: n, budget }
    : { status: "exceeded", trip: n, budget };
}

function main() {
  const opts = parseArgs(process.argv.slice(2));
  const report = { verify: { turn: opts.turn ?? null, started_at: new Date().toISOString() } };

  // 1. capture
  const capArgs = [path.join(__dirname, "capture.mjs"), opts.url, "--output", opts.out,
    "--viewports", opts.viewports, "--states", opts.states];
  const cap = run(process.execPath, capArgs, "capture");
  fs.mkdirSync(opts.out, { recursive: true });
  fs.writeFileSync(path.join(opts.out, "verify-capture.json"), cap.stdout || "{}");
  let diagnostics = null;
  if (cap.ok) {
    try { diagnostics = JSON.parse(cap.stdout).diagnostics_summary ?? null; } catch { /* keep raw */ }
  } else {
    report.verify.capture_failed = cap.stderr || `exit ${cap.status}`;
  }
  report.capture = diagnostics ? { diagnostics_summary: diagnostics } : { raw_saved: "verify-capture.json", failed: !cap.ok };

  // 2. detect (best effort)
  if (opts.artifact) {
    const det = run(process.execPath, [path.join(__dirname, "detect.py"), "--artifact", opts.artifact], "detect");
    if (det.ok) {
      try {
        const parsed = JSON.parse(det.stdout);
        const hits = (parsed.findings || []).filter((f) => f.status === "hit").map((f) => f.rule);
        const prose = (parsed.unchecked || []).map((u) => u.rule);
        report.detect = { checked: parsed.checked, hits, prose_only_owed: prose };
      } catch { report.detect = { unparseable: true }; }
    } else {
      report.detect = { error: det.stderr || `exit ${det.status}` };
    }
  }

  // 3. divergence presence (soft — missing structure is a warning, never a gate)
  if (opts.records) {
    const divArgs = [path.join(__dirname, "check_divergence.py"), "--records", opts.records];
    const div = run(process.execPath, divArgs, "divergence");
    if (div.ok) {
      try { report.divergence = JSON.parse(div.stdout); } catch { report.divergence = { unparseable: true }; }
    } else {
      report.divergence = { error: div.stderr || `exit ${div.status}` };
    }
  }

  // 4. portal sync (canonical path only)
  if (opts.portal) {
    const por = run(process.execPath, [path.join(__dirname, "generate_review_portal.py"), "--root", opts.root], "portal");
    report.portal = por.ok ? { synced: "prototype/review-portal.html" } : { error: por.stderr || `exit ${por.status}` };
  }

  // 5. budget circuit breaker
  const budget = budgetCheck(opts.turn, opts.out);
  report.budget = budget;

  console.log(JSON.stringify(report, null, 2));

  if (budget.status === "exceeded") {
    console.error(`BUDGET_EXCEEDED: turn ${opts.turn} has used ${budget.trip} of ${budget.budget} verification trips. Record the residue as PARTIAL and stop; do not open another inspection round.`);
    process.exit(42);
  }
  if (!cap.ok) process.exit(1);
}

main();
