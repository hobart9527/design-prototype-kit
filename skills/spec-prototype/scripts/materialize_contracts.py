#!/usr/bin/env python3
"""Compile discussion and product records into generic, high-fidelity design contracts."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, List


def extract_section_by_patterns(text: str, patterns: list[str]) -> str:
    """Extract markdown field or section matching any of the regex patterns."""
    for pat in patterns:
        m_field = re.search(rf"^[-*+]?\s*(?:{pat})\s*[:=]\s*([^\n]+)", text, re.MULTILINE | re.IGNORECASE)
        if m_field and m_field.group(1).strip():
            return m_field.group(1).strip()
    for pat in patterns:
        m = re.search(rf"^##+[^\n]*?(?:{pat})[^\n]*\n(.*?)(?=\n##+|\Z)", text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        if m and m.group(1).strip():
            return m.group(1).strip()
    return ""


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _bullets(text: str) -> list[str]:
    return [re.sub(r"^[-*+]\s+", "", line).strip() for line in text.splitlines() if re.match(r"^[-*+]\s+", line)]


def extract_surfaces(disc_text: str, prod_text: str) -> list[str]:
    """Extract declared surfaces supporting both English and Chinese heading conventions."""
    surfaces_sec = extract_section_by_patterns(disc_text, ["Surface", "表面", "拓扑", "Topology"]) or \
                   extract_section_by_patterns(prod_text, ["Surface", "表面", "拓扑", "Topology"])
    surfaces = _bullets(surfaces_sec) if surfaces_sec else []
    if not surfaces:
        # Fallback: sweep entire disc_text for surface bullet declarations
        for line in disc_text.splitlines():
            if re.match(r"^[-*+]\s+.*?(?:主工作区|上下文|支撑|Primary|Contextual|Supporting|hero-anchor|surfaces/)", line):
                surfaces.append(re.sub(r"^[-*+]\s+", "", line).strip())
    return surfaces


def extract_action_verbs(disc_text: str, slice_id: str) -> list[dict[str, str]]:
    """Extract 4-phase action verb lifecycle table from discussion or derive grounded defaults."""
    verbs_sec = extract_section_by_patterns(disc_text, ["Action Verb", "动作动词", "Verb Lifecycle", "动作流转"])
    extracted: list[dict[str, str]] = []
    if verbs_sec:
        for line in verbs_sec.splitlines():
            if line.strip().startswith("|") and not line.strip().startswith("|---"):
                parts = [p.strip() for p in line.split("|") if p.strip()]
                if parts and len(parts) >= 4 and parts[0].lower() not in ("action id", "action_id"):
                    extracted.append({
                        "action_id": parts[0],
                        "trigger_btn": parts[1],
                        "modal_header": parts[2],
                        "commit_btn": parts[3],
                        "toast": parts[4] if len(parts) > 4 else f"{parts[1]} Completed",
                        "impact": parts[5] if len(parts) > 5 else "Executes action",
                    })
    if not extracted:
        # 2. Extract action mentions from text — candidate verbs must be marked as hypothesis unless explicitly authored
        action_verb_patterns = [
            (r"(?:node\s+)?drain(?:\s+operations|\s+node)?", "drain-node", "Drain Node", "Drain GPU Node", "Confirm Drain", "Node Drained Successfully", "[Hypothesis] Evicts active batch workload from node; requires empirical validation"),
            (r"preempt(?:\s+vram)?", "preempt-vram", "Preempt VRAM", "Preempt VRAM Allocation", "Execute Preempt", "VRAM Eviction Committed", "[Hypothesis] Releases VRAM pool back to shared cluster; requires empirical validation"),
            (r"isolate(?:\s+cluster|\s+region)?", "isolate-cluster", "Isolate Cluster", "Emergency Region Isolation", "Authorize Isolation", "Region Traffic Rerouted", "[Hypothesis] Isolates failing region to contain blast radius; requires empirical validation"),
            (r"bookmark(?:\s+story|\s+article)?", "bookmark-story", "Bookmark Story", "Save Bookmark", "Confirm Save", "Story Saved to Reading List", "[Hypothesis] Stores story to reading list; requires empirical validation"),
            (r"checkout|order", "checkout-order", "Proceed to Checkout", "Confirm Order Payment", "Authorize Payment", "Order Placed Successfully", "[Hypothesis] Initiates checkout and order confirmation; requires empirical validation"),
            (r"publish(?:\s+document)?", "publish-document", "Publish Document", "Confirm Publication", "Publish Now", "Document Published to Feed", "[Hypothesis] Publishes document across designated channels; requires empirical validation"),
            (r"accept(?:\s+ai|\s+diff)?", "accept-ai-diff", "Accept AI Revision", "Review AI Inline Revision", "Accept & Merge", "Paragraph Revised Successfully", "[Hypothesis] Merges AI revision into draft; requires empirical validation"),
            (r"(?:confirm\s+)?booking|reservation", "confirm-reservation-slot", "Confirm Time Slot", "Review Booking Details", "Confirm & Reserve", "Appointment Slot Confirmed", "[Hypothesis] Confirms appointment booking; requires empirical validation"),
        ]
        for pattern, act_id, trig, modal, commit, toast, imp in action_verb_patterns:
            if re.search(pattern, disc_text, re.IGNORECASE):
                extracted.append({
                    "action_id": act_id,
                    "trigger_btn": trig,
                    "modal_header": modal,
                    "commit_btn": commit,
                    "toast": toast,
                    "impact": imp,
                })
                if len(extracted) >= 2:
                    break

    if not extracted:
        # 3. Generic Grammar Extraction: parse bullet action declarations matching phrases
        action_declarations = re.findall(
            r"(?:[-*]\s*[`*]?([A-Za-z0-9一-龥\s_-]+)[`*]?\s*[:：]\s*([^\n]+))",
            disc_text
        )
        for name, desc in action_declarations:
            name_clean = name.strip()
            if any(k in name_clean.lower() for k in ("bg-", "accent-", "energy", "finish", "density", "weight", "seriousness", "palette", "domain", "http", "ruthless", "material")):
                continue
            if 2 < len(name_clean) < 32 and not name_clean.startswith("#"):
                slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", name_clean).strip("-").lower()
                if not slug:
                    slug = f"action-{len(extracted)+1}"
                act_label = name_clean.title() if name_clean.isascii() else name_clean
                extracted.append({
                    "action_id": slug,
                    "trigger_btn": act_label,
                    "modal_header": f"Confirm {act_label}",
                    "commit_btn": f"Execute {act_label}",
                    "toast": f"{act_label} Completed",
                    "impact": desc.strip()[:100],
                })
                if len(extracted) >= 3:
                    break

    # Tertiary Fallback: Candidate hypothesis derived from slice_id — never fabricated as frozen fact
    if not extracted:
        clean_slice = slice_id.replace("-", " ").title()
        action_id = f"execute-{slice_id}"
        extracted.append({
            "action_id": action_id,
            "trigger_btn": f"Commit {clean_slice}",
            "modal_header": f"Confirm {clean_slice} Action",
            "commit_btn": "Confirm",
            "toast": f"{clean_slice} Action Completed",
            "impact": f"[Hypothesis] Candidate operational flow for {slice_id}; unresolved pending empirical validation in Stage 2/4",
        })
    return extracted


def extract_cognitive_ledger(disc_text: str, slice_id: str) -> dict[str, str]:
    """Extract or synthesize the Cognitive Budgeting & Energy Return Ledger."""
    routine_m = re.search(r"(?:Routine Conventions|Zero-learning|零借贷区|低熵基座)[`*:]*\s*([^\n]+)", disc_text, re.IGNORECASE)
    decisive_m = re.search(r"(?:Decisive Innovation|Borrowed focus|高产出借贷区|能量溢价特区)[`*:]*\s*([^\n]+)", disc_text, re.IGNORECASE)
    repayment_m = re.search(r"(?:Repayment|Settlement|偿还机制|状态沉降)[`*:]*\s*([^\n]+)", disc_text, re.IGNORECASE)

    zero_base = routine_m.group(1).strip() if routine_m else "Standard top navigation, breadcrumbs, and filter facets strictly follow established conventions with zero learning curve and zero distracting motion."
    borrow_zone = decisive_m.group(1).strip() if decisive_m else f"Primary operational {slice_id} workspace is allocated focused attention: tactile feedback and clear state transitions."
    repayment = repayment_m.group(1).strip() if repayment_m else "Upon action completion or contextual panel dismissal, focus and transient indicators settle smoothly into calm baseline equilibrium."

    return {
        "zero_borrow_base": zero_base,
        "high_yield_borrow_zone": borrow_zone,
        "repayment_settlement": repayment,
    }


def extract_ruthless_omissions(disc_text: str, prod_text: str) -> list[str]:
    """Extract or synthesize domain-aware Ruthless Omissions."""
    combined = disc_text + "\n" + prod_text
    m = re.search(r"(?:Ruthless Omission|Deliberately Excluded|Omission|舍弃|排除|非目标)[^\n]*\n((?:[ \t]*[-*0-9.]+[^\n]+\n?)+)", combined, re.IGNORECASE)
    if m:
        items = [re.sub(r"^[ \t]*[-*0-9.]+\s*", "", line).strip() for line in m.group(1).splitlines() if line.strip()]
        if len(items) >= 1:
            return items[:5]

    if re.search(r"Baseline 3|Editorial|阅读|文章|知识库", combined, re.IGNORECASE):
        return [
            "Zero distracting kinetic telemetry, flashing badges, or noisy decorative sidebars.",
            "Zero multi-level modal dialogs that disrupt continuous reading and comprehension flow.",
            "Zero unconsidered low-contrast gray text washes that compromise typographic legibility."
        ]
    elif re.search(r"Baseline 4|Touch|Consumer|消费|移动|社交", combined, re.IGNORECASE):
        return [
            "Zero dense multi-column tables requiring desktop cursor precision.",
            "Zero sub-44px touch targets or microscopic navigation links in primary thumb zones.",
            "Zero intrusive unskippable onboarding carousels that block immediate interaction."
        ]
    elif re.search(r"Baseline 2|SaaS|Commerce|电商|订单|交易", combined, re.IGNORECASE):
        return [
            "Zero multi-window fragmentations or detached popup windows.",
            "Zero dead-end error notifications without actionable recovery paths.",
            "Zero gratuitous animation or ungrounded decorative graphics that slow transaction flow."
        ]
    return [
        "Zero generic marketing cards, promotional hero banners, or superficial carousel widgets.",
        "Zero nested modal inception or multi-step wizard deadlocks; interactions stay in-canvas or single contextual drawer.",
        "Zero ungrounded alien physics, gratuitous full-screen particles, or unconsidered neutral gray #808080 washes."
    ]


def extract_material_invariants(disc_text: str, prod_text: str) -> list[str]:
    """Extract or synthesize domain-aware Material Non-Transfer Boundaries."""
    combined = disc_text + "\n" + prod_text
    m = re.search(r"(?:Material Non-Transfer|Material Invariant|材质不可跨界|材质边界|物理映射)[^\n]*\n((?:[ \t]*[-*0-9.]+[^\n]+\n?)+)", combined, re.IGNORECASE)
    if m:
        items = [re.sub(r"^[ \t]*[-*0-9.]+\s*", "", line).strip() for line in m.group(1).splitlines() if line.strip()]
        if len(items) >= 1:
            return items[:5]

    if re.search(r"Baseline 3|Editorial|阅读|文章|知识库", combined, re.IGNORECASE):
        return [
            "Typographic Ink & Paper Tone: Contrast mimics calibrated ink on high-grade paper; never harsh blinding raw #ffffff with unpadded margins.",
            "Calm Micro-detents: Subtle chapter transitions and bookmark toggles; never bouncy arcade elastic animations.",
            "Structural Marginalia: Footnotes and annotations live alongside reading flow; never popover stacks."
        ]
    elif re.search(r"Baseline 4|Touch|Consumer|消费|移动|社交", combined, re.IGNORECASE):
        return [
            "Fluid Touch Springs: Gestures feature natural deceleration and thumb-zone compliance; never mechanical desktop snaps.",
            "Tactile Haptic Emulation: Visual compression (:active press) gives immediate feedback without sluggish delays.",
            "Direct Card Physics: Surfaces elevate with contextual drop-shadows; never fake heavy skeuomorphic textures."
        ]
    return [
        "Digital Glass & Surface Layering: Semi-transparency expresses spatial depth hierarchy only, never gratuitous frosted blur that compromises contrast.",
        "Machined Tactile Detents: Interactive controls possess mechanical micro-press (:active feedback) resistance; never frictionless float.",
        "Precision Telemetry Emissives: Status indicators simulate calibrated hardware LEDs with subtle ambient bloom; never raw flat neon washes."
    ]


def materialize(root: Path, slice_id: str, force: bool = False, phase: str = "all") -> dict[str, str]:
    disc_path = root / "prototype/discussion.md"
    prod_path = root / "prototype/product.md"
    if not disc_path.is_file():
        raise FileNotFoundError(f"Missing mandatory entry index: {disc_path}")
    disc_text = disc_path.read_text(encoding="utf-8")

    created: dict[str, str] = {}

    # Support Phase 1 synthesis of product.md if missing or requested
    if not prod_path.is_file() or (force and phase.lower() in ("1", "product")):
        p_title = extract_section_by_patterns(disc_text, ["Product Title", "Product", "产品名称", "产品"]) or slice_id.replace("-", " ").title()
        p_baseline = extract_section_by_patterns(disc_text, ["Baseline", "基准"]) or "Baseline 1: Dense Data & Engineering Workbench"
        p_anchors = extract_section_by_patterns(disc_text, ["Reality Anchors", "Anchors", "地锚", "对标"]) or "Linear, Datadog"
        p_tension = extract_section_by_patterns(disc_text, ["Core Tension", "Tension", "张力", "冲突"]) or "Instant Operational Throughput vs Zero-Mistake Safety"
        omissions = extract_ruthless_omissions(disc_text, "")
        omissions_md = "\n".join(f"- {o}" for o in omissions)
        prod_content = f"""# Product Thesis: {p_title}

- Dominant Baseline: {p_baseline}
- Reality Anchors: {p_anchors}
- Core Tension: {p_tension}
- Status: candidate

## 3 Ruthless Omissions (克制舍弃清单)
{omissions_md}
"""
        prod_path.parent.mkdir(parents=True, exist_ok=True)
        prod_path.write_text(prod_content, encoding="utf-8")
        created["product"] = str(prod_path)

    prod_text = prod_path.read_text(encoding="utf-8")
    product_title = next((line.lstrip("# ").strip() for line in prod_text.splitlines() if line.startswith("#")), "Product")
    tension = extract_section_by_patterns(prod_text, ["Core Tension", "Tension", "张力", "冲突"]) or \
              extract_section_by_patterns(disc_text, ["Core Tension", "Tension", "张力", "冲突"]) or \
              "Not yet decided"
    surfaces = extract_surfaces(disc_text, prod_text)
    action_verbs = extract_action_verbs(disc_text, slice_id)

    # Determine profile-aware assertions and interaction patterns
    is_reading = bool(re.search(r"Baseline 3|Editorial|Reading|Article|阅读|排版", prod_text + " " + disc_text, re.IGNORECASE))
    is_marketing = bool(re.search(r"Marketing|Product Landing|Landing|官网|宣传|介绍", prod_text + " " + disc_text, re.IGNORECASE))
    is_mobile = bool(re.search(r"Baseline 4|Consumer|Mobile|Touch|Booking|移动|预约|触控", prod_text + " " + disc_text, re.IGNORECASE))
    is_writer_canvas = bool(re.search(r"Writer|Writing|Editor|Canvas|写作|编辑|协同写作", prod_text + " " + disc_text, re.IGNORECASE))

    if is_writer_canvas:
        contract_assertions = """| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| Document canvas clarity: distraction-free focus, content-first typography | present | unverified |
| Inline state preservation: seamless revision and diff review flow | present | unverified |
| Tabular Numerics: font-variant-numeric: tabular-nums on document metrics | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Keyboard ergonomics: operable shortcuts (e.g. Esc, Space) | present | unverified |
| Action Verb Lifecycle closure: trigger -> review/diff -> commit -> toast | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |"""
    elif is_reading:
        contract_assertions = """| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| Focused typography column: max-width constrained (65-75ch) | present | unverified |
| Reading metric units present (e.g. min read, words) | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Quiet feedback: non-blocking inline state updates, no intrusive modals | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |"""
    elif is_marketing:
        contract_assertions = """| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| Hero visual anchor: clear value proposition and primary call-to-action | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Action verb progression: clear engagement path | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |"""
    elif is_mobile:
        contract_assertions = """| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| Touch Target Floor: minimum 44x44px interactive tap zones | present | unverified |
| Gesture Detents: pull-to-refresh or bottom sheet swipe dismissal | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Tactile Active State: active scale tap feedback | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |"""
    else:
        contract_assertions = """| Assertion | Expected | Observed |
|---|---|---|
| Declared product intent is represented | present | unverified |
| Zero Naked Metrics: every metric has reference baseline or micro sparkline | present | unverified |
| Tabular Numerics: font-variant-numeric: tabular-nums on all metrics | present | unverified |
| Concentric Radii Formula: outer radius >= inner radius + padding | present | unverified |
| High text-to-background contrast compliant with WCAG 2.2 AA | present | unverified |
| Dual-channel keyboard shortcuts (Space / Esc) operable | present | unverified |
| Action Verb Lifecycle closure: trigger -> drawer/modal -> commit -> toast | present | unverified |
| The Break Protocol: unbreakable string, empty state, 320px fold | present | unverified |"""

    targets = {
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "slice_contract": root / f"prototype/contracts/slices/{slice_id}/c1.md",
        "specification": root / f"prototype/specifications/{slice_id}/r1.md",
    }

    phase_map = {
        "1": ["product"],
        "product": ["product"],
        "2": ["surface_map"],
        "surface_map": ["surface_map"],
        "3": ["foundation"],
        "foundation": ["foundation"],
        "4": ["slice_contract", "specification"],
        "slice": ["slice_contract", "specification"],
        "all": ["product", "surface_map", "foundation", "slice_contract", "specification"],
    }
    active_keys = set(phase_map.get(phase.lower(), phase_map["all"]))

    for key, path in targets.items():
        if key not in active_keys:
            continue
        if path.is_file() and not force:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        if key == "surface_map":
            surface_lines = "\n".join(f"- {s}" for s in surfaces) if surfaces else "- No surface decision recorded"
            content = f"""# Product Surface Map: m1

- Product: {product_title}
- Source discussion: `prototype/discussion.md`, {_digest(disc_path)}
- Status: candidate

## Declared surfaces
{surface_lines}
"""
        elif key == "foundation":
            omissions = extract_ruthless_omissions(disc_text, prod_text)
            omissions_md = "\n".join(f"- {o}" for o in omissions)
            invariants = extract_material_invariants(disc_text, prod_text)
            invariants_md = "\n".join(f"- {inv}" for inv in invariants)
            content = f"""# Project Experience Foundation: f1

- Product: {product_title}
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Core tension: {tension}
- Status: candidate

## Product Context & Alignment
{prod_text.strip()}

## 3 Ruthless Omissions (克制舍弃清单)
{omissions_md}

## Material Non-Transfer Boundaries (材质不可跨界定律)
{invariants_md}
"""
        elif key == "slice_contract":
            c_ledger = extract_cognitive_ledger(disc_text, slice_id)
            verb_table = "\n".join(
                f"| `{v['action_id']}` | `{v['trigger_btn']}` | `{v['modal_header']}` | `{v['commit_btn']}` | `{v['toast']}` | {v['impact']} |"
                for v in action_verbs
            )
            content = f"""# Prototype Slice Contract: {slice_id}

- Slice ID: {slice_id}
- Foundation revision: f1
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Canonical Ontology: Nine Pillars Mapping (Object, Journey, Attention, Interaction, Resilience)
- Status: candidate

## Intent & Value Anchor
{tension}

## Cognitive Budgeting & Energy Return Ledger (认知借贷收支账本)

| Ledger Zone | Scope & Interaction Invariant | Allocation Rule | Cognitive Cost & Yield |
|---|---|---|---|
| **Low-Entropy Base (零借贷基座)** | {c_ledger['zero_borrow_base']} | 0 learning friction, zero distracting motion, standard UI conventions | Zero cognitive drain; preserves operator attention for decisive tasks |
| **High-Yield Borrow Zone (能量溢价特区)** | {c_ledger['high_yield_borrow_zone']} | High-tension visual craft: tactile detents, micro-sparklines, kinetic pulses | Borrowed visual energy delivers 10x situational awareness and commit certainty |
| **Settlement & Repayment (闭环偿还机制)** | {c_ledger['repayment_settlement']} | Transition locks settle to steady state within 180ms | Restores baseline low entropy immediately after decision execution |

## Action Verb Lifecycle Table (4-Phase Atomic Terminology)

| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
{verb_table}

## Fault Tolerance & Error Recovery Contract (容错与撤销边界)

| Operation Category | Hazard / Reversibility Level | Defensive Mechanism | Recovery Path |
|---|---|---|---|
| **Contextual Parameter / Filter** | Low / Fully Reversible | Optimistic live update, zero blocking modal | Instant reset via reset chip or `Esc` key |
| **Operational State Transition** | Medium / Conditionally Reversible | Immediate tactile commit with 5s undo toast | Click 'Undo' in toast within 5s to revert state |
| **Destructive Resource Mutation** | High / Irreversible | Two-phase commit modal with explicit confirmation | Explicit cancel button or `Esc`; audit log entry |

## Decisive Exchange 3-Frame Specification (核心决定性交换三帧推演)

- **Frame 1 (Intent Input)**: Operator activates target trigger via mouse click or `Space` key; contextual inspector slides in with operational parameters.
- **Frame 2 (Decisive Commit)**: Operator hits commit action; trigger undergoes tactile `:active scale(0.97)` mechanical response; inline state locks to prevent duplicate submissions.
- **Frame 3 (State Settlement & Focus Restoration)**: Target badge transitions state deterministically; feedback toast displays completion; focus deterministically restores to originating anchor.

## Context Preservation Rules (上下文绝对保持法则)

- **Draft Context**: Dismissing inspector or drawer without submitting preserves filter parameters and active tab.
- **Spatial & Filter Context**: Scroll offsets and active facet filters remain strictly pinned upon drawer close or return.
"""
        else:
            scope_suffix = "hero-anchor" if "hero-anchor" in disc_text else "anchor"
            if is_mobile:
                ergonomics_section = """## Touch-First Ergonomics (Gesture Detents & Haptic Recovery)

| Gesture Vector | Target Action / Interaction | Scope | Focus / State Settlement |
|---|---|---|---|
| `Tap` / `Press` | Direct manipulation of reservation card / action trigger | Active card or action slot | Tactile scale(0.97) micro-feedback |
| `Swipe Down` | Dismiss modal sheet / parameter drawer | Bottom sheet overlay | Restore viewport to originating card |
| `Edge Swipe` | Navigate back through historical booking steps | Global screen edge | Settle immediately into previous step |"""
            else:
                ergonomics_section = """## Dual-Channel Ergonomics (Keyboard Shortcuts & Focus Recovery)

| Shortcut Key | Target Action / Interaction | Scope | Focus Restoration Anchor |
|---|---|---|---|
| `Space` or `P` | Activate primary operational trigger / toggle inspector drawer | Active operational item or selection | Active selection anchor |
| `Esc` | Dismiss inspector drawer / modal | Global overlay | Restore focus to originating trigger |
| `J` / `K` | Navigate primary items or table rows | Active collection or matrix | Active selection index |"""

            content = f"""# Prototype Specification: {slice_id} / r1

- Candidate revision: r1
- Compilation status: candidate
- Product source: `prototype/product.md`, {_digest(prod_path)}
- Discussion source: `prototype/discussion.md`, {_digest(disc_path)}
- Prototype write scope: `prototype/experiments/{slice_id}/{scope_suffix}/`
- Evidence write scope: `prototype/evidence/probes/{slice_id}/`
- Visual verification: unverified
- Browser verification: unverified

{ergonomics_section}

## The Break Protocol Stress Checkpoints (四维破坏性极限压测)

| Reality Breaker | Concrete Test Vector / Input | Expected Graceful Behavior | Observed Result |
|---|---|---|---|
| **Unbreakable String** | `unbreakable-entity-hash-00000000-0000-0000-0000-000000000000` | CSS ellipsis + title tooltip, zero container blowout | `pending` |
| **Zero-Item Empty State** | Filter: 0 results / empty list | Actionable empty card with reset filter button | `pending` |
| **Extreme 320px Fold** | 320px viewport width test | Horizontal scroll or vertical reflow, primary action reachable | `pending` |
| **Rapid Interruption** | Double-click / rapid Space hits | Debounced submission, single idempotency state transition | `pending` |

## Verifiable Design Assertions

{contract_assertions}
"""
        path.write_text(content, encoding="utf-8")
        created[key] = str(path)
    return created


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize generic Stage 1 contracts")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--slice", default="console")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--phase", default="all", help="Diamond Phase to materialize: 1 (product), 2 (surface_map), 3 (foundation), 4 (slice), or all")
    args = parser.parse_args()
    try:
        print(json.dumps({"status": "ok", "slice_id": args.slice, "phase": args.phase, "materialized": materialize(args.root.resolve(), args.slice, args.force, args.phase)}, indent=2))
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
