#!/usr/bin/env node

// Deterministically resolve an optional OpenSpec product-source reference.
// Hard references may select; text similarity only ranks candidates.

import { existsSync, readFileSync, readdirSync, realpathSync, statSync } from "node:fs";
import path from "node:path";

function fail(message) {
  process.stderr.write(`${message}\n`);
  process.exit(1);
}

const argv = process.argv.slice(2);
const root = path.resolve(argv.shift() ?? process.cwd());
const options = { intent: "", changeId: "", artifact: "", foundationOnly: false };
for (let index = 0; index < argv.length; index += 1) {
  const argument = argv[index];
  if (argument === "--foundation-only") options.foundationOnly = true;
  else if (argument === "--intent") options.intent = argv[++index] ?? fail("--intent requires a value");
  else if (argument === "--change-id") options.changeId = argv[++index] ?? fail("--change-id requires a value");
  else if (argument === "--artifact") options.artifact = argv[++index] ?? fail("--artifact requires a value");
  else fail(`unknown argument: ${argument}`);
}

if (!existsSync(root) || !statSync(root).isDirectory()) fail(`repository root is not a directory: ${root}`);

const changesRoot = path.join(root, "openspec", "changes");
const active = listChanges(changesRoot, false);
const archived = listChanges(path.join(changesRoot, "archive"), true);
const all = [...active, ...archived];

if (options.foundationOnly) emit({ disposition: "not_required", selected: null, candidates: [], reason: "project Foundation work does not require a Change" });

const explicit = normalizeExplicit(options.changeId);
if (explicit) {
  const found = all.find((item) => item.change_id === explicit);
  if (found) resolve(found, "explicit Change reference");
  emit({ disposition: "missing", selected: null, candidates: [], reason: `explicit Change not found: ${explicit}` });
}

if (options.artifact) {
  const artifact = path.resolve(root, options.artifact);
  if (!insideRoot(artifact)) {
    emit({ disposition: "missing", selected: null, candidates: [], reason: "artifact is outside repository root" });
  }
  const fromPath = changeFromPath(artifact);
  if (fromPath) {
    const found = all.find((item) => item.change_id === fromPath);
    if (found) resolve(found, "current artifact path");
    emit({ disposition: "missing", selected: null, candidates: [], reason: `Change not found: ${fromPath}` });
  }
  if (existsSync(artifact) && statSync(artifact).isFile()) {
    const text = readFileSync(artifact, "utf8");
    const match = text.match(/(?:Change ID|Change):\s*`?([a-z0-9][a-z0-9._-]*)`?/i)
      ?? text.match(/openspec\/changes\/([a-z0-9][a-z0-9._-]*)/i);
    if (match) {
      const found = all.find((item) => item.change_id === match[1]);
      if (found) resolve(found, "Change reference in current artifact");
      emit({ disposition: "missing", selected: null, candidates: [], reason: `Change not found: ${match[1]}` });
    }
  }
}

if (active.length === 1) resolve(active[0], "sole active Change");
if (active.length === 0) emit({ disposition: "not_required", selected: null, candidates: [], reason: "no active OpenSpec product source; prototype slice remains independent" });

const ranked = active
  .map((item) => rank(item, options.intent))
  .sort((left, right) => right.score - left.score || left.change_id.localeCompare(right.change_id));
emit({
  disposition: "ambiguous",
  selected: null,
  candidates: ranked.map(({ score, ...item }) => item),
  reason: "multiple active Changes remain; ranking is display-only and human selection is required",
});

function listChanges(directory, isArchived) {
  if (!existsSync(directory) || !statSync(directory).isDirectory()) return [];
  return readdirSync(directory, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && entry.name !== "archive" && !entry.name.startsWith("."))
    .map((entry) => describe(path.join(directory, entry.name), entry.name, isArchived));
}

function describe(directory, changeId, isArchived) {
  const proposalPath = path.join(directory, "proposal.md");
  const proposal = existsSync(proposalPath) ? readFileSync(proposalPath, "utf8") : "";
  const heading = proposal.match(/^#\s+(?:Proposal:\s*)?(.+)$/m)?.[1]?.trim();
  const capabilities = new Set();
  for (const match of proposal.matchAll(/(?:Affected capabilities|Capabilities?|Specs?)\s*:\s*([^\n]+)/gi)) {
    for (const value of match[1].split(/[,|]/)) if (value.trim()) capabilities.add(value.trim().replace(/`/g, ""));
  }
  const specsRoot = path.join(directory, "specs");
  if (existsSync(specsRoot)) {
    for (const entry of readdirSync(specsRoot, { withFileTypes: true })) if (entry.isDirectory()) capabilities.add(entry.name);
  }
  return {
    change_id: changeId,
    title: heading || changeId,
    affected_capabilities: [...capabilities].sort(),
    archived: isArchived,
    path: path.relative(root, directory).split(path.sep).join("/"),
    search_text: `${changeId} ${heading ?? ""} ${proposal}`.toLowerCase(),
  };
}

function normalizeExplicit(value) {
  if (!value) return "";
  const normalized = value.replaceAll("\\", "/").replace(/\/$/, "");
  const marker = "/openspec/changes/";
  if (normalized.includes(marker)) return normalized.split(marker)[1].split("/").filter((part) => part !== "archive")[0] ?? "";
  if (normalized.startsWith("openspec/changes/")) return normalized.slice("openspec/changes/".length).split("/").filter((part) => part !== "archive")[0] ?? "";
  return path.basename(normalized);
}

function changeFromPath(artifact) {
  const relative = path.relative(changesRoot, artifact).split(path.sep);
  if (relative[0] === ".." || relative.length === 0) return "";
  return relative[0] === "archive" ? relative[1] ?? "" : relative[0];
}

function insideRoot(candidate) {
  try {
    const base = realpathSync(root);
    const real = realpathSync(candidate);
    return real === base || real.startsWith(base + path.sep);
  } catch { return false; }
}

function tokens(text) {
  return [...new Set((text.toLowerCase().match(/[\p{L}\p{N}][\p{L}\p{N}._-]*/gu) ?? []).filter((item) => item.length > 1))];
}

function rank(item, intent) {
  const matched = tokens(intent).filter((token) => item.search_text.includes(token));
  return {
    ...withoutSearch(item),
    score: matched.length,
    match_reasons: matched.length ? [`intent terms: ${matched.slice(0, 8).join(", ")}`] : ["active Change"],
  };
}

function withoutSearch(item) {
  const { search_text, ...publicItem } = item;
  return publicItem;
}

function resolve(item, reason) {
  emit({ disposition: "resolved", selected: { ...withoutSearch(item), match_reasons: [reason] }, candidates: [], reason });
}

function emit(value) {
  process.stdout.write(`${JSON.stringify(value)}\n`);
  process.exit(0);
}
