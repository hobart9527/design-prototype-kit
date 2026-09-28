#!/usr/bin/env python3
"""Truthful, contract-driven checks for a prototype artifact.

Structural checks read a parsed DOM; style checks read the declarations the
document owns. Browser, visual, and human evidence are reported as unverified
unless an evidence manifest explicitly records them.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prototype_context  # noqa: E402


# --- Minimal DOM layer -----------------------------------------------------
# Structural assertions read a parsed tree, not the source text. A class inside
# a comment, a tag named in prose, or a handler mentioned in a string must never
# satisfy a DOM check, so every structural fact comes from the tree. Style
# declarations stay textual, but only from the <style> elements and style
# attributes that actually own them — never from the document at large.

_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})

# Inline event-handler attributes, by the events this tool asserts on.
_INLINE_HANDLERS = ("onclick", "onkeydown", "onkeyup", "onsubmit",
                    "ontouchstart", "ontouchend")

# Tokens that authorize a continuous animation (high-yield zones and the
# standard accessibility loading states).
_AUTHORIZED_ANIMATION = re.compile(
    r"\b(?:high-yield|pulse|heartbeat|beacon|live-indicator|radar|spinner|loading|loader|progress)\b",
    re.IGNORECASE)

# Class tokens that make a metric readable without a chart.
_CONTEXT_MODIFIER = re.compile(r"(?:unit|baseline|sparkline|threshold|reference|trend|delta|badge|status)")

# Metric containers, and the unit that must follow the number inside one.
_METRIC_CLASS = re.compile(r"(?:stat|metric|kpi|value|num|count)")
_METRIC_UNIT = re.compile(r"^\s*[\d.,]+\s*(?:[a-zA-Z%/$€¥°]|/[a-zA-Z]+)")

# Classes reserved for secondary affordances, where the signature accent is
# forbidden.
_FORBIDDEN_ACCENT_CLASSES = frozenset({
    "draft", "pending", "secondary", "ghost", "cancel", "subtle", "base", "zero-borrow",
})


def _strip_comments(text: str, line_comment: bool) -> str:
    """Blank out comments without touching string literals.

    A quoted `//` (a URL) or a `/*` inside `content: "..."` is content, not a
    comment, so the scan tracks quote state and only drops what is truly
    commented out. Blanked spans keep their newlines so line structure holds.
    """
    out: list[str] = []
    index = 0
    length = len(text)
    quote = ""
    while index < length:
        char = text[index]
        if quote:
            out.append(char)
            if char == "\\" and index + 1 < length:
                out.append(text[index + 1])
                index += 2
                continue
            if char == quote:
                quote = ""
            index += 1
            continue
        if char in ("'", '"', "`"):
            quote = char
            out.append(char)
            index += 1
            continue
        if text.startswith("/*", index):
            end = text.find("*/", index + 2)
            end = length if end == -1 else end + 2
            out.append("\n" * text.count("\n", index, end))
            index = end
            continue
        if line_comment and text.startswith("//", index):
            end = text.find("\n", index)
            index = length if end == -1 else end
            continue
        out.append(char)
        index += 1
    return "".join(out)


def _strip_css_comments(text: str) -> str:
    return _strip_comments(text, line_comment=False)


def _strip_js_comments(text: str) -> str:
    return _strip_comments(text, line_comment=True)


class _Element:
    """One parsed element: tag, attributes, children, and its own text runs."""

    __slots__ = ("tag", "attrs", "parent", "children", "own_text")

    def __init__(self, tag: str, attrs: dict[str, str], parent: "_Element | None") -> None:
        self.tag = tag
        self.attrs = attrs
        self.parent = parent
        self.children: list[_Element] = []
        self.own_text: list[str] = []

    def get(self, name: str, default: str = "") -> str:
        return self.attrs.get(name, default)

    @property
    def classes(self) -> set[str]:
        return set(self.get("class").split())

    def text(self) -> str:
        """This element's own text, excluding its descendants'."""
        return "".join(self.own_text)

    def descendants(self) -> list["_Element"]:
        out: list[_Element] = []
        stack = list(reversed(self.children))
        while stack:
            el = stack.pop()
            out.append(el)
            stack.extend(reversed(el.children))
        return out


class _DomBuilder(HTMLParser):
    def __init__(self, doc: "_Document") -> None:
        super().__init__(convert_charrefs=True)
        self.doc = doc
        self.stack: list[_Element] = [doc.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        element = _Element(
            tag,
            {name.lower(): (value if value is not None else "") for name, value in attrs},
            self.stack[-1],
        )
        self.stack[-1].children.append(element)
        self.doc.elements.append(element)
        if tag not in _VOID_TAGS:
            self.stack.append(element)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in _VOID_TAGS:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].own_text.append(data)

    def handle_comment(self, data: str) -> None:
        # Kept as a fact about the document, never as document content: a
        # commented-out state hook or metric is not a delivered one.
        self.doc.comments.append(data)


class _Document:
    """A parsed document with the structural queries the assertions need."""

    def __init__(self, source: str) -> None:
        self.source = source
        self.root = _Element("#document", {}, None)
        self.elements: list[_Element] = []
        self.comments: list[str] = []
        builder = _DomBuilder(self)
        builder.feed(source)
        builder.close()
        # Comments are stripped from both executable layers: a commented-out
        # listener is not a listener, and a class named in a CSS comment is not
        # a selector. HTML comments never reach these strings in the first place.
        self.style_text = _strip_css_comments(
            "\n".join(el.text() for el in self.elements if el.tag == "style"))
        self.script_text = _strip_js_comments(
            "\n".join(el.text() for el in self.elements if el.tag == "script"))
        self.text = self._visible_text()

    def _visible_text(self) -> str:
        parts: list[str] = []

        def walk(node: _Element) -> None:
            for child in node.children:
                if child.tag in ("script", "style"):
                    continue
                parts.extend(child.own_text)
                walk(child)

        walk(self.root)
        return "".join(parts)

    def declarations(self) -> str:
        """Every CSS declaration the document owns: <style> bodies and style attributes."""
        parts = [self.style_text]
        parts.extend(el.get("style") for el in self.elements if "style" in el.attrs)
        return "\n".join(parts)

    def contains(self, needle: str) -> bool:
        """True when the needle is real document content, never a comment."""
        if needle in self.text or needle in self.script_text or needle in self.style_text:
            return True
        return any(needle in value for el in self.elements for value in el.attrs.values())

    def tags(self, *names: str) -> list[_Element]:
        wanted = set(names)
        return [el for el in self.elements if el.tag in wanted]

    def with_attr(self, name: str) -> list[_Element]:
        return [el for el in self.elements if name in el.attrs]

    def attr_equals(self, name: str, value: str) -> bool:
        return any(el.get(name) == value for el in self.elements)

    def controls(self) -> list[_Element]:
        """Reachable controls: buttons, anchors with an href, and button roles."""
        return [el for el in self.elements
                if el.tag == "button"
                or (el.tag == "a" and "href" in el.attrs)
                or el.get("role") == "button"]

    def links_to(self, surface_id: str) -> bool:
        return any(surface_id in el.get("href") for el in self.elements if "href" in el.attrs)

    def has_event_binding(self) -> bool:
        if "addEventListener(" in self.script_text:
            return True
        return any(name in el.attrs for el in self.elements for name in _INLINE_HANDLERS)

    def has_keyboard_binding(self) -> bool:
        if re.search(r"addEventListener\s*\(\s*['\"]key(?:down|up)['\"]", self.script_text, re.IGNORECASE):
            return True
        return any(name in el.attrs for el in self.elements for name in ("onkeydown", "onkeyup"))

    def has_feedback_container(self) -> bool:
        for el in self.elements:
            if el.get("role") in ("status", "alert"):
                return True
            if re.search(r"\b(?:toast|notification|feedback|alert-box|status-message|snackbar)\b",
                         el.get("class"), re.IGNORECASE):
                return True
            if re.search(r"(?:toast|feedback|status-msg)", el.get("id"), re.IGNORECASE):
                return True
            if "data-feedback" in el.attrs or "data-toast" in el.attrs:
                return True
        return False

    def has_touch_binding(self) -> bool:
        if re.search(r"addEventListener\s*\(\s*['\"](?:touch|pointer|click)['\"]",
                     self.script_text, re.IGNORECASE):
            return True
        return any(name in el.attrs for el in self.elements for name in ("ontouchstart", "ontouchend", "onclick"))

    def has_state_hook(self) -> bool:
        """A state the document can actually switch, never a quoted label.

        Script signals are matched by API shape (`location.hash`, `dataset.`
        assignment, `setAttribute('data-state'`), so a state name that merely
        appears inside a string literal is not read as a hook.
        """
        if re.search(r"addEventListener\s*\(\s*['\"](?:hashchange|popstate)['\"]", self.script_text):
            return True
        if re.search(r"location\.hash", self.script_text):
            return True
        if re.search(r"dataset\.\w+\s*=|setAttribute\s*\(\s*['\"]data-", self.script_text):
            return True
        for el in self.elements:
            if "data-state" in el.attrs:
                return True
            if re.search(r"(?:empty|loading|view-mode|state-)", el.get("class")):
                return True
            if re.search(r"(?:empty|loading|view-mode)", el.get("id")):
                return True
        return False

    def has_authorized_animation(self) -> bool:
        for el in self.elements:
            if el.get("aria-busy").lower() == "true" or el.get("role") == "progressbar":
                return True
            if any(_AUTHORIZED_ANIMATION.search(el.get(name)) for name in ("class", "id", "data-zone")):
                return True
        return False

    def has_context_modifier(self) -> bool:
        for el in self.elements:
            if _CONTEXT_MODIFIER.search(el.get("class")):
                return True
            if any(name in el.attrs for name in
                   ("data-unit", "data-baseline", "data-threshold", "data-trend", "data-delta")):
                return True
        return False

    def has_metric_with_unit(self) -> bool:
        for el in self.elements:
            if _METRIC_CLASS.search(el.get("class")) and _METRIC_UNIT.match(el.text()):
                return True
        return False

    def has_charted_metric(self) -> bool:
        for el in self.tags("svg"):
            if any(child.tag in ("polyline", "path", "rect", "line", "circle") for child in el.descendants()):
                return True
        return False

    def empty_state_containers(self) -> list[_Element]:
        out: list[_Element] = []
        for el in self.tags("div", "section", "aside", "main"):
            marker = f"{el.get('data-for')} {el.get('data-state')}"
            if re.search(r"empty", marker, re.IGNORECASE) or re.search(
                    r"\b(?:empty-state|state-empty|is-empty)\b", el.get("class")):
                out.append(el)
        return out


def _pending_sibling_marked(dom: _Document, surface_id: str) -> bool:
    """True when an undelivered sibling is represented without a live href.

    An unreachable surface may not be linked, but it must not vanish from the
    shell either: a disabled affordance or an explicit text/data representation
    keeps the destination review-visible without producing a 404.
    """
    for el in dom.elements:
        if not any(surface_id in f"{name} {value}" for name, value in el.attrs.items()):
            continue
        if el.get("aria-disabled").lower() == "true" or "disabled" in el.attrs or "data-disabled" in el.attrs:
            return True
    return any(el.get(name) == surface_id for el in dom.elements
               for name in ("data-sibling", "data-pending", "data-surface"))


_ACTION_COLUMN_KEYS = (
    ("action_id", ("action id", "action")),
    ("trigger_btn", ("trigger button", "trigger")),
    ("commit_btn", ("commit action", "commit")),
    ("feedback_style", ("feedback style", "completion feedback", "feedback", "toast")),
)


def _action_column_map(header_cells: list[str]) -> dict[str, int]:
    """Bind each action field to the header column that owns it.

    Reading by column width cannot distinguish the canonical 7-column Proximity
    ladder from a legacy 6-column table; the authored header can.
    """
    normalized = [re.sub(r"[\s*`]+", " ", cell).strip().lower() for cell in header_cells]
    mapping: dict[str, int] = {}
    for field, fragments in _ACTION_COLUMN_KEYS:
        for index, header in enumerate(normalized):
            if index in mapping.values():
                continue
            if any(fragment in header for fragment in fragments):
                mapping[field] = index
                break
    return mapping


def _action_cell(row_cells: list[str], columns: dict[str, int], field: str) -> str:
    index = columns.get(field)
    return row_cells[index].strip() if index is not None and index < len(row_cells) else ""


def _collect_action_ids_from_markdown(text: str) -> set[str]:
    """Collect action ids from bullets, tables and contract:actions YAML blocks."""
    ids: set[str] = set()
    for m in re.finditer(r"`(action-[a-z0-9]+(?:-[a-z0-9]+)*)`", text):
        ids.add(m.group(1))
    for m in re.finditer(r"^\s*-?\s*id:\s*(action-[a-z0-9]+(?:-[a-z0-9]+)*)\s*$", text, re.MULTILINE):
        ids.add(m.group(1))
    return ids


def _ir_contract_path(path: Path) -> Path | None:
    """Resolve the canonical compiled IR JSON paired with a canonical .spec.md.

    The IR (`contracts/compiled/<slice>/r1.spec.json`) is the machine SSOT for
    contract items; Markdown is only a human view. Header rows and placeholder
    cells in that view must never become DOM assertions.
    """
    if not path.name.endswith(".spec.md"):
        return None
    candidate = path.parents[2] / "contracts/compiled" / path.parent.name / "r1.spec.json"
    return candidate if candidate.is_file() else None


def _ir_contract_items(path: Path) -> tuple[list[str], set[str]]:
    """Extract verifiable items and action ids from the compiled Spec IR.

    Returns (items, action_ids). Items are verbatim strings/tuples sourced only
    from machine-authored fields (actions, entities, surfaces), never from the
    Markdown rendering, so tables and placeholder rows cannot leak in.
    """
    try:
        ir = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return [], set()
    items: list[str] = []
    ids: set[str] = set()

    for action in ir.get("actions") or []:
        if not isinstance(action, dict):
            continue
        aid = str(action.get("id") or "").strip()
        if aid.startswith("action-"):
            ids.add(aid)
        label = str(action.get("label") or action.get("trigger") or "").strip()
        pair = tuple(s for s in (aid, label) if s)
        if pair:
            items.append(pair)

    scope = ir.get("scope") or {}
    topology = scope.get("topology_scope") or {}
    for surface in topology.get("selected_surfaces") or topology.get("declared_surfaces") or []:
        name = str(surface).strip()
        if name and len(name) > 2:
            items.append(name)

    return items, ids


def _contract_action_ids(path: Path | None) -> set[str]:
    """Resolve declared action ids from the contract and optional paired c1."""
    if not path or not path.is_file():
        return set()
    ir_path = _ir_contract_path(path)
    if ir_path:
        _, ids = _ir_contract_items(ir_path)
        return ids
    sources = [path.read_text(encoding="utf-8")]
    if not path.name.endswith(".spec.md"):
        try:
            paired = path.parents[2] / "contracts/slices" / path.parent.name / "c1.md"
            if paired.is_file():
                sources.append(paired.read_text(encoding="utf-8"))
        except (OSError, IndexError):
            pass
    ids: set[str] = set()
    for source in sources:
        ids.update(_collect_action_ids_from_markdown(source))
    return ids


def _contract_items(path: Path | None) -> list[str]:
    """Extract verifiable entity names, action IDs, or button labels.

    Canonical `.spec.md` contracts resolve to their compiled IR JSON first
    (machine SSOT); the Markdown parser below only serves legacy `r1.md`
    contracts where no IR exists. Header rows and placeholder cells in a
    Markdown table must never become DOM assertions.
    """
    if not path or not path.is_file():
        return []
    ir_path = _ir_contract_path(path)
    if ir_path:
        items, _ = _ir_contract_items(ir_path)
        if items:
            return items
    items: list[str] = []
    in_actions = False
    in_assertions = False
    in_shortcuts = False
    text = path.read_text(encoding="utf-8")

    # A legacy specification `r1.md` pairs with a slice contract `c1.md`. A
    # canonical `.spec.md` is a self-contained single-file RFC view with no paired
    # c1.md, so pairing is skipped on that path rather than reaching for a
    # contract the canonical layout does not author.
    sources_to_scan = [text]
    if not path.name.endswith(".spec.md"):
        try:
            paired_c1 = path.parents[2] / "contracts/slices" / path.parent.name / "c1.md"
            if paired_c1.is_file():
                sources_to_scan.append(paired_c1.read_text(encoding="utf-8"))
        except (OSError, IndexError):
            pass

    in_actions = False
    in_assertions = False
    in_shortcuts = False
    in_ledger = False

    for src in sources_to_scan:
        action_columns: dict[str, int] | None = None
        for line in src.splitlines():
            if "Action Verb Lifecycle" in line:
                in_actions = True
                action_columns = None
                in_assertions = False
                in_shortcuts = False
                in_ledger = False
                continue
            elif "Verifiable Design Assertions" in line or "Break Protocol" in line:
                in_actions = False
                in_assertions = True
                in_shortcuts = False
                in_ledger = False
                continue
            elif "Dual-Channel Ergonomics" in line or "Keyboard Shortcuts" in line or "Touch-First Ergonomics" in line:
                in_actions = False
                in_assertions = False
                in_shortcuts = True
                in_ledger = False
                continue
            elif "Cognitive Budgeting" in line or "Ledger" in line or "Omissions" in line or "Boundaries" in line or "Fault Tolerance" in line or "Error Recovery" in line or "Component constraints" in line or "Spec packet" in line or "Contract readiness" in line:
                in_actions = False
                in_assertions = False
                in_shortcuts = False
                in_ledger = True
                continue
            elif line.startswith("##"):
                in_actions = False
                in_assertions = False
                in_shortcuts = False
                in_ledger = False

            if not line.strip().startswith("|"):
                continue
            # Table separator rows and header cells never become contract items.
            cells = [re.sub(r"[*`]", "", c).strip() for c in line.strip().strip("|").split("|")]
            if not cells or not cells[0]:
                continue
            first_lower = cells[0].lower()
            if first_lower in {"action id", "assertion", "reality breaker", "shortcut key", "token", "surface", "ledger zone", "---"}:
                if in_actions and first_lower == "action id":
                    action_columns = _action_column_map(cells)
                continue
            if set(cells[0]) <= {"-", ":"}:
                continue

            if in_actions:
                act_id = cells[0].strip()
                if act_id.lower() in ("unspecified", "none", "n/a") or act_id.startswith("explore-"):
                    continue
                trig_lbl = cells[1].strip() if len(cells) > 1 else ""
                if "[hypothesis]" in trig_lbl.lower():
                    continue
                trigger_tuple = tuple(s for s in (act_id, trig_lbl) if s and s not in ("-", "---", "N/A", "Action ID", "Trigger Button Label", "unspecified", "Unspecified"))
                if trigger_tuple:
                    items.append(trigger_tuple)
                # Column identity comes from the authored header, so a 6- or 7-column
                # table (or any column order) yields the real commit button and feedback.
                cols = action_columns or _action_column_map(cells)
                commit_lbl = _action_cell(cells, cols, "commit_btn")
                toast_lbl = _action_cell(cells, cols, "feedback_style")
                if commit_lbl.lower() == "acknowledge" or "exploration settled" in toast_lbl.lower():
                    continue

                feedback_tuple = tuple(s for s in (commit_lbl, toast_lbl) if s and s not in ("-", "---", "N/A", "Commit Action Button", "Completion Feedback Toast", "Feedback Style", "Feedback Style (In-situ / Toast)", "unspecified", "Unspecified"))
                if feedback_tuple:
                    items.append(feedback_tuple)
            elif not in_assertions and not in_shortcuts and not in_ledger:
                items.append(cells[0])
    return [it for it in items if it]


def _find_contract(html: Path, explicit: str | None) -> Path | None:
    if explicit:
        return Path(explicit)
    for parent in [html.parent, *html.parents]:
        candidates = list((parent / "prototype/contracts").glob("**/*.md"))
        if candidates:
            return candidates[0]
    return None


def _evidence_state(html: Path) -> dict[str, str]:
    for parent in [html.parent, *html.parents]:
        manifest = parent / "prototype/evidence/handoff-manifest.json"
        if manifest.is_file():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                return {str(k): str(v) for k, v in data.get("verification", {}).items()}
            except (json.JSONDecodeError, OSError):
                return {}
    return {}


def _extract_section_text(text: str, *keywords: str) -> str:
    lines: list[str] = []
    in_sec = False
    for line in text.splitlines():
        if line.strip().startswith("#"):
            header = line.lstrip("#").strip().lower()
            if any(kw.lower() in header for kw in keywords):
                in_sec = True
                continue
            elif in_sec:
                break
        elif in_sec:
            lines.append(line)
    return "\n".join(lines)


# Last coverage run's structured flags, published so the report can surface an
# absent spec instead of letting empty-string matching pass silently.
LAST_COVERAGE_RESULTS: dict[str, object] = {}


# --- Tiered evidence chain -------------------------------------------------
# L1 = DOM/ARIA/data-state structural checks (always available, parsed tree).
# L2 = computed-style checks (available only when a headless style engine is
#      reachable). L3 = screenshot comparison (best-effort capture).
# A missing browser, fonts, or GPU degrades the run to the reachable tier and is
# reported as environment_not_ready with the tier reached — never as a
# code-assertion failure. Only L1 failures block.

_STYLE_ENGINE_CANDIDATES = (
    "chromium", "chrome", "google-chrome", "google-chrome-stable",
    "microsoft-edge", "msedge", "firefox",
)

# Capability probes are environment facts, not per-document facts: cache by
# engine so one verification run launches the browser at most once per tier.
_TIER_PROBE_CACHE: dict[str, tuple[bool, str | None]] = {}

# Tiered evidence record of the last assert_quality run: names which tiers ran
# and the reason for every tier that did not.
LAST_TIER_EVIDENCE: dict[str, object] = {}


def _style_engine_command() -> str | None:
    """Return a usable headless style engine command, or None when absent."""
    for name in _STYLE_ENGINE_CANDIDATES:
        found = shutil.which(name)
        if found:
            return found
    # macOS app bundles are common but not on PATH.
    for app in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ):
        if Path(app).exists():
            return app
    import importlib.util
    if importlib.util.find_spec("playwright") is not None:
        return "playwright"
    return None


def _chrome_like_flags(engine: str, profile_dir: Path) -> list[str]:
    flags = ["--headless", "--disable-gpu", "--no-first-run",
             f"--user-data-dir={profile_dir}"]
    if engine != "firefox":
        flags.append("--no-sandbox")
    return flags


def _probe_computed_style(html: Path) -> tuple[bool, str | None]:
    """L2 probe: confirm a style engine can render the document."""
    engine = _style_engine_command()
    if not engine:
        return False, "environment_not_ready: no headless style engine available for computed-style checks"
    cached = _TIER_PROBE_CACHE.get(f"style:{engine}")
    if cached is not None:
        return cached
    if engine == "playwright":
        result = _playwright_probe(html, capture=False)
    else:
        with tempfile.TemporaryDirectory() as td:
            cmd = [engine, *_chrome_like_flags(engine, Path(td)),
                   "--dump-dom", html.resolve().as_uri()]
            result = _run_engine_probe(cmd, "computed-style probe")
    _TIER_PROBE_CACHE[f"style:{engine}"] = result
    return result


def _probe_screenshot(html: Path) -> tuple[bool, str | None]:
    """L3 probe: confirm the engine can capture a screenshot for comparison."""
    engine = _style_engine_command()
    if not engine:
        return False, "environment_not_ready: no headless style engine available for screenshot comparison"
    cached = _TIER_PROBE_CACHE.get(f"screenshot:{engine}")
    if cached is not None:
        return cached
    if engine == "playwright":
        result = _playwright_probe(html, capture=True)
    else:
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tier3.png"
            cmd = [engine, *_chrome_like_flags(engine, Path(td)),
                   f"--screenshot={out}", "--window-size=1280,800",
                   html.resolve().as_uri()]
            ok, reason = _run_engine_probe(cmd, "screenshot capture")
            if ok and not out.is_file():
                ok, reason = False, "environment_not_ready: screenshot capture produced no image"
            result = (ok, reason)
    _TIER_PROBE_CACHE[f"screenshot:{engine}"] = result
    return result


def _run_engine_probe(cmd: list[str], label: str) -> tuple[bool, str | None]:
    try:
        proc = subprocess.run(cmd, capture_output=True, timeout=20)
    except subprocess.TimeoutExpired:
        return False, f"environment_not_ready: {label} timed out"
    except OSError as exc:
        return False, f"environment_not_ready: {label} failed ({exc.__class__.__name__})"
    if proc.returncode != 0:
        return False, f"environment_not_ready: {label} exited non-zero"
    return True, None


def _playwright_probe(html: Path, capture: bool) -> tuple[bool, str | None]:
    label = "screenshot capture" if capture else "computed-style probe"
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(html.resolve().as_uri())
            if capture:
                page.screenshot(path=tempfile.mkstemp(suffix=".png")[1])
            browser.close()
    except Exception as exc:  # noqa: BLE001 — any launch/render failure is environmental
        return False, f"environment_not_ready: {label} failed ({exc.__class__.__name__})"
    return True, None


def probe_craft_floors(html: Path, viewport_width: int = 1280) -> tuple[bool, str | None]:
    """Browser-check press feedback, nested radii, and tabular numeric stability."""
    node = shutil.which("node")
    probe_mjs = Path(__file__).resolve().parents[3] / "benchmarks" / "runners" / "browser_probe.mjs"
    if not node or not probe_mjs.is_file():
        return False, "environment_not_ready: craft floor probe needs node and browser_probe.mjs"

    script = r'''(() => {
      const visible = (el) => {
        const r = el.getBoundingClientRect(), s = getComputedStyle(el);
        return r.width > 0 && r.height > 0 && s.display !== "none" && s.visibility !== "hidden";
      };
      const corners = ["TopLeft", "TopRight", "BottomRight", "BottomLeft"];
      const radius = (style, corner) => parseFloat(style[`border${corner}Radius`]) || 0;
      const label = (el) => (el.getAttribute("aria-label") || el.id || el.className || el.tagName).toString().slice(0, 80);
      const failures = [];
      const commit = [...document.querySelectorAll('button[type="submit"], button[data-action], form button, [role="button"][data-action], [role="dialog"] button')]
        .filter(visible);
      const activeRules = [...document.styleSheets].flatMap((sheet) => {
        try { return [...sheet.cssRules].filter((r) => r.selectorText && /:active\b/.test(r.selectorText)); }
        catch { return []; }
      });
      for (const el of commit) {
        const hasActive = activeRules.some((rule) => {
          try { return el.matches(rule.selectorText.replace(/::?[\w-]+(?:\([^)]*\))?/g, "")) &&
            [...rule.style].some((p) => ["transform", "scale", "filter", "box-shadow", "background-color", "border-color", "opacity"].includes(p)); }
          catch { return false; }
        });
        if (!hasActive) failures.push(`press feedback: ${label(el)} has no detectable :active visual change`);
      }
      for (const inner of document.querySelectorAll("*")) {
        if (!visible(inner)) continue;
        const parent = inner.parentElement;
        if (!parent || !visible(parent)) continue;
        const childStyle = getComputedStyle(inner), parentStyle = getComputedStyle(parent);
        if (!corners.some((corner) => radius(childStyle, corner) > 0)
            || !corners.some((corner) => radius(parentStyle, corner) > 0)) continue;
        const p = Math.max(parseFloat(parentStyle.paddingTop) || 0, parseFloat(parentStyle.paddingRight) || 0,
          parseFloat(parentStyle.paddingBottom) || 0, parseFloat(parentStyle.paddingLeft) || 0);
        for (const corner of corners) {
          const expected = Math.max(0, radius(parentStyle, corner) - p);
          const actual = radius(childStyle, corner);
          if (Math.abs(actual - expected) > 1)
            failures.push(`concentric radius: ${label(inner)} ${corner} radius ${actual}px, expected ${expected}px within 1px`);
        }
      }
      const numeric = document.querySelectorAll("td, th, time, data, output, meter, [aria-live], [data-metric]");
      for (const el of numeric) {
        if (!visible(el) || !/\d/.test(el.textContent || el.value || "")) continue;
        if (!getComputedStyle(el).fontVariantNumeric.split(/\s+/).includes("tabular-nums"))
          failures.push(`tabular numerals: ${label(el)} must compute font-variant-numeric: tabular-nums`);
      }
      return { failures, checked: { commit: commit.length, numeric: numeric.length } };
    })()'''
    import base64
    import json as _json
    try:
        proc = subprocess.run(
            [node, str(probe_mjs), "craft", "--url", html.resolve().as_uri(),
             "--viewport", f"{viewport_width}x900", "--script", base64.b64encode(script.encode()).decode()],
            capture_output=True, text=True, timeout=60, cwd=str(probe_mjs.parents[1]))
    except (subprocess.TimeoutExpired, OSError) as exc:
        return False, f"environment_not_ready: craft floor probe failed ({exc.__class__.__name__})"
    if proc.returncode != 0:
        return False, f"environment_not_ready: craft floor probe exited {proc.returncode}"
    try:
        result = _json.loads(proc.stdout.strip().splitlines()[-1]).get("result")
        failures = result["failures"]
    except (KeyError, ValueError, IndexError, TypeError):
        return False, "environment_not_ready: craft floor probe returned unparseable output"
    if failures:
        return False, "craft floor assertion: " + "; ".join(failures[:8])
    return True, None


def probe_touch_targets(html: Path, viewport_width: int = 390, min_px: int = 44) -> tuple[bool, str | None]:
    """Measure interactive controls smaller than min_px at the given viewport
    width, so a touch-target violation surfaces at build time instead of only
    at downstream benchmark judging (which runs at 390px).

    Uses the benchmark's CDP probe (browser_probe.mjs) when node is available:
    it evaluates JS in the page and already implements the same measurement
    the judge consumes. Falls back to a playwright evaluation; chrome
    --dump-dom cannot evaluate and reports environment_not_ready.
    """
    node = shutil.which("node")
    # scripts/ -> spec-prototype/ -> skills/ -> repo root
    probe_mjs = Path(__file__).resolve().parents[3] / "benchmarks" / "runners" / "browser_probe.mjs"
    if node and probe_mjs.is_file():
        cached = _TIER_PROBE_CACHE.get(f"touch:{viewport_width}:{html}")
        if cached is not None:
            return cached
        import json as _json
        try:
            proc = subprocess.run(
                [node, str(probe_mjs), "snapshot", "--url", html.resolve().as_uri(),
                 "--viewport", f"{viewport_width}x900"],
                capture_output=True, text=True, timeout=60,
                cwd=str(probe_mjs.parents[1]))
        except subprocess.TimeoutExpired:
            return False, "environment_not_ready: touch-target probe timed out"
        except OSError as exc:
            return False, f"environment_not_ready: touch-target probe failed ({exc.__class__.__name__})"
        if proc.returncode != 0:
            return False, f"environment_not_ready: touch-target probe exited {proc.returncode}"
        try:
            out = _json.loads(proc.stdout.strip().splitlines()[-1])
            count = int(out["snapshot"]["smallTargetCount"])
            names = out["snapshot"].get("smallTargets") or []
        except (KeyError, ValueError, IndexError, TypeError):
            return False, "environment_not_ready: touch-target probe returned unparseable output"
        if count > 0:
            result = False, (f"touch_target assertion: {count} control(s) below {min_px}px "
                             f"at {viewport_width}px: {'; '.join(str(n) for n in names[:5])}")
        else:
            result = True, None
        _TIER_PROBE_CACHE[f"touch:{viewport_width}:{html}"] = result
        return result

    if importlib.util.find_spec("playwright") is not None:
        script = (
            "(() => {"
            "const visible = (el) => { const r = el.getBoundingClientRect();"
            "return r.width > 0 && r.height > 0 && getComputedStyle(el).visibility !== 'hidden'"
            "&& getComputedStyle(el).display !== 'none'; };"
            "const sel = 'button, a, input, select, textarea, [role=button], [role=tab], [role=menuitem]';"
            "let small = 0; const names = [];"
            "for (const el of document.querySelectorAll(sel)) {"
            "if (!visible(el)) continue; const r = el.getBoundingClientRect();"
            "if (r.width < %d || r.height < %d) { small++; if (names.length < 5)"
            "names.push((el.getAttribute('aria-label') || el.innerText || el.tagName).trim().slice(0, 40)); } }"
            "return small + '|' + names.join(';;'); })()"
        ) % (min_px, min_px)
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page(viewport={"width": viewport_width, "height": 900})
                page.goto(html.resolve().as_uri())
                raw = page.evaluate(script)
                browser.close()
        except Exception as exc:  # noqa: BLE001
            return False, f"environment_not_ready: touch-target probe failed ({exc.__class__.__name__})"
        try:
            count_str, _, names = str(raw).partition("|")
            count = int(count_str)
        except (ValueError, AttributeError):
            return False, "environment_not_ready: touch-target probe returned unparseable output"
        if count > 0:
            return False, (f"touch_target assertion: {count} control(s) below {min_px}px "
                           f"at {viewport_width}px: {names}")
        return True, None

    return False, ("environment_not_ready: touch-target probe needs node (browser_probe.mjs) "
                   "or playwright; neither is available")


def tiered_quality_evidence(html: Path, l1_failures: list[str]) -> dict[str, object]:
    """Build the tiered evidence record for one verification run.

    Names which tiers ran and why the rest did not. Confirmed L1/L2 defects
    block; environment gaps are recorded as environment_not_ready reasons.
    """
    tiers: dict[str, dict[str, object]] = {}
    evidence: dict[str, object] = {
        "tiers": tiers, "tier_reached": "L1", "outcome": "passed",
        "environment_not_ready": False,
    }
    if l1_failures:
        tiers["L1"] = {"status": "failed", "failure_count": len(l1_failures)}
        blocked = "upstream_blocked: L1 structural checks failed"
        tiers["L2"] = {"status": "skipped", "reason": blocked}
        tiers["L3"] = {"status": "skipped", "reason": blocked}
        evidence["tier_reached"] = "L1"
        evidence["outcome"] = "blocked"
        return evidence
    tiers["L1"] = {"status": "passed"}
    evidence["tier_reached"] = "L2"

    l2_ok, l2_reason = _probe_computed_style(html)
    if l2_ok:
        tiers["L2"] = {"status": "passed"}
    else:
        tiers["L2"] = {"status": "degraded", "reason": l2_reason}

    if l2_ok:
        craft_ok, craft_reason = probe_craft_floors(html)
        if craft_reason and "environment_not_ready" in craft_reason:
            tiers["L2"] = {"status": "degraded", "reason": craft_reason}
            evidence["craft_floor_not_verified"] = craft_reason
            evidence["environment_not_ready"] = True
        elif not craft_ok and craft_reason:
            tiers["L2"] = {"status": "failed", "reason": craft_reason}
            evidence["tier_reached"] = "L2"
            evidence["outcome"] = "failed"
            tiers["L3"] = {"status": "skipped", "reason": "upstream_blocked: craft floor failure"}
            return evidence

        # The style engine renders; measure touch targets at mobile width so a
        # 44px violation surfaces at build time, not only at downstream judging.
        touch_ok, touch_reason = probe_touch_targets(html)
        if not touch_ok and touch_reason and "environment_not_ready" not in touch_reason:
            tiers["L2"] = {"status": "failed", "reason": touch_reason}
            evidence["tier_reached"] = "L2"
            evidence["outcome"] = "failed"
            tiers["L3"] = {"status": "skipped", "reason": "upstream_blocked: L2 touch-target check failed"}
            return evidence

    if l2_ok:
        l3_ok, l3_reason = _probe_screenshot(html)
    else:
        # The style engine is unreachable this run; capture cannot run either.
        l3_ok, l3_reason = False, (
            "environment_not_ready: screenshot comparison skipped "
            "(style engine unavailable)")
    if l3_ok:
        tiers["L3"] = {"status": "passed"}
        evidence["tier_reached"] = "L3"
    else:
        tiers["L3"] = {"status": "skipped", "reason": l3_reason}

    env_reasons = [
        str(rec["reason"]) for rec in tiers.values()
        if str(rec.get("reason", "")).startswith("environment_not_ready")
    ]
    evidence["environment_not_ready"] = bool(env_reasons)
    if env_reasons:
        evidence["environment_reasons"] = env_reasons
    return evidence


def coverage_failures(html: Path, contract_path: Path | str | None = None) -> list[str]:
    """Reconcile the authored scope with delivery and evidence.

    Scope membership, delivery and evidence stay separate facts; a documented
    blocker never discharges an obligation and a pending destination stays
    href-free rather than becoming a broken link.
    """
    results: dict[str, object] = {}
    LAST_COVERAGE_RESULTS.clear()
    root = None
    for parent in [html.parent, *html.parents]:
        if (parent / "prototype/contracts/surface-maps/m1.md").is_file():
            root = parent
            break
    if root is None:
        return []
    texts = {}
    for key, path in (
        ("surface_map", root / "prototype/contracts/surface-maps/m1.md"),
        ("product", root / "prototype/product.md"),
        ("foundation", root / "prototype/contracts/foundation/f1.md"),
    ):
        texts[key] = path.read_text(encoding="utf-8") if path.is_file() else ""
    # The canonical single-file RFC view is `*.spec.md`; the legacy multi-file
    # path authors `r1.md`. Glob both, canonical wins per slice, so a migrated
    # repository is never silently read through a stale legacy file.
    spec_files_legacy = sorted((root / "prototype/specifications").glob("*/r1.md"))
    spec_files_canonical = sorted((root / "prototype/specifications").glob("*/*.spec.md"))
    spec_by_slice: dict[str, Path] = {}
    for p in spec_files_legacy:
        spec_by_slice[p.parent.name] = p
    for p in spec_files_canonical:
        spec_by_slice[p.parent.name] = p  # canonical overrides legacy
    spec_files = list(spec_by_slice.values())
    texts["specification"] = spec_files[0].read_text(encoding="utf-8") if spec_files else ""
    if not str(texts["specification"]).strip():
        # An absent or empty spec is recorded rather than read as a clean pass:
        # downstream identity checks would otherwise match against "".
        results["specification_missing"] = True
    if not texts["surface_map"]:
        return []

    context = prototype_context.read_context(**texts)
    delivered: dict[str, str] = {}
    pages = sorted((root / "prototype/surfaces").glob("*/index.html")) + sorted(
        (root / "prototype/experiments").glob("*/**/index.html"))
    for page in pages:
        name = page.parent.parent.name if page.parent.name in ("anchor", "hero-anchor") else page.parent.name
        delivered[name] = page.read_text(encoding="utf-8")
    if contract_path:
        slice_name = Path(contract_path).parent.name
        if slice_name not in delivered and html.is_file():
            content = html.read_text(encoding="utf-8")
            dom = _Document(content)
            has_surface_identity = (
                dom.attr_equals("data-surface", slice_name) or
                dom.attr_equals("data-slice", slice_name) or
                dom.attr_equals("id", slice_name) or
                dom.attr_equals("class", slice_name) or
                dom.contains(f"surface-{slice_name}") or
                slice_name in html.as_posix() or
                (len(content.strip()) > 50 and dom.tags("main", "body", "html", "div"))
            )
            if has_surface_identity and len(content.strip()) > 50:
                delivered[slice_name] = content
    reconciliation = prototype_context.reconcile_obligations(
        context, delivered=list(delivered), evidence=None, blocked=None,
        bound_revision=context["surface_map"]["revision"])

    failures: list[str] = []
    # An unusable scope withholds completion rather than passing: the check fails
    # and names the governing error instead of laundering a met completion.
    if reconciliation["governing_error"]:
        error = reconciliation["governing_error"]
        failures.append(f"coverage assertion: resolved scope is unusable ({error['code']}); "
                        "completion is withheld until the scope error is resolved")
    if reconciliation["coverage"] == "unresolved" and context["surface_map"]["surfaces"]:
        failures.append("coverage assertion: surface map declares surfaces without an explicit selected/full-product coverage")
    if reconciliation["missing_delivery"]:
        failures.append("coverage assertion: selected obligations undelivered ("
                        + ", ".join(reconciliation["missing_delivery"][:5])
                        + "); absent surfaces remain review-visible, not silently dropped")
    if reconciliation["stale_revision"]:
        failures.append("coverage assertion: delivered scope does not match the retained map revision")
    for surface in reconciliation["in_round"]:
        source = delivered.get(surface, "")
        if not source:
            continue
        # A live href to an undelivered sibling is a 404 in waiting. Read the
        # parsed anchors: an href named inside a comment or a string is not a link.
        dom = _Document(source)
        for sibling in reconciliation["in_round"]:
            if sibling == surface or sibling in delivered:
                continue
            if dom.links_to(sibling):
                failures.append(f"coverage assertion: pending sibling {sibling} linked from {surface} but not delivered (render a disabled affordance instead)")
    LAST_COVERAGE_RESULTS.clear()
    LAST_COVERAGE_RESULTS.update(results)
    return failures


def assert_quality(html_path: str, tokens_path: str, check_stale: bool = False,
                   contract_path: str | None = None) -> bool:
    html = Path(html_path)
    tokens = Path(tokens_path)
    if not html.is_file() or not tokens.is_file():
        print(f"FAILED: required artifact missing (html={html}, tokens={tokens})")
        return False
    source = html.read_text(encoding="utf-8")
    token_source = tokens.read_text(encoding="utf-8")
    dom = _Document(source)
    declarations = dom.declarations()
    # Fatal only: task completion, contract conformance, contrast/a11y, state
    # handling. Subjective aesthetic craft lands in `advisories` instead.
    failures: list[str] = []
    advisories: list[str] = []

    # DOM and interaction assertions read the parsed tree, never the source text:
    # a class named in a comment or a tag quoted inside a string is not a hook.
    inspectable = [
        el for el in dom.elements
        if "id" in el.attrs or "class" in el.attrs
        or any(name.startswith("data-") for name in el.attrs)
    ]
    if len(inspectable) < 3 and not dom.controls():
        failures.append("DOM assertion: no inspectable semantic elements")
    if not dom.has_event_binding():
        failures.append("interaction assertion: no declarative or imperative event binding")
    if not dom.controls():
        failures.append("interaction assertion: no reachable control")

    contract_file = Path(contract_path) if contract_path else None
    declared = _contract_items(contract_file)
    required_action_ids = _contract_action_ids(contract_file)
    rendered_action_ids = {
        el.get("data-action") for el in dom.with_attr("data-action")
        if re.fullmatch(r"action-[a-z0-9]+(?:-[a-z0-9]+)*", el.get("data-action"))
    }
    missing_actions = sorted(required_action_ids - rendered_action_ids)
    if missing_actions:
        failures.append(
            "action identity assertion: authored action id(s) missing from DOM data-action: "
            + ", ".join(missing_actions[:8])
        )
    missing: list[str] = []
    for item in declared:
        if isinstance(item, tuple):
            if not any(dom.contains(sub) for sub in item if sub and len(sub) > 2):
                missing.append("/".join(sub for sub in item if sub))
        elif len(item) > 2 and not dom.contains(item):
            missing.append(item)
    if missing:
        failures.append("contract assertion: declared items absent from DOM: " + ", ".join(missing[:5]))

    # Hard floor: reject raw inline hex colors in style attributes (enforces token inheritance)
    raw_style_hex = [
        el.get("style") for el in dom.with_attr("style")
        if re.search(r"#[0-9a-fA-F]{3,8}\b", el.get("style"))
    ]
    if raw_style_hex:
        failures.append(f"craft assertion: raw inline hex colors in style attributes ({len(raw_style_hex)} found; use CSS custom properties / var(--...))")

    # Navigation integrity: every relative href must resolve inside the delivered prototype scope
    broken_nav = []
    # Only navigable anchors are checked here: stylesheet/asset links are validated by token inheritance.
    for el in dom.tags("a"):
        href = el.get("href")
        if not href or href.startswith(("#", "http://", "https://", "mailto:", "data:", "javascript:")):
            continue
        if not (html.parent / href).resolve().exists():
            broken_nav.append(href)
    if broken_nav:
        failures.append(
            "navigation assertion: relative href(s) do not resolve inside the artifact "
            f"({', '.join(sorted(set(broken_nav))[:4])}); link only to delivered surfaces or render a disabled affordance"
        )

    # Accessibility floor: conditional prefers-reduced-motion when animations or transitions are present
    has_motion = bool(re.search(r'(?:transition|animation)\s*:\s*(?!none\b)[^;}{]+', declarations, re.IGNORECASE))
    if has_motion:
        if not re.search(r'@media\s*\(\s*prefers-reduced-motion', dom.style_text, re.IGNORECASE):
            failures.append("a11y assertion: dynamic transitions/animations declared without @media (prefers-reduced-motion: reduce) override")

    # Hard floor: reject rogue :root color property redeclarations in <style>
    if re.search(r":root\s*\{[^}]*--(?:accent|bg|border|text)-[a-zA-Z0-9_-]+\s*:[^}]*\}", dom.style_text):
        failures.append("token assertion: rogue :root color tokens declared in <style> (shadows tokens.css; must consume tokens from tokens.css)")

    # Signature Accent Discipline: enforce strict negative boundary for --accent-seal
    # var(--accent-seal) is reserved for authority seals, decisive commits, and fatal collisions;
    # it is strictly forbidden on draft, pending, secondary, ghost, or cancel affordances.
    if "--accent-seal" in token_source or "--accent-seal" in source:
        # Inline: an element that carries both a reserved class and the accent.
        inline_leak = any(
            el.classes & _FORBIDDEN_ACCENT_CLASSES and "--accent-seal" in el.get("style")
            for el in dom.elements
        )
        # Stylesheet: a rule whose selector names a reserved class and whose body
        # consumes the accent. Selector and body are read from the same rule, so a
        # forbidden class elsewhere in the sheet cannot trigger it.
        rule_leak = any(
            any(re.search(rf"[.\-]{re.escape(name)}(?![\w-])", selector) for name in _FORBIDDEN_ACCENT_CLASSES)
            and "--accent-seal" in body
            for selector, body in re.findall(r"([^{}]+)\{([^{}]*)\}", dom.style_text)
        )
        if inline_leak or rule_leak:
            failures.append(
                "token-discipline assertion: Signature Accent Leak detected. "
                "var(--accent-seal) is strictly reserved for authoritative gate, seal imprint, or fatal collision; "
                "forbidden on draft, pending, secondary, ghost, cancel, or zero-borrow base elements."
            )

    # Cognitive Budgeting & Energy Return Ledger (借贷法则门禁):
    # 1. Applicability-driven: triggers only when contract explicitly declares non-placeholder borrow zones.
    # 2. Exempts legitimate transient loading states (aria-busy, role="progressbar", spinner).
    # 3. Dynamic visual energy is reserved for high-yield zones; non-high-yield areas must settle back.
    if contract_path and Path(contract_path).is_file():
        contract_text = Path(contract_path).read_text(encoding="utf-8")
        has_ledger_decl = bool(re.search(r"(?:Cognitive Budgeting|借贷法则|Energy Return Ledger)", contract_text, re.IGNORECASE))
        has_concrete_ledger = bool(re.search(r"(?:high_yield_borrow_zone|High-Yield|Borrow Zone|借贷区)[^\n]*[:=]\s*(?![`*_]*(?:unspecified|none|n/a|not declared)\b)[^\n]+", contract_text, re.IGNORECASE))
        if has_ledger_decl and has_concrete_ledger:
            # Check for unauthorized rogue infinite animations in the base UI
            has_infinite_anim = bool(re.search(r"animation\s*:\s*[^;}]*\binfinite\b", declarations, re.IGNORECASE))
            if has_infinite_anim:
                # Infinite animations are permitted for high-yield containers, live indicators, or standard accessibility loading states
                if not dom.has_authorized_animation():
                    failures.append(
                        "cognitive-budget assertion: Energy leak in zero-borrow base UI. "
                        "Continuous infinite animations are forbidden outside explicit high-yield/pulse containers or loading states; "
                        "routine UI must settle to baseline calm equilibrium."
                    )

    # Dual-channel keyboard ergonomics check: when declared in contract, ensure event listener exists
    if contract_path and Path(contract_path).is_file():
        contract_text = Path(contract_path).read_text(encoding="utf-8")
        if "Dual-Channel Ergonomics" in contract_text or "Shortcut Key" in contract_text:
            if not dom.has_keyboard_binding():
                failures.append("ergonomics assertion: declared dual-channel keyboard shortcuts not bound (missing keydown/keyup listener)")

        # Action Verb Lifecycle feedback closure: when commit mutations or toasts are declared
        verb_sec = _extract_section_text(contract_text, "action verb", "verb lifecycle")
        verb_rows = [
            line for line in verb_sec.splitlines()
            if line.strip().startswith("|") and not re.match(r"^\|\s*[-:]+\s*\|", line.strip()) and "Action ID" not in line and "Trigger Button" not in line
        ]
        active_commit_verbs = [
            r for r in verb_rows
            if not re.search(r"\b(?:N/A|None|Not Applicable|无|不适用)\b", r, re.IGNORECASE)
            and len([c for c in r.split("|") if c.strip()]) >= 4
        ]
        has_active_verbs = bool(active_commit_verbs) or (
            bool(verb_sec) and not bool(re.search(r"(?:Action Verb|Verb Lifecycle).*?(?:N/A|Not Applicable|纯阅读|无状态变迁|无破坏性动作|不适用)", verb_sec, re.IGNORECASE | re.DOTALL))
        )
        if has_active_verbs:
            if not dom.has_feedback_container():
                failures.append("action-lifecycle assertion: Action Verb Lifecycle declared in contract but DOM lacks visible feedback container (role='status|alert', class='toast|feedback', or id='toast')")

        # Touch-first gesture detents check: when touch-first ergonomics are declared in contract
        if "Touch-First Ergonomics" in contract_text or "Gesture Detents" in contract_text:
            if not dom.has_touch_binding():
                failures.append("touch ergonomics assertion: declared touch-first gestures or tap detents not bound (missing touch/pointer/click handler)")

        # Dynamic state machine check: when multi-state or Break Protocol stress checkpoints are declared
        break_sec = _extract_section_text(contract_text, "break protocol", "stress checkpoint")
        break_rows = [
            line for line in break_sec.splitlines()
            if "Reality Breaker" not in line and line.strip().startswith("|") and not re.match(r"^\|\s*[-:]+\s*\|", line.strip())
        ]
        active_break_checkpoints = [
            r for r in break_rows
            if not re.search(r"\b(?:N/A|None|Not Applicable|无|不适用)\b", r, re.IGNORECASE)
        ]
        has_active_break = bool(active_break_checkpoints) or (
            bool(break_sec) and not bool(re.search(r"(?:The Break Protocol|Stress Checkpoints).*?(?:N/A|Not Applicable|无需破坏压测|不适用)", break_sec, re.IGNORECASE | re.DOTALL))
        )
        if has_active_break:
            if not dom.has_state_hook():
                failures.append("state-machine assertion: stress checkpoints declared but no state-switching hook detected (use hashchange / location.hash / data-state / class empty|loading|view-mode)")
            if not re.search(r"text-overflow\s*:\s*ellipsis|overflow(?:-[xy])?\s*:\s*(?:hidden|auto|scroll)|break-word|break-all|truncate|clamp\(|overflow-wrap\s*:\s*(?:anywhere|break-word)|word-break\s*:\s*break-all", declarations, re.IGNORECASE):
                failures.append("break-protocol assertion: missing string overflow containment (use text-overflow: ellipsis, overflow containment, truncate, or word-break: break-all)")

            # Actionable empty-state floor: empty-state presentation surface must provide an actionable trigger (button or link bait)
            for container in dom.empty_state_containers():
                reachable = [el for el in container.descendants() if el in dom.controls()]
                if not reachable:
                    failures.append("contextual agency assertion: empty state container lacks actionable trigger (<button> or <a href>)")
                    break

        # Zero Naked Metrics / Contextual Data Floor check
        if "Zero Naked Metrics" in contract_text or "Micro Sparklines" in contract_text or "sparkline" in contract_text.lower():
            # Domain Context Awareness: Narrative/Editorial literature surfaces measure prose by words/reading time, NOT telemetry graphs
            is_narrative = bool(re.search(r"editorial|reading|essay|narrative|阅读|长文|文学", contract_text, re.IGNORECASE))
            has_narrative_units = bool(re.search(r"\b\d+[\d,.]*\s*(?:字|词|min|分钟|words?|mins?|章|节|段|篇)\b", dom.text, re.IGNORECASE))
            has_html5_data = bool(dom.tags("meter", "progress", "data", "canvas"))
            if not (dom.has_charted_metric() or has_html5_data or dom.has_context_modifier()
                    or dom.has_metric_with_unit() or (is_narrative and has_narrative_units)):
                failures.append("data-craft assertion: Zero Naked Metrics violation (metrics must carry reference baseline, unit context, delta trend, visual sparkline/meter/canvas, or authentic narrative units)")

        # Additional press-physics recipes remain advisory; the scoped visible
        # :active response is enforced by the rendered craft-floor probe above.
        if "Cognitive Budgeting" in contract_text or "Decisive Exchange 3-Frame" in contract_text or "Tactile Detents" in contract_text:
            has_active = bool(re.search(r":active\s*\{[^}]*(?:transform|scale|translate|filter|box-shadow|inset|opacity|background|border|color|duration|transition|motion|ease|cubic|rgb)", declarations, re.IGNORECASE))
            has_tailwind_active = bool(re.search(r"active:(?:scale|translate|bg|shadow|opacity)-", declarations))
            has_focus_visible = bool(re.search(r":focus-visible\s*\{", declarations, re.IGNORECASE))
            has_transition = bool(re.search(r"transition\s*:\s*[^;]+(?:transform|all|ease|cubic|duration|opacity|color)", declarations, re.IGNORECASE))
            has_pointer_mutation = bool(re.search(r"addEventListener\s*\(\s*['\"](?:pointerdown|touchstart|mousedown)['\"].*?(?:classList|style|scale|active|transform)", dom.script_text, re.DOTALL | re.IGNORECASE))
            if not (has_active or has_tailwind_active) and not (has_focus_visible and has_transition) and not has_pointer_mutation:
                advisories.append("craft advisory (non-blocking): interactive controls use no detected press/motion response; consider :active physics, :focus-visible transition, or pointer state mutation")

        # Multi-surface topology navigation check: when surface map m1.md declares sibling surfaces
        smap_candidates = []
        for p in [Path(contract_path).resolve(), html.resolve()]:
            curr = p.parent
            depth = 0
            while curr != curr.parent and depth < 5:
                smap_candidates.extend([
                    curr / "contracts/surface-maps/m1.md",
                    curr / "prototype/contracts/surface-maps/m1.md"
                ])
                if (curr / ".git").is_dir() or (curr / "skills").is_dir():
                    break
                curr = curr.parent
                depth += 1
        smap_file = next((p for p in smap_candidates if p.is_file()), None)
        if smap_file:
            smap_text = smap_file.read_text(encoding="utf-8")
            declared_surfaces = []
            for line in smap_text.splitlines():
                m = re.search(r"\*\*(.+?)\*\*\s*:\s*`([^`]+)`", line)
                if m:
                    p_raw = m.group(2).strip()
                    sid = p_raw.split("/")[0] if ("hero-anchor" in p_raw or "anchor" in p_raw) else p_raw.replace("surfaces/", "")
                    declared_surfaces.append(sid)
            current_id = html.parent.parent.name if html.parent.name in ("hero-anchor", "anchor") else html.parent.name
            # Only enforce topology sibling navigation if current_id is an actual declared member of this surface map
            if current_id in declared_surfaces:
                siblings = [sid for sid in declared_surfaces if sid != current_id]
                # Sibling navigation follows delivery: a delivered sibling must be
                # reachable by live href, an undelivered one must stay visible as a
                # disabled affordance or text without a link (a link would 404).
                prototype_root = smap_file.parent
                while prototype_root.name != "prototype" and prototype_root != prototype_root.parent:
                    prototype_root = prototype_root.parent
                for sid in siblings:
                    delivered_sibling = prototype_root.name == "prototype" and any(
                        prototype_root.rglob(f"{sid}/**/index.html"))
                    has_link = dom.links_to(sid)
                    if delivered_sibling and not has_link:
                        failures.append(f"topology assertion: delivered sibling {sid} is not reachable by navigation link from {current_id}")
                    if not delivered_sibling and has_link:
                        failures.append(f"topology assertion: undelivered sibling {sid} linked by live href from {current_id} (404); render a disabled affordance instead")
                    if not delivered_sibling and not _pending_sibling_marked(dom, sid):
                        failures.append(f"topology assertion: undelivered sibling {sid} is neither linked nor represented as a disabled affordance from {current_id}")

    failures.extend(coverage_failures(html, contract_path=contract_path))

    if check_stale:
        if re.search(r"\b(?:Lorem ipsum|placeholder text|sample copy)\b", dom.text, re.IGNORECASE):
            failures.append("stale-template assertion: unconsidered placeholder content detected")

    states = _evidence_state(html)
    LAST_TIER_EVIDENCE.clear()
    LAST_TIER_EVIDENCE.update(tiered_quality_evidence(html, failures))
    tier_outcome = LAST_TIER_EVIDENCE.get("outcome")
    print("STATIC: " + ("pass" if not failures and tier_outcome not in ("failed", "blocked") else "fail"))
    if LAST_COVERAGE_RESULTS.get("specification_missing"):
        # Surfaces to the operator that no spec text was found, so a pass was
        # not earned against an empty string.
        print("SPECIFICATION: missing")
    print("BROWSER: " + states.get("browser", "unverified"))
    print("VISUAL: " + states.get("visual", "unverified"))
    print("HUMAN: " + states.get("human", "unverified"))
    for tier_id in ("L1", "L2", "L3"):
        record = LAST_TIER_EVIDENCE["tiers"][tier_id]
        status = record["status"]
        reason = f" ({record['reason']})" if record.get("reason") else ""
        print(f"TIER {tier_id}: {status}{reason}")
    if LAST_TIER_EVIDENCE.get("environment_not_ready"):
        print("ENVIRONMENT: not_ready (degraded to tier "
              f"{LAST_TIER_EVIDENCE['tier_reached']})")
    if LAST_TIER_EVIDENCE.get("craft_floor_not_verified"):
        print("CRAFT FLOORS: not_verified (" + str(LAST_TIER_EVIDENCE["craft_floor_not_verified"]) + ")")
        return False
    for advisory in advisories:
        print(f"  [advisory] {advisory}")
    if failures:
        for i, failure in enumerate(failures, 1):
            print(f"  [{i}] {failure}")
        return False
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Contract-driven prototype quality assertions")
    parser.add_argument("html", nargs="?", default=None, help="Target HTML file")
    parser.add_argument("tokens", nargs="?", default=None, help="Shared tokens stylesheet")
    parser.add_argument("--slice", dest="slice_id", help="Slice ID for convention-over-configuration auto-resolution")
    parser.add_argument("--root", dest="root", help="Repository root for --slice auto-resolution (defaults to cwd)")
    parser.add_argument("--tokens", dest="tokens_opt")
    parser.add_argument("--contract", dest="contract")
    parser.add_argument("--strict-divergence", action="store_true")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path.cwd()
    if args.slice_id:
        slice_id = args.slice_id
        candidates = [
            root / f"prototype/experiments/{slice_id}/r1/index.html",
            root / f"prototype/experiments/{slice_id}/index.html",
            root / f"prototype/experiments/{slice_id}/anchor/index.html",
            root / f"prototype/experiments/{slice_id}/hero-anchor/index.html",
            root / f"prototype/surfaces/{slice_id}/index.html",
        ]
        html_path = next((p for p in candidates if p.is_file()), candidates[0])
        token_path = root / "prototype/shared/tokens.css"
        canonical_spec = root / f"prototype/specifications/{slice_id}/r1.spec.md"
        legacy_spec = root / f"prototype/specifications/{slice_id}/r1.md"
        spec_path = canonical_spec if canonical_spec.is_file() else legacy_spec
        contract_path = str(spec_path) if spec_path.is_file() else (args.contract or "")
        sys.exit(0 if assert_quality(str(html_path), str(token_path), args.strict_divergence, contract_path) else 1)

    if not args.html:
        parser.error("Must provide HTML path or --slice <id>")

    html = Path(args.html)
    token_arg = args.tokens_opt or args.tokens
    if not token_arg:
        token_arg = next((str(p) for p in (html.parent / "tokens.css", root / "prototype/shared/tokens.css") if p.is_file()), "prototype/shared/tokens.css")
    sys.exit(0 if assert_quality(str(html), token_arg, args.strict_divergence, args.contract) else 1)
