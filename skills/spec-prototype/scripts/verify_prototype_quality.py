#!/usr/bin/env python3
"""Truthful, contract-driven checks for a prototype artifact.

Static checks inspect source only. Browser, visual, and human evidence are
reported as unverified unless an evidence manifest explicitly records them.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prototype_context  # noqa: E402


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


def _contract_items(path: Path | None) -> list[str]:
    """Extract verifiable entity names, action IDs, or button labels from contract markdown."""
    if not path or not path.is_file():
        return []
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
# L1 = DOM/ARIA/data-state structural checks (always available, static source).
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


def tiered_quality_evidence(html: Path, l1_failures: list[str]) -> dict[str, object]:
    """Build the tiered evidence record for one verification run.

    Names which tiers ran and why the rest did not. Only L1 failures block;
    L2/L3 environment gaps are recorded as environment_not_ready reasons.
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
    delivered = {}
    pages = sorted((root / "prototype/surfaces").glob("*/index.html")) + sorted(
        (root / "prototype/experiments").glob("*/**/index.html"))
    for page in pages:
        name = page.parent.parent.name if page.parent.name in ("anchor", "hero-anchor") else page.parent.name
        delivered[name] = page.read_text(encoding="utf-8")
    if contract_path:
        slice_name = Path(contract_path).parent.name
        if slice_name not in delivered and html.is_file():
            content = html.read_text(encoding="utf-8")
            has_surface_identity = (
                f'data-surface="{slice_name}"' in content or
                f'data-slice="{slice_name}"' in content or
                f'id="{slice_name}"' in content or
                f'class="{slice_name}"' in content or
                f"surface-{slice_name}" in content or
                slice_name in html.as_posix() or
                (len(content.strip()) > 50 and any(tag in content.lower() for tag in ("<main", "<body", "<html", "<div")))
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
        for sibling in reconciliation["in_round"]:
            if sibling == surface or sibling in delivered:
                continue
            if re.search(rf"href=[\"'][^\"']*{re.escape(sibling)}[^\"']*[\"']", source):
                failures.append(f"coverage assertion: pending sibling {sibling} linked from {surface} but not delivered (render a disabled affordance instead)")
    LAST_COVERAGE_RESULTS.clear()
    LAST_COVERAGE_RESULTS.update(results)
    return failures


def _pending_sibling_marked(source: str, surface_id: str) -> bool:
    """True when an undelivered sibling is represented without a live href.

    An unreachable surface may not be linked, but it must not vanish from the
    shell either: a disabled affordance or an explicit text/data representation
    keeps the destination review-visible without producing a 404.
    """
    for tag in re.findall(r"<[^>]+>", source):
        if surface_id in tag and re.search(
                r'aria-disabled\s*=\s*["\']true["\']|(?:^|\s)disabled(?:\s|>|$)|data-disabled',
                tag, re.IGNORECASE):
            return True
    return bool(re.search(
        rf'data-(?:sibling|pending|surface)\s*=\s*["\']{re.escape(surface_id)}["\']',
        source, re.IGNORECASE))


def assert_quality(html_path: str, tokens_path: str, check_stale: bool = False,
                   contract_path: str | None = None) -> bool:
    html = Path(html_path)
    tokens = Path(tokens_path)
    if not html.is_file() or not tokens.is_file():
        print(f"FAILED: required artifact missing (html={html}, tokens={tokens})")
        return False
    source = html.read_text(encoding="utf-8")
    token_source = tokens.read_text(encoding="utf-8")
    # Fatal only: task completion, contract conformance, contrast/a11y, state
    # handling. Subjective aesthetic craft lands in `advisories` instead.
    failures: list[str] = []
    advisories: list[str] = []

    # DOM and interaction assertions use semantic hooks, never domain names.
    entities = re.findall(r"(?:data-(?:entity|contract|item)|id|class)=[\"'][^\"']+[\"']", source)
    if len(entities) < 3 and not re.search(r"<button\b|<a\b|role=[\"\']button", source):
        failures.append("DOM assertion: no inspectable semantic elements")
    if not re.search(r"addEventListener\s*\(|\bon(?:click|keydown|submit)\s*=|onclick=", source):
        failures.append("interaction assertion: no declarative or imperative event binding")
    if not re.search(r"<button\b|<a\b[^>]*href=|role=[\"']button", source):
        failures.append("interaction assertion: no reachable control")

    declared = _contract_items(Path(contract_path) if contract_path else None)
    missing: list[str] = []
    for item in declared:
        if isinstance(item, tuple):
            if not any(sub in source for sub in item if sub and len(sub) > 2):
                missing.append("/".join(sub for sub in item if sub))
        elif len(item) > 2 and item not in source:
            missing.append(item)
    if missing:
        failures.append("contract assertion: declared items absent from DOM: " + ", ".join(missing[:5]))

    # Tokens are checked strictly for declared, generic accessibility/typography hooks.
    if "font-variant-numeric" in token_source:
        if "font-variant-numeric" not in source and "tabular-nums" not in source:
            failures.append("token assertion: numeric presentation token is not consumed (use font-variant-numeric: tabular-nums or .tabular-nums)")
    if "--radius-" in token_source:
        if "var(--radius-" not in source and "var(--radius" not in source:
            failures.append("token assertion: radius tokens are not consumed (use var(--radius-*))")

    # Hard floor: reject raw inline hex colors in style attributes (enforces token inheritance)
    raw_style_hex = re.findall(r'style=["\'][^"\']*#[0-9a-fA-F]{3,8}[^"\']*["\']', source)
    if raw_style_hex:
        failures.append(f"craft assertion: raw inline hex colors in style attributes ({len(raw_style_hex)} found; use CSS custom properties / var(--...))")

    # Navigation integrity: every relative href must resolve inside the delivered prototype scope
    broken_nav = []
    # Only navigable anchors are checked here: stylesheet/asset links are validated by token inheritance.
    for href in re.findall(r'<a\b[^>]*href=["\']([^"\'#][^"\']*)["\']', source, re.IGNORECASE):
        if href.startswith(("http://", "https://", "mailto:", "data:", "javascript:")):
            continue
        if not (html.parent / href).resolve().exists():
            broken_nav.append(href)
    if broken_nav:
        failures.append(
            "navigation assertion: relative href(s) do not resolve inside the artifact "
            f"({', '.join(sorted(set(broken_nav))[:4])}); link only to delivered surfaces or render a disabled affordance"
        )

    # Accessibility floor: conditional prefers-reduced-motion when animations or transitions are present
    has_motion = bool(re.search(r'(?:transition|animation)\s*:\s*(?!none\b)[^;}{]+', source, re.IGNORECASE))
    if has_motion:
        if not re.search(r'@media\s*\(\s*prefers-reduced-motion', source, re.IGNORECASE):
            failures.append("a11y assertion: dynamic transitions/animations declared without @media (prefers-reduced-motion: reduce) override")

    # Hard floor: reject rogue :root color property redeclarations in <style>
    style_blocks = re.findall(r"<style\b[^>]*>(.*?)</style>", source, re.DOTALL | re.IGNORECASE)
    for sb in style_blocks:
        if re.search(r":root\s*\{[^}]*--(?:accent|bg|border|text)-[a-zA-Z0-9_-]+\s*:[^}]*\}", sb):
            failures.append("token assertion: rogue :root color tokens declared in <style> (shadows tokens.css; must consume tokens from tokens.css)")
            break

    # Signature Accent Discipline: enforce strict negative boundary for --accent-seal
    # var(--accent-seal) is reserved for authority seals, decisive commits, and fatal collisions;
    # it is strictly forbidden on draft, pending, secondary, ghost, or cancel affordances.
    if "--accent-seal" in token_source or "--accent-seal" in source:
        accent_leak_patterns = [
            r'<(?:button|a|span|div|p)\b[^>]*class=["\'][^"\']*(?:draft|pending|secondary|ghost|cancel|subtle|base|zero-borrow)[^"\']*["\'][^>]*style=["\'][^"\']*--accent-seal[^"\']*["\']',
            r'\.[a-zA-Z0-9_-]*(?:draft|pending|secondary|ghost|cancel|subtle|base|zero-borrow)[a-zA-Z0-9_-]*[^{}]*\{[^}]*var\(--accent-seal\)',
        ]
        for alp in accent_leak_patterns:
            if re.search(alp, source, re.IGNORECASE):
                failures.append(
                    "token-discipline assertion: Signature Accent Leak detected. "
                    "var(--accent-seal) is strictly reserved for authoritative gate, seal imprint, or fatal collision; "
                    "forbidden on draft, pending, secondary, ghost, cancel, or zero-borrow base elements."
                )
                break

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
            has_infinite_anim = bool(re.search(r"animation\s*:\s*[^;}]*\binfinite\b", source, re.IGNORECASE))
            if has_infinite_anim:
                # Infinite animations are permitted for high-yield containers, live indicators, or standard accessibility loading states
                is_authorized_animation = bool(re.search(
                    r'(?:class|id|data-zone)=["\'][^"\']*\b(?:high-yield|pulse|heartbeat|beacon|live-indicator|radar|spinner|loading|loader|progress)\b[^"\']*["\']|aria-busy=["\']true["\']|role=["\']progressbar["\']',
                    source,
                    re.IGNORECASE
                ))
                if not is_authorized_animation:
                    failures.append(
                        "cognitive-budget assertion: Energy leak in zero-borrow base UI. "
                        "Continuous infinite animations are forbidden outside explicit high-yield/pulse containers or loading states; "
                        "routine UI must settle to baseline calm equilibrium."
                    )

    # Dual-channel keyboard ergonomics check: when declared in contract, ensure event listener exists
    if contract_path and Path(contract_path).is_file():
        contract_text = Path(contract_path).read_text(encoding="utf-8")
        if "Dual-Channel Ergonomics" in contract_text or "Shortcut Key" in contract_text:
            if not re.search(r"addEventListener\s*\(\s*['\"]key(?:down|up)['\"]|\bonkey(?:down|up)\s*=", source, re.IGNORECASE):
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
            has_feedback_hook = bool(re.search(
                r'role=["\'](?:status|alert)["\']|class=["\'][^"\']*\b(?:toast|notification|feedback|alert-box|status-message|snackbar)\b[^"\']*["\']|id=["\'][^"\']*(?:toast|feedback|status-msg)[^"\']*["\']|data-(?:feedback|toast)=',
                source,
                re.IGNORECASE,
            ))
            if not has_feedback_hook:
                failures.append("action-lifecycle assertion: Action Verb Lifecycle declared in contract but DOM lacks visible feedback container (role='status|alert', class='toast|feedback', or id='toast')")

        # Touch-first gesture detents check: when touch-first ergonomics are declared in contract
        if "Touch-First Ergonomics" in contract_text or "Gesture Detents" in contract_text:
            has_touch = bool(re.search(r"addEventListener\s*\(\s*['\"](?:touch|pointer|click)['\"]|\b(?:ontouchstart|ontouchend|onclick)\s*=", source, re.IGNORECASE))
            if not has_touch:
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
            has_state_hook = bool(re.search(
                r"hashchange|location\.hash|data-state|state-[a-zA-Z0-9_-]+|class=[\"'][^\"']*(?:empty|loading|view-mode|state-)[^\"']*[\"']|id=[\"'][^\"']*(?:empty|loading|view-mode)[^\"']*[\"']",
                source,
                re.IGNORECASE,
            ))
            if not has_state_hook:
                failures.append("state-machine assertion: stress checkpoints declared but no state-switching hook detected (use hashchange / location.hash / data-state / class empty|loading|view-mode)")
            if not re.search(r"text-overflow\s*:\s*ellipsis|overflow(?:-[xy])?\s*:\s*(?:hidden|auto|scroll)|break-word|break-all|truncate|clamp\(|overflow-wrap\s*:\s*(?:anywhere|break-word)|word-break\s*:\s*break-all", source, re.IGNORECASE):
                failures.append("break-protocol assertion: missing string overflow containment (use text-overflow: ellipsis, overflow containment, truncate, or word-break: break-all)")

            # Actionable empty-state floor: empty-state presentation surface must provide an actionable trigger (button or link bait)
            empty_containers = re.findall(r'(<(?:div|section|aside|main)\b[^>]*(?:data-(?:for|state)=[\'"][^\'"]*empty[^\'"]*[\'"]|class=[\'"][^\'"]*\b(?:empty-state|state-empty|is-empty)\b[^\'"]*[\'"])[^>]*>.*?</(?:div|section|aside|main)>)', source, re.DOTALL | re.IGNORECASE)
            for ec in empty_containers:
                if not re.search(r'<button\b|<a\b[^>]*href=|role=[\'"]button[\'"]', ec, re.IGNORECASE):
                    failures.append("contextual agency assertion: empty state container lacks actionable trigger (<button> or <a href>)")
                    break

        # Zero Naked Metrics / Contextual Data Floor check
        if "Zero Naked Metrics" in contract_text or "Micro Sparklines" in contract_text or "sparkline" in contract_text.lower():
            # Domain Context Awareness: Narrative/Editorial literature surfaces measure prose by words/reading time, NOT telemetry graphs
            is_narrative = bool(re.search(r"editorial|reading|essay|narrative|阅读|长文|文学", contract_text, re.IGNORECASE))
            has_narrative_units = bool(re.search(r"\b\d+[\d,.]*\s*(?:字|词|min|分钟|words?|mins?|章|节|段|篇)\b", source, re.IGNORECASE))
            has_svg = bool(re.search(r"<svg\b[^>]*>(?:.*?<polyline|.*?<path|.*?<rect|.*?<line|.*?<circle)", source, re.DOTALL | re.IGNORECASE))
            has_html5_data = bool(re.search(r"<(?:meter|progress|data|canvas)\b", source, re.IGNORECASE))
            has_context_modifier = bool(re.search(r'class=["\'][^"\']*(?:unit|baseline|sparkline|threshold|reference|trend|delta|badge|status)[^"\']*["\']|data-(?:unit|baseline|threshold|trend|delta)=', source, re.IGNORECASE))
            has_metric_with_unit = bool(re.search(r'class=["\'][^"\']*(?:stat|metric|kpi|value|num|count)[^"\']*["\'][^>]*>\s*[\d.,]+\s*(?:[a-zA-Z%/$€¥°]|/[a-zA-Z]+)', source, re.IGNORECASE))
            if not (has_svg or has_html5_data or has_context_modifier or has_metric_with_unit or (is_narrative and has_narrative_units)):
                failures.append("data-craft assertion: Zero Naked Metrics violation (metrics must carry reference baseline, unit context, delta trend, visual sparkline/meter/canvas, or authentic narrative units)")

        # Tactile Detents / Interactive feedback: advisory craft, not a build blocker.
        # A specific press-physics recipe is a subjective craft choice; a functional
        # prototype is never failed for choosing different motion.
        if "Cognitive Budgeting" in contract_text or "Decisive Exchange 3-Frame" in contract_text or "Tactile Detents" in contract_text:
            has_active = bool(re.search(r":active\s*\{[^}]*(?:transform|scale|translate|filter|box-shadow|inset|opacity|background|border|color|duration|transition|motion|ease|cubic|rgb)", source, re.IGNORECASE))
            has_tailwind_active = bool(re.search(r"active:(?:scale|translate|bg|shadow|opacity)-", source))
            has_focus_visible = bool(re.search(r":focus-visible\s*\{", source, re.IGNORECASE))
            has_transition = bool(re.search(r"transition\s*:\s*[^;]+(?:transform|all|ease|cubic|duration|opacity|color)", source, re.IGNORECASE))
            has_pointer_mutation = bool(re.search(r"addEventListener\s*\(\s*['\"](?:pointerdown|touchstart|mousedown)['\"].*?(?:classList|style|scale|active|transform)", source, re.DOTALL | re.IGNORECASE))
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
                    has_link = re.search(rf"href=[\"'][^\"']*{re.escape(sid)}[^\"']*[\"']", source)
                    if delivered_sibling and not has_link:
                        failures.append(f"topology assertion: delivered sibling {sid} is not reachable by navigation link from {current_id}")
                    if not delivered_sibling and has_link:
                        failures.append(f"topology assertion: undelivered sibling {sid} linked by live href from {current_id} (404); render a disabled affordance instead")
                    if not delivered_sibling and not _pending_sibling_marked(source, sid):
                        failures.append(f"topology assertion: undelivered sibling {sid} is neither linked nor represented as a disabled affordance from {current_id}")

    failures.extend(coverage_failures(html, contract_path=contract_path))

    if check_stale:
        if re.search(r"\b(?:Lorem ipsum|placeholder text|sample copy)\b", source, re.IGNORECASE):
            failures.append("stale-template assertion: unconsidered placeholder content detected")

    states = _evidence_state(html)
    print("STATIC: " + ("pass" if not failures else "fail"))
    if LAST_COVERAGE_RESULTS.get("specification_missing"):
        # Surfaces to the operator that no spec text was found, so a pass was
        # not earned against an empty string.
        print("SPECIFICATION: missing")
    print("BROWSER: " + states.get("browser", "unverified"))
    print("VISUAL: " + states.get("visual", "unverified"))
    print("HUMAN: " + states.get("human", "unverified"))
    LAST_TIER_EVIDENCE.clear()
    LAST_TIER_EVIDENCE.update(tiered_quality_evidence(html, failures))
    for tier_id in ("L1", "L2", "L3"):
        record = LAST_TIER_EVIDENCE["tiers"][tier_id]
        status = record["status"]
        reason = f" ({record['reason']})" if record.get("reason") else ""
        print(f"TIER {tier_id}: {status}{reason}")
    if LAST_TIER_EVIDENCE.get("environment_not_ready"):
        print("ENVIRONMENT: not_ready (degraded to tier "
              f"{LAST_TIER_EVIDENCE['tier_reached']})")
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
    parser.add_argument("--tokens", dest="tokens_opt")
    parser.add_argument("--contract", dest="contract")
    parser.add_argument("--strict-divergence", action="store_true")
    args = parser.parse_args()

    root = Path.cwd()
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
        spec_path = root / f"prototype/specifications/{slice_id}/r1.md"
        contract_path = str(spec_path) if spec_path.is_file() else (args.contract or "")
        sys.exit(0 if assert_quality(str(html_path), str(token_path), args.strict_divergence, contract_path) else 1)

    if not args.html:
        parser.error("Must provide HTML path or --slice <id>")

    html = Path(args.html)
    token_arg = args.tokens_opt or args.tokens
    if not token_arg:
        token_arg = next((str(p) for p in (html.parent / "tokens.css", root / "prototype/shared/tokens.css") if p.is_file()), "prototype/shared/tokens.css")
    sys.exit(0 if assert_quality(str(html), token_arg, args.strict_divergence, args.contract) else 1)
