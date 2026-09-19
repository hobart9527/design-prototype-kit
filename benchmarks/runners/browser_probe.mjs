#!/usr/bin/env node
// Zero-dependency headless browser probe over the Chrome DevTools Protocol.
// Used by the task runner and the visual manifest. It never uses a CSS selector
// authored for one specific prototype: targets are matched by role/name/text.
//
// Usage:
//   node browser_probe.mjs snapshot  --url <url> --viewport 1280 [--out dir]
//   node browser_probe.mjs click     --url <url> --viewport 1280 --match "排空"
//   node browser_probe.mjs screenshot --url <url> --viewport 390 --outshots <dir>
//   node browser_probe.mjs session   --url <url> --viewport 1280
//     session mode keeps one page alive and reads JSON commands on stdin, one
//     per line: {"cmd":"snapshot"} {"cmd":"click","match":"..."}
//     {"cmd":"scroll","dy":600} {"cmd":"screenshot","file":"..."} {"cmd":"quit"}
// Prints one JSON object on stdout.

import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";

const CHROME_CANDIDATES = [
  process.env.BENCH_CHROME,
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  "/Applications/Chromium.app/Contents/MacOS/Chromium",
  "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
  "/usr/bin/google-chrome",
].filter(Boolean);

function chromePath() {
  for (const candidate of CHROME_CANDIDATES) {
    if (fs.existsSync(candidate)) return candidate;
  }
  throw new Error("no Chrome/Chromium binary found (set BENCH_CHROME)");
}

function parseArgs(argv) {
  const args = { _command: argv[0] };
  for (let i = 1; i < argv.length; i += 2) args[argv[i].replace(/^--/, "")] = argv[i + 1];
  return args;
}

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

async function launch(profileDir) {
  fs.mkdirSync(profileDir, { recursive: true });
  const child = spawn(chromePath(), [
    "--headless=new", "--disable-gpu", "--no-first-run", "--no-default-browser-check",
    "--remote-debugging-port=0", `--user-data-dir=${profileDir}`,
    "--window-size=1600,1000", "about:blank",
  ], { stdio: ["ignore", "pipe", "pipe"] });

  const port = await new Promise((resolve, reject) => {
    let buffer = "";
    const timer = setTimeout(() => reject(new Error("chrome devtools port timeout")), 30000);
    child.stderr.on("data", (chunk) => {
      buffer += chunk.toString();
      const match = buffer.match(/DevTools listening on ws:\/\/127\.0\.0\.1:(\d+)/);
      if (match) { clearTimeout(timer); resolve(match[1]); }
    });
    child.on("exit", (code) => { clearTimeout(timer); reject(new Error(`chrome exited early: ${code}`)); });
  });
  return { child, port };
}

class CDP {
  constructor(ws) { this.ws = ws; this.id = 0; this.pending = new Map(); }
  static async connect(port) {
    const res = await fetch(`http://127.0.0.1:${port}/json/new?about:blank`, { method: "PUT" });
    const target = await res.json();
    const ws = new WebSocket(target.webSocketDebuggerUrl);
    await new Promise((resolve, reject) => { ws.onopen = resolve; ws.onerror = reject; });
    const cdp = new CDP(ws);
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      const entry = cdp.pending.get(msg.id);
      if (entry) { cdp.pending.delete(msg.id); entry(msg); }
    };
    return cdp;
  }
  send(method, params = {}) {
    const id = ++this.id;
    return new Promise((resolve) => {
      this.pending.set(id, resolve);
      this.ws.send(JSON.stringify({ id, method, params }));
    });
  }
  async evaluate(expression) {
    const out = await this.send("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (out.error) throw new Error(out.error.message);
    if (out.result?.exceptionDetails) throw new Error(out.result.exceptionDetails.text);
    return out.result?.result?.value;
  }
}

const SNAPSHOT_JS = `(() => {
  const visible = (el) => {
    const rect = el.getBoundingClientRect();
    const style = getComputedStyle(el);
    return rect.width > 0 && rect.height > 0 && style.visibility !== "hidden" && style.display !== "none" && style.opacity !== "0";
  };
  const nameOf = (el) => (el.getAttribute("aria-label") || el.getAttribute("title") || el.innerText || el.value || "").trim().replace(/\\s+/g, " ").slice(0, 90);
  const roleOf = (el) => el.getAttribute("role") || ({BUTTON:"button", A:"link", INPUT:"textbox", SELECT:"combobox", TEXTAREA:"textbox", DETAILS:"group", SUMMARY:"button"}[el.tagName] || el.tagName.toLowerCase());
  const controls = [];
  for (const el of document.querySelectorAll("button, a, input, select, textarea, [role=button], [role=tab], [role=menuitem], [data-action]")) {
    if (!visible(el)) continue;
    controls.push({ index: controls.length, role: roleOf(el), name: nameOf(el), tag: el.tagName.toLowerCase(), actions: el.getAttribute("data-action") || "" });
    el.setAttribute("data-bench-index", String(controls.length - 1));
    if (controls.length >= 120) break;
  }
  const smallTargets = controls.filter((c, i) => {
    const el = document.querySelector('[data-bench-index="' + i + '"]');
    if (!el) return false;
    const rect = el.getBoundingClientRect();
    return rect.width < 44 || rect.height < 44;
  }).map((c) => c.name);
  const surface = document.querySelector("main") || document.body;
  return {
    title: document.title,
    text: (document.body.innerText || "").replace(/\\n{3,}/g, "\\n\\n").slice(0, 12000),
    controls,
    dialogs: document.querySelectorAll('[role=dialog], dialog[open], [aria-modal=true]').length,
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
    bodyTextLength: (surface.innerText || "").length,
    smallTargetCount: smallTargets.length,
    smallTargets: smallTargets.slice(0, 10),
    interactiveCount: controls.length,
  };
})()`;

const CLICK_JS = (match) => `(() => {
  const needle = ${JSON.stringify(match)};
  const candidates = [...document.querySelectorAll('[data-bench-index]')];
  const scored = [];
  for (const el of candidates) {
    const name = (el.getAttribute("aria-label") || el.innerText || el.value || "").trim();
    if (!name) continue;
    if (name === needle) scored.push({ el, score: 3 });
    else if (name.includes(needle)) scored.push({ el, score: 2 });
    else if (needle.includes(name.slice(0, 6))) scored.push({ el, score: 1 });
  }
  if (!scored.length) return { clicked: null, reason: "no control matched: " + needle };
  scored.sort((a, b) => b.score - a.score);
  const el = scored[0].el;
  el.scrollIntoView({ block: "center" });
  el.click();
  return { clicked: (el.getAttribute("aria-label") || el.innerText || "").trim().slice(0, 90), tag: el.tagName.toLowerCase() };
})()`;

async function withPage(viewport, url, fn) {
  const width = Number(String(viewport).split("x")[0]);
  const height = Number(String(viewport).split("x")[1] || 900);
  const profile = fs.mkdtempSync("/tmp/bench-chrome-");
  const { child, port } = await launch(profile);
  try {
    const cdp = await CDP.connect(port);
    await cdp.send("Page.enable");
    await cdp.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width <= 500 });
    await cdp.send("Page.navigate", { url });
    await sleep(1800);
    return await fn(cdp, { width, height });
  } finally {
    child.kill("SIGKILL");
  }
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const url = args.url;
  const viewport = args.viewport || "1280x900";
  if (!url) throw new Error("--url is required");
  if (args._command === "session") return sessionMain(url, viewport);
  const out = await withPage(viewport, url, async (cdp) => {
    if (args._command === "click") {
      const before = await cdp.evaluate(SNAPSHOT_JS);
      const click = await cdp.evaluate(CLICK_JS(args.match || ""));
      await sleep(900);
      const after = await cdp.evaluate(SNAPSHOT_JS);
      return { action: "click", match: args.match, click, before, after };
    }
    if (args._command === "screenshot") {
      const dir = args.outshots || ".";
      fs.mkdirSync(dir, { recursive: true });
      const shot = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
      const file = path.join(dir, `shot-${String(viewport).replace("x", "-")}.png`);
      fs.writeFileSync(file, Buffer.from(shot.result.data, "base64"));
      return { action: "screenshot", file, bytes: fs.statSync(file).size };
    }
    return { action: "snapshot", snapshot: await cdp.evaluate(SNAPSHOT_JS) };
  });
  process.stdout.write(JSON.stringify(out));
}

async function sessionMain(url, viewport) {
  const width = Number(String(viewport).split("x")[0]);
  const height = Number(String(viewport).split("x")[1] || 900);
  const { child, port } = await launch(fs.mkdtempSync("/tmp/bench-chrome-"));
  const cdp = await CDP.connect(port);
  await cdp.send("Page.enable");
  await cdp.send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width <= 500 });
  await cdp.send("Page.navigate", { url });
  await sleep(1800);
  const rl = readline.createInterface({ input: process.stdin });
  for await (const line of rl) {
    if (!line.trim()) continue;
    let response;
    try {
      const cmd = JSON.parse(line);
      if (cmd.cmd === "snapshot") {
        response = { snapshot: await cdp.evaluate(SNAPSHOT_JS) };
      } else if (cmd.cmd === "click") {
        const click = await cdp.evaluate(CLICK_JS(cmd.match || ""));
        await sleep(900);
        response = { click, snapshot: await cdp.evaluate(SNAPSHOT_JS) };
      } else if (cmd.cmd === "scroll") {
        await cdp.evaluate(`window.scrollBy(0, ${Number(cmd.dy) || 600}); null`);
        await sleep(500);
        response = { scroll: true, snapshot: await cdp.evaluate(SNAPSHOT_JS) };
      } else if (cmd.cmd === "screenshot") {
        const shot = await cdp.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
        fs.mkdirSync(path.dirname(cmd.file), { recursive: true });
        fs.writeFileSync(cmd.file, Buffer.from(shot.result.data, "base64"));
        response = { file: cmd.file, bytes: fs.statSync(cmd.file).size };
      } else if (cmd.cmd === "quit") {
        process.stdout.write(JSON.stringify({ bye: true }) + "\n");
        break;
      } else {
        response = { error: `unknown cmd: ${cmd.cmd}` };
      }
    } catch (error) {
      response = { error: String(error && error.message || error) };
    }
    process.stdout.write(JSON.stringify(response) + "\n");
  }
  child.kill("SIGKILL");
}

main().catch((error) => {
  process.stdout.write(JSON.stringify({ error: String(error && error.message || error) }));
  process.exitCode = 1;
});
