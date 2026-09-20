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


def _contract_lint_gate(root: Path, slice_id: str) -> List[Dict[str, str]]:
    try:
        return formal_contract_lint(root, slice_id)
    except Exception as error:  # preserve context; never let a broken lint open the gate
        return [{"code": "E010_STALE_CONTRACT", "path": str(root), "message": str(error)}]


def check_spec_completeness(root: Path, slice_id: str, *, lint: bool = True) -> Dict[str, Path]:
    """Verify that all required Stage 1 design contract artifacts exist and meet minimum content floors."""
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
            f"All 6 contract pillars must be materialized before Stage 2 prototype building."
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
    pattern = rf"^- {re.escape(label)}:[ \t]*(.+)$"
    match = re.search(pattern, content, re.MULTILINE)
    return match.group(1).strip() if match else default


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
    for sc in selected_scored:
        m = sc["method"]
        result.append({
            "id": m.get("id"),
            "name": m.get("name"),
            "pillars": m.get("pillars", []),
            "invariants": m.get("invariants", []),
            "reference_file": m.get("file", ""),
            "matched_triggers": sc["matched_triggers"],
        })
    return result


def assemble(root: Path, slice_id: str, *, lint: bool = True) -> Dict[str, Any]:
    """Assemble an envelope for either exploration or formal candidate work."""
    brief = _brief_path(root, slice_id)
    specification = root / f"prototype/specifications/{slice_id}/r1.md"
    if brief is not None and not specification.is_file():
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
    reality_anchors = anchors_match.group(1).strip() if anchors_match else ""

    # Determine layout profile & composable context
    # Reference patterns are composable archetypes derived naturally from physical domain properties, not rigid silos
    baseline_match = re.search(r"^[-*+]?\s*(?:Dominant\s+Baseline|Baseline|基线|Reference\s+Pattern)\s*[:=]\s*([^\n]+)", product_content, re.MULTILINE | re.IGNORECASE)
    declared_baseline = baseline_match.group(1).strip() if baseline_match else ""

    if re.search(r"Baseline 4|Consumer|Mobile|Touch|消费|移动|触控|somatic", declared_baseline, re.IGNORECASE):
        layout_profile = "somatic-touchflow"
    elif re.search(r"Baseline 3|Editorial|Reading|阅读|文章|出版|editorial", declared_baseline, re.IGNORECASE):
        layout_profile = "editorial-reading"
    elif re.search(r"Baseline 2|SaaS|Commerce|Project|画布|业务|交易|canvas", declared_baseline, re.IGNORECASE):
        layout_profile = "operational-canvas"
    elif re.search(r"Baseline 1|Console|Control|工作台|控制台|运维|telemetry", declared_baseline, re.IGNORECASE):
        layout_profile = "dense-console"
    else:
        all_spec_text = product_content + " " + spec_content + " " + reality_anchors
        if re.search(r"\bBaseline 4\b|mobile-first|touch-friendly", all_spec_text, re.IGNORECASE):
            layout_profile = "somatic-touchflow"
        elif re.search(r"\bBaseline 3\b|editorial-reading|long-form|ia\s+writer|new\s+yorker|readwise", all_spec_text, re.IGNORECASE):
            layout_profile = "editorial-reading"
        elif re.search(r"\bBaseline 2\b|operational-canvas|master-detail", all_spec_text, re.IGNORECASE):
            layout_profile = "operational-canvas"
        elif re.search(r"\bBaseline 1\b|dense-console|telemetry-grid|datadog|bloomberg", all_spec_text, re.IGNORECASE):
            layout_profile = "dense-console"
        else:
            layout_profile = "adaptive-workspace"

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
            if parts and len(parts) >= 4 and parts[0] not in ("Action ID",):
                verb_lifecycle.append({
                    "action_id": parts[0],
                    "trigger_btn": parts[1],
                    "modal_header": parts[2],
                    "commit_btn": parts[3],
                    "toast": parts[4] if len(parts) > 4 else "",
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
    capture_cmd = f"node skills/spec-prototype/scripts/capture.mjs --slice {slice_id}"

    # Extract OOUX Cardinality & Spatial Mapping from surface map or profile defaults
    # v10.1: Cardinality constrains candidate structures; task/device/context determine layout mode.
    # Default is adaptive rather than forced master-detail.
    cardinality_match = re.search(r"(?:Cardinality|OOUX|实体基数|基数映射)[^\n]*[:=]?\s*(1:1|1:N|N:M)", smap_content + " " + spec_content, re.IGNORECASE)
    if cardinality_match:
        ooux_cardinality = cardinality_match.group(1).upper()
        if ooux_cardinality == "1:1":
            ooux_layout_mode = "focused-cockpit"
        elif ooux_cardinality == "1:N":
            # Adapt layout mode: master-detail for dense workbenches, feed/stream for reading and mobile touch
            if layout_profile in ("editorial-reading", "somatic-touchflow"):
                ooux_layout_mode = "stream-feed"
            else:
                ooux_layout_mode = "split-master-detail"
        elif ooux_cardinality == "N:M":
            ooux_layout_mode = "node-link-canvas"
        else:
            ooux_layout_mode = "adaptive"
    else:
        # Context/Profile-driven heuristics without forcing master-detail on unknown profiles
        if layout_profile == "dense-console":
            ooux_cardinality = "1:N"
            ooux_layout_mode = "split-master-detail"
        elif layout_profile == "editorial-reading":
            ooux_cardinality = "1:1"
            ooux_layout_mode = "focused-column"
        elif layout_profile == "operational-canvas":
            ooux_cardinality = "N:M"
            ooux_layout_mode = "interactive-workspace"
        elif layout_profile == "somatic-touchflow":
            ooux_cardinality = "1:N"
            ooux_layout_mode = "card-stream"
        else:
            # v10.1: adaptive topology for unknown products
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

    # Extract authored states from spec or contract if present; otherwise default to minimal standard states
    authored_states: List[str] = []
    for line in spec_content.splitlines() + contract_content.splitlines():
        m_st = re.search(r"(?:Supported States|States|状态流转|支持状态)\s*[:=]\s*([^\n]+)", line, re.IGNORECASE)
        if m_st:
            raw_states = [s.strip("`'\" ") for s in re.split(r"[,/|;]", m_st.group(1)) if s.strip("`'\" ")]
            if raw_states:
                authored_states = raw_states
                break
    if not authored_states:
        found_states = []
        for a in assertions + break_checkpoints:
            a_lower = a.lower()
            if "empty" in a_lower and "empty" not in found_states:
                found_states.append("empty")
            if ("error" in a_lower or "alert" in a_lower) and "error" not in found_states:
                found_states.append("error")
            if ("select" in a_lower or "highlight" in a_lower) and "selecting" not in found_states:
                found_states.append("selecting")
            if ("note" in a_lower or "annotate" in a_lower) and "annotating" not in found_states:
                found_states.append("annotating")
            if ("undo" in a_lower or "recover" in a_lower) and "undo_pending" not in found_states:
                found_states.append("undo_pending")
        if found_states:
            authored_states = ["default"] + found_states
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
    if _is_dense:
        # Full rich interaction contract for workbench/console profiles
        if shortcuts:
            interaction_spec["dual_channel_shortcuts"] = shortcuts
        interaction_spec["action_verb_lifecycle"] = verb_lifecycle
        interaction_spec["decisive_exchange_frames"] = decisive_frames
        interaction_spec["context_preservation_rules"] = context_rules
        interaction_spec["profile_notes"] = (
            "dense-console: implement Action Verb Lifecycle (trigger→drawer/modal→commit→toast), "
            "declared keyboard shortcuts (if any), tabular-nums telemetry where comparative data is displayed, and SVG micro-sparklines."
        )
    elif _is_editorial:
        # Reading profile: quiet interactions, no intrusive modals
        # Sanitize verb lifecycle for reading profile: purge drawer/modal instructions so Builder receives unambiguous in-situ commands
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
        # Touch/mobile: thumb-zone ergonomics, spring physics
        interaction_spec["profile_notes"] = (
            "somatic-touchflow: implement 44px thumb-zone touch targets, spring physics gesture hints, "
            "bottom-sheet action trays. Desktop keyboard shortcuts are NOT required."
        )
        interaction_spec["touch_ergonomics"] = {
            "min_touch_target": "44px",
            "action_tray": "bottom-sheet",
            "gesture_hints": True,
        }
        interaction_spec["context_preservation_rules"] = context_rules
    else:
        # adaptive-workspace / custom-composite
        interaction_spec["profile_notes"] = (
            "adaptive-workspace: composable layout guided by product context and task requirements. "
            "Implement responsive hierarchy, clear state transitions, and accessible semantic interactions."
        )
        interaction_spec["dual_channel_shortcuts"] = shortcuts
        interaction_spec["action_verb_lifecycle"] = verb_lifecycle
        interaction_spec["decisive_exchange_frames"] = decisive_frames
        interaction_spec["context_preservation_rules"] = context_rules

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

    # Five Axes Calibration & DTCG token extraction
    from compile_tokens import parse_five_axes
    discussion_path = root / "prototype/discussion.md"
    discussion_text = discussion_path.read_text(encoding="utf-8") if discussion_path.is_file() else ""
    five_axes = parse_five_axes(discussion_text + "\n" + spec_content)

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

    creative_envelope = {
        "layout_profile": layout_profile,
        "five_axes": five_axes,
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

    envelope = {
        "envelope_version": "2.0",
        "envelope_architecture": "3.0-dual",
        "authority_status": "sealed_provisional",
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
        "constraint_envelope": constraint_envelope,
        "creative_envelope": creative_envelope,
        "domain_thesis": constraint_envelope["domain_thesis"],
        "ooux_topology": ooux_topology,
        "attention_routing": creative_envelope["attention_routing"],
        "data_stress_boundaries": constraint_envelope["data_stress_boundaries"],
        "app_shell_blueprint": creative_envelope["suggested_blueprints"],
        "app_shell_contract": creative_envelope["reference_pattern_guidance"],
        "target_html_path": target_html,
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
            "coverage": platform_context["surface_map"]["coverage"],
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
        "contract_lint": _contract_lint_gate(root, slice_id),
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
        env = assemble(root, args.slice)
        out_json = json.dumps(env, indent=2, ensure_ascii=False)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(out_json, encoding="utf-8")
        print(out_json)
    except Exception as e:
        print(f"Error assembling envelope: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
