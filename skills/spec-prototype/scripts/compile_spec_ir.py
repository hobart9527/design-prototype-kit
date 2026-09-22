#!/usr/bin/env python3
"""compile_spec_ir.py: Canonical Prototype Specification IR Compiler.

Parses prototype/discussion.md (and/or upstream OpenSpec declarations) into a strict,
Schema-validated Canonical IR (`prototype/contracts/compiled/<slice_id>/<candidate_id>.spec.json`),
and deterministically renders the single-file human RFC Specification view
(`prototype/specifications/<slice_id>/<candidate_id>.spec.md`).

This replaces the 6-file scatter (product.md, m1.md, f1.md, t1.md, c1.md, r1.md)
and eliminates bidirectional/circular SHA-256 hash rebinding.

Machine authority layers (two distinct schemas with disjoint field sets; do not conflate them):
- Canonical Spec IR (`prototype-spec/v1`): `r1.spec.json` - schema-validated,
  discussion-derived, the single source of machine-truth spec content. Produced
  by this script.
- Executable Design IR: embedded inside `envelope.json` - produced by
  `assemble_envelope.py`, consumed by the Builder. Derived from the Canonical
  Spec IR and the legacy 6-piece contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import jsonschema
except ImportError:
    jsonschema = None


SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas/prototype-spec.v1.json"


def sha256_text(text: str) -> str:
    """Compute sha256 digest of utf-8 text."""
    return f"sha256:{hashlib.sha256(text.encode('utf-8')).hexdigest()}"


def sha256_file(path: Path) -> str:
    """Compute sha256 digest of a file if it exists, else empty."""
    if not path.is_file():
        return ""
    return f"sha256:{hashlib.sha256(path.read_bytes()).hexdigest()}"


def extract_section(text: str, heading_pattern: str, next_heading_pattern: str = r"^##\s+") -> str:
    """Extract markdown text under heading_pattern until next_heading_pattern."""
    lines = text.splitlines()
    capturing = False
    captured = []
    h_re = re.compile(heading_pattern, re.IGNORECASE)
    next_re = re.compile(next_heading_pattern)

    for line in lines:
        if not capturing:
            if h_re.search(line):
                capturing = True
            continue
        # Check end of section
        if next_re.match(line):
            break
        captured.append(line)
    return "\n".join(captured).strip()


def parse_5_dial_register(text: str) -> Dict[str, str]:
    """Extract 5-dial style register attributes."""
    dials = {
        "density": "balanced",
        "energy": "focused",
        "materiality": "subtle",
        "rhythm": "fluid",
        "character": "restrained",
    }
    # Look for `- \`?(\w+)\`?: \`?([^\`\n]+)\`?`
    for line in text.splitlines():
        m = re.search(r"[-*]\s*`?([A-Za-z]+)`?:\s*`?([^`\n]+)`?", line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().lower()
            if key in dials:
                dials[key] = val
            # Legacy dial aliases mirror compile_tokens.LEGACY_DIAL_MAP exactly;
            # the same key never maps to two different axes.
            elif key == "finish":
                dials["materiality"] = val
            elif key == "weight":
                dials["materiality"] = val
            elif key == "seriousness":
                dials["character"] = val
    return dials


def compile_canonical_ir(
    root: Path,
    slice_id: str,
    candidate_id: str = "r1",
    contract_rev: str = "c1",
    authority_status: str = "sealed_provisional",
    stage: str = "hero_probe",
    selected_surfaces: Optional[List[str]] = None,
    viewports: Optional[List[int]] = None,
) -> Dict[str, Any]:
    """Compile prototype/discussion.md into Canonical Specification IR."""
    disc_path = root / "prototype/discussion.md"
    disc_text = disc_path.read_text(encoding="utf-8") if disc_path.is_file() else ""
    disc_digest = sha256_text(disc_text) if disc_text else ""

    # Extract Product / Identity
    title_m = re.search(r"#\s*Design\s*Discussion:\s*([^\n]+)", disc_text, re.IGNORECASE)
    product_title = title_m.group(1).strip() if title_m else slice_id.replace("-", " ").title()
    product_id = re.sub(r"[^a-z0-9]+", "-", product_title.lower()).strip("-") or "product"

    # Extract Core Tension
    tension_text = extract_section(disc_text, r"###?\s*.*(?:Core Tension|张力|极端张力)")
    # Absent authored tension stays None: never fabricate a domain claim that
    # would propagate downstream as a real constraint.
    if not tension_text:
        tension_text = None

    # Extract Reality Anchors
    anchors_text = extract_section(disc_text, r"###?\s*.*(?:Reality.*Anchors|现实双地锚|地锚)")
    anchors = []
    for line in anchors_text.splitlines():
        line = line.strip()
        if line.startswith(("-", "*", "1.", "2.", "3.")):
            anchors.append(re.sub(r"^[-*0-9.]+\s*", "", line).strip())
    if not anchors:
        anchors = ["Industrial detents and operational density"]

    # Extract 5-Dial Register
    style_text = extract_section(disc_text, r"###?\s*.*(?:5-Dial|风格寄存器|Style Register)")
    five_axes = parse_5_dial_register(style_text or disc_text)

    # Extract OOUX / Surfaces
    surfaces_text = extract_section(disc_text, r"###?\s*.*(?:OOUX|实体拓扑|Surfaces|表面分配)")
    declared_surfaces = []
    primary_surface = None
    for line in surfaces_text.splitlines():
        line = line.strip()
        m_surf = re.search(r"`([a-zA-Z0-9_\-\/]+)`", line)
        if m_surf:
            s_name = Path(m_surf.group(1)).name
            if s_name not in declared_surfaces:
                declared_surfaces.append(s_name)
            if "primary" in line.lower() or "主" in line:
                primary_surface = s_name

    if not declared_surfaces:
        declared_surfaces = [slice_id, "inspector", "telemetry"]
    if not primary_surface:
        primary_surface = declared_surfaces[0]

    # Build Scope vs Topology Scope separation
    if selected_surfaces:
        active_build_surfaces = selected_surfaces
    elif stage in ("hero_probe", "surface_slice"):
        active_build_surfaces = [primary_surface]
    else:
        active_build_surfaces = declared_surfaces

    context_surfaces = [s for s in declared_surfaces if s not in active_build_surfaces]

    # State Model
    domain_states = [
        {"id": "draft", "label": "Draft Unsealed", "description": "Mutable operational working state"},
        {"id": "sealed", "label": "Sealed Baseline", "description": "Immutable verified authoritative state"},
    ]
    interaction_states = ["idle", "hovering", "inspecting", "confirming", "committing", "settled"]
    data_scenarios = [
        {"id": "zero-feedback", "description": "Empty state with zero prior data or alerts"},
        {"id": "peak-load", "description": "High density saturated cluster state"},
    ]
    stress_fixtures = [
        {"id": "long-string", "vector": "1000-char unbroken token string", "expected_behavior": "Truncate with ellipsis and tooltip, no container blow-out"},
        {"id": "rapid-commit", "vector": "10 repeated clicks in 200ms", "expected_behavior": "Single idempotent commit execution with locked button"},
        {"id": "viewport-320", "vector": "320px narrow mobile viewport", "expected_behavior": "Horizontal overflow suppressed, critical actions stacked or drawer-accessible"},
    ]

    # Invariants (Design Rules). Compiler-inferred template rules, not authored
    # requirements: authority=inferred and no upstream_ref (the former REQ-*
    # identifiers were fictional and must not masquerade as traced authority).
    invariants = [
        {
            "id": f"{slice_id.upper()}-A1",
            "authority": "inferred",
            "statement": "Operator must distinguish fault state vs normal telemetry within 2 seconds of screen load.",
            "severity": "blocking",
            "applies_to": ["draft", "sealed"],
            "verification_method": "screenshot_review",
        },
        {
            "id": f"{slice_id.upper()}-A2",
            "authority": "inferred",
            "statement": "Action verification: high-hazard commits require Proximity Level >= 2 dedicated confirmation.",
            "severity": "blocking",
            "applies_to": ["confirming", "committing"],
            "verification_method": "dom_query",
        },
        {
            "id": f"{slice_id.upper()}-A3",
            "authority": "inferred",
            "statement": "Signature accent seal color (--accent-seal) is strictly forbidden on draft, pending, or secondary controls.",
            "severity": "blocking",
            "applies_to": ["draft", "idle"],
            "verification_method": "computed_style",
        },
    ]

    # Actions: compiler-inferred defaults carrying no authority field, so downstream
    # consumers read them as inferred rather than authored facts.
    actions = [
        {
            "id": "inspect-entity",
            "verb": "检视实体",
            "trigger": "Row click / Space key",
            "proximity_level": 1,
            "commit_action": "Open contextual inspector drawer",
            "feedback": "Highlight border and display details",
            "consequence": "Read-only inspection without state mutation",
        },
        {
            "id": "commit-drain",
            "verb": "确定隔离排空",
            "trigger": "Drain Button / Enter key in modal",
            "proximity_level": 2,
            "commit_action": "Execute irreversible node drain",
            "feedback": "Display seal badge and transition node to drained state",
            "consequence": "State permanently sealed and marked offline",
        },
    ]

    ir = {
        "schema_version": "prototype-spec/v1",
        "identity": {
            "product_id": product_id,
            "slice_id": slice_id,
            "contract_revision": contract_rev,
            "candidate_revision": candidate_id,
            "authority_status": authority_status,
            "title": product_title,
        },
        "sources": {
            "discussion_ref": "prototype/discussion.md",
            "discussion_sha256": disc_digest,
            # Requirement ids are compiler-derived placeholders, not traced upstream
            # authority; mark them inferred and point provenance at discussion.md.
            "requirements": [{
                "id": f"REQ-{slice_id.upper()}",
                "scenarios": ["SCN-01", "SCN-02"],
                "authority": "inferred",
                "source": "discussion.md",
            }],
            "reality_anchors": anchors,
            "core_tension": tension_text,
        },
        "scope": {
            "topology_scope": {
                "coverage": "key-journey" if len(declared_surfaces) > 1 else "slice-isolated",
                "declared_surfaces": declared_surfaces,
                "primary_surface": primary_surface,
                "navigation_topology": "workspace-inspector",
            },
            "build_scope": {
                "stage": stage,
                "selected_surfaces": active_build_surfaces,
                "context_surfaces": context_surfaces,
            },
            "verification_scope": {
                # Single viewport authority: callers (e.g. assemble_envelope's
                # _mandatory_viewports) may inject the authored device set; only
                # an absent injection falls back to this default.
                "viewports": list(viewports) if viewports else [320, 390, 1280],
                "required_states": ["draft", "sealed", "zero-feedback", "long-string"],
            },
        },
        "foundation": {
            "five_axes": five_axes,
            "palette_discipline": {
                "accent_seal": "var(--accent-seal, #D93829)",
                "accent_policy": "Forbidden in draft/pending states; reserved exclusively for irreversible authority seals.",
            },
        },
        "state_model": {
            "domain_states": domain_states,
            "interaction_states": interaction_states,
            "data_scenarios": data_scenarios,
            "stress_fixtures": stress_fixtures,
        },
        "actions": actions,
        "invariants": invariants,
        "artifacts_binding": {
            "tokens_css": "prototype/shared/tokens.css",
            "tokens_json": "prototype/contracts/tokens/t1.json",
            "human_spec_md": f"prototype/specifications/{slice_id}/{candidate_id}.spec.md",
            "prototype_html": f"prototype/experiments/{slice_id}/{candidate_id}/index.html",
        },
    }

    # Validate against schema if jsonschema is available
    if jsonschema and SCHEMA_PATH.is_file():
        schema_obj = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        jsonschema.validate(instance=ir, schema=schema_obj)

    return ir


def render_single_spec_md(ir: Dict[str, Any]) -> str:
    """Render Canonical IR into a unified, human-readable single-file RFC Specification."""
    ident = ir["identity"]
    src = ir["sources"]
    scope = ir["scope"]
    fnd = ir["foundation"]
    states = ir["state_model"]

    md = []
    md.append(f"# Prototype Specification: {ident['title']} ({ident['slice_id']}/{ident['candidate_revision']})")
    md.append("")
    md.append(f"> **Authority Status**: `{ident['authority_status'].upper()}` | **Revision**: `{ident['contract_revision']}` / `{ident['candidate_revision']}`")
    md.append(f"> **Source Reference**: `{src['discussion_ref']}` ({src.get('discussion_sha256', 'untracked')})")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Product & Architecture Context (Pillars: Value · Research)")
    md.append(f"- **Product ID**: `{ident['product_id']}`")
    if src.get("core_tension"):
        md.append(f"- **Core Tension**: {src['core_tension']}")
    else:
        md.append("- **Core Tension**: *(未从 discussion.md 提取到——请在 discussion 中明确描述核心张力)*")
    md.append("- **Reality Anchors**:")
    for a in src["reality_anchors"]:
        md.append(f"  - {a}")
    md.append("")
    md.append("### Topology & IA Scope (Pillars: Object · Topology)")
    md.append(f"- **Coverage Mode**: `{scope['topology_scope']['coverage']}`")
    md.append(f"- **Navigation Topology**: `{scope['topology_scope']['navigation_topology']}`")
    md.append(f"- **Primary Surface**: `{scope['topology_scope']['primary_surface']}`")
    md.append(f"- **Declared Surfaces**: {', '.join(f'`{s}`' for s in scope['topology_scope']['declared_surfaces'])}")
    md.append(f"- **Active Build Stage**: `{scope['build_scope']['stage']}`")
    md.append(f"- **Active Build Surfaces**: {', '.join(f'`{s}`' for s in scope['build_scope']['selected_surfaces'])}")
    if scope['build_scope']['context_surfaces']:
        md.append(f"- **Context Surfaces**: {', '.join(f'`{s}`' for s in scope['build_scope']['context_surfaces'])}")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Sensory Calibration & Token Discipline (Pillars: Expression · Attention · 5-Axes)")
    md.append("- **Five-Axis Sensory Register**:")
    for k, v in fnd["five_axes"].items():
        md.append(f"  - `{k}`: `{v}`")
    md.append(f"- **Signature Accent Policy**: {fnd['palette_discipline'].get('accent_policy', 'Strict')}")
    md.append(f"- **Tokens Stylesheet**: `{ir['artifacts_binding']['tokens_css']}`")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. State Models & Action Lifecycle (Pillars: Journey · Interaction)")
    md.append("### Domain States")
    for ds in states["domain_states"]:
        md.append(f"- `{ds['id']}` ({ds['label']}): {ds.get('description', '')}")
    md.append("")
    md.append(f"### Interaction States: {', '.join(f'`{s}`' for s in states['interaction_states'])}")
    md.append("")
    md.append("### Actions Matrix")
    md.append("| Action ID | Verb | Trigger | Proximity | Commit Consequence | Feedback |")
    md.append("|---|---|---|---|---|---|")
    for act in ir["actions"]:
        md.append(f"| `{act['id']}` | {act['verb']} | `{act['trigger']}` | L{act.get('proximity_level', 1)} | {act['consequence']} | {act['feedback']} |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 4. Verifiable Design Invariants & Break Protocol (Pillar: Resilience)")
    md.append("### Verifiable Assertions")
    for inv in ir["invariants"]:
        md.append(f"- **[{inv['id']}]** (`{inv['severity']}` · `{inv['verification_method']}`): {inv['statement']}")
        md.append(f"  - Applies to states: {', '.join(f'`{s}`' for s in inv.get('applies_to', []))}")
    md.append("")
    md.append("### Break Protocol Stress Fixtures")
    for sf in states["stress_fixtures"]:
        md.append(f"- **`{sf['id']}`**: Vector: `{sf['vector']}` ➔ Expected: *{sf['expected_behavior']}*")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 5. Verification Scope & Evidence Binding")
    vscope = scope["verification_scope"]
    md.append(f"- **Target Viewports**: {', '.join(f'{vp}px' for vp in vscope['viewports'])}")
    md.append(f"- **Mandatory Test States**: {', '.join(f'`{st}`' for st in vscope['required_states'])}")
    md.append(f"- **Prototype Implementation**: `{ir['artifacts_binding']['prototype_html']}`")
    proto_html = ir["artifacts_binding"]["prototype_html"]
    proto_scope = str(Path(proto_html).parent) + "/"
    evidence_scope = f"prototype/evidence/{ident['slice_id']}/{ident['candidate_revision']}/"
    md.append(f"- **Prototype write scope**: `{proto_scope}`")
    md.append(f"- **Evidence write scope**: `{evidence_scope}`")
    md.append(f"- **Authority status**: `{ident['authority_status']}`")
    md.append("")

    return "\n".join(md)


def main():
    parser = argparse.ArgumentParser(description="Compile canonical prototype specification IR and single-file spec view.")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--slice", required=True, help="Slice identifier (e.g. sample-gate)")
    parser.add_argument("--candidate", default="r1", help="Candidate revision (e.g. r1)")
    parser.add_argument("--contract", default="c1", help="Contract revision (e.g. c1)")
    parser.add_argument("--status", default="sealed_provisional", choices=["draft", "sealed_provisional", "validated", "frozen_approved"])
    parser.add_argument("--stage", default="hero_probe", choices=["hero_probe", "walking_skeleton", "surface_slice", "full_product"])
    parser.add_argument("--surfaces", nargs="*", help="Override build scope surfaces")
    parser.add_argument("--output-ir", help="Output JSON IR path (default: prototype/contracts/compiled/<slice>/<cand>.spec.json)")
    parser.add_argument("--output-md", help="Output markdown path (default: prototype/specifications/<slice>/<cand>.spec.md)")

    args = parser.parse_args()
    root = Path(args.root).resolve()

    ir = compile_canonical_ir(
        root=root,
        slice_id=args.slice,
        candidate_id=args.candidate,
        contract_rev=args.contract,
        authority_status=args.status,
        stage=args.stage,
        selected_surfaces=args.surfaces,
    )

    out_ir = Path(args.output_ir) if args.output_ir else root / f"prototype/contracts/compiled/{args.slice}/{args.candidate}.spec.json"
    out_md = Path(args.output_md) if args.output_md else root / f"prototype/specifications/{args.slice}/{args.candidate}.spec.md"

    out_ir.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)

    out_ir.write_text(json.dumps(ir, indent=2, ensure_ascii=False), encoding="utf-8")
    rendered_md = render_single_spec_md(ir)
    out_md.write_text(rendered_md, encoding="utf-8")

    print(f"Compiled Canonical Spec IR: {out_ir}")
    print(f"Rendered Unified Spec MD: {out_md}")


if __name__ == "__main__":
    main()
