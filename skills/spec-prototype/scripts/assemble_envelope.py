#!/usr/bin/env python3
"""Synthesize a self-contained execution envelope for spec-prototype-builder.

Validates that Stage 1 Design Spec contracts exist and extracts all layout,
token, state machine, and assertion parameters into a single envelope JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional


SKILL = Path(__file__).resolve().parents[1]
if str(SKILL / "scripts") not in sys.path:
    sys.path.insert(0, str(SKILL / "scripts"))


def formal_contract_lint(root: Path, slice_id: str) -> List[Dict[str, str]]:
    """Run the real contract lint at the formal entry and return bounded failure records."""
    import lint_spec_contracts

    lint_errors = lint_spec_contracts.lint_formal_entry(root, slice_id)
    return [{"code": e.rule, "path": e.file_path, "message": e.message} for e in lint_errors]


def read_formal_context(root: Path, slice_id: str) -> Dict[str, Any]:
    """Normalized coverage/platform context, read from the retained authored sources."""
    import lint_spec_contracts

    return lint_spec_contracts.read_formal_context(root, slice_id)


# `prototype_context` normalizes authored facts with its own persisted vocabulary
# (`selected | full-product | legacy | unresolved`; `legacy`/`unresolved` are the
# absent-scope states, never buildable). The compiled envelope reports the shared
# `prototype-spec/v1` coverage enum instead: `key-journey` is the bounded,
# explicitly selected journey the runtime calls `selected`.
_ENVELOPE_COVERAGE = {
    "selected": "key-journey",
    "full-product": "full-product",
    "slice-isolated": "slice-isolated",
    "legacy": "legacy",
    "unresolved": "unresolved",
}


def _envelope_coverage(value: Any) -> Any:
    """Map a runtime coverage value onto the compiled envelope vocabulary."""
    return _ENVELOPE_COVERAGE.get(value, value)


def _contract_lint_gate(root: Path, slice_id: str) -> List[Dict[str, str]]:
    try:
        return formal_contract_lint(root, slice_id)
    except (OSError, ValueError) as error:
        # An unreadable artifact or an authored contract violation is a bounded
        # lint outcome. Programmer errors (ImportError, SyntaxError, TypeError,
        # AttributeError) are not: they propagate so a broken linter is never
        # silently reported as a stale contract.
        return [{"code": "E010_STALE_CONTRACT", "path": str(root), "message": str(error)}]


# Rules whose evidence is a legacy pillar (m1/f1/c1/r1). A canonical-IR entry
# owns those facts in compiled form, so on that path they are not actionable; the
# rules that read canonical paths, coverage, or map identity still apply.
_LEGACY_PRESENCE_RULES = ("E001", "E002", "E003", "E004", "E005", "E006", "E007", "E008")


def _canonical_contract_lint(root: Path, slice_id: str) -> List[Dict[str, str]]:
    """Run the formal lint on a canonical-IR entry, dropping legacy-presence rules.

    The lint reads the authored legacy pillars when they exist and stays silent
    when they do not, so a canonical-only repository still enforces every rule
    whose evidence it actually owns instead of skipping the lint wholesale.
    """
    try:
        import lint_spec_contracts

        errors = lint_spec_contracts.lint_formal_entry(root, slice_id)
    except (OSError, ValueError) as error:
        return [{"code": "E010_STALE_CONTRACT", "path": str(root), "message": str(error)}]
    return [
        {"code": e.rule, "path": e.file_path, "message": e.message}
        for e in errors
        if not e.rule.startswith(_LEGACY_PRESENCE_RULES)
    ]


_VERB_COLUMN_KEYS = (
    # (field, header fragments matched in priority order)
    ("action_id", ("action id", "action")),
    ("trigger_btn", ("trigger button", "trigger")),
    ("proximity_level", ("proximity",)),
    ("container_form", ("container form", "container", "modal / drawer", "drawer")),
    ("commit_btn", ("commit action", "commit")),
    ("feedback_style", ("feedback style", "completion feedback", "feedback", "toast")),
    ("consequence", ("impact", "consequence")),
)


def _verb_column_map(header_cells: List[str]) -> Dict[str, int]:
    """Bind each semantic field to the authored header column that owns it.

    The authored table owns its schema: a legacy 6-column table and the canonical
    7-column Proximity ladder both map correctly, and no column is read by position.
    """
    normalized = [re.sub(r"[\s*`]+", " ", cell).strip().lower() for cell in header_cells]
    mapping: Dict[str, int] = {}
    for field, fragments in _VERB_COLUMN_KEYS:
        for index, header in enumerate(normalized):
            if index in mapping.values():
                continue
            if any(fragment in header for fragment in fragments):
                mapping[field] = index
                break
    return mapping


def _verb_cells(row_cells: List[str], columns: Dict[str, int],
                header_cells: Optional[List[str]] = None) -> Dict[str, str]:
    def cell(field: str) -> str:
        index = columns.get(field)
        return row_cells[index].strip() if index is not None and index < len(row_cells) else ""

    container = cell("container_form")
    proximity = cell("proximity_level")
    if not proximity:
        # Legacy tables carry no Proximity column: infer the level from the
        # authored container, falling back to the header that framed that column
        # (a bare container value may name no container at all).
        hint = container.lower()
        index = columns.get("container_form")
        if header_cells and index is not None and index < len(header_cells):
            hint = f"{hint} {header_cells[index].lower()}"
        proximity = ("Level 4" if "modal" in hint
                     else "Level 3" if "drawer" in hint
                     else "Level 2" if "inspector" in hint or "margin" in hint
                     else "Level 1" if "flyout" in hint
                     else "Level 0")
    return {
        "action_id": cell("action_id"),
        "trigger_btn": cell("trigger_btn"),
        "proximity_level": proximity,
        "container_form": container,
        "commit_btn": cell("commit_btn"),
        "feedback_style": cell("feedback_style") or "Toast",
        "consequence": cell("consequence"),
    }


def check_spec_completeness(root: Path, slice_id: str, *, lint: bool = True) -> Dict[str, Path]:
    """Verify that required Stage 1 design contract artifacts exist and meet minimum content floors.

    Supports both:
    1. Modern Canonical IR: `prototype/contracts/compiled/<slice_id>/r1.spec.json`
       and `prototype/specifications/<slice_id>/r1.spec.md`
    2. Legacy 6-piece files: product.md, m1.md, f1.md, t1.md, c1.md, r1.md
    """
    canonical_ir = root / f"prototype/contracts/compiled/{slice_id}/r1.spec.json"
    canonical_md = root / f"prototype/specifications/{slice_id}/r1.spec.md"
    tokens_css = root / "prototype/shared/tokens.css"

    # If canonical IR is present, it serves as the single source of truth alongside tokens.css
    if canonical_ir.is_file() and tokens_css.is_file():
        if lint:  # the canonical entry runs the real lint
            failures = _canonical_contract_lint(root, slice_id)
            if failures:
                detail = "; ".join(
                    f"{f['code']}:{f['path']} ({f['message']})" if f["message"] else f"{f['code']}:{f['path']}"
                    for f in failures)
                raise ValueError(
                    f"Stage 1 contract lint failed at the formal entry. {detail}. "
                    f"Existing artifacts are unchanged; resolve each failure and re-assemble."
                )
        return {
            "canonical_ir": canonical_ir,
            "canonical_md": canonical_md,
            "tokens_css": tokens_css,
            # Backwards compatibility fallbacks if legacy files exist alongside
            "product": root / "prototype/product.md" if (root / "prototype/product.md").is_file() else canonical_md,
            "surface_map": root / "prototype/contracts/surface-maps/m1.md" if (root / "prototype/contracts/surface-maps/m1.md").is_file() else canonical_md,
            "foundation": root / "prototype/contracts/foundation/f1.md" if (root / "prototype/contracts/foundation/f1.md").is_file() else canonical_md,
            "tokens_md": root / "prototype/contracts/tokens/t1.md" if (root / "prototype/contracts/tokens/t1.md").is_file() else canonical_md,
            "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md" if (root / f"prototype/contracts/slices/{slice_id}/c1.md").is_file() else canonical_md,
            "specification": root / f"prototype/specifications/{slice_id}/r1.md" if (root / f"prototype/specifications/{slice_id}/r1.md").is_file() else canonical_md,
        }

    required = {
        "product": root / "prototype/product.md",
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "tokens_css": root / "prototype/shared/tokens.css",
        "tokens_md": root / "prototype/contracts/tokens/t1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }
    missing = [name for name, p in required.items() if not p.is_file()]
    if missing:
        raise ValueError(
            f"Stage 1 Spec Contract incomplete. Missing required artifacts: {', '.join(missing)}. "
            f"Either compile canonical IR (compile_spec_ir.py) or materialize legacy contract pillars."
        )

    if lint:  # the formal entry runs the real lint, not a parallel copy of it
        failures = _contract_lint_gate(root, slice_id)
        if failures:
            # Carry the rule's own detail: a stale map identity must name the
            # revision or digest that differs, not merely that something differs.
            detail = "; ".join(
                f"{f['code']}:{f['path']} ({f['message']})" if f["message"] else f"{f['code']}:{f['path']}"
                for f in failures)
            raise ValueError(
                f"Stage 1 contract lint failed at the formal entry. {detail}. "
                f"Existing artifacts are unchanged; resolve each failure and re-assemble."
            )

    return required


def extract_field(content: str, label: str, default: str = "") -> str:
    # The authored line may carry an annotation between the label and its value,
    # e.g. `- Content language (locked): en-US`. The annotation is descriptive
    # prose, not part of the value, so it is matched and discarded.
    pattern = rf"^- {re.escape(label)}(?: \([^)]*\))?:[ \t]*(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default


def parse_reality_anchors(raw: str) -> List[str]:
    """Split an authored Reality Anchors line into discrete anchor strings.

    The authored field is a comma/semicolon separated list ("Linear, Stripe
    Dashboard"), never a single string to be iterated character by character.
    An absent declaration yields [] rather than a fabricated anchor.
    """
    if not raw:
        return []
    return [part.strip() for part in re.split(r"[,;、]", raw) if part.strip()]


def _brief_path(root: Path, slice_id: str) -> Optional[Path]:
    """Find the retained direction brief without treating it as a formal spec."""
    candidates = (
        root / f"prototype/briefs/{slice_id}-probe.md",
        root / f"prototype/briefs/{slice_id}.md",
    )
    return next((path for path in candidates if path.is_file()), None)


def _brief_scope(value: str, fallback: str) -> str:
    scope = value.strip("`'\" ") or fallback
    return scope.rstrip("/") + "/"


def assemble_direction(root: Path, slice_id: str, brief: Path) -> Dict[str, Any]:
    """Assemble a direction-probe envelope from one exploration brief."""
    content = brief.read_text(encoding="utf-8")
    probe_id = extract_field(content, "Probe ID", slice_id).strip("`'\" ")
    raw_target = extract_field(content, "Probe target path", "")
    target_clean = raw_target.strip("`'\" ")
    if target_clean.endswith(".html"):
        target_html = target_clean
        proto_scope = target_clean.rsplit("/", 1)[0] + "/"
    elif target_clean:
        proto_scope = target_clean.rstrip("/") + "/"
        target_html = proto_scope + "index.html"
    else:
        proto_scope = f"prototype/experiments/probes/{probe_id}/"
        target_html = proto_scope + "index.html"

    evidence = _brief_scope(extract_field(content, "Evidence write scope"),
                            f"prototype/evidence/probes/{probe_id}/")
    return {
        "envelope_version": "1.0",
        "repository_root": str(root.resolve()),
        "skill_root": str(SKILL.resolve()),
        "slice_id": slice_id,
        "probe_id": probe_id,
        "mode": "direction-probe",
        "target_html_path": target_html,
        "prototype_write_scope": proto_scope,
        "evidence_write_scope": evidence,
        "brief": {"path": brief.relative_to(root).as_posix(),
                  "sha256": hashlib.sha256(brief.read_bytes()).hexdigest()},
        "constraints": {"thesis": extract_field(content, "Core design thesis")},
    }


def extract_css_tokens(css_text: str) -> Dict[str, str]:
    """Parse flat CSS custom property dictionary from tokens.css."""
    tokens: Dict[str, str] = {}
    for m in re.finditer(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", css_text):
        tokens[m.group(1).strip()] = m.group(2).strip()
    return tokens


def load_method_registry(registry_path: Path) -> List[Dict[str, Any]]:
    """Load craft methods from registry.yaml."""
    if not registry_path.is_file():
        return []
    try:
        import yaml
        content = registry_path.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        if isinstance(data, dict) and "methods" in data:
            return data["methods"]
    except Exception:
        pass
    return []


METHOD_ANCHORS: Dict[str, List[str]] = {
    "container-proximity-ladder": ["container proximity ladder", "proximity ladder", "flow preservation", "level 0"],
    "ooux-mapping": ["cardinality-to-layout", "model objects and content before containers", "cardinality"],
    "context-preservation": ["coherent wayfinding, context preservation", "context preservation", "content mechanics as interaction"],
    "progressive-disclosure": ["design information and interaction at the decision moment", "decision moment", "cognitive noise"],
    "action-verb-lifecycle": ["ceremony economy", "platform & somatic ergonomics", "action verb lifecycle", "action verb"],
    "decisive-3-frame": ["prototype the decisive exchange", "decisive exchange", "intent", "detent"],
    "the-break-protocol": ["the organic break protocol", "the break protocol", "extreme edge data"],
    "fault-tolerance-recovery": ["make consequential boundaries understandable", "sensitive or consequential", "reversibility"],
    "data-context-metrics": ["contextual semantic registers", "telemetry vs narrative", "zero naked metrics"],
    "form-ergonomics": ["form ergonomics and input orchestration", "form ergonomics", "input orchestration"],
    "visual-rhythm-density": ["materiality calibration", "lightweight native craft recipes", "anti-default palette"],
}


def extract_labeled_entries(text: str, label_pattern: str) -> List[Dict[str, str]]:
    """Parse a labeled section body into term/definition pairs.

    Accepts a Markdown table (`| Term | Definition |`) or bullet lines
    (`- Term: Definition`). Returns [] when the label is absent so an unauthored
    section stays unrepresented rather than fabricated.
    """
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        label = stripped.lstrip("#").strip()
        if re.match(label_pattern, label, re.IGNORECASE) and (stripped.startswith("#") or ":" in stripped):
            start = i + 1
            break
    if start is None:
        return []
    entries: List[Dict[str, str]] = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("#"):
            break
        if not stripped:
            continue
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) >= 2 and not set(cells[0]) <= set("-: "):
                entries.append({"term": cells[0].strip("`* "), "definition": cells[1].strip("`* ")})
            continue
        bullet = re.match(r"^[-*+]\s*(.+)$", stripped)
        if bullet:
            body = bullet.group(1)
            if ":" in body:
                term, _, definition = body.partition(":")
                entries.append({"term": term.strip("`* "), "definition": definition.strip()})
            else:
                entries.append({"term": body.strip("`* "), "definition": ""})
    # Discard a textual table header row such as `| Term | Definition |`.
    if entries and entries[0]["term"].lower() in ("term", "terminology", "token", "component", "constraint"):
        entries = entries[1:]
    return entries


def _extract_craft_guidance(skill_dir: Path, rel_file: str, method_id: str) -> str:
    """Extract actionable craft method guidance from the authoritative reference file."""
    if not rel_file:
        return ""
    ref_path = skill_dir / rel_file
    if not ref_path.is_file():
        return ""
    try:
        text = ref_path.read_text(encoding="utf-8")
        anchors = METHOD_ANCHORS.get(method_id, [method_id.replace("-", " ")])
        lines = []
        capture_level: Optional[int] = None
        for line in text.splitlines():
            sline = line.strip()
            if sline.startswith("#"):
                level = len(sline) - len(sline.lstrip("#"))
                # A same-or-higher-level header closes the captured section.
                if capture_level is not None and level <= capture_level:
                    break
                header = sline.lstrip("#").strip().lower()
                if any(a in header for a in anchors):
                    capture_level = level
                    lines.append(sline)
                continue
            elif capture_level is not None and sline:
                lines.append(sline)
        if not lines:
            for line in text.splitlines():
                sline = line.strip()
                if sline.startswith("| Level") or sline.startswith("| **Level") or sline.startswith("| Frame") or sline.startswith("| **Frame"):
                    lines.append(sline)
                if len(lines) >= 10:
                    break
        return "\n".join(lines) if lines else text[:300].strip()
    except Exception:
        return ""


def select_active_methods(
    registry_path: Path,
    stage: int = 2,
    layout_profile: str = "adaptive-workspace",
    spec_text: str = "",
    contract_text: str = "",
    product_text: str = "",
    slice_id: str = "",
    limit_range: tuple[int, int] = (3, 6),
) -> List[Dict[str, Any]]:
    """Select 3-6 relevant craft methods from registry.yaml based on stage and context triggers.

    Loads methods lazily, scores against observed triggers, and excludes non-matching methods.
    """
    all_methods = load_method_registry(registry_path)
    if not all_methods:
        return []

    combined = f"{slice_id} {layout_profile} {product_text} {contract_text} {spec_text}".lower()

    # Detect context features (triggers)
    active_triggers = set()

    # 1. State mutation & actions
    if re.search(r"\b(action|verb|mutation|drain|delete|quarantine|commit|isolate|revert|cancel|retry|lifecycle)\b", combined):
        active_triggers.add("state_mutation")
        active_triggers.add("decisive_commit")
    if re.search(r"\b(destructive|irreversible|hazard|permanent|remove|drop|evict)\b", combined):
        active_triggers.add("destructive_operations")
    if re.search(r"\b(multi-step|wizard|stepper|confirm\s+dialog|modal\s+header)\b", combined):
        active_triggers.add("multi_step_commit")

    # 2. Telemetry & Metrics
    if re.search(r"\b(telemetry|kpi|metric|metrics|sparkline|throughput|latency|chart|dashboard|counter|tabular-nums|numeric)\b", combined):
        active_triggers.add("telemetry_display")
        active_triggers.add("kpi_dashboard")
        active_triggers.add("real_time_monitoring")

    # 3. Forms & Inputs
    if re.search(r"\b(form|input|fields|validation|text-field|textarea|select|checkbox|submit|tabindex|tab\s+order)\b", combined):
        active_triggers.add("multi_field_input")
        active_triggers.add("inline_validation")
        active_triggers.add("complex_form")

    # 4. Topology & Entity cardinality
    if re.search(r"\b(1:n|n:m|cardinality|master-detail|entity|entities|relational|node-link|graph)\b", combined):
        active_triggers.add("multi_entity_domain")
        active_triggers.add("complex_cardinality")
        active_triggers.add("relational_navigation")

    # 5. Context & Navigation / Interruption
    if re.search(r"\b(drawer|modal|inspector|overlay|sheet|filter|facet|tab|preserve|resume|interruption)\b", combined):
        active_triggers.add("interruption_likely")
        active_triggers.add("drawer_or_modal_interaction")
        active_triggers.add("resumable_work")
        active_triggers.add("multi_object_context")

    # 6. Progressive disclosure & Density
    if layout_profile in ("dense-console", "operational-canvas") or re.search(r"\b(workbench|console|dense|advanced|secondary|parameters|disclosure)\b", combined):
        active_triggers.add("dense_data_workbench")
        active_triggers.add("advanced_parameters")
        active_triggers.add("secondary_actions")

    # 7. Visual rhythm & composition
    active_triggers.add("hero_anchor_layout")
    active_triggers.add("typographic_hierarchy")
    active_triggers.add("spatial_composition")

    # 8. Stress & Break protocol
    if re.search(r"\b(break\s+protocol|stress|unbreakable|320px|empty\s+state|overflow|debounce|edge\s+case)\b", combined):
        active_triggers.add("edge_case_audit")
        active_triggers.add("extreme_viewport_320px")
        active_triggers.add("unbreakable_strings")
        active_triggers.add("zero_one_thousand_data")

    # 9. Fault tolerance & Undo
    if re.search(r"\b(undo|rollback|revert|recovery|fault\s+tolerance|reversib)\b", combined):
        active_triggers.add("undoable_actions")
        active_triggers.add("network_recovery")

    # 10. Tactile & Decisive feedback
    if re.search(r"\b(tactile|detent|press|feedback|spring|haptic|settlement|frame)\b", combined):
        active_triggers.add("tactile_feedback")
        active_triggers.add("state_settlement")

    scored_candidates = []
    for m in all_methods:
        stages = m.get("stages", [])
        if stages and stage not in stages:
            continue

        method_triggers = set(m.get("activate_when", []))
        matched = method_triggers.intersection(active_triggers)
        score = len(matched) * 2

        # Bonus: explicit mention of method id or name
        if m.get("id", "").lower() in combined or m.get("name", "").lower() in combined:
            score += 10

        # Bonus: explicit mention of pillars in combined
        for p in m.get("pillars", []):
            if p.lower() in combined:
                score += 1

        if score > 0:
            scored_candidates.append({
                "method": m,
                "score": score,
                "matched_triggers": sorted(list(matched)),
            })

    # Sort candidates by score descending
    scored_candidates.sort(key=lambda x: x["score"], reverse=True)

    min_limit, max_limit = limit_range
    selected_scored = scored_candidates[:max_limit]

    result = []
    skill_dir = Path(__file__).resolve().parent.parent
    for sc in selected_scored:
        m = sc["method"]
        rel_file = m.get("file", "")
        guidance = _extract_craft_guidance(skill_dir, rel_file, m.get("id", ""))
        result.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "pillars": m.get("pillars", []),
            "invariants": m.get("invariants", []),
            "reference_file": rel_file,
            "actionable_guidance": guidance,
            "matched_triggers": sc["matched_triggers"],
        })
    return result


# ── Lean Builder Payload ──
# The builder prompt carries the compiled executable IR plus the execution
# context it needs to run. Legacy intermediate blobs stay available on the
# in-memory envelope for downstream tooling, but are demoted out of the prompt
# so they stop competing with the IR for the Builder's attention.
_IR_FIELDS = (
    "identity",
    "semantic_contract",
    "layout_directives",
    "visual_directives",
    "action_contracts",
    "verification_contract",
    "open_design_space",
)
_PAYLOAD_CONTEXT_FIELDS = (
    "envelope_version",
    "envelope_architecture",
    "authority_status",
    "build_authority",
    "has_hypothesis_actions",
    "builder_guidance",
    "mode",
    "repository_root",
    "skill_root",
    "slice_id",
    "platform",
    "coverage",
    "target_html_path",
    "evidence_output_dir",
    "verification_command",
    "capture_command",
    "inspection_contract",
    "spec_sources",
    "spec_references",
    "token_stylesheet_ref",
    "token_link_tag",
    # Authored/derived contracts the Builder must read directly: the content
    # language lock, the shared navigation shell, and the state machine were
    # demoted with the legacy blobs and became unreadable downstream.
    "content_language",
    "topology_context",
    "interaction_spec",
)
_PAYLOAD_METHOD_FIELDS = ("id", "name", "pillars", "invariants", "reference_file")
# Intermediate synthesis products retained for diagnostics and downstream
# consumers; they are not part of the Builder's authored authority.
_DEBUG_CONTEXT_FIELDS = (
    "constraint_envelope",
    "creative_envelope",
    "available_tokens",
    "app_shell_blueprint",
    "app_shell_contract",
    "ooux_topology",
    "cognitive_ledger",
    "fault_tolerance_protocol",
    "design_constraints",
    "verifiable_assertions",
    "domain_thesis",
    "attention_routing",
    "data_stress_boundaries",
    "active_methods",
    "five_axes",
    "dtcg_tokens",
    "layout_profile",
    "candidate_patterns",
    "selected_pattern",
    "reality_anchors",
    "specification",
    "tokens_md_ref",
)


def build_builder_payload(envelope: Dict[str, Any], *, include_debug: bool = False) -> Dict[str, Any]:
    """Project an assembled envelope onto the lean prompt the Builder receives.

    The default payload keeps the 7-field executable IR and the execution context
    only. `include_debug=True` re-attaches the demoted intermediate blobs under
    `debug_context` for inspection, keeping the lean view intact.
    """
    payload = {
        field: envelope[field]
        for field in _IR_FIELDS + _PAYLOAD_CONTEXT_FIELDS
        if field in envelope
    }
    # Slim craft-method metadata rides along with the payload; the verbose
    # `actionable_guidance` duplicate is reachable through `reference_file`.
    if "active_methods" in envelope:
        payload["active_methods"] = [
            {field: method[field] for field in _PAYLOAD_METHOD_FIELDS if field in method}
            for method in envelope["active_methods"]
        ]
    if include_debug:
        payload["debug_context"] = {
            field: envelope[field] for field in _DEBUG_CONTEXT_FIELDS if field in envelope}
    return payload


def _mandatory_viewports(platform: Dict[str, Any]) -> List[Dict[str, str]]:
    """Derive the inspection viewports from the authored device fact.

    A mismatched viewport gate is a false negative, not a stricter one: a
    desktop-only console has no authored mobile contract to violate, and a
    touch-primary flow has no authored desktop one. An undeclared device keeps
    both extremes rather than inventing a restricted set.
    """
    device = str(platform.get("device_context") or "").strip().lower()
    desktop = {"width": 1280, "name": "desktop-canvas",
               "focus": "spatial hierarchy and high-density telemetry"}
    mobile = {"width": 390, "name": "mobile-somatic",
              "focus": "44px touch targets and responsive folding without amnesia"}
    tablet = {"width": 768, "name": "tablet-canvas",
              "focus": "adaptive reflow and touch-reachable controls without amnesia"}
    if device == "desktop":
        return [desktop]
    if device in ("mobile", "phone", "handheld"):
        return [mobile]
    if device in ("tablet", "ipad"):
        return [tablet]
    # responsive / hybrid / undeclared: both authored extremes stay checked.
    return [desktop, mobile]


def assemble(root: Path, slice_id: str, *, lint: bool = True, exploratory: bool = False) -> Dict[str, Any]:
    """Assemble an envelope for either exploration or formal candidate work."""
    brief = _brief_path(root, slice_id)
    specification = root / f"prototype/specifications/{slice_id}/r1.md"
    # A canonical build authors `r1.spec.md` (and usually the compiled IR) instead
    # of `r1.md`; either form means a specification exists and must not be routed
    # into the direction-probe path.
    canonical_md = root / f"prototype/specifications/{slice_id}/r1.spec.md"
    canonical_ir = root / f"prototype/contracts/compiled/{slice_id}/r1.spec.json"
    has_specification = (
        specification.is_file() or canonical_ir.is_file() or canonical_md.is_file())

    # If exploratory mode is requested, synthesize direction brief from discussion.md
    if exploratory and not has_specification:
        disc_path = root / "prototype/discussion.md"
        if disc_path.is_file() and brief is None:
            # Auto-synthesize a dynamic exploratory brief from discussion
            brief_dir = root / "prototype/briefs"
            brief_dir.mkdir(parents=True, exist_ok=True)
            synthetic_brief = brief_dir / f"{slice_id}.md"
            if not synthetic_brief.is_file():
                synthetic_brief.write_text(f"""# Direction Brief: {slice_id}
- Probe ID: `{slice_id}`
- Core design thesis: Exploratory direction probe derived from prototype/discussion.md
- Probe target path: `prototype/experiments/probes/{slice_id}/index.html`
- Evidence write scope: `prototype/evidence/probes/{slice_id}/`
""", encoding="utf-8")
            brief = synthetic_brief

    if brief is not None and not has_specification:
        return assemble_direction(root, slice_id, brief)
    paths = check_spec_completeness(root, slice_id, lint=lint)

    product_content = paths["product"].read_text(encoding="utf-8")
    smap_content = paths["surface_map"].read_text(encoding="utf-8")
    contract_content = paths["slice_contract"].read_text(encoding="utf-8")
    spec_content = paths["specification"].read_text(encoding="utf-8")

    # Target scopes: support both neutral anchor/ and legacy hero-anchor/
    default_scope = f"prototype/experiments/{slice_id}/anchor/"
    write_scope = extract_field(spec_content, "Prototype write scope", default_scope)
    write_scope_clean = write_scope.strip("`'\" ")
    if not write_scope_clean.endswith("/"):
        write_scope_clean += "/"

    target_html = write_scope_clean + "index.html"
    evidence_scope = extract_field(spec_content, "Evidence write scope", f"prototype/evidence/probes/{slice_id}/").strip("`'\" ")

    # ── Content Language Lock (语种锁定) ──
    # Stage 1 declares the shipped-copy language; every downstream fixture must honour it.
    lang_raw = (
        extract_field(spec_content, "Content language", "")
        or extract_field(contract_content, "Content language", "")
        or extract_field(product_content, "Content Language", "")
    ).strip("`'\" ")
    lang_token = re.split(r"[\s(（;、,]", lang_raw.strip())[0].strip("`'\" ") if lang_raw else ""
    if not re.match(r"^[a-zA-Z]{2,3}(-[a-zA-Z0-9]{2,8})*$", lang_token or ""):
        discussion_path = root / "prototype/discussion.md"
        discussion_text = discussion_path.read_text(encoding="utf-8") if discussion_path.is_file() else ""
        disc_lang = re.search(r"(?:Content\s+Language|语种|语言)\s*[:=]?\s*`?([a-zA-Z]{2,3}(?:-[a-zA-Z0-9]{2,8})*)`?", discussion_text, re.IGNORECASE)
        lang_token = disc_lang.group(1) if disc_lang else ""
    content_language = {
        "tag": lang_token or "undetermined",
        "locked": bool(lang_token),
        "rule": (
            f"All shipped copy, fixture content and aria labels MUST be authored in `{lang_token}` "
            "(secondary language allowed only where the declaration includes it). "
            "Set <html lang> to match."
            if lang_token else
            "Stage 1 did not declare a content language. Author copy in the language of the brief "
            "and set <html lang> to match; do not silently translate surfaced content."
        ),
    }

    # ── Universal Physical Grounding & Reality Anchor Extraction ──
    # Rather than rigid 4-baseline silos, extract authored Reality Anchors and physical lifeworld analogies
    anchors_match = re.search(r"^[-*+]?\s*(?:Reality\s+(?:Benchmark\s+)?Anchors?|Physical\s+Anchors?|Reality\s+Anchors?|对标|地锚)\s*[:=]?\s*([^\n]+)", product_content + "\n" + spec_content, re.MULTILINE | re.IGNORECASE)
    reality_anchors_raw = anchors_match.group(1).strip() if anchors_match else ""
    reality_anchors = parse_reality_anchors(reality_anchors_raw)

    # ── Advisory pattern candidates (CPC-004) ──
    # Product category is a weak signal, not a lock: it only orders advisory candidates.
    # Layout and component topology remain the Builder's decision unless an upstream
    # authored design specification explicitly names one pattern.
    PATTERN_SIGNALS = (
        ("dense-console", r"Baseline 1|Console|Control|工作台|控制台|运维|telemetry|dense-console|telemetry-grid|datadog|bloomberg"),
        ("operational-canvas", r"Baseline 2|SaaS|Commerce|Project|画布|业务|交易|canvas|operational-canvas|master-detail"),
        ("editorial-reading", r"Baseline 3|Editorial|Reading|阅读|文章|出版|editorial-reading|long-form|new\s+yorker|readwise"),
        ("somatic-touchflow", r"Baseline 4|Consumer|Mobile|Touch|消费|移动|触控|somatic|touch-friendly|mobile-first"),
    )
    # Narrow fallback: explicit pattern names only, so incidental prose stays adaptive.
    FALLBACK_SIGNALS = (
        ("somatic-touchflow", r"\bBaseline 4\b|mobile-first|touch-friendly"),
        ("editorial-reading", r"\bBaseline 3\b|editorial-reading|long-form|ia\s+writer|new\s+yorker|readwise"),
        ("operational-canvas", r"\bBaseline 2\b|operational-canvas|master-detail"),
        ("dense-console", r"\bBaseline 1\b|dense-console|telemetry-grid|datadog|bloomberg"),
    )
    all_spec_text = product_content + " " + spec_content + " " + reality_anchors_raw

    baseline_match = re.search(r"^[-*+]?\s*(?:Dominant\s+Baseline|Baseline|基线)\s*[:=]\s*([^\n]+)", product_content, re.MULTILINE | re.IGNORECASE)
    declared_baseline = baseline_match.group(1).strip() if baseline_match else ""

    candidate_patterns: List[str] = []
    if declared_baseline:
        for name, signal in PATTERN_SIGNALS:
            if re.search(signal, declared_baseline, re.IGNORECASE):
                candidate_patterns.append(name)
                break
    for name, signal in FALLBACK_SIGNALS:
        if name not in candidate_patterns and re.search(signal, all_spec_text, re.IGNORECASE):
            candidate_patterns.append(name)

    # An explicit authored declaration is the only confirmation route.
    explicit_match = re.search(
        r"^[-*+]?\s*(?:Layout\s+Profile|Selected\s+Pattern|Confirmed\s+Pattern)\s*[:=]\s*([^\n]+)",
        product_content + "\n" + spec_content, re.MULTILINE | re.IGNORECASE)
    selected_pattern: Optional[str] = None
    if explicit_match:
        declared_pattern = explicit_match.group(1).strip().lower()
        selected_pattern = next(
            (name for name, _ in PATTERN_SIGNALS if name == declared_pattern), None)

    # `layout_profile` retained for backward compatibility with downstream consumers
    # (test_pipeline.py, test_v10_integrity.py); the Builder owns the final decision.
    # Unselected patterns stay advisory: no candidate is promoted into a topology lock.
    layout_profile = selected_pattern or "adaptive-workspace"

    # Extract verifiable assertions & Break Protocol
    assertions: List[str] = []
    break_checkpoints: List[str] = []
    shortcuts: List[str] = []
    verb_lifecycle: List[Dict[str, str]] = []
    decisive_frames: List[str] = []
    context_rules: List[str] = []

    # Parse assertions
    in_section: Optional[str] = None
    for line in spec_content.splitlines():
        if "Verifiable Design Assertions" in line or "Required screenshot checkpoints" in line:
            in_section = "assertions"
            continue
        elif "The Break Protocol Stress Checkpoints" in line:
            in_section = "break"
            continue
        elif "Dual-Channel Ergonomics" in line:
            in_section = "shortcuts"
            continue
        elif line.startswith("#"):
            in_section = None
            continue

        if line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if not parts:
                continue
            if in_section == "assertions" and parts[0] not in ("Surface / interaction", "Assertion"):
                assertions.append(parts[0])
            elif in_section == "break" and parts[0] not in ("Reality Breaker",):
                break_checkpoints.append(f"{parts[0]}: {parts[1] if len(parts) > 1 else ''}")
            elif in_section == "shortcuts" and parts[0] not in ("Shortcut Key",):
                shortcuts.append(parts[0])

    # Parse Action Verb Lifecycle and Frame deduction from slice contract
    cognitive_ledger = {
        "zero_borrow_base": "Standard navigation, filter chips, and basic data tables must maintain zero cognitive friction with zero distracting motion.",
        "high_yield_borrow_zone": f"Primary operational {slice_id} workspace is granted visual energy budget: perceptible tactile feedback, baseline sparklines, and micro-flow liveliness.",
        "repayment_settlement": "Upon decisive action commit or inspector close, all dynamic visual indicators settle back into baseline calm equilibrium."
    }
    in_ledger = False
    in_verbs = False
    in_frames = False
    in_rules = False
    in_fault = False
    verb_columns: Optional[Dict[str, int]] = None
    verb_header: List[str] = []
    fault_tolerance: List[Dict[str, str]] = []
    for line in contract_content.splitlines():
        if "Cognitive Budgeting & Energy Return Ledger" in line:
            in_ledger = True
            in_verbs = False
            in_frames = False
            in_rules = False
            in_fault = False
            continue
        elif "Action Verb Lifecycle Table" in line:
            in_ledger = False
            in_verbs = True
            in_frames = False
            in_rules = False
            in_fault = False
            verb_columns = None
            continue
        elif "Fault Tolerance & Error Recovery Contract" in line:
            in_ledger = False
            in_verbs = False
            in_frames = False
            in_rules = False
            in_fault = True
            continue
        elif "Decisive Exchange 3-Frame" in line:
            in_ledger = False
            in_verbs = False
            in_frames = True
            in_rules = False
            in_fault = False
            continue
        elif "Context Preservation Rules" in line:
            in_ledger = False
            in_verbs = False
            in_frames = False
            in_rules = True
            in_fault = False
            continue
        elif line.startswith("##"):
            in_ledger = False
            in_verbs = False
            in_frames = False
            in_rules = False
            in_fault = False
            continue

        if in_fault and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [re.sub(r"[*`]", "", p).strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 3 and parts[0] not in ("Operation Category",):
                fault_tolerance.append({
                    "category": parts[0],
                    "hazard_level": parts[1] if len(parts) > 1 else "",
                    "defense": parts[2] if len(parts) > 2 else "",
                    "recovery": parts[3] if len(parts) > 3 else ""
                })

        if in_ledger and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 2 and parts[0] not in ("Ledger Zone",):
                zone_name = parts[0].lower()
                if "zero" in zone_name or "base" in zone_name or "基座" in zone_name:
                    cognitive_ledger["zero_borrow_base"] = parts[1]
                elif "borrow" in zone_name or "特区" in zone_name or "溢价" in zone_name:
                    cognitive_ledger["high_yield_borrow_zone"] = parts[1]
                elif "repayment" in zone_name or "settle" in zone_name or "偿还" in zone_name:
                    cognitive_ledger["repayment_settlement"] = parts[1]
        elif in_verbs and line.strip().startswith("|") and not line.strip().startswith("|---"):
            parts = [re.sub(r"[*`]", "", p).strip() for p in line.split("|") if p.strip()]
            if parts and len(parts) >= 4:
                # Header-driven column mapping: the first row after the section
                # heading is the authored header and owns the schema, so a 5/6/7-column
                # table or any column order maps without positional crosstalk.
                if verb_columns is None:
                    verb_columns = _verb_column_map(parts)
                    verb_header = parts
                    continue
                cells = _verb_cells(parts, verb_columns, verb_header)
                if not cells["action_id"]:
                    continue
                act_id = cells["action_id"]
                trig_btn = cells["trigger_btn"]
                prox_level = cells["proximity_level"]
                cont_form = cells["container_form"]
                commit_btn = cells["commit_btn"]
                fb_style = cells["feedback_style"]
                consequence = cells["consequence"]

                # Derive physical container implementation directive based on Proximity Level 0~4
                prox_lower = prox_level.lower()
                if "0" in prox_lower or "in-situ" in prox_lower or "popover" in cont_form.lower():
                    physical_directive = "Level 0 (In-situ): use inline popover, tooltip, or dropdown; NEVER render blocking backdrop or modal."
                elif "1" in prox_lower or "flyout" in cont_form.lower():
                    physical_directive = "Level 1 (Anchored Flyout): render anchored floating card adjacent to trigger; background remains active."
                elif "2" in prox_lower or "inspector" in cont_form.lower() or "margin" in cont_form.lower():
                    physical_directive = "Level 2 (Inspector Column): render side margin column or collapsible dock; primary canvas stays focused."
                elif "3" in prox_lower or "drawer" in cont_form.lower():
                    physical_directive = "Level 3 (Contextual Drawer): render contextual slide-over drawer; preserve uncommitted draft state on dismiss."
                elif "4" in prox_lower or "modal" in cont_form.lower():
                    physical_directive = "Level 4 (Modal Dialog): render native <dialog> with paired Confirm/Cancel buttons and explicit ESC dismiss."
                else:
                    physical_directive = f"Container: render {cont_form} respecting non-blocking layout proximity."

                verb_lifecycle.append({
                    "action_id": act_id,
                    "trigger_btn": trig_btn,
                    "proximity_level": prox_level,
                    "container_form": cont_form,
                    "commit_btn": commit_btn,
                    "feedback_style": fb_style,
                    "consequence": consequence,
                    "physical_directive": physical_directive,
                    # Backward-compatibility alias keys
                    "modal_header": cont_form,
                    "toast": fb_style,
                })
        elif in_frames and line.strip().startswith("- "):
            decisive_frames.append(line.strip()[2:].strip())
        elif in_rules and line.strip().startswith("- "):
            context_rules.append(line.strip()[2:].strip())

    # Extract 3 Ruthless Omissions and Material Invariants from Foundation / Product
    f1_text = paths["foundation"].read_text(encoding="utf-8")
    omissions: List[str] = []
    invariants: List[str] = []
    in_om = False
    in_inv = False
    for line in f1_text.splitlines():
        if "3 Ruthless Omissions" in line:
            in_om = True
            in_inv = False
            continue
        elif "Material Non-Transfer" in line:
            in_om = False
            in_inv = True
            continue
        elif line.startswith("##"):
            in_om = False
            in_inv = False
            continue
        if in_om and line.strip().startswith("- "):
            omissions.append(line.strip()[2:].strip())
        elif in_inv and line.strip().startswith("- "):
            invariants.append(line.strip()[2:].strip())

    constraints = {
        "dual_channel_shortcuts": shortcuts,
        "action_verb_lifecycle": verb_lifecycle,
        "break_protocol_checkpoints": break_checkpoints,
        "decisive_exchange_frames": decisive_frames,
        "context_preservation_rules": context_rules,
        "ruthless_omissions": omissions or [
            "No unauthored promotional hero widgets or marketing carousels.",
            "No nested modal deadlocks; interactions stay in-canvas or single contextual drawer.",
            "No ungrounded alien physics or decorative animations."
        ],
        "material_non_transfer_boundaries": invariants or [
            "Surface contrast and visual hierarchy respect design tokens; zero unconsidered flat grays.",
            "Interactive controls provide immediate, perceptible state feedback without layout shift.",
            "Visual indicators and state badges deliver calibrated operational signals."
        ],
    }
    # Authored component constraints travel with the constraint envelope so the
    # Builder reads declared component boundaries instead of guessing them.
    constraints["component_constraints"] = extract_labeled_entries(
        spec_content, r"Component\s+Constraints?|组件约束")
    explicit_turns = extract_field(spec_content, "Maximum operational repair attempts")
    if explicit_turns:
        constraints["maximum_operational_repair_attempts"] = explicit_turns

    spec_rel = paths["specification"].relative_to(root).as_posix()
    target_dir = (root / target_html).parent
    token_rel_href = os.path.relpath(paths["tokens_css"], target_dir)
    token_link_tag = f'<link rel="stylesheet" href="{token_rel_href}">'

    # Parse shared topology navigation from surface map
    nav_links = []
    current_role = "primary"
    for line in smap_content.splitlines():
        m = re.search(r"\*\*(.+?)\*\*\s*:\s*`([^`]+)`", line)
        if m:
            role_label, path_raw = m.group(1).strip(), m.group(2).strip()
            if "hero-anchor" in path_raw:
                surf_path = root / f"prototype/experiments/{path_raw}/index.html"
                sid = path_raw.split("/")[0]
            elif "anchor" in path_raw:
                surf_path = root / f"prototype/experiments/{path_raw}/index.html"
                sid = path_raw.split("/")[0]
            elif path_raw.startswith("surfaces/"):
                surf_path = root / f"prototype/{path_raw}/index.html"
                sid = path_raw.replace("surfaces/", "")
            else:
                p_anchor = root / f"prototype/experiments/{path_raw}/anchor/index.html"
                p_hero = root / f"prototype/experiments/{path_raw}/hero-anchor/index.html"
                if p_anchor.is_file():
                    surf_path = p_anchor
                elif p_hero.is_file():
                    surf_path = p_hero
                else:
                    surf_path = root / f"prototype/{path_raw}/index.html"
                sid = path_raw

            is_active = (sid == slice_id or path_raw == slice_id)
            if is_active:
                if "Primary" in role_label or "主工作区" in role_label:
                    current_role = "primary"
                elif "Contextual" in role_label or "上下文" in role_label:
                    current_role = "contextual"
                else:
                    current_role = "supporting"

            rel_href = os.path.relpath(surf_path, target_dir)
            label = sid.replace("-", " ").title()
            # Navigation integrity: the current slice will be written by this dispatch,
            # but a sibling surface only gets an href when it is actually delivered.
            # An undelivered surface becomes a declared pending entry, never a broken link.
            delivered = is_active or surf_path.is_file()
            entry = {
                "slice_id": sid,
                "label": label,
                "role": role_label,
                "active": is_active,
                "delivered": delivered,
            }
            if delivered:
                entry["href"] = rel_href
            else:
                entry["href"] = None
                entry["pending_note"] = (
                    "Surface not delivered in this slice. Render a disabled affordance with no href; "
                    "never emit a link that escapes the prototype scope."
                )
            nav_links.append(entry)

    verification_cmd = f"python3 skills/spec-prototype/scripts/verify_prototype_quality.py --slice {slice_id}"
    # The capture command is assembled after the authored viewport and state
    # contracts resolve, so the derived gates actually reach capture.mjs.
    capture_cmd = f"node skills/spec-prototype/scripts/capture.mjs --slice {slice_id}"

    # Extract OOUX Cardinality & Spatial Mapping from authored surface map or spec contract.
    # Authority invariant: Object Cardinality -> Topology Constraints -> Layout Candidate.
    # Inverse inference (Layout Profile -> Object Cardinality) is strictly prohibited.
    cardinality_match = re.search(r"(?:Cardinality|OOUX|实体基数|基数映射)[^\n]*[:=]?\s*(1:1|1:N|N:M)", smap_content + " " + spec_content, re.IGNORECASE)
    if cardinality_match:
        ooux_cardinality = cardinality_match.group(1).upper()
        if ooux_cardinality == "1:1":
            ooux_layout_mode = "focused-cockpit"
        elif ooux_cardinality == "1:N":
            if layout_profile in ("editorial-reading", "somatic-touchflow"):
                ooux_layout_mode = "stream-feed"
            else:
                ooux_layout_mode = "split-master-detail"
        elif ooux_cardinality == "N:M":
            ooux_layout_mode = "node-link-canvas"
        else:
            ooux_layout_mode = "adaptive"
    else:
        # Without explicit authoring, cardinality stays adaptive; layout mode remains adaptive-flow
        # No reverse inference from layout profile (e.g. dense-console -> 1:N)
        ooux_cardinality = "adaptive"
        ooux_layout_mode = "adaptive-flow"

    ooux_topology = {
        "cardinality": ooux_cardinality,
        "layout_mode": ooux_layout_mode,
        "spatial_rule": (
            "1:1 Focused Cockpit: Single focal instrument or deep reading column; zero split distraction."
            if ooux_cardinality == "1:1" else
            "1:N Master-Detail: High-density stream or list paired with sticky contextual parameter inspection."
            if ooux_cardinality == "1:N" else
            "N:M Relational Matrix / Canvas: Multi-node interconnected graph or multi-facet filtering grid."
            if ooux_cardinality == "N:M" else
            "Adaptive Flow: Spatial topology tailored to task context and primary object without forced split."
        )
    }

    # Profile-aware interaction_spec: only emit what the Builder must actually implement.
    # dense-console / operational-canvas: full lifecycle, shortcuts, sparklines.
    # editorial-reading: focus on typography reading experience; strip heavy action modals.
    # somatic-touchflow: strip desktop shortcuts; keep thumb-zone state machine only.
    _is_dense = layout_profile in ("dense-console", "operational-canvas")
    _is_editorial = layout_profile == "editorial-reading"
    _is_touch = layout_profile == "somatic-touchflow"

    # Domain states are authoritative only when a literal States / Supported
    # States line is declared in c1/r1. Absence stays absent: the IR must not
    # promote discovered behavior into the explicit domain layer.
    explicit_domain_states: List[str] = []
    for line in spec_content.splitlines() + contract_content.splitlines():
        m_st = re.search(r"(?:Supported States|States|状态流转|支持状态)\s*[:=]\s*([^\n]+)", line, re.IGNORECASE)
        if m_st:
            raw_states = [s.strip("`'\" ") for s in re.split(r"[,/|;]", m_st.group(1)) if s.strip("`'\" ")]
            if raw_states:
                explicit_domain_states = raw_states
                break

    # Experience states are derived from assertions and break-protocol
    # checkpoints; they carry derived authority, never explicit.
    derived_experience_states: List[str] = []
    for a in assertions + break_checkpoints:
        a_lower = a.lower()
        if "empty" in a_lower and "empty" not in derived_experience_states:
            derived_experience_states.append("empty")
        if ("error" in a_lower or "alert" in a_lower) and "error" not in derived_experience_states:
            derived_experience_states.append("error")
        if ("select" in a_lower or "highlight" in a_lower) and "selecting" not in derived_experience_states:
            derived_experience_states.append("selecting")
        if ("note" in a_lower or "annotate" in a_lower) and "annotating" not in derived_experience_states:
            derived_experience_states.append("annotating")
        if ("undo" in a_lower or "recover" in a_lower) and "undo_pending" not in derived_experience_states:
            derived_experience_states.append("undo_pending")

    # UI transient states exist only when c1 genuinely names them; otherwise [].
    derived_transient_states: List[str] = [
        kw for kw in ("submitting", "failed", "loading", "saving", "pending")
        if re.search(r"\b" + kw + r"\b", contract_content, re.IGNORECASE)
    ]

    # Legacy interaction_spec keeps a usable default; the explicit domain layer
    # above stays strictly authored.
    if explicit_domain_states:
        authored_states = list(explicit_domain_states)
    elif derived_experience_states:
        authored_states = ["default"] + list(derived_experience_states)
    else:
        authored_states = ["default"]

    interaction_spec: Dict[str, Any] = {
        "state_machine": {
            "type": "hash_state",
            "query_param": "state",
            "supported_states": authored_states,
            "dom_hook": "document.body.dataset.state"
        },
        "break_protocol_checkpoints": break_checkpoints,
    }
    # Dynamic interaction spec projection based on profile and authored rules
    interaction_spec["dual_channel_shortcuts"] = shortcuts
    interaction_spec["action_verb_lifecycle"] = verb_lifecycle
    interaction_spec["decisive_exchange_frames"] = decisive_frames
    interaction_spec["context_preservation_rules"] = context_rules

    if _is_dense:
        interaction_spec["profile_notes"] = (
            "dense-console: implement Action Verb Lifecycle (trigger→drawer/modal→commit→toast), "
            "declared keyboard shortcuts (if any), tabular-nums telemetry where comparative data is displayed, and SVG micro-sparklines."
        )
    elif _is_editorial:
        sanitized_verbs = []
        for v in verb_lifecycle:
            v_clean = dict(v)
            v_clean["container_mode"] = "in_situ_popover"
            v_clean["modal_header"] = "N/A (Inline popover only; no blocking drawer or modal)"
            sanitized_verbs.append(v_clean)

        interaction_spec["profile_notes"] = (
            "editorial-reading: prioritize focused typography (max-width 68ch), paper-contrast palette, "
            "quiet inline feedback. Do NOT implement modal dialogs, full-height action drawers, or telemetry sparklines. "
            "Selection actions must appear in-situ via floating popover or companion margin column. "
            "Reading metric labels (e.g. '8 min read') are sufficient interactive feedback."
        )
        interaction_spec["action_verb_lifecycle"] = sanitized_verbs
        constraints["action_verb_lifecycle"] = sanitized_verbs
        interaction_spec["reading_ergonomics"] = {
            "measure_max": "68ch",
            "contrast_floor": ">7:1 text-to-background",
            "feedback_style": "inline non-blocking state labels only",
            "selection_container": "in_situ_popover",
        }
    elif _is_touch:
        interaction_spec["profile_notes"] = (
            "somatic-touchflow: implement 44px thumb-zone touch targets, spring physics gesture hints, "
            "bottom-sheet action trays. Desktop keyboard shortcuts are NOT required."
        )
        interaction_spec["touch_ergonomics"] = {
            "min_touch_target": "44px",
            "action_tray": "bottom-sheet",
            "gesture_hints": True,
        }
    else:
        interaction_spec["profile_notes"] = (
            "adaptive-workspace: composable layout guided by product context and task requirements. "
            "Implement responsive hierarchy, clear state transitions, and accessible semantic interactions."
        )

    app_shell_blueprints = {
        "adaptive-workspace": {
            "profile": "adaptive-workspace",
            "spatial_roles": ["header_navigation", "primary_workspace", "contextual_inspector"],
            "density_rules": "fluid responsive layout, semantic spacing scale, zero rigid pixel clamping",
            "composition_guidance": "Design shell adapted to product thesis; structure surfaces for cognitive clarity and task continuity; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "dense-console": {
            "profile": "dense-console",
            "spatial_roles": ["global_nav", "operational_viewport", "context_inspector", "status_telemetry"],
            "density_rules": "4px micro-grid, 11-13px tabular-nums telemetry, multi-pane instrument rack, zero promotional banner",
            "composition_guidance": "Pin viewport height (100vh); enable independent scrolling within operational matrix and contextual inspector; no page-level runaway scroll; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "operational-canvas": {
            "profile": "operational-canvas",
            "spatial_roles": ["workspace_header", "entity_rail", "operational_canvas", "context_panel"],
            "density_rules": "8px grid rhythm, progressive visual elevation, master-detail hierarchy",
            "composition_guidance": "Support fluid zoom/pan or split-view master-detail; contextual inspectors should overlay or dock non-destructively; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "editorial-reading": {
            "profile": "editorial-reading",
            "spatial_roles": ["reading_header", "marginalia_nav", "reading_measure"],
            "density_rules": "68ch line-length measure, paper-contrast foundation, quiet marginalia",
            "composition_guidance": "Prioritize typographic rhythm, asymmetrical marginalia for citations/telemetry, and distraction-free central column; enforce @media (prefers-reduced-motion: reduce) resilience."
        },
        "somatic-touchflow": {
            "profile": "somatic-touchflow",
            "spatial_roles": ["touch_header", "touch_surface", "thumb_zone_nav"],
            "density_rules": "44px thumb-zone touch targets, fluid spring curves, high-contrast expressive surfaces",
            "composition_guidance": "Anchor primary decisive actions to bottom thumb-reach reach zone; implement spring physics and gesture signifiers; enforce @media (prefers-reduced-motion: reduce) resilience."
        }
    }

    product_title_raw = next((line.lstrip("# ").strip() for line in product_content.splitlines() if line.startswith("#")), "Product")
    brand_title = re.sub(r"^Product(?:\s+Thesis)?\s*[:\-]\s*", "", product_title_raw, flags=re.IGNORECASE).strip() or "Product Console"

    app_shell_contracts = {
        "adaptive-workspace": {
            "profile": "adaptive-workspace",
            "header": "Responsive header adapted to product thesis with navigation and primary state indicator",
            "main_viewport": "Primary content/workspace slot structured according to OOUX entity topology",
            "context_drawer": "Contextual inspection panel, drawer, or modal invoked on demand",
            "status_bar": "Calm status/metadata bar providing contextual grounding and feedback"
        },
        "dense-console": {
            "profile": "dense-console",
            "header": "Top bar containing system title, active slice indicator, and topology navigation",
            "main_viewport": "Primary operational slot matching declared entity cardinality",
            "context_drawer": "Contextual parameter inspection drawer or modal",
            "status_bar": "Footer telemetry and shortcuts guide"
        },
        "operational-canvas": {
            "profile": "operational-canvas",
            "header": "Workspace header with breadcrumb navigation and primary actions",
            "main_viewport": "Fluid canvas or master-detail interactive work area",
            "context_drawer": "Contextual parameter inspector panel or drawer",
            "status_bar": "Canvas view controls and operational status indicator"
        },
        "editorial-reading": {
            "profile": "editorial-reading",
            "header": "Minimalist header with publication title, reading progress, and index toggle",
            "main_viewport": "Focused typography-driven reading column (68ch max width)",
            "context_drawer": "Asymmetrical marginalia for annotations, outline, or related links",
            "status_bar": "Calm reading footer with chapter navigation and font controls"
        },
        "somatic-touchflow": {
            "profile": "somatic-touchflow",
            "header": "Compact mobile header with contextual title and back action",
            "main_viewport": "Touch-friendly card feed with thumb-zone ergonomics and gesture hints",
            "context_drawer": "Bottom sheet or modal action tray for quick modifications",
            "status_bar": "Persistent bottom thumb navigation bar"
        }
    }

    # Coverage and platform context, normalized from the retained authored sources.
    # Absent fields stay absent: a missing selection never becomes full-product, an
    # unselected dependency is disclosed rather than added, and a native target built
    # in a browser medium keeps its validation gap.
    platform_context = read_formal_context(root, slice_id)
    selected_surfaces = list(platform_context["surface_map"]["selected_surfaces"])
    target_surfaces = list(platform_context["surface_map"]["target_surfaces"])
    if platform_context["authorizes_full_product"]:
        selected_surfaces = target_surfaces

    # Extract product thesis, core tension and reality anchors (authored only).
    prod_thesis_raw = ""
    prod_tension_raw = ""
    for line in product_content.splitlines():
        if "Core Tension:" in line or "Tension:" in line:
            prod_tension_raw = line.split(":", 1)[1].strip()
        elif line.startswith("# Product Thesis:"):
            prod_thesis_raw = line.split(":", 1)[1].strip()
    if prod_tension_raw in ("unspecified", "Not yet decided"):
        prod_tension_raw = ""  # an unauthored tension does not become a domain claim

    # Runtime Method Registry selection & lazy loading (v10.2.1)
    active_methods = select_active_methods(
        registry_path=SKILL / "methods/registry.yaml",
        stage=2,
        layout_profile=layout_profile,
        spec_text=spec_content,
        contract_text=contract_content,
        product_text=product_content,
        slice_id=slice_id,
    )

    requires_tabular = bool(
        re.search(r"\b(tabular-nums|tabular\s+numbers|telemetry|metrics|latency|throughput|counter|kpi|currency|timestamp)\b", spec_content + " " + contract_content + " " + product_content, re.IGNORECASE)
        or any(m["id"] == "data-context-metrics" for m in active_methods)
    )

    # Dual-Envelope Architecture (v10): Decouple rigid constraints from creative agency
    domain_thesis: Dict[str, Any] = {
        "title": brand_title,
        "product_thesis": prod_thesis_raw or brand_title,
    }
    if prod_tension_raw:
        domain_thesis["core_tension"] = prod_tension_raw

    constraint_envelope = {
        "domain_thesis": domain_thesis,
        "ooux_topology": ooux_topology,
        "interaction_spec": interaction_spec,
        "fault_tolerance_protocol": fault_tolerance,
        "data_stress_boundaries": {
            "overflow_protection": "text-overflow: ellipsis, overflow-wrap: anywhere, or word-break: break-all required on dynamic labels",
            "empty_state_guidance": (
                f"Actionable guidance: render meaningful empty state paired with '{verb_lifecycle[0]['trigger_btn']}' recovery action"
                if verb_lifecycle else
                "Explicit guidance message required; provide recovery action if state is user-correctable"
            ),
            "tabular_numbers_required": requires_tabular
        },
        "target_html_path": target_html,
        "token_stylesheet_ref": token_rel_href,
        "verifiable_assertions": assertions,
        "content_language": content_language,
        "interaction_affordance_integrity": (
            "Every promised interaction verb (e.g. actions, toggles, navigation) must render visible, "
            "directly clickable triggers and clear feedback in the declared content language. "
            "Never leave core interactions as hidden stubs."
        ),
        "a11y_floors": {
            "contrast": "WCAG 2.2 AA compliant (>4.5:1 text, >3:1 UI components)",
            "motion": "@media (prefers-reduced-motion: reduce) override required",
            "min_touch_target": "44px on touch-first somatic, 32px on compact workbench"
        }
    }

    # Attention routing calibrated to product context, not rigid console prior
    if layout_profile == "editorial-reading":
        l1_scan = "Document title, reading progress, and primary reading actions"
        l2_inspect = "In-line annotations, footnotes, or chapter table-of-contents"
        l3_diag = "Bibliography, revision history, or document metadata"
    elif layout_profile == "somatic-touchflow":
        l1_scan = "Current step or primary entity status and decisive thumb-zone CTA"
        l2_inspect = "Contextual configuration sheet or secondary parameters"
        l3_diag = "Confirmation receipt, order/booking history, or terms"
    elif layout_profile == "operational-canvas":
        l1_scan = "Workspace title, active project state, and primary creation action"
        l2_inspect = "Selected entity properties, inline comments, or activity stream"
        l3_diag = "Version history, dependency matrix, or integration settings"
    elif layout_profile == "dense-console":
        l1_scan = "Persistent core identity, key system health/progress metrics, and primary action trigger"
        l2_inspect = "In-place details, expandable drawer, or docked inspection panel"
        l3_diag = "Full event logs, raw payload inspector, and historical audit trail"
    else:
        # adaptive-workspace
        l1_scan = f"Primary {slice_id} workspace status and primary decisive action trigger"
        l2_inspect = "Contextual entity inspection, inline details, or adaptive drawer"
        l3_diag = "Complete entity audit, auxiliary parameters, or secondary flow"

    # Five Axes Calibration & DTCG token extraction.
    # Axes resolve strictly from materialized foundation (f1) plus the slice
    # specification (r1); the unmaterialized discussion is not a source of the
    # sealed executable IR.
    from compile_tokens import parse_five_axes
    discussion_path = root / "prototype/discussion.md"
    discussion_text = discussion_path.read_text(encoding="utf-8") if discussion_path.is_file() else ""
    five_axes = parse_five_axes(f1_text + "\n" + spec_content)

    dtcg_tokens: Dict[str, Any] = {}
    t1_json_path = root / "prototype/contracts/tokens/t1.json"
    if t1_json_path.is_file():
        try:
            dtcg_tokens = json.loads(t1_json_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    # Extract OOUX entity definitions
    ooux_entities: List[Dict[str, str]] = []
    m_ent = re.search(r"(?:Core entities|Entities|实体)\s*[:=]\s*([^\n]+)", discussion_text + "\n" + product_content, re.IGNORECASE)
    if m_ent:
        for raw_e in re.split(r"[,;、](?![^(]*\))", m_ent.group(1)):
            raw_e = raw_e.strip()
            if raw_e:
                e_match = re.match(r"^([a-zA-Z0-9_\u4e00-\u9fa5]+)(?:\s*\(([^)]*)\))?", raw_e)
                if e_match:
                    ooux_entities.append({
                        "name": e_match.group(1).strip(),
                        "attributes": e_match.group(2).strip() if e_match.group(2) else ""
                    })
    ooux_topology["entities"] = ooux_entities
    ooux_topology["terminology"] = extract_labeled_entries(
        contract_content, r"OOUX\s+Terminology|(?:^|\W)Terminology\b|术语")

    creative_envelope = {
        "layout_profile": layout_profile,
        "candidate_patterns": candidate_patterns,
        "selected_pattern": selected_pattern,
        "five_axes": five_axes,
        "reality_anchors": reality_anchors,
        "spatial_composition_agency": "Builder owns layout rhythm, panel proportions, and responsive flow. No pre-baked rigid HTML scaffolding mandated.",
        "attention_routing": {
            "primary_visual_anchor": f"Primary {slice_id} focal workspace & status indicator",
            "disclosure_levels": {
                "l1_ambient_scan": l1_scan,
                "l2_contextual_inspection": l2_inspect,
                "l3_deep_diagnostics": l3_diag
            },
            "noise_budget": {
                "max_simultaneous_emissive_alerts": 3,
                "rule": "Avoid saturated multi-alert flashing; maintain atmospheric calm under normal operational states"
            }
        },
        "cognitive_ledger": cognitive_ledger,
        "suggested_blueprints": app_shell_blueprints.get(layout_profile, app_shell_blueprints["adaptive-workspace"]),
        "reference_pattern_guidance": app_shell_contracts.get(layout_profile, app_shell_contracts["adaptive-workspace"])
    }

    # P0-1: Build Authority Gate
    # In formal build mode (lean-builder-envelope), actions marked with [Hypothesis] cannot be built as frozen fact
    # unless explicitly allowed via probe mode or non-formal flag.
    has_hypothesis_action = False
    for v in verb_lifecycle:
        # Check action label, modal header or impact for hypothesis markers
        for val in v.values():
            if isinstance(val, str) and "[hypothesis]" in val.lower():
                has_hypothesis_action = True
                break
        if has_hypothesis_action:
            break

    # Determine build authority
    build_authority = "formal"
    if has_hypothesis_action:
        build_authority = "probe_only"

    # -------------------------------------------------------------
    # 7-Field Executable Design IR (Stage 2B / 2C)
    # -------------------------------------------------------------
    ir_identity = {
        "slice_id": slice_id,
        "authority_lifecycle": "sealed_provisional",
        "build_authority": build_authority,
        "target_html": target_html,
        "source": "contracts/slices/" + slice_id + "/c1.md",
        "authority": "explicit"
    }

    # Each authored anchor becomes one structured record; an absent or empty
    # declaration yields [] with no fabricated grounding.
    anchor_objects = [
        {"source": anchor, "transfer": [], "non_transfer": [], "authority": "explicit",
         "source_ref": "product.md#reality-anchors"}
        for anchor in reality_anchors
    ]

    ir_semantic_contract = {
        "domain_thesis": domain_thesis.get("product_thesis", brand_title),
        "primary_entities": [e.get("name", "entity") for e in ooux_entities] if ooux_entities else [slice_id],
        "domain_states": [{"name": s, "type": "domain_state", "authority": "explicit", "source": "c1.md#states"} for s in explicit_domain_states],
        "experience_states": [{"name": s, "type": "experience_state", "authority": "derived", "source": "r1.md#assertions"} for s in derived_experience_states],
        "ui_transient_states": [{"name": s, "type": "ui_transient_state", "authority": "derived", "source": "c1.md#actions"} for s in derived_transient_states],
        "anchors": anchor_objects
    }

    ir_regions = []
    if ooux_topology.get("primary_region"):
        ir_regions.append({
            "id": ooux_topology["primary_region"].get("id", "primary_workspace"),
            "role": "primary",
            "relation": "primary-focus",
            "scroll_owner": "self",
            "continuity": "preserve-primary-context",
            "authority": "explicit",
            "source": "m1.md#topology"
        })
    if ooux_topology.get("context_region"):
        ir_regions.append({
            "id": ooux_topology["context_region"].get("id", "contextual_inspector"),
            "role": "contextual",
            "relation": "adjacent-to-primary",
            "scroll_owner": "self",
            "continuity": "preserve-during-mutation",
            "authority": "explicit",
            "source": "m1.md#topology"
        })
    # No synthetic topology: an undeclared region set stays empty and the
    # spatial decision is disclosed as open design space instead.

    ir_layout_directives = {
        "viewport_strategy": "100vh-locked" if layout_profile in ("dense-console", "operational-canvas") else "natural-flow",
        "regions": ir_regions,
        "navigation": nav_links,
        "authority": "explicit",
        "source": "m1.md"
    }

    ir_visual_directives = {
        "token_baseline": token_rel_href,
        "sensory_dials": five_axes,
        "density_calibration": {
            "base_spacing": "var(--space-2)",
            "typography": "var(--font-sans)",
            "tabular_numbers": requires_tabular,
            "authority": "derived",
            "source": "f1.md#five-axes"
        }
    }

    ir_action_contracts = []
    for idx, v in enumerate(verb_lifecycle):
        act_id = v.get("action_id", f"action-{idx}")
        act_verb = v.get("verb") or v.get("action_id") or v.get("trigger_btn") or act_id
        trig_label = v.get("trigger_btn") or act_verb
        # Trigger role follows authored semantics, never list position.
        if re.search(r"\bprimary\b", trig_label, re.IGNORECASE):
            trig_role = "primary-action"
        elif re.search(r"\bsecondary\b", trig_label, re.IGNORECASE):
            trig_role = "secondary-action"
        else:
            trig_role = "action"
        # Transient states exist only when c1 authored them for this action.
        action_transients = [
            kw for kw in ("submitting", "failed", "loading", "saving", "pending")
            if re.search(r"\b" + kw + r"\b", contract_content, re.IGNORECASE)
        ]
        feedback_message = v.get("toast", "")
        feedback: Dict[str, Any] = {"continuity": "preserve-context"}
        if feedback_message:
            feedback["visible"] = True
            feedback["message"] = feedback_message
        else:
            feedback["visible"] = False
        ir_action_contracts.append({
            "id": act_id,
            "verb": act_verb,
            "trigger": {
                "role": trig_role,
                "semantic_label": trig_label
            },
            "consequence": v.get("consequence") or v.get("impact") or "state-mutation",
            "ui_transient_states": action_transients,
            "feedback": feedback,
            "authority": "explicit",
            "source": "c1.md#actions"
        })

    ir_negative_bounds = []
    for i, bound in enumerate(assertions):
        ir_negative_bounds.append({
            "id": f"assertion-{i+1}",
            "scope": "quality-contract",
            "rule": bound,
            "severity": "blocking",
            "verification": "static" if "token" in bound.lower() else "runtime",
            "source": "r1.md#assertions",
            "authority": "explicit"
        })
    # Real projection ledger: each source section is listed with the IR target
    # it actually compiled into. Absent sources are reported as unmapped rather
    # than asserted "none".
    projection_sources = [
        ("f1#foundation", "visual_directives", bool(f1_text.strip())),
        # Report compiled only when regions were actually derived into the IR; an
        # authored topology that produced no region would be a false receipt.
        ("m1#topology", "layout_directives", bool(ir_regions)),
        ("c1#behavior", "action_contracts", bool(verb_lifecycle)),
        ("r1#specification", "verification_contract", bool(assertions)),
        ("t1#tokens", "visual_directives", bool(dtcg_tokens)),
    ]
    sources_mapped = [
        {"source": source, "target": target,
         "status": "compiled" if present else "unmapped"}
        for source, target, present in projection_sources
    ]
    unmapped_sections = [e["source"] for e in sources_mapped if e["status"] != "compiled"]

    ir_verification_contract = {
        "negative_bounds": ir_negative_bounds,
        "command": verification_cmd,
        "projection_digest": {
            "sources_mapped": sources_mapped,
            "unmapped_sections": unmapped_sections,
        }
    }

    ir_open_design_space = [
        "exact-region-proportions",
        "local-spacing-rhythm",
        "iconography-and-micro-graphics",
        "container-elevation-subtlety",
        "transient-animation-timings-within-tokens"
    ]
    if not ir_regions:
        ir_open_design_space.append("spatial-topology")

    # The derived inspection contract must actually reach capture.mjs, otherwise
    # the authored device fact has no consumer. A declared device forwards its
    # derived viewports and states; an undeclared one leaves capture.mjs's own
    # device discovery intact rather than inventing a restricted set.
    mandatory_viewports = _mandatory_viewports(dict(platform_context["platform"]))
    device_declared = bool(str(platform_context["platform"].get("device_context") or "").strip())
    if device_declared:
        capture_cmd = (
            f"node skills/spec-prototype/scripts/capture.mjs --slice {slice_id}"
            f" --viewports {','.join(str(v['width']) for v in mandatory_viewports)}"
            f" --states {','.join(authored_states)}"
        )

    # `--status` records its ruling inside the canonical IR. Carry that authored
    # status forward rather than flattening every build back to the default; the
    # fallback remains for a legacy pillar-only assembly with no canonical IR.
    _ir_status = "sealed_provisional"
    if "canonical_ir" in paths and paths["canonical_ir"].is_file():
        try:
            _ir_data = json.loads(paths["canonical_ir"].read_text(encoding="utf-8"))
            _ir_status = _ir_data.get("identity", {}).get("authority_status") or "sealed_provisional"
        except (OSError, ValueError):
            pass

    # Surface the same lint evidence the gate already enforced: an empty list
    # must mean "lint clean", never "lint never ran".
    contract_lint = (
        _canonical_contract_lint(root, slice_id)
        if paths.get("canonical_ir") and paths["canonical_ir"].is_file()
        else _contract_lint_gate(root, slice_id)
    ) if lint else []

    envelope = {
        # 7-Field Executable Design IR Canonical Interface
        "identity": ir_identity,
        "semantic_contract": ir_semantic_contract,
        "layout_directives": ir_layout_directives,
        "visual_directives": ir_visual_directives,
        "action_contracts": ir_action_contracts,
        "verification_contract": ir_verification_contract,
        "open_design_space": ir_open_design_space,

        "envelope_version": "2.0",
        "envelope_architecture": "3.0-dual",
        "authority_status": _ir_status,
        "builder_guidance": {
            "authority_ceiling": "Stage 2 prototypes remain 'sealed_provisional'; do not self-declare 'frozen approved'.",
            "observable_affordances": "Render explicit visible controls and text for all declared interactive verbs.",
            "responsive_folding": "Ensure fluid reflow down to 390px mobile viewport without horizontal overflow."
        },
        "build_authority": build_authority,
        "has_hypothesis_actions": has_hypothesis_action,
        "active_methods": active_methods,
        "five_axes": five_axes,
        "dtcg_tokens": dtcg_tokens,
        "repository_root": str(root.resolve()),
        "skill_root": str(SKILL.resolve()),
        "slice_id": slice_id,
        "mode": "lean-builder-envelope",
        "layout_profile": layout_profile,
        "candidate_patterns": candidate_patterns,
        "selected_pattern": selected_pattern,
        "constraint_envelope": constraint_envelope,
        "creative_envelope": creative_envelope,
        "reality_anchors": reality_anchors,
        "domain_thesis": constraint_envelope["domain_thesis"],
        "ooux_topology": ooux_topology,
        "attention_routing": creative_envelope["attention_routing"],
        "data_stress_boundaries": constraint_envelope["data_stress_boundaries"],
        "app_shell_blueprint": creative_envelope["suggested_blueprints"],
        "app_shell_contract": creative_envelope["reference_pattern_guidance"],
        "target_html_path": target_html,
        "content_language": content_language,
        "evidence_output_dir": evidence_scope,
        "token_stylesheet_ref": token_rel_href,
        "token_link_tag": token_link_tag,
        "topology_context": {
            "current_slice": slice_id,
            "surface_role": current_role,
            "shared_shell": {
                "brand_title": brand_title,
                "navigation_links": nav_links
            }
        },
        "verification_command": verification_cmd,
        "capture_command": capture_cmd,
        "cognitive_ledger": cognitive_ledger,
        "fault_tolerance_protocol": fault_tolerance,
        "available_tokens": extract_css_tokens(paths["tokens_css"].read_text(encoding="utf-8")),
        "interaction_spec": interaction_spec,
        "design_constraints": constraints,
        "verifiable_assertions": assertions,
        "specification": {
            "path": spec_rel,
            "sha256": hashlib.sha256(paths["specification"].read_bytes()).hexdigest(),
        },
        "spec_references": {
            "product_thesis": paths["product"].relative_to(root).as_posix(),
            "surface_topology": paths["surface_map"].relative_to(root).as_posix(),
            "foundation_craft": paths["foundation"].relative_to(root).as_posix(),
            "slice_contract": paths["slice_contract"].relative_to(root).as_posix(),
            "specification": paths["specification"].relative_to(root).as_posix(),
            "tokens_stylesheet": paths["tokens_css"].relative_to(root).as_posix(),
        },
        # Retained source references, including the tokens Markdown revision the
        # boundary re-checks for staleness.
        "tokens_md_ref": paths["tokens_md"].relative_to(root).as_posix(),
        "coverage": {
            "coverage": _envelope_coverage(platform_context["surface_map"]["coverage"]),
            "selection_source": platform_context["surface_map"]["selection_source"],
            "selected_surfaces": selected_surfaces,
            "target_surfaces": target_surfaces,
            "unselected_surfaces": [s for s in platform_context["surface_map"]["surfaces"]
                                    if s not in target_surfaces],
            "applicability": dict(platform_context["surface_map"]["applicability"]),
            "authorizes_full_product": platform_context["authorizes_full_product"],
            "recommendation_required": platform_context["recommendation_required"],
        },
        "platform": dict(platform_context["platform"]),
        "contract_lint": contract_lint,
        "inspection_contract": {
            "mandatory_viewports": _mandatory_viewports(dict(platform_context["platform"])),
            "mandatory_states": authored_states,
            "visual_inspection_mandate": "Critic must use Read tool to visually inspect captured screenshots at every mandatory viewport; textual HTML review alone is non-independent."
        },
        "spec_sources": {
            "product_digest": hashlib.sha256(paths["product"].read_bytes()).hexdigest(),
            "surface_map_digest": hashlib.sha256(paths["surface_map"].read_bytes()).hexdigest(),
            "foundation_digest": hashlib.sha256(paths["foundation"].read_bytes()).hexdigest(),
            "tokens_css_digest": hashlib.sha256(paths["tokens_css"].read_bytes()).hexdigest(),
            "tokens_md_digest": hashlib.sha256(paths["tokens_md"].read_bytes()).hexdigest(),
            "contract_digest": hashlib.sha256(paths["slice_contract"].read_bytes()).hexdigest(),
            "specification_digest": hashlib.sha256(paths["specification"].read_bytes()).hexdigest(),
        }
    }

    return envelope


def main():
    parser = argparse.ArgumentParser(description="Assemble self-contained builder envelope")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Repository root")
    parser.add_argument("--slice", type=str, required=True, help="Slice ID (e.g. console, cockpit)")
    parser.add_argument("--check-spec", action="store_true", help="Only verify Spec completeness")
    parser.add_argument("--output", type=Path, help="Write envelope JSON to file")
    parser.add_argument("--full-envelope", action="store_true",
                        help="Emit the full diagnostic envelope instead of the lean builder payload")

    parser.add_argument(
        "--exploratory",
        action="store_true",
        help="Permit synthesizing an exploratory direction probe directly from discussion.md before formal spec completion",
    )
    args = parser.parse_args()
    root = args.root.resolve()

    if args.check_spec:
        try:
            check_spec_completeness(root, args.slice)
            print(json.dumps({"status": "spec_complete", "slice_id": args.slice}))
            sys.exit(0)
        except Exception as e:
            print(json.dumps({"status": "spec_incomplete", "error": str(e)}), file=sys.stderr)
            sys.exit(1)

    try:
        env = assemble(root, args.slice, exploratory=args.exploratory)
        # The written artifact is the Builder's prompt: lean by default, with the
        # full diagnostic envelope available behind an explicit flag.
        emitted = env if args.full_envelope else build_builder_payload(env)
        out_json = json.dumps(emitted, indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out_json, encoding="utf-8")
        print(out_json)
    except Exception as e:
        print(f"Error assembling envelope: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
