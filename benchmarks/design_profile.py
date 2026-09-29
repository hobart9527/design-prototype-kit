#!/usr/bin/env python3
"""A deterministic design profile of a delivered prototype: measurement, not a grade.

Why this exists
---------------
Every other number the harness produces is a pass/fail gate. Gates answer "did it
break a rule", never "did it get better", so a suite of rounds can show a wall of
green while the design itself regresses — which is what happened: r16 shipped a
richer artifact than r13 and scored worse on every task, and nothing in the
harness could say whether the *design* had improved.

The meter this replaces (`evaluate_design_signals.py`) was retired for a reason
worth restating: it grepped `tokens.css` for token *names* (`--bg-void`,
`--reading-measure-max`) and contracts for section *headings* ("Fault
Tolerance"). Copying the house template scored 100%. It measured the skill's own
vocabulary, so it could never disagree with the skill.

This profile reads only what the browser actually renders — computed styles and
geometry — so no token name, class name or heading can satisfy it. It returns
numbers with no threshold and no verdict: a profile is compared against another
profile, and the comparison is the finding. That is the whole point. A single
absolute score would just become another gate.

What it measures, and why each is a design property rather than a house style
--------------------------------------------------------------------------------
- `gap_uniformity` — coefficient of variation of the vertical gaps between
  sibling blocks that are actually stacked (horizontally overlapping; a grid or
  table row's children are not). The skill's "Compression & Release" doctrine
  explicitly refuses the uniform card grid, so near-zero variation is the
  anti-pattern. High variation is not automatically good: a screen can be
  chaotic. The number is a prompt to look, not a verdict.
- `gap_median` / `gap_distinct` — the typical stacked gap and how many distinct
  gap values appear. Read together with `gap_uniformity`: a small distinct count
  with a large spread is a rhythm, a small distinct count with a near-zero spread
  is a grid.
- `spacing_scale` — the distinct `row-gap` values the layout actually uses. A
  table-driven console spaces with cell padding and grid gap, not margins, so its
  sibling gaps read 0; this reads the spacing mechanism directly and makes "does
  this page have a spacing scale" answerable either way.
- `type_scale_ratios` — the ratios between distinct rendered font sizes. A
  modular scale produces a few recurring ratios; ad-hoc sizing produces many
  irregular ones.
- `hierarchy_levels` — distinct (size, weight) pairs actually rendered. This is
  hierarchy depth as the eye receives it.
- `alignment_edges` — distinct left-edge x positions of block-level elements.
  A grid produces a small set; drift produces many.
- `palette_size` / `palette_share` — distinct opaque rendered colors, and the
  share of painted area held by the top three. Concentration is what separates a
  palette from an accident.
- `data_specificity` — the share of text nodes carrying a digit or a unit. A
  proxy for the "Zero Naked Metrics" / real-content floor.
- `control_density` — interactive controls per 1000px² of rendered content.
- `whitespace_ratio` — share of the document box no glyph covers, measured from
  text-node ink boxes (see the note in the script on why element boxes lie).

A break the profile cannot help but see: if the anchor's stylesheet link does not
resolve, the page renders unstyled and the numbers collapse together
(`palette_size` 1, `gap_uniformity` high, `whitespace_ratio` high). That is a
defect, not a design, and it is worth reading the profile as "did the stylesheet
load" before reading it as "is this well designed".

Hermetic: no network, no LLM, no browser download. Needs node + a Chrome-family
browser, exactly like the existing craft probe; without them it reports
`environment_not_ready` rather than inventing numbers.
"""
from __future__ import annotations

import argparse
import base64
import json
import pathlib
import shutil
import subprocess
import sys

BENCH = pathlib.Path(__file__).resolve().parent
PROBE = BENCH / "runners" / "browser_probe.mjs"

# One evaluate() call in the page. Every number below is read from geometry or
# computed style; nothing reads an attribute name, a class, or the source text.
_PROBE_SCRIPT = r'''(() => {
  const visible = (el) => {
    const r = el.getBoundingClientRect(), s = getComputedStyle(el);
    return r.width > 1 && r.height > 1 && s.display !== "none"
      && s.visibility !== "hidden" && parseFloat(s.opacity) > 0.05;
  };
  const rect = (el) => el.getBoundingClientRect();

  // --- Rhythm: vertical gaps between vertically-stacked visible siblings -----
  // A gap only exists between siblings that are stacked, not side by side. In a
  // grid, flex row or table row the children sit on the same line, so
  // `b.top - a.bottom` is 0 or negative and measures nothing; those pairs are
  // excluded by requiring the two boxes to overlap horizontally. Without this
  // the "rhythm" of every table-driven console is an artefact of its <td>s.
  const gaps = [];
  for (const parent of document.querySelectorAll("body *")) {
    if (!visible(parent)) continue;
    const kids = [...parent.children].filter(visible);
    if (kids.length < 3) continue;
    for (let i = 1; i < kids.length; i++) {
      const a = rect(kids[i - 1]), b = rect(kids[i]);
      const overlap = Math.min(a.right, b.right) - Math.max(a.left, b.left);
      const minW = Math.min(a.width, b.width);
      if (minW <= 0 || overlap / minW < 0.5) continue;
      const gap = b.top - a.bottom;
      if (gap >= 0 && gap < 2000) gaps.push(gap);
    }
  }
  const mean = gaps.length ? gaps.reduce((s, g) => s + g, 0) / gaps.length : 0;
  const sd = gaps.length > 1
    ? Math.sqrt(gaps.reduce((s, g) => s + (g - mean) ** 2, 0) / gaps.length) : 0;
  // Zero mean with gaps present means every stacked pair is flush — perfectly
  // uniform spacing, which is the anti-pattern the doctrine names, so it is 0
  // and not null. Null is reserved for "no stacked siblings to measure at all".
  const gap_uniformity = !gaps.length ? null : (mean > 0 ? +(sd / mean).toFixed(4) : 0);
  const sortedGaps = [...gaps].sort((a, b) => a - b);
  const gap_median = sortedGaps.length
    ? +sortedGaps[Math.floor(sortedGaps.length / 2)].toFixed(1) : null;
  const gap_distinct = new Set(sortedGaps.map((g) => Math.round(g))).size;

  // --- Spacing scale: the row-gap values the layout actually uses -----------
  // Sibling gaps alone read 0 on a table-driven console, which does its spacing
  // with cell padding and grid gap rather than margins. This reads the gap
  // mechanism itself, so "does this page have a spacing scale" is answerable
  // without depending on which of the two mechanisms the author chose.
  const spacing = new Set();
  for (const el of document.querySelectorAll("body *")) {
    if (!visible(el)) continue;
    const rg = parseFloat(getComputedStyle(el).rowGap);
    if (rg > 0) spacing.add(Math.round(rg * 10) / 10);
  }
  const spacing_scale = [...spacing].sort((a, b) => a - b);

  // --- Type: distinct rendered sizes, their scale ratios, and weight pairs ---
  const textEls = [...document.querySelectorAll("body *")].filter(
    (el) => visible(el) && (el.textContent || "").trim().length > 0
      && [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim()));
  const sizes = new Set(), pairs = new Set(), weights = new Set();
  for (const el of textEls) {
    const s = getComputedStyle(el);
    const px = Math.round(parseFloat(s.fontSize) * 10) / 10;
    sizes.add(px); weights.add(s.fontWeight); pairs.add(px + "/" + s.fontWeight);
  }
  const sorted = [...sizes].sort((a, b) => a - b);
  const ratios = [];
  for (let i = 1; i < sorted.length; i++) {
    if (sorted[i - 1] > 0) ratios.push(+(sorted[i] / sorted[i - 1]).toFixed(3));
  }

  // --- Alignment: distinct left edges of block-level visible elements --------
  const edges = new Set();
  for (const el of document.querySelectorAll("body *")) {
    const s = getComputedStyle(el);
    if (!visible(el) || s.display === "inline") continue;
    if (rect(el).height < 8) continue;
    edges.add(Math.round(rect(el).left));
  }

  // --- Palette: opaque rendered colors and how concentrated they are --------
  const colorArea = new Map();
  for (const el of document.querySelectorAll("body *")) {
    if (!visible(el)) continue;
    const s = getComputedStyle(el);
    const bg = s.backgroundColor;
    if (!bg || bg === "rgba(0, 0, 0, 0)" || bg === "transparent") continue;
    const r = rect(el);
    colorArea.set(bg, (colorArea.get(bg) || 0) + r.width * r.height);
  }
  const totalArea = [...colorArea.values()].reduce((s, a) => s + a, 0);
  const ranked = [...colorArea.values()].sort((a, b) => b - a);
  const palette_share = totalArea > 0
    ? +(ranked.slice(0, 3).reduce((s, a) => s + a, 0) / totalArea).toFixed(4) : null;

  // --- Content: how much text carries a real value -------------------------
  let textNodes = 0, specificNodes = 0;
  for (const el of textEls) {
    const own = [...el.childNodes].filter((n) => n.nodeType === 3)
      .map((n) => n.textContent).join(" ").trim();
    if (own.length < 2) continue;
    textNodes++;
    if (/\d/.test(own) || /\b(ms|s|px|GB|MB|%|QPS|rps|台|次|秒|毫秒)\b/i.test(own)) specificNodes++;
  }

  // --- Controls: affordance density over painted area ----------------------
  const controls = [...document.querySelectorAll(
    "button, a[href], input, select, textarea, [role=button], [role=tab], [role=menuitem], summary"
  )].filter(visible);
  let contentArea = 0;
  for (const el of document.querySelectorAll("body *")) {
    if (!visible(el)) continue;
    const r = rect(el);
    contentArea = Math.max(contentArea, r.width * r.height);
  }

  // --- Whitespace: share of the document box that no glyph occupies ---------
  // Measured with Range over each text node, which yields the ink box itself.
  // Summing the boxes of *elements* that contain text double-counts every
  // ancestor (`<li>Foo <b>bar</b></li>` counts Foo's box and then bar's box
  // inside it), which is how a ratio can drift toward "no whitespace" on a page
  // that is mostly empty.
  const docH = Math.max(document.body.scrollHeight, 1), docW = Math.max(document.body.scrollWidth, 1);
  let inkArea = 0;
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    if (!n.textContent.trim()) continue;
    const range = document.createRange();
    range.selectNodeContents(n);
    for (const r of range.getClientRects()) {
      if (r.width > 0 && r.height > 0) inkArea += r.width * r.height;
    }
  }
  const whitespace_ratio = +(1 - Math.min(inkArea / (docW * docH), 1)).toFixed(4);
  return {
    gap_count: gaps.length,
    gap_uniformity,
    gap_median,
    gap_distinct,
    spacing_scale,
    spacing_scale_size: spacing.size,
    type_sizes: sorted,
    type_scale_ratios: ratios,
    type_weights: [...weights].sort(),
    hierarchy_levels: pairs.size,
    alignment_edges: edges.size,
    palette_size: colorArea.size,
    palette_share,
    text_nodes: textNodes,
    specific_text_nodes: specificNodes,
    data_specificity: textNodes ? +(specificNodes / textNodes).toFixed(4) : null,
    controls: controls.length,
    content_area_px: Math.round(contentArea),
    control_density: contentArea > 0
      ? +(controls.length / (contentArea / 1000)).toFixed(5) : null,
    whitespace_ratio,
    document: { w: docW, h: docH },
  };
})()'''


def profile_artifact(html: pathlib.Path, viewport: str = "1280x900") -> dict:
    """Render `html` and return its design profile, or an explicit unverified record."""
    node = shutil.which("node")
    if not node or not PROBE.is_file():
        return {"status": "environment_not_ready",
                "reason": "design profile needs node and browser_probe.mjs"}
    try:
        proc = subprocess.run(
            [node, str(PROBE), "craft", "--url", html.resolve().as_uri(),
             "--viewport", viewport,
             "--script", base64.b64encode(_PROBE_SCRIPT.encode()).decode()],
            capture_output=True, text=True, timeout=90, cwd=str(PROBE.parents[1]))
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"status": "environment_not_ready",
                "reason": f"probe failed ({exc.__class__.__name__})"}
    if proc.returncode != 0:
        return {"status": "environment_not_ready",
                "reason": f"probe exited {proc.returncode}: {proc.stderr.strip()[:200]}"}
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1]).get("result")
    except (ValueError, IndexError, TypeError):
        return {"status": "environment_not_ready", "reason": "probe output unparseable"}
    if not isinstance(result, dict):
        return {"status": "environment_not_ready", "reason": "probe returned no profile"}
    result["status"] = "measured"
    result["artifact"] = str(html)
    result["viewport"] = viewport
    return result


# Fields that are a level, not a count: compared as "higher/lower", never summed.
_COMPARABLE = (
    "gap_uniformity", "gap_median", "gap_distinct", "spacing_scale",
    "spacing_scale_size", "hierarchy_levels", "alignment_edges", "palette_size",
    "palette_share", "data_specificity", "control_density", "whitespace_ratio",
    "type_sizes", "type_scale_ratios", "controls", "text_nodes",
)


def compare(profiles: dict) -> dict:
    """Side-by-side comparable fields. No winner is declared.

    Deliberately absent: a total, a rank, or a recommendation. Every one of these
    numbers is legitimate at both ends — few alignment edges can be discipline or
    poverty, high gap variation can be rhythm or chaos — so a ranking would
    invent the judgment the profile exists to inform. Read the columns.
    """
    rows = {}
    for field in _COMPARABLE:
        row = {}
        for label, prof in profiles.items():
            row[label] = prof.get(field) if prof.get("status") == "measured" else None
        rows[field] = row
    return {"rows": rows, "labels": list(profiles)}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deterministic design profile of delivered prototypes (measurement, not a grade)")
    parser.add_argument("artifacts", nargs="+", help="anchor index.html paths to profile")
    parser.add_argument("--labels", default=None,
                        help="comma-separated labels, one per artifact in order "
                             "(default: the experiment directory name)")
    parser.add_argument("--viewport", default="1280x900")
    parser.add_argument("--json", dest="json_out", default=None)
    args = parser.parse_args()

    labels = (args.labels.split(",") if args.labels
              else [pathlib.Path(p).parent.parent.name or str(i)
                    for i, p in enumerate(args.artifacts)])
    if len(labels) != len(args.artifacts):
        parser.error(f"--labels has {len(labels)} entries for {len(args.artifacts)} artifacts")
    profiles = {}
    for label, path in zip(labels, args.artifacts):
        profiles[label] = profile_artifact(pathlib.Path(path), args.viewport)

    payload = {"profiles": profiles, "comparison": compare(profiles)}
    if args.json_out:
        pathlib.Path(args.json_out).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for label, prof in profiles.items():
        if prof.get("status") != "measured":
            print(f"{label}: {prof.get('status')} ({prof.get('reason', '')})")
            continue
        print(f"{label}:")
        for field in ("gap_uniformity", "gap_median", "gap_distinct",
                      "spacing_scale", "hierarchy_levels", "alignment_edges",
                      "palette_size", "palette_share", "data_specificity",
                      "control_density", "whitespace_ratio"):
            print(f"    {field:<20} {prof.get(field)}")
        print(f"    {'type_sizes':<20} {prof.get('type_sizes')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
