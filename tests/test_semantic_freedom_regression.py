"""CPC-003 / CPC-004 end-to-end regression defense for semantic freedom.

One chain, five seams, no invented fact at any of them:

1. An unspecified discussion platform materializes into a contract that retains
   `unknown` instead of fabricating an operating-system target.
2. The token compiler stays neutral when no dial is authored.
3. The envelope offers advisory candidate patterns instead of locking one.
4. The Builder contract is bounded by the five integrity categories.
5. The Critic evaluates the accessibility floor without aesthetic gatekeeping.

These are mechanism checks against the authored seam, not live-session evidence.
Every fixture lives in `tmp_path`; the repository is read, never written.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"
sys.path.insert(0, str(SCRIPTS))

import assemble_envelope  # noqa: E402
import compile_tokens  # noqa: E402
import materialize_contracts  # noqa: E402
import prototype_context  # noqa: E402

BUILDER = ROOT / "agents/spec-prototype-builder.md"
CRITIC = ROOT / "agents/spec-prototype-critic.md"
SLICE = "console"

# A consumer booking discussion with a mobile viewport and touch input but no
# authored OS: the exact shape that used to promote itself into an iOS runtime.
UNSPECIFIED_PLATFORM_DISCUSSION = """# Discussion
- Product: Concierge Booking
- Baseline: Baseline 4: Consumer Mobile
- Viewport: 390px touch surface with booking confirmation flows
## Declared Surfaces
- Primary: booking-flow
- Contextual: booking-detail
"""


# --- seam 1: discussion -> materialized contract -----------------------------


def test_unspecified_platform_materializes_as_unknown(tmp_path):
    proto = tmp_path / "prototype"
    proto.mkdir(parents=True, exist_ok=True)
    (proto / "discussion.md").write_text(UNSPECIFIED_PLATFORM_DISCUSSION, encoding="utf-8")
    materialize_contracts.materialize(tmp_path, "booking-flow", phase="1")

    product = (proto / "product.md").read_text(encoding="utf-8")
    assert not re.search(r"target-context:\s*(?:ios|android)\b", product, re.IGNORECASE)
    section = prototype_context.parse_section(product, "product")
    assert section["target_context"] == "unknown"
    assert section["device_context"] == "mobile"  # retained as a device fact, not an OS
    assert section["input_context"] == "touch"


# --- seam 2: token compilation stays neutral ---------------------------------


def test_token_compilation_stays_neutral_without_authored_dials():
    tokens = compile_tokens.compute_tokens({})
    colors = tokens["colors"]

    def channel(hex_code: str) -> tuple[int, int, int]:
        raw = hex_code.lstrip("#")
        return int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16)

    def is_gray(hex_code: str) -> bool:
        r, g, b = channel(hex_code)
        return max(r, g, b) - min(r, g, b) == 0

    assert is_gray(colors["accent_primary"])
    assert is_gray(colors["bg_void"])
    assert colors["accent_primary"] != "#d6f56b"  # no remembered lime accent
    assert colors["bg_void"] != "#080b0b"  # no remembered industrial void
    css = compile_tokens.generate_css(tokens)
    assert "machined-industrial" not in css


# --- seam 3: envelope candidate patterns stay advisory ------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _formal_repo(tmp_path: Path, *, baseline: str) -> Path:
    """A complete Stage 1 contract set; no field is invented by the compiler."""
    write = _write
    write(tmp_path / "prototype/product.md",
          "# Product Thesis: Console\n\n"
          "- Reality Anchors: Linear, Stripe Dashboard\n"
          "- Core Tension: Operational Density vs Reading Calm\n"
          f"- Dominant Baseline: {baseline}\n- Status: candidate\n\n"
          "```prototype-context\nrecord: product\ntarget-context: unknown\n"
          "device-context: desktop\ninput-context: pointer-and-keyboard\n```\n")
    write(tmp_path / "prototype/contracts/surface-maps/m1.md",
          "# Product Surface Map\n\n- Surface Map revision: r7 (draft)\n\n"
          "```prototype-context\nrecord: surface-map\nrevision: r7\ncoverage: selected\n"
          "selection-source: prototype/discussion/scope-r7.md\n"
          "surfaces: S1-feed, S2-detail, S3-compose\n"
          "selected-surfaces: S1-feed, S2-detail, S3-compose\n```\n")
    write(tmp_path / "prototype/contracts/foundation/f1.md",
          "# Experience Foundation\n\n```prototype-context\nrecord: experience-foundation\n"
          "invariants: object-identity, permission-scope, selected-context, required-return\n```\n")
    write(tmp_path / "prototype/contracts/tokens/t1.md",
          "# Token Revision: t1\n\n- Token source: authored\n")
    write(tmp_path / "prototype/shared/tokens.css",
          ":root {\n  --surface-bg: #101418;\n  --text-primary: #e6edf3;\n}\n")
    write(tmp_path / f"prototype/contracts/slices/{SLICE}/c1.md",
          f"# Prototype Slice Contract: {SLICE}\n\n- Slice ID: {SLICE}\n"
          "- Content language: en-US\n\n## Action Verb Lifecycle Table\n\n"
          "| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button |"
          " Completion Feedback Toast | Impact |\n"
          "|---|---|---|---|---|---|\n"
          "| act-1 | Retry | Retry sync | Retry | Sync retried | Requeues work |\n")
    write(tmp_path / f"prototype/specifications/{SLICE}/r1.md",
          f"# Prototype Specification: {SLICE} / r1\n\n"
          f"- Prototype write scope: prototype/experiments/{SLICE}/anchor/\n"
          f"- Evidence write scope: prototype/evidence/probes/{SLICE}/\n"
          "- Content language: en-US\n\n## Verifiable Design Assertions\n\n"
          "| Assertion | Expected | Status |\n|---|---|---|\n"
          "| Header renders | visible | unverified |\n\n"
          "## The Break Protocol Stress Checkpoints\n\n"
          "| Checkpoint | Vector | N/A rationale |\n|---|---|---|\n"
          "| Refresh | reload | not applicable to anchor |\n\n"
          "```prototype-context\nrecord: prototype-specification\n"
          "prototype-medium: HTML\nverification-environment: headless-chromium-120\n```\n")
    return tmp_path


def test_envelope_offers_advisory_candidates_without_locking_a_profile(tmp_path):
    root = _formal_repo(tmp_path, baseline="Baseline 2: SaaS Commerce")
    env = assemble_envelope.assemble(root, SLICE)
    assert env["selected_pattern"] is None  # category alone is not a confirmation
    assert env["candidate_patterns"]  # advisory, ordered
    assert "operational-canvas" in env["candidate_patterns"]
    assert env["platform"]["target_context"] == "unknown"  # unknown survives the envelope


def test_an_authored_pattern_is_the_only_selection_route(tmp_path):
    root = _formal_repo(tmp_path, baseline="Baseline 2: SaaS Commerce")
    spec = root / f"prototype/specifications/{SLICE}/r1.md"
    spec.write_text(spec.read_text(encoding="utf-8") + "\n- Layout Profile: editorial-reading\n",
                    encoding="utf-8")
    env = assemble_envelope.assemble(root, SLICE)
    assert env["selected_pattern"] == "editorial-reading"
    assert "operational-canvas" in env["candidate_patterns"]  # alternatives stay visible


# --- seam 4: builder contract bounded by five integrity categories -----------


def test_builder_contract_is_bounded_by_the_five_integrity_categories():
    text = BUILDER.read_text(encoding="utf-8")
    for category in ("Semantic Integrity", "Task Integrity", "Accessibility Integrity",
                     "State & Recovery Integrity", "Platform Integrity"):
        assert category in text, f"builder contract dropped {category}"
    assert "Five Core Integrity Categories" in text


# --- seam 5: critic evaluates the floor, not aesthetic taste ------------------


def test_critic_keeps_aesthetic_craft_advisory_not_a_build_gate():
    # Markdown wraps prose, so compare against a whitespace-normalized copy.
    text = re.sub(r"\s+", " ", CRITIC.read_text(encoding="utf-8"))
    assert "SHALL NOT fail a build" in text
    assert "advisory" in text.lower()
    # Only floor breaches gate; stylistic geometry is critique, not refusal.
    assert re.search(r"only accessibility breaches", text, re.IGNORECASE)
