#!/usr/bin/env python3
"""Deterministic AI-slop and category-rut detector over a prototype artifact.

This is the *measuring stick* for taste, not a gate: it reports findings with a
stable rule id, a severity and the evidence it read, and never repairs or blocks
anything. Every rule is checkable from the artifact's own bytes (markup and the
declarations the document owns), so a finding can always be traced back to the
line that produced it.

The rule set is the machine-checkable subset of the craft floor
(`skills/spec-prototype/references/02-craft-methods/craft-floor.md`) and the
AI-slop test. Rules that need human judgement (is this card grid *earned*?) stay
in the taste judge, which reads screenshots; this module never guesses at them.

Severity:
  high   — the category default was taken while the axis was free; a reader can
           tell a model assembled this without being told.
  medium — a craft-floor mechanic is missing or weakened.
  low    — a signal worth inspecting, plausibly earned by the brief.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "runners"))
import bench_lib as bl  # noqa: E402

STYLE_RE = re.compile(r"<style[^>]*>(.*?)</style>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<([a-zA-Z][a-zA-Z0-9-]*)((?:[^>\"']|\"[^\"]*\"|'[^']*')*)>")
CLASS_RE = re.compile(r'class\s*=\s*"([^"]*)"')
STYLE_ATTR_RE = re.compile(r'style\s*=\s*"([^"]*)"')
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RULE_RE = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}]+)")
FONT_VAR_NUM_RE = re.compile(r"font-variant-numeric\s*:\s*[^;}]*(tabular-nums|lining-nums)")
# Heading text that is a bare ordinal or a decorative kicker.
ORDINAL_HEADING_RE = re.compile(r"^\s*(?:0[1-9]|1[0-9])\s*$")
# Pictographs borrowed to stand in an icon's place. The arrows block
# (U+2190–U+21FF) is deliberately excluded: `→` between runbook steps and `↗`
# on a trend readout are typography, not borrowed iconography, and flagging them
# measures the artifact's prose rather than its design.
EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
GRADIENT_TEXT_RE = re.compile(r"background-clip\s*:\s*text", re.IGNORECASE)
# A side accent stripe is a container treatment. Row-level change markers ride
# 1–2px (VS Code and diff UFs use exactly that on list items), so the floor for
# "stripe" is 3px: anything thinner is an item marker, not a container accent.
SIDE_STRIPE_RE = re.compile(r"border-(?:left|right)\s*:\s*([3-9]|\d{2,})px\s+solid", re.IGNORECASE)
# The model-default faces: reaching for one of these as the *only* face means the
# typographic axis was never decided.
REFLEX_FACES = ("inter", "roboto", "open sans", "lato", "montserrat", "poppins",
                "nunito", "source sans", "system-ui", "-apple-system", "segoe ui",
                "helvetica neue", "arial")
PILL_RADIUS_RE = re.compile(r"border-radius\s*:\s*(?:9999px|999px|100px|50em|99999px)", re.IGNORECASE)
BLUR_RE = re.compile(r"backdrop-filter\s*:\s*blur", re.IGNORECASE)
HARD_SHADOW_RE = re.compile(r"box-shadow\s*:\s*[^;{}]*?\b(\d{1,2})px\s+\1px\s+0(?:px)?\b")
PURE_GRAY_RE = re.compile(r"#(?:808080|888888|7f7f7f|999999|666666|333333|cccccc|eeeeee)\b", re.IGNORECASE)
DEEP_INDIGO_RE = re.compile(r"#(?:0[dD]0[bB]1[aA]|1[0-3][0-9a-fA-F]{4}|0[0-9a-fA-F]{5})")
TRANSITION_ALL_RE = re.compile(r"transition\s*:\s*all\b", re.IGNORECASE)
CARD_CLASS_RE = re.compile(r"(?:^|[-_])(card|tile|panel|box)(?:$|[-_])", re.IGNORECASE)
METRIC_CLASS_RE = re.compile(r"(?:stat|metric|kpi|hero-number|big-number)", re.IGNORECASE)


def _declarations(text: str) -> list[tuple[str, str]]:
    """Property/value pairs from a declaration block, comments already stripped."""
    return [(m.group(1).strip().lower(), m.group(2).strip())
            for m in RULE_RE.finditer(text)]


def _elements(markup: str) -> list[tuple[str, str, str]]:
    """(tag, classes, inline style) for every element, from a light tag scan.

    Deliberately independent of the Skill's own DOM layer: a judge that reused
    the artifact tooling would inherit its blind spots.
    """
    out = []
    for match in TAG_RE.finditer(markup):
        tag, attrs = match.group(1).lower(), match.group(2)
        classes = " ".join(CLASS_RE.findall(attrs))
        style = " ".join(STYLE_ATTR_RE.findall(attrs))
        out.append((tag, classes, style))
    return out


def _text_nodes(markup: str) -> list[str]:
    stripped = re.sub(r"<[^>]+>", "\n", markup)
    return [line.strip() for line in stripped.splitlines() if line.strip()]


class _Findings:
    def __init__(self) -> None:
        self.items: list[dict] = []
        self.counts: dict[str, int] = {}

    def add(self, rule: str, severity: str, file: str, evidence: str) -> None:
        self.counts[rule] = self.counts.get(rule, 0) + 1
        self.items.append({"rule": rule, "severity": severity, "file": file,
                           "evidence": evidence.strip()[:200]})

    def rule(self, rule: str, severity: str, file: str, evidence: str, *, times: int = 1) -> None:
        for _ in range(times):
            self.add(rule, severity, file, evidence)


def detect(artifacts_dir: pathlib.Path, *, max_per_rule: int = 4) -> dict:
    artifacts_dir = pathlib.Path(artifacts_dir)
    texts = bl.artifact_texts(artifacts_dir)
    if not texts:
        return {"judge": "slop_detector", "status": "blocked",
                "note": "no text artifacts to read", "findings": [], "counts": {}}
    findings = _Findings()
    markup_by_file, css_by_file = {}, {}
    for name, text in texts.items():
        # The review portal is an operational wrapper the Skill emits from the
        # coverage record, not authored design surface. `runtime_judge` already
        # excludes it from the candidate's artifacts; a taste score that kept
        # reading it charged the candidate for the harness (four of r19's nine
        # findings and seven of r20's twelve points came from there alone).
        if name.rsplit("/", 1)[-1] == "review-portal.html":
            continue
        if name.endswith((".html", ".htm")):
            markup_by_file[name] = text
        elif name.endswith(".css"):
            css_by_file[name] = text

    for name, markup in markup_by_file.items():
        css = "\n".join(STYLE_RE.findall(markup))
        if css:
            css_by_file[f"{name}::<style>"] = css
        _scan_markup(name, markup, findings)
    for name, css in css_by_file.items():
        _scan_css(name, css, findings)

    all_css = "\n".join(css_by_file.values())
    _scan_document(markup_by_file, all_css, findings)

    findings.items.sort(key=lambda f: ({"high": 0, "medium": 1, "low": 2}[f["severity"]], f["rule"]))
    capped, overflow = [], {}
    seen: dict[str, int] = {}
    for item in findings.items:
        seen[item["rule"]] = seen.get(item["rule"], 0) + 1
        if seen[item["rule"]] <= max_per_rule:
            capped.append(item)
        else:
            overflow[item["rule"]] = overflow.get(item["rule"], 0) + 1
    # Severity counts mirror the capped list the report ranks from; counting the
    # overflow too would report more high findings than it ever names.
    by_severity = {level: sum(1 for f in capped if f["severity"] == level)
                   for level in ("high", "medium", "low")}
    severity_of = {}
    for item in findings.items:
        severity_of.setdefault(item["rule"], item["severity"])
    return {
        "judge": "slop_detector",
        "status": "detected",
        "files_scanned": sorted(set(markup_by_file) | {n.split("::")[0] for n in css_by_file}),
        "findings": capped,
        "counts": dict(sorted(findings.counts.items())),
        "counts_truncated": overflow,
        "by_severity": by_severity,
        "slop_score": sum(count * _SEVERITY_WEIGHT.get(severity_of.get(rule, "low"), 1)
                          for rule, count in findings.counts.items()),
        "note": "deterministic scan; judgement-only rules stay with the taste judge",
    }


_SEVERITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


class _CardNestingScanner(HTMLParser):
    VOID_TAGS = frozenset({
        "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "param", "source", "track", "wbr",
    })

    def __init__(self) -> None:
        super().__init__()
        self.stack: list[bool] = []
        self.nesting = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in self.VOID_TAGS:
            return
        classes = ""
        for name, val in attrs:
            if name.lower() == "class" and val:
                classes = val
                break
        # Discrete card / tile surface (excludes layout panels, boxes, sections).
        is_card = bool(re.search(r"(?:^|[-_ ])(card|tile)(?:$|[-_ ])", classes, re.IGNORECASE))
        if is_card and any(self.stack):
            self.nesting += 1
        self.stack.append(is_card)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self.VOID_TAGS:
            return
        if self.stack:
            self.stack.pop()


def _scan_markup(name: str, markup: str, out: _Findings) -> None:
    elements = _elements(markup)
    texts = _text_nodes(markup)

    # A glyph that *leads* a text node is occupying an icon's slot — the shape
    # this rule is about. One appearing mid-sentence is prose.
    emoji_hits = [t for t in texts if EMOJI_RE.match(t)]
    if emoji_hits:
        out.add("SLOP-009", "high", name, f"emoji/glyph as icon: {emoji_hits[0]}")

    # A bare ordinal heading is a section number with no sequence to carry.
    ordinal = [t for t in texts if ORDINAL_HEADING_RE.match(t)]
    if ordinal:
        out.add("SLOP-014", "low", name, f"section ordinal heading: {ordinal[0]}")

    cards = [c for tag, c, _ in elements if CARD_CLASS_RE.search(c or "")]
    if cards:
        # Nested cards: a card surface nested inside another card surface in the DOM.
        scanner = _CardNestingScanner()
        try:
            scanner.feed(markup)
            if scanner.nesting:
                out.rule("SLOP-004", "high", name, "card class nested inside a card", times=scanner.nesting)
        except Exception:
            pass

    # Ghost card: a hairline border under a wide soft shadow on the same rule.
    if re.search(r"border\s*:\s*1px\s+solid[^;{}]*;[^}]*box-shadow\s*:[^;{}]*\b(?:1[0-9]|[2-9][0-9])px",
                 markup, re.IGNORECASE | re.DOTALL):
        out.add("SLOP-003", "medium", name, "1px border plus wide soft shadow (declare elevation once)")

    inline_hex = HEX_RE.findall(" ".join(style for _, _, style in elements))
    if inline_hex:
        out.add("SLOP-024", "medium", name, f"inline hex outside tokens: {inline_hex[0]}")

    if re.search(r"<(?:dialog|div)[^>]*class=\"[^\"]*modal[^\"]*\"", markup, re.IGNORECASE):
        out.add("SLOP-025", "low", name, "modal container present; confirm the task needs interruption")


def _scan_css(name: str, css: str, out: _Findings) -> None:
    decls = _declarations(css)
    values = {prop: val for prop, val in decls}

    if GRADIENT_TEXT_RE.search(css):
        out.add("SLOP-001", "high", name, "background-clip: text (gradient text as emphasis)")
    if SIDE_STRIPE_RE.search(css):
        out.add("SLOP-002", "high", name, "thick side accent stripe on a container")
    if TRANSITION_ALL_RE.search(css):
        out.add("SLOP-006", "medium", name, "transition: all (unscoped animation)")
    if BLUR_RE.search(css):
        out.add("SLOP-021", "low", name, "backdrop-filter blur; confirm it is an effect, not decoration")
    if PILL_RADIUS_RE.search(css):
        out.add("SLOP-012", "medium", name, "pill radius; confirm it is a small control, not a container")
    if HARD_SHADOW_RE.search(css):
        out.add("SLOP-010", "medium", name, "hard offset shadow with zero blur")
    gray = PURE_GRAY_RE.search(css)
    if gray:
        out.add("SLOP-007", "low", name, f"untinted pure gray {gray.group(0)} (tint the neutral)")
    if re.search(r"background(?:-color)?\s*:\s*#0[dD]0[bB]1[aA]", css):
        out.add("SLOP-008", "high", name, "deep indigo/near-black-purple background (AI default)")
    if re.search(r"(?:repeating-)?(?:linear|radial)-gradient[^;{}]*(?:stripe|grid|blueprint)", css, re.IGNORECASE):
        out.add("SLOP-013", "low", name, "stripe/grid overlay texture; confirm a canvas underneath")

    faces = " ".join(val for prop, val in decls if prop in ("font-family",))
    if faces:
        system_chain = any(s in faces.lower() for s in ("system-ui", "-apple-system", "blinkmacsystemfont"))
        generic_reflex = [f for f in ("inter", "roboto", "open sans", "lato", "montserrat", "poppins", "nunito") if f in faces.lower()]
        # One reflex face is a choice; multiple generic AI webfonts stacked together is a rut.
        # Standard cross-platform OS system font fallback stacks are low severity.
        if generic_reflex and len(generic_reflex) >= 2:
            out.add("SLOP-023", "medium", name, f"reflex font stack: {generic_reflex[0]} (+{len(generic_reflex) - 1})")
        elif system_chain:
            out.add("SLOP-023", "low", name, "system-ui fallback stack")
        elif generic_reflex:
            out.add("SLOP-023", "low", name, f"model-default face: {generic_reflex[0]}")

    radius_groups = [val for prop, val in decls if prop == "border-radius"]
    radii = set(radius_groups)
    if len(radii) == 1 and len(radius_groups) >= 3 and not PILL_RADIUS_RE.search(next(iter(radii))):
        out.add("SLOP-011", "low", name,
                f"one radius value ({next(iter(radii))}) across {len(radius_groups)} rule groups")

    if METRIC_CLASS_RE.search(css) and not FONT_VAR_NUM_RE.search(css):
        out.add("SLOP-019", "medium", name, "metric classes without tabular-nums")

    if re.search(r"transition[^;{}]*ease(?:-in-out|-in|-out)?\b", css, re.IGNORECASE):
        if not re.search(r"spring-(?:snappy|gentle|bounce)", css):
            out.add("SLOP-026", "medium", name, "mechanical ease curve without spring token reference")


def _scan_document(markup_by_file: dict, all_css: str, out: _Findings) -> None:
    """Cross-file rules: browser surfaces and press detents."""
    if not markup_by_file:
        return
    name = sorted(markup_by_file)[0]
    for surface, pattern in (("::selection", r"::selection\b"),
                             ("caret", r"caret-color\b"),
                             ("scrollbar", r"::-webkit-scrollbar|scrollbar-color\b"),
                             ("focus ring", r":focus-visible\b")):
        if not re.search(pattern, all_css):
            out.add("SLOP-017", "medium", name, f"browser surface unthemed: {surface}")

    commit_classes = re.compile(r"(?:^|[-_ ])(?:confirm|submit|apply|save|drain|delete|destroy|deploy|commit)"
                                r"(?:$|[-_ ])", re.IGNORECASE)
    commit_buttons = 0
    for file, markup in markup_by_file.items():
        for match in re.finditer(r"<button([^>]*)>", markup, re.IGNORECASE):
            attrs = match.group(1)
            classes = " ".join(CLASS_RE.findall(attrs))
            if commit_classes.search(classes):
                commit_buttons += 1
    has_active = re.search(r":active\b", all_css)
    if commit_buttons and not has_active:
        out.add("SLOP-018", "high", name,
                f"{commit_buttons} commit control(s) with no :active press detent")


def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic slop/rut scan over a prototype artifact")
    parser.add_argument("--artifacts", required=True)
    parser.add_argument("--out", default="-")
    args = parser.parse_args()
    result = detect(pathlib.Path(args.artifacts))
    if args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        bl.write_json(pathlib.Path(args.out), result)
    return 0 if result["status"] in ("detected",) else 2


if __name__ == "__main__":
    sys.exit(main())
