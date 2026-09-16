#!/usr/bin/env node
// Read-only, product-neutral evidence gallery for spec-prototype artifacts.
// Usage: node preview.mjs <repository-root> [port] [--no-open]

import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const root = path.resolve(process.argv[2] || ".");
const requestedPort = Number(process.argv[3] || 0);
const protoRoot = path.join(root, "prototype");

const MIME = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".gif": "image/gif",
  ".ico": "image/x-icon",
  ".md": "text/plain; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
};

function safeJoin(base, relativePath) {
  const target = path.resolve(base, String(relativePath).replace(/^\/+/, ""));
  if (target !== base && !target.startsWith(base + path.sep)) return null;
  try {
    const realBase = fs.realpathSync(base);
    const realTarget = fs.realpathSync(target);
    if (realTarget !== realBase && !realTarget.startsWith(realBase + path.sep)) return null;
    return realTarget;
  } catch {
    return null;
  }
}

function* walk(directory, depth = 0) {
  if (depth > 8) return;
  let entries = [];
  try {
    entries = fs.readdirSync(directory, { withFileTypes: true });
  } catch {
    return;
  }
  for (const entry of entries) {
    if (entry.name.startsWith(".")) continue;
    const candidate = path.join(directory, entry.name);
    if (entry.isDirectory()) yield* walk(candidate, depth + 1);
    else yield candidate;
  }
}

function relativeToPrototype(file) {
  return path.relative(protoRoot, file).split(path.sep).join("/");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function collectArtifacts() {
  const entries = [];
  const shots = [];
  const seen = new Set();
  for (const file of walk(protoRoot)) {
    const relative = relativeToPrototype(file);
    if (/\.(png|jpg|jpeg|webp)$/i.test(file)) shots.push(relative);
    if (!file.endsWith("index.html")) continue;
    const directory = path.dirname(file);
    const key = relativeToPrototype(directory);
    if (seen.has(key)) continue;
    seen.add(key);
    const kind = key.startsWith("experiments/probes/")
      ? "probe"
      : key.startsWith("experiments/")
        ? "experiment"
        : key.startsWith("evidence/")
          ? "evidence page"
          : "other";
    entries.push({ key, kind, url: `/${key}/` });
  }
  entries.sort((a, b) => a.key.localeCompare(b.key));
  shots.sort((a, b) => a.localeCompare(b));
  return { entries, shots };
}

function viewportLabel(width) {
  if (Number(width) >= 900) return `Desktop (${width}px)`;
  if (Number(width) >= 600) return `Tablet (${width}px)`;
  return `Mobile (${width}px)`;
}

function capturesFor(artifactId, shots) {
  const prefix = `evidence/${artifactId}/`;
  const groups = new Map();
  const other = [];
  for (const shot of shots.filter((item) => item.startsWith(prefix))) {
    const filename = path.posix.basename(shot);
    const directory = path.posix.dirname(shot);
    const match = filename.match(/^(?:(.+)[-_])?(\d{3,4})\.(png|jpg|jpeg|webp)$/i);
    if (!match) {
      other.push(shot);
      continue;
    }
    const state = match[1] || (
      directory === prefix.slice(0, -1)
        ? `unspecified-state-${match[2]}`
        : directory.slice(prefix.length)
    );
    const key = `${directory}/${state}`;
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push({ shot, width: match[2] });
  }
  return { groups, other };
}

function renderCaptureGroup(state, views) {
  const sorted = [...views].sort((a, b) => Number(b.width) - Number(a.width));
  const hasWide = sorted.some((view) => Number(view.width) >= 900);
  const hasNarrow = sorted.some((view) => Number(view.width) < 900);
  return `
    <section aria-label="${escapeHtml(state)}">
      <div class="capture-title">Capture set: ${escapeHtml(state)}</div>
      <div class="viewport-grid">
        ${sorted.map(({ shot, width }) => `
          <figure class="viewport-frame">
            <figcaption>${viewportLabel(width)} <span>${escapeHtml(path.posix.basename(shot))}</span></figcaption>
            <a href="/${escapeHtml(shot)}" target="_blank"><img src="/${escapeHtml(shot)}" loading="lazy" alt="${escapeHtml(state)} at ${escapeHtml(width)}px"></a>
          </figure>`).join("")}
        ${!hasWide || !hasNarrow ? '<p class="missing">Missing capture: no matched desktop/mobile counterpart in this set.</p>' : ""}
      </div>
    </section>`;
}

function renderArtifactCard(entry, shots) {
  const artifactId = entry.key.slice("experiments/".length);
  const { groups, other } = capturesFor(artifactId, shots);
  const captures = [...groups.entries()]
    .map(([state, views]) => renderCaptureGroup(state, views))
    .join("");
  const title = entry.kind === "probe" ? `Probe: ${artifactId}` : `Artifact: ${artifactId}`;
  return `
    <article class="review-card">
      <header class="card-header">
        <div><span class="badge">${escapeHtml(entry.kind)}</span><h3>${escapeHtml(title)}</h3></div>
        <a class="open" href="${escapeHtml(entry.url)}" target="_blank">Open Live Sandbox ↗</a>
      </header>
      ${captures || '<p class="empty">No bound viewport capture found for this revision.</p>'}
      ${other.length ? `<div class="other"><h4>Additional evidence</h4>${other.map((shot) => `<a href="/${escapeHtml(shot)}" target="_blank"><img src="/${escapeHtml(shot)}" loading="lazy" alt="Additional evidence ${escapeHtml(shot)}"></a>`).join("")}</div>` : ""}
    </article>`;
}

function renderIndex() {
  const { entries, shots } = collectArtifacts();
  const runnable = entries.filter((entry) => entry.key.startsWith("experiments/"));
  const cards = runnable.map((entry) => renderArtifactCard(entry, shots)).join("\n");
  const list = entries.length
    ? entries.map((entry) => `<li><span>${escapeHtml(entry.kind)}</span><a href="${escapeHtml(entry.url)}" target="_blank">${escapeHtml(entry.key)}</a></li>`).join("")
    : "<li>No runnable artifacts yet.</li>";

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Spec Prototype · Revision Gallery</title>
  <style>
    :root { color-scheme: light dark; font-family: ui-sans-serif, system-ui, sans-serif; }
    * { box-sizing: border-box; }
    body { margin: 0; background: #f4f3ef; color: #171714; }
    main { width: min(1240px, calc(100% - 32px)); margin: 0 auto; padding: 40px 0 64px; }
    .intro { display: flex; gap: 24px; justify-content: space-between; align-items: end; margin-bottom: 28px; }
    h1 { margin: 0; font: 650 clamp(28px, 5vw, 54px)/1 ui-serif, Georgia, serif; }
    .intro p { max-width: 580px; margin: 0; color: #5f5e57; }
    .review-card { margin: 0 0 24px; background: #fff; border: 1px solid #d9d7cf; border-radius: 12px; overflow: hidden; }
    .card-header { padding: 14px 16px; border-bottom: 1px solid #e8e6df; display: flex; align-items: center; justify-content: space-between; gap: 16px; }
    .card-header div { display: flex; align-items: center; gap: 10px; }
    h3 { margin: 0; font-size: 15px; }
    .badge { padding: 3px 7px; border-radius: 999px; background: #eceae2; color: #5a594f; font-size: 11px; text-transform: uppercase; }
    a { color: #1b57a6; }
    .open { font-size: 13px; font-weight: 650; text-decoration: none; }
    .capture-title { padding: 9px 16px; color: #66645b; background: #faf9f6; font-size: 12px; }
    .viewport-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 16px; padding: 16px; }
    .viewport-frame { margin: 0; border: 1px solid #dfddd5; border-radius: 8px; overflow: hidden; background: #f8f7f3; }
    figcaption { padding: 7px 9px; display: flex; justify-content: space-between; gap: 10px; color: #5f5e57; font-size: 11px; }
    figcaption span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    img { display: block; width: 100%; height: auto; }
    .missing, .empty { margin: 0; padding: 18px 16px; color: #77756c; }
    .other { border-top: 1px solid #e8e6df; padding: 16px; }
    .other h4 { margin: 0 0 10px; }
    .other a { display: inline-block; width: 120px; margin-right: 8px; vertical-align: top; }
    .raw { margin-top: 36px; padding-top: 24px; border-top: 1px solid #cbc9c1; }
    .raw ul { padding: 0; list-style: none; }
    .raw li { display: flex; gap: 10px; padding: 5px 0; }
    .raw li span { min-width: 88px; color: #77756c; font-size: 12px; }
    @media (max-width: 700px) { .intro { align-items: start; flex-direction: column; } main { width: min(100% - 20px, 1240px); padding-top: 24px; } }
    @media (prefers-color-scheme: dark) {
      body { background: #151513; color: #efeee8; }
      .intro p, .capture-title, figcaption, .missing, .empty, .raw li span { color: #aaa89f; }
      .review-card { background: #1e1e1b; border-color: #3a3934; }
      .card-header, .other { border-color: #35342f; }
      .capture-title, .viewport-frame { background: #191917; border-color: #35342f; }
      .badge { background: #33322d; color: #c7c5bb; }
      a { color: #8ab8ee; }
      .raw { border-color: #3a3934; }
    }
  </style>
</head>
<body>
  <main>
    <header class="intro">
      <div><div class="badge">Read-only evidence</div><h1>Revision Gallery</h1></div>
      <p>Inspect runnable artifacts and evidence bound to each revision. Selection, critique and approval remain in their authoritative design records.</p>
    </header>
    ${cards || '<p class="empty">No runnable slice or probe artifacts generated yet.</p>'}
    <section class="raw"><h2>Artifact index</h2><ul>${list}</ul></section>
  </main>
</body>
</html>`;
}

function openBrowser(url) {
  if (process.argv.includes("--no-open")) return;
  if (process.env.CI || process.env.PYTEST_CURRENT_TEST || process.env.NODE_ENV === "test") return;
  let command;
  let args;
  if (process.platform === "darwin") {
    command = "open";
    args = [url];
  } else if (process.platform === "win32") {
    command = "cmd.exe";
    args = ["/c", "start", "", url];
  } else {
    command = "xdg-open";
    args = [url];
  }
  try {
    const child = spawn(command, args, { stdio: "ignore", detached: true });
    child.unref();
  } catch {
    // The URL is printed even when the host cannot open a browser.
  }
}

function respondText(response, status, text) {
  response.writeHead(status, { "content-type": "text/plain; charset=utf-8" });
  response.end(text);
}

const server = http.createServer((request, response) => {
  let url;
  try {
    url = new URL(request.url, "http://localhost");
  } catch {
    respondText(response, 400, "bad request");
    return;
  }

  if (!['GET', 'HEAD'].includes(request.method || 'GET')) {
    response.writeHead(405, { Allow: "GET, HEAD", "content-type": "text/plain; charset=utf-8" });
    response.end("read-only preview");
    return;
  }

  if (url.pathname === "/" || url.pathname === "/__index") {
    const html = renderIndex();
    response.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    response.end(request.method === "HEAD" ? undefined : html);
    return;
  }

  let decoded;
  try {
    decoded = decodeURIComponent(url.pathname);
  } catch {
    respondText(response, 400, "bad request");
    return;
  }
  let file = safeJoin(protoRoot, decoded);
  try {
    if (file && fs.statSync(file).isDirectory()) {
      const indexRelative = path.relative(protoRoot, path.join(file, "index.html"));
      file = safeJoin(protoRoot, indexRelative);
    }
    if (file && fs.statSync(file).isFile()) {
      response.writeHead(200, {
        "content-type": MIME[path.extname(file).toLowerCase()] || "application/octet-stream",
      });
      if (request.method === "HEAD") response.end();
      else fs.createReadStream(file).pipe(response);
      return;
    }
  } catch {
    // Resolve missing or disallowed paths as 404.
  }
  respondText(response, 404, "not found");
});

server.on("error", (error) => {
  console.error(`spec-prototype preview failed: ${error.message}`);
  process.exitCode = 1;
});

server.listen(Number.isFinite(requestedPort) ? requestedPort : 0, "127.0.0.1", () => {
  const address = server.address();
  const url = `http://127.0.0.1:${address.port}/`;
  console.log(`spec-prototype preview: ${url}`);
  console.log(`serving read-only: ${protoRoot}`);
  openBrowser(url);
});
