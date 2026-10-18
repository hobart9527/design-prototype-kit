#!/usr/bin/env python3
"""Rule-ID detector: the craft floor's prose and the machine checks, anchored both ways.

`craft-floor.md` states the floor in prose; this detector checks the part a shallow
artifact scan can reach. Without an explicit anchor, a rule can be added to one side
and not the other, and the prose quietly stops describing what is enforced.

This module is that anchor. Every craft-floor rule carries a stable id, and each id
declares how it is detected:

  `check`      a function in this module, runnable against an artifact
  `prose_only` no mechanical check — a judgement the craft floor owns by hand

`anchor_report()` returns the registry in both directions, so a test can assert the
prose and the detectors still agree. Rules that are prose-only are listed as such
rather than silently absent: "not machine-checkable" is a status, not a gap.

Detection is deliberately shallow — a regex over the artifact's own bytes. It exists
to keep the registry honest, not to replace the craft review.

An HTML artifact is scanned together with the stylesheets it actually links, so a
rule that lives in `anchor.css` (`:active`, `tabular-nums`, `::selection`) is seen
when the artifact is `index.html`. Folded sources and unreadable links are both
reported: a link the detector could not read is `unresolved`, never silently
absent, because "not measured" and "clean" are different statuses.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

# -- detectors -----------------------------------------------------------------

class _StylesheetLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []
        self.inline_styles: list[str] = []
        self._in_style = False
        self._style_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag.lower() == "link" and "stylesheet" in (values.get("rel") or "").lower().split():
            href = values.get("href")
            if href:
                self.hrefs.append(href)
        elif tag.lower() == "style":
            self._in_style = True
            self._style_parts = []

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self._style_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._in_style:
            self.inline_styles.append("".join(self._style_parts))
            self._in_style = False
            self._style_parts = []


def _scan_root(path: pathlib.Path) -> pathlib.Path:
    """The nearest ancestor that owns the artifact — a repository root or the
    directory holding a `prototype/` tree.

    An anchor links shared token CSS that lives outside its own folder
    (`../../../shared/tokens.css`), so confining reads to the artifact's parent
    would report a real stylesheet as unresolved. The ownership boundary is
    still bounded: a link that escapes the repository is unresolved, never read.
    """
    for parent in (path.parent, *path.parent.parents):
        if (parent / ".git").exists() or (parent / "prototype").is_dir():
            return parent
    return path.parent


def _artifact_sources(path: pathlib.Path) -> tuple[str, list[str], list[str]]:
    """Read the HTML artifact and local linked CSS without following remote URLs."""
    sources: list[str] = []
    unresolved: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return "", sources, [str(path)]
    sources.append(str(path))
    parser = _StylesheetLinks()
    try:
        parser.feed(text)
    except Exception:
        return text, sources, unresolved
    pieces = [text, *parser.inline_styles]
    root = _scan_root(path).resolve()
    for href in parser.hrefs:
        if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.IGNORECASE) or href.startswith("//"):
            continue
        css_path = (path.parent / href.split("#", 1)[0].split("?", 1)[0]).resolve()
        try:
            css_path.relative_to(root)
        except ValueError:
            unresolved.append(href)
            continue
        try:
            pieces.append(css_path.read_text(encoding="utf-8", errors="replace"))
            sources.append(str(css_path))
        except OSError:
            unresolved.append(href)
    return "\n".join(pieces), sources, unresolved


def _artifact_text(path: pathlib.Path) -> str:
    return _artifact_sources(path)[0]


def _source_report(path: pathlib.Path) -> dict[str, list[str]]:
    _, sources, unresolved = _artifact_sources(path)
    return {"sources": sources, "unresolved_links": unresolved}


# A rule whose applicability depends on the artifact's own declaration (the
# content locale, say) returns this instead of True/False, so "does not apply"
# is a recorded status rather than a false `clear`.
NOT_APPLICABLE = object()


def _has_active_detent(path: pathlib.Path) -> bool:
    return bool(re.search(r":active\b", _artifact_text(path)))


def _has_tabular_nums(path: pathlib.Path) -> bool:
    return bool(re.search(r"font-variant-numeric\s*:\s*[^;}]*tabular-nums",
                          _artifact_text(path)))


def _has_focus_visible(path: pathlib.Path) -> bool:
    return bool(re.search(r":focus-visible\b", _artifact_text(path)))


def _has_selection_theme(path: pathlib.Path) -> bool:
    return bool(re.search(r"::selection\b", _artifact_text(path)))


def _has_caret_theme(path: pathlib.Path) -> bool:
    return bool(re.search(r"caret-color\b", _artifact_text(path)))


def _has_scrollbar_theme(path: pathlib.Path) -> bool:
    return bool(re.search(r"::-webkit-scrollbar|scrollbar-color\b", _artifact_text(path)))


def _has_gradient_text(path: pathlib.Path) -> bool:
    return bool(re.search(r"background-clip\s*:\s*text", _artifact_text(path), re.IGNORECASE))


def _has_emoji_icon(path: pathlib.Path) -> bool:
    emoji = re.compile("[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F2FF]")
    return bool(emoji.search(_artifact_text(path)))


def _has_action_feedback(path: pathlib.Path) -> bool:
    text = _artifact_text(path)
    has_commit = bool(re.search(
        r"(?:data-action|class)\s*=\s*[\"'][^\"']*(?:drain|delete|destroy|terminate|offline|rollback|deploy)",
        text, re.IGNORECASE))
    if not has_commit:
        return False
    return bool(re.search(
        r"处理中|进行中|执行中|已排空|已完成|已执行|已提交|已生效|已切换|已迁移|已回滚|撤销|撤回|回滚|恢复|"
        r"draining|rollback|undo|revert|restore|in progress|completed",
        text, re.IGNORECASE))


def _has_reduced_motion(path: pathlib.Path) -> bool:
    text = _artifact_text(path)
    if not re.search(r"prefers-reduced-motion", text, re.IGNORECASE):
        return False
    # Presence alone is not correctness: a reduced-motion block that leaves
    # transitions and animations intact is a token gesture. The fallback must
    # actually neutralize motion inside its media block (duration ~0 or none,
    # or scroll-behavior forced to auto), matching the floor's "motion is
    # enhancement, state change is contract".
    block = re.search(r"@media[^{]*prefers-reduced-motion[^{]*\{(.*?)\}\s*\}",
                      text, re.IGNORECASE | re.DOTALL)
    body = block.group(1) if block else text
    return bool(re.search(
        r"(animation|transition)[^;{}]*(duration|delay)\s*:\s*0(?:\.0+1)?m?s|"
        r"animation\s*:\s*none|transition\s*:\s*none|scroll-behavior\s*:\s*auto",
        body, re.IGNORECASE))


def _has_aria_live(path: pathlib.Path) -> bool:
    return bool(re.search(r"aria-live\s*=\s*[\"'](?:polite|assertive)[\"']",
                          _artifact_text(path), re.IGNORECASE))


def _has_fluid_type(path: pathlib.Path) -> bool:
    return bool(re.search(r"font-size\s*:[^;{}]*\b(?:clamp|min|max)\(|--[\w-]*(?:font|text|type)[\w-]*\s*:\s*clamp\(",
                          _artifact_text(path), re.IGNORECASE))

def _has_color_scheme(path: pathlib.Path) -> bool:
    text = _artifact_text(path)
    return bool(re.search(r"color-scheme\s*:|<meta[^>]+name=[\"']color-scheme[\"']", text, re.IGNORECASE))

def _has_dark_mode_adaptation(path: pathlib.Path) -> bool:
    # A dual-theme surface adapts to the OS scheme rather than pinning one
    # palette: prefers-color-scheme present, or color-scheme declares both
    # light and dark. Advisory — a single-scheme product legitimately stays
    # dark-only (CRAFT-THEME-ORIGIN), so this is a presence signal, not a floor.
    text = _artifact_text(path)
    return bool(re.search(r"prefers-color-scheme", text, re.IGNORECASE)
                or re.search(r"color-scheme\s*:\s*light\s+dark|color-scheme\s*:\s*dark\s+light",
                             text, re.IGNORECASE))

def _has_lang_and_dir(path: pathlib.Path) -> bool:
    # i18n floor: the root element names its locale so hyphenation, font
    # selection and bidi resolve. Cheap text check on the html tag.
    text = _artifact_text(path)
    return bool(re.search(r"<html[^>]+\blang\s*=\s*[\"'][^\"']+[\"']", text, re.IGNORECASE))

def _has_loading_state(path: pathlib.Path) -> bool:
    return bool(re.search(r"aria-busy\s*=|skeleton|shimmer|role=[\"']progressbar[\"']|<progress\b",
                          _artifact_text(path), re.IGNORECASE))

def _has_text_wrap(path: pathlib.Path) -> bool:
    # Headings balance, running text pretty; the cheapest modern typographic win
    # and a pure presence signal (advisory).
    return bool(re.search(r"text-wrap\s*:\s*(balance|pretty)", _artifact_text(path), re.IGNORECASE))

def _has_viewport_units(path: pathlib.Path) -> bool:
    # Dynamic viewport units survive mobile browser chrome; `100vh` does not.
    return bool(re.search(r"\b\d+(?:\.\d+)?(?:dvh|svh|lvh)\b", _artifact_text(path), re.IGNORECASE))

def _has_view_transition(path: pathlib.Path) -> bool:
    # A view transition is only a floor when its motion can be neutralized:
    # pairing rule, mirroring CRAFT-REDUCED-MOTION's shape.
    text = _artifact_text(path)
    return bool(re.search(r"startViewTransition", text)
                and _has_reduced_motion(path))

def _has_cjk_typeset(path: pathlib.Path) -> object:
    text = _artifact_text(path)
    lang = re.search(r"<html[^>]+\blang\s*=\s*[\"']([^\"']+)[\"']", text, re.IGNORECASE)
    locale = (lang.group(1) if lang else "").lower()
    if not (locale.startswith("zh") or locale.startswith("ja") or locale.startswith("ko")):
        return NOT_APPLICABLE
    return bool(re.search(r"text-spacing-trim|text-autospace|line-break\s*:|:lang\(", text, re.IGNORECASE))

def _hex_outside_tokens(path: pathlib.Path) -> bool:
    # A component stylesheet that names a raw colour instead of a token breaks the
    # one-way inheritance. Custom-property declarations are the token layer and
    # are exempt; only a hex that lands in a non-token declaration counts.
    text = re.sub(r"--[\w-]+\s*:[^;{}]*", "", _artifact_text(path))
    return bool(re.search(r"#[0-9a-fA-F]{3,8}\b", text))

def _has_font_loading(path: pathlib.Path) -> bool:
    # A locally-embedded font declares @font-face with a display strategy so a
    # delayed or failed face never hides content. No @font-face at all means no
    # loading risk to measure.
    text = _artifact_text(path)
    if not re.search(r"@font-face", text, re.IGNORECASE):
        return NOT_APPLICABLE
    return bool(re.search(r"font-display\s*:", text, re.IGNORECASE))

def _has_haptic_pairing(path: pathlib.Path) -> bool:
    # A vibration call is only a floor when a non-haptic channel carries the same
    # signal: the pairing shape shared with CRAFT-REDUCED-MOTION.
    text = _artifact_text(path)
    if not re.search(r"navigator\.vibrate|\.vibrate\(", text):
        return NOT_APPLICABLE
    return bool(re.search(r"aria-live\s*=|role=[\"']status[\"']|role=[\"']alert[\"']", text, re.IGNORECASE))

# -- registry ------------------------------------------------------------------
# id -> (rule as the craft floor states it, kind, detector or None)
# A `prose_only` entry names why it cannot be mechanised, so the reason is on the
# record rather than inferred from the detector's absence.

RULES: dict[str, dict] = {
    "CRAFT-PRESS-DETENT": {
        "prose": "every commit control shows a perceptible :active change",
        "kind": "check", "polarity": "presence", "detector": _has_active_detent,
    },
    "CRAFT-TABULAR-NUMS": {
        "prose": "values that update in place or align in columns carry tabular-nums",
        "kind": "check", "polarity": "presence", "detector": _has_tabular_nums,
    },
    "CRAFT-FOCUS-RING": {
        "prose": "focus rings are themed from the palette, not left at browser default",
        "kind": "check", "polarity": "presence", "detector": _has_focus_visible,
    },
    "CRAFT-SELECTION": {
        "prose": "text selection carries the design",
        "kind": "check", "polarity": "presence", "detector": _has_selection_theme,
    },
    "CRAFT-CARET": {
        "prose": "the caret carries the design",
        "kind": "check", "polarity": "presence", "detector": _has_caret_theme,
    },
    "CRAFT-SCROLLBAR": {
        "prose": "custom scrollbars carry the design",
        "kind": "check", "polarity": "presence", "detector": _has_scrollbar_theme,
    },
    "CRAFT-NO-GRADIENT-TEXT": {
        "prose": "gradient text is refused as emphasis",
        "kind": "check", "polarity": "violation", "detector": _has_gradient_text,
    },
    "CRAFT-NO-EMOJI-ICON": {
        "prose": "emoji or Unicode glyphs are not the icon system",
        "kind": "check", "polarity": "violation", "detector": _has_emoji_icon,
    },
    # Judgement calls the craft floor owns by hand. Listed so their absence from
    # the detectors reads as a decision, not an oversight.
    "CRAFT-CONCENTRIC-RADII": {
        "prose": "a rounded child in a rounded parent satisfies R_inner = max(0, R_outer - P)",
        "kind": "prose_only",
        "why": "needs the computed geometry of a nested pair, not a text scan; "
               "checked by verify_prototype_quality's rendered probe",
    },
    "CRAFT-SURFACE-SHEEN": {
        "prose": "hairline highlights are optional when their optical character supports the direction; flat surfaces and border-only containment are equally valid",
        "kind": "prose_only",
        "why": "surface optics are chosen from the committed direction; token presence cannot establish whether sheen is appropriate",
    },
    "CRAFT-KINETIC-SPRING": {
        "prose": "motion follows task precision and direction; spring, easing, linear motion and instant changes are valid, with no required spring token",
        "kind": "prose_only",
        "why": "motion physics depend on task precision and the committed direction; a spring token is neither required nor sufficient",
    },
    "CRAFT-ACTION-FEEDBACK": {
        "prose": "destructive or high-stakes actions show consequence before commit, explicit status after, and a recovery route",
        "kind": "check", "polarity": "presence", "detector": _has_action_feedback,
    },
    "CRAFT-REDUCED-MOTION": {
        "prose": "spring or animated transitions pair with a prefers-reduced-motion fallback",
        "kind": "check", "polarity": "presence", "detector": _has_reduced_motion,
    },
    "CRAFT-ARIA-LIVE": {
        "prose": "dynamically updating status regions expose aria-live so assistive tech perceives change",
        "kind": "check", "polarity": "presence", "detector": _has_aria_live,
    },
    "CRAFT-FLUID-TYPE": {
        "prose": "display and body type scale fluidly between viewports (clamp/min/max) instead of jumping at breakpoints",
        "kind": "check", "polarity": "presence", "detector": _has_fluid_type,
    },
    "CRAFT-COLOR-SCHEME": {
        "prose": "the declared theme sets color-scheme so native controls, scrollbars and form fields follow it",
        "kind": "check", "polarity": "presence", "detector": _has_color_scheme,
    },
    "CRAFT-DARK-MODE": {
        "prose": "when the brief spans lighting conditions, the surface adapts to prefers-color-scheme or declares a light+dark color-scheme",
        "kind": "check", "polarity": "presence", "detector": _has_dark_mode_adaptation,
    },
    "CRAFT-LANG": {
        "prose": "the root element declares lang (and dir where applicable) so fonts, hyphenation and bidi resolve for the content locale",
        "kind": "check", "polarity": "presence", "detector": _has_lang_and_dir,
    },
    "CRAFT-LOADING-STATE": {
        "prose": "regions that load or refresh show a skeleton or aria-busy state rather than blank space",
        "kind": "check", "polarity": "presence", "detector": _has_loading_state,
    },
    "CRAFT-TEXT-WRAP": {
        "prose": "headings balance and running text uses pretty wrapping instead of leaving orphans",
        "kind": "check", "polarity": "presence", "detector": _has_text_wrap,
    },
    "CRAFT-VIEWPORT-UNITS": {
        "prose": "full-height layout uses dynamic viewport units (dvh/svh/lvh) so mobile browser chrome does not clip it",
        "kind": "check", "polarity": "presence", "detector": _has_viewport_units,
    },
    "CRAFT-VIEW-TRANSITION": {
        "prose": "a view transition (startViewTransition) pairs with a prefers-reduced-motion fallback that neutralizes the motion",
        "kind": "check", "polarity": "presence", "detector": _has_view_transition,
    },
    "CRAFT-CJK-TYPESET": {
        "prose": "CJK content sets text-spacing-trim/text-autospace, line-break and a :lang() font stack so punctuation, kinsoku and glyph forms resolve",
        "kind": "check", "polarity": "presence", "detector": _has_cjk_typeset,
    },
    "CRAFT-TOKEN-ONLY": {
        "prose": "component declarations reference design tokens; a raw hex outside the token layer breaks the one-way inheritance",
        "kind": "check", "polarity": "violation", "detector": _hex_outside_tokens,
    },
    "CRAFT-FONT-LOADING": {
        "prose": "a self-hosted @font-face carries a font-display strategy so a delayed or failed face never hides content",
        "kind": "check", "polarity": "presence", "detector": _has_font_loading,
    },
    "CRAFT-HAPTIC-PAIRING": {
        "prose": "a vibration call pairs with a non-haptic (visual or ARIA) channel carrying the same signal",
        "kind": "check", "polarity": "presence", "detector": _has_haptic_pairing,
    },
    "CRAFT-CONTEXTUAL-METRIC": {
        "prose": "a metric carries a baseline, unit, delta or sparkline; a naked number is not information",
        "kind": "prose_only",
        "why": "judged by the VPQ data-craft signal against the rendered DOM, not by a text pattern",
    },
    "CRAFT-TOUCH-TARGET": {
        "prose": "interactive controls measure at least 44x44px in touch contexts",
        "kind": "prose_only",
        "why": "needs rendered box metrics at a declared viewport",
    },
    "CRAFT-CARD-GRID-EARNED": {
        "prose": "same-size card grids are refused unless the objects are genuinely peers",
        "kind": "prose_only",
        "why": "whether a card grid is earned is a design judgement",
    },
    "CRAFT-NO-EYEBROW": {
        "prose": "an eyebrow or kicker above a heading is refused",
        "kind": "prose_only",
        "why": "distinguishing a kicker from a legitimate label needs reading the content",
    },
    "CRAFT-REAL-CONTENT": {
        "prose": "plausible domain copy and real assets, never a gradient blob in an image slot",
        "kind": "prose_only",
        "why": "content plausibility is judged against the brief, not a pattern",
    },
    "CRAFT-THEME-ORIGIN": {
        "prose": "light or dark is chosen from the use scene, not the product category",
        "kind": "prose_only",
        "why": "the use scene is in the brief, not the artifact",
    },

    # -- universal design content invariants (Pillar 3) ------------------------
    # Registered as prose_only so the anchor test can see them and any later
    # mechanization has a mount point. They are content invariants, not CSS
    # patterns: a text scan cannot judge whether a capability is fabricated.
    "INV-ENTITY-GROUNDING": {
        "prose": "every surface, object, integration and promised capability is grounded in what the brief actually names; no fabricated lateral domains, billing, scheduling, notification channels or unprompted technical capabilities",
        "kind": "prose_only",
        "why": "grounding is judged against the brief's entity list and scope, not an artifact pattern",
    },
    "INV-HISTORICAL-FIDELITY": {
        "prose": "declared irreversible history is never retroactively negated; recovery applies only to prospective in-flight operations",
        "kind": "prose_only",
        "why": "whether a claim reverses a stated fact needs the brief's history, not a regex",
    },
    "INV-LIFECYCLE-CLOSURE": {
        "prose": "workflows close at the requested boundary; no speculative post-task stages, derivative systems or auto-generated reports beyond explicit scope",
        "kind": "prose_only",
        "why": "scope is defined by the request, not detectable in the artifact",
    },
}

def scan(artifact: pathlib.Path) -> dict:
    """Run every mechanical rule against one artifact. Judgement rules are listed."""
    artifact = pathlib.Path(artifact)
    if not artifact.is_file():
        raise FileNotFoundError(f"Craft floor detector target artifact not found: {artifact}")
    findings, unchecked = [], []
    for rule_id, entry in sorted(RULES.items()):
        if entry["kind"] != "check":
            unchecked.append({"rule": rule_id, "why": entry["why"]})
            continue
        try:
            outcome = entry["detector"](artifact)
        except Exception as exc:  # a broken detector must surface, not read as clean
            findings.append({"rule": rule_id, "status": "error", "error": str(exc)})
            continue
        if outcome is NOT_APPLICABLE:
            findings.append({"rule": rule_id, "status": "not_applicable",
                             "polarity": entry["polarity"], "prose": entry["prose"]})
            continue
        findings.append({"rule": rule_id, "status": "hit" if outcome else "clear",
                         "polarity": entry["polarity"], "prose": entry["prose"]})
    sources = _source_report(artifact)
    if sources["unresolved_links"]:
        findings.append({"rule": "SOURCE-COVERAGE", "status": "unmeasured",
                         "unresolved_links": sources["unresolved_links"],
                         "prose": "one or more local stylesheets could not be scanned"})
    checked = sum(1 for f in findings if f["status"] in ("hit", "clear"))
    return {"detector": "craft-floor", "artifact": str(artifact),
            "sources": sources["sources"], "unresolved_links": sources["unresolved_links"],
            "source_coverage": "partial" if sources["unresolved_links"] else "complete",
            "findings": findings, "unchecked": unchecked, "checked": checked,
            "unmeasured": sum(1 for f in findings if f["status"] in ("not_applicable", "unmeasured"))}


def anchor_report() -> dict:
    """The registry in both directions, for the drift test."""
    return {
        "rules": {rid: {"kind": e["kind"], "prose": e["prose"], **({"polarity": e["polarity"]} if "polarity" in e else {})} for rid, e in RULES.items()},
        "counts": {
            "total": len(RULES),
            "check": sum(1 for e in RULES.values() if e["kind"] == "check"),
            "prose_only": sum(1 for e in RULES.values() if e["kind"] == "prose_only"),
        },
    }


def advisory_summary(result: dict) -> str:
    """One-screen digest of a scan, for a post-write advisory.

    The full report is a file a reviewer reads; this is the line a writer needs
    while the artifact is still open. Only hits and unmeasured items are named —
    a clear rule is not news, and dropping it keeps the summary short enough to
    actually be read.
    """
    hits = [f["rule"] for f in result["findings"] if f["status"] == "hit"]
    errors = [f"{f['rule']} ({f['error']})" for f in result["findings"] if f["status"] == "error"]
    unmeasured = [f["rule"] for f in result["findings"] if f["status"] == "unmeasured"]
    if result["unresolved_links"]:
        unmeasured.append("SOURCE-COVERAGE")
    parts = [f"craft-floor scan of {pathlib.Path(result['artifact']).name}: "
             f"{result['checked']} checked, {len(hits)} hit, {result['unmeasured']} unmeasured."]
    if hits:
        parts.append("Hits (leads to confirm against the render, not verdicts): " + ", ".join(hits) + ".")
    if unmeasured:
        parts.append("Not measured — do not read as clean: " + ", ".join(unmeasured) + ".")
    if errors:
        parts.append("Detector errors: " + ", ".join(errors) + ".")
    if not hits and not unmeasured and not errors:
        parts.append("No hits and full source coverage.")
    return " ".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Craft-floor rule-ID detector")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--out", default="-")
    parser.add_argument("--summary", action="store_true",
                         help="Print a short advisory summary instead of the full report")
    args = parser.parse_args()
    try:
        result = scan(pathlib.Path(args.artifact))
    except FileNotFoundError as err:
        sys.stderr.write("Error: " + str(err) + "\n")
        return 1
    if args.summary:
        print(advisory_summary(result))
    elif args.out == "-":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        pathlib.Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
