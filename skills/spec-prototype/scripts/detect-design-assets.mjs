#!/usr/bin/env node

// Deterministic design-language asset detection for spec-prototype.
// Scans the repository root for three asset classes:
//   1. design tokens files       (tokens.*, design-tokens.*, ...)
//   2. DESIGN documents          (DESIGN.md / DESIGN.mdx, exact case)
//   3. committed brand colors    (brand-colors.* tracked at git HEAD)
// Emits `{ "design_assets": "present"|"absent", "sources": [<path>...] }`.
// Pure local file scan: no network, no dependencies.
//
// Rules stay minimal and err toward `absent`: on doubt the caller runs the
// initialization path instead of overwriting existing assets.
//
// Usage:
//   node detect-design-assets.mjs [<repository-root>]

import { execFileSync } from "node:child_process";
import { existsSync, readdirSync, statSync } from "node:fs";
import path from "node:path";

const root = path.resolve(process.argv[2] ?? process.cwd());

if (!existsSync(root) || !statSync(root).isDirectory()) {
  console.error(`repository root is not a directory: ${root}`);
  process.exit(1);
}

// Tool configuration (including installed Skill templates), vendored and
// generated trees are not the product's inherited design identity.
const ignoredDirectories = new Set([
  ".agent",
  ".agents",
  ".claude",
  ".codex",
  ".git",
  ".next",
  "build",
  "coverage",
  "dist",
  "node_modules",
  "vendor",
]);

function relativeToRoot(filePath) {
  return path.relative(root, filePath).split(path.sep).join("/");
}

// Deterministic iterative walk; symlinked entries are not followed. An
// explicit stack avoids recursion-depth overflow on deep trees, and matches
// are collected during the walk instead of gathering every file first, so a
// large repository cannot exhaust the call stack or grow a huge file list.
function collectAssetPaths(committed) {
  const matched = [];
  const stack = [root];
  while (stack.length > 0) {
    const directory = stack.pop();
    const entries = readdirSync(directory, { withFileTypes: true }).sort(
      (left, right) => left.name.localeCompare(right.name),
    );
    for (const entry of entries) {
      if (entry.isDirectory() && ignoredDirectories.has(entry.name)) continue;
      const filePath = path.join(directory, entry.name);
      if (entry.isDirectory()) {
        stack.push(filePath);
      } else if (
        entry.isFile() &&
        (isTokenFile(filePath) ||
          isDesignDocument(filePath) ||
          isModernDesignConfig(filePath) ||
          isCommittedBrandColor(filePath, committed))
      ) {
        matched.push(filePath);
      }
    }
  }
  return matched;
}

// Matches tokens.json, design-tokens.json, design.tokens.css, tokens.base.yml,
// ... but NOT arbitrary *.tokens.json suffixes (e.g. foo.tokens.json) — a
// suffix-only match is too easy to hit inside vendored code, and a false
// `present` would make the skill inherit something that is not a design asset.
function isTokenFile(filePath) {
  const name = path.basename(filePath);
  return /^(?:design[-_. ]?tokens?|tokens)(?:[-_.][a-z0-9]+)*\.(?:json|css|scss|sass|less|js|ts|yaml|yml|md)$/i.test(
    name,
  );
}

// Lowercase `design.md` is an OpenSpec change document, not a design-language
// doc. Only the exact-case DESIGN.md / DESIGN.mdx counts as an asset.
function isDesignDocument(filePath) {
  return /^(?:DESIGN\.md|DESIGN\.mdx)$/.test(path.basename(filePath));
}

// Modern frontend asset configurations (Tailwind, shadcn/ui components.json, theme configs)
function isModernDesignConfig(filePath) {
  const name = path.basename(filePath).toLowerCase();
  return /^(?:tailwind\.config\.(?:js|cjs|mjs|ts)|components\.json|theme\.config\.(?:js|ts)|theme\.json)$/.test(name);
}

function committedFiles() {
  try {
    return new Set(
      execFileSync(
        "git",
        ["-C", root, "ls-tree", "-r", "--name-only", "-z", "HEAD"],
        { encoding: "utf8", stdio: ["ignore", "pipe", "ignore"] },
      )
        .split("\0")
        .filter(Boolean),
    );
  } catch {
    // Not a git repo, or no HEAD yet: nothing can be committed, so a
    // brand-colors file present only on disk is not an inherited asset.
    return new Set();
  }
}

function isCommittedBrandColor(filePath, committed) {
  const name = path.basename(filePath).toLowerCase();
  return (
    committed.has(relativeToRoot(filePath)) &&
    /^(?:brand-colors|品牌色|品牌颜色)\.(?:json|css|scss|sass|less|yaml|yml|md)$/.test(name)
  );
}

const committed = committedFiles();
const sources = collectAssetPaths(committed).map(relativeToRoot).sort();

process.stdout.write(
  JSON.stringify({
    design_assets: sources.length > 0 ? "present" : "absent",
    sources,
  }),
);
process.stdout.write("\n");
