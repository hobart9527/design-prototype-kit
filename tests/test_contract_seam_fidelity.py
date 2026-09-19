import json
import tempfile
from pathlib import Path
import pytest
from tests.test_pipeline import _load, SCRIPTS

def test_materialize_and_assemble_seam_fidelity():
    """Verify that Stage 1 discussion faithfully projects into contracts and envelope without friction or loss."""
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")
    assemble_mod = _load("assemble_envelope", "assemble_envelope.py")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        proto_dir = root / "prototype"
        proto_dir.mkdir(parents=True, exist_ok=True)

        discussion_text = """# Design discussion
- *Core Tension & Inversions*: Deep Contemplation vs Digital Attention Economy (Distraction-Free Immersion vs Immediate Actionability)
- Content Language (Locked): zh-CN

## Working understanding (Nine Pillars Canonical Ontology)
| Pillar | Focus | Current statement | Evidence status | Source |
|---|---|---|---|---|
| **Value** | Product thesis & outcome | A contemplative long-form reading sanctuary that honors reader attention. | explicit | Brief |
| **Object** | Entities, content & authority | Core entities: Article (Title, Author, Measure, Sections, Word Count, Reading Time), Highlight (Text Range, Color, Timestamp), Annotation (Anchor, Markdown Note), Library Entry (Article Ref, Scroll Detent, Completion Percentage, Tags). | explicit | Brief |
| **Topology** | Derived surface architecture | Primary: Focused Article Canvas (1:1 Dedicated Reader with marginalia). Secondary: Personal Library & Reading Progress Drawer; Annotation Shelf Drawer. Supporting: Typography & Theme Controls. | derived | OOUX 1:1 |
| **Expression** | Five-Axis sensory calibration | Density: sparse. Energy: quiet. Materiality: paper-warm. Rhythm: calm. Character: humanist. | derived | Brief |

## Action Verb Lifecycle Table
| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
| `save-to-library` | `Save Article` | `Save to Library` | `Confirm Save` | `Article Saved to Library` | Adds to reading list |
| `add-annotation` | `Annotate` | `Add Margin Note` | `Save Note` | `Annotation Recorded` | Inline note anchored |
"""
        (proto_dir / "discussion.md").write_text(discussion_text, encoding="utf-8")

        # 1. Materialize contracts
        res = mat_mod.materialize(root, "editorial-reader", force=True)
        prod_path = Path(res["product"])
        spec_path = Path(res["specification"])
        f1_path = Path(res["foundation"])

        assert prod_path.is_file()
        prod_text = prod_path.read_text(encoding="utf-8")
        
        # Tension check: must NOT be fallback "Instant Operational Throughput vs Zero-Mistake Safety"
        assert "Instant Operational Throughput" not in prod_text
        assert "Deep Contemplation vs Digital Attention Economy" in prod_text

        # Assertion check: must be editorial reading assertions, NOT writer canvas or telemetry ops
        spec_text = spec_path.read_text(encoding="utf-8")
        assert "Focused typography column: max-width constrained" in spec_text
        assert "Reading metric units present" in spec_text
        assert "diff review flow" not in spec_text
        assert "tabular-nums on document metrics" not in spec_text

        # f1.md deduplication check: 3 Ruthless Omissions must not be duplicated
        f1_text = f1_path.read_text(encoding="utf-8")
        assert f1_text.count("## 3 Ruthless Omissions") <= 1

        # 2. Setup token files for envelope assembly
        shared_dir = root / "prototype/shared"
        shared_dir.mkdir(parents=True, exist_ok=True)
        (shared_dir / "tokens.css").write_text(":root { --bg-void: #FAF7F2; --text-main: #23201D; }\n", encoding="utf-8")

        tokens_dir = root / "prototype/contracts/tokens"
        tokens_dir.mkdir(parents=True, exist_ok=True)
        (tokens_dir / "t1.md").write_text("# Tokens\n", encoding="utf-8")
        sample_dtcg = {
            "$schema": "https://design-tokens.github.io/community-group/format/v1.0.0/schema.json",
            "primitives": {"color": {"primary": {"$value": "#9b4221"}}}
        }
        (tokens_dir / "t1.json").write_text(json.dumps(sample_dtcg), encoding="utf-8")

        # 3. Assemble envelope
        envelope = assemble_mod.assemble(root, "editorial-reader")

        # 4. Verify envelope carries Five Axes, DTCG tokens, and OOUX entities
        assert "five_axes" in envelope
        assert envelope["five_axes"].get("density") == "sparse"
        assert envelope["five_axes"].get("energy") == "quiet"

        assert "creative_envelope" in envelope
        assert envelope["creative_envelope"].get("five_axes", {}).get("density") == "sparse"

        assert "dtcg_tokens" in envelope
        assert envelope["dtcg_tokens"].get("primitives", {}).get("color", {}).get("primary", {}).get("$value") == "#9b4221"

        assert "ooux_topology" in envelope
        entities = envelope["ooux_topology"].get("entities", [])
        assert len(entities) >= 2
        entity_names = [e["name"] for e in entities]
        assert "Article" in entity_names

        # 5. Verify action_verb_lifecycle authority alignment
        spec_verbs = envelope.get("interaction_spec", {}).get("action_verb_lifecycle", [])
        constraint_verbs = envelope.get("design_constraints", {}).get("action_verb_lifecycle", [])
        assert spec_verbs == constraint_verbs


def test_lint_spec_contracts_catches_contamination_and_passes_clean():
    """Verify that lint_spec_contracts catches SRE contamination and validates complete contracts."""
    lint_mod = _load("lint_spec_contracts", SCRIPTS / "lint_spec_contracts.py")
    mat_mod = _load("materialize_contracts", "materialize_contracts.py")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        proto_dir = root / "prototype"
        proto_dir.mkdir(parents=True, exist_ok=True)

        # 1. Clean contract test
        disc_text = """# Design discussion
- *Core Tension & Inversions*: Deep Contemplation vs Digital Attention Economy
- Content Language (Locked): zh-CN
- Reality Anchors: iA Writer, The New Yorker

## Action Verb Lifecycle Table
| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact / Consequence |
|---|---|---|---|---|---|
| `save-to-library` | `Save Article` | `Save to Library` | `Confirm Save` | `Article Saved to Library` | Adds to reading list |
"""
        (proto_dir / "discussion.md").write_text(disc_text, encoding="utf-8")
        mat_mod.materialize(root, "editorial-reader", force=True)

        # Setup tokens files
        shared_dir = root / "prototype/shared"
        shared_dir.mkdir(parents=True, exist_ok=True)
        (shared_dir / "tokens.css").write_text(":root { --bg: #fff; }\n", encoding="utf-8")
        tokens_dir = root / "prototype/contracts/tokens"
        tokens_dir.mkdir(parents=True, exist_ok=True)
        (tokens_dir / "t1.md").write_text("# Tokens\n", encoding="utf-8")

        # Run lint on clean contract
        errors = lint_mod.lint_spec_contracts(root, "editorial-reader")
        assert len(errors) == 0, f"Expected 0 errors on clean contract, got: {[str(e) for e in errors]}"

        # 2. Contaminated tension test
        prod_path = root / "prototype/product.md"
        prod_content = prod_path.read_text(encoding="utf-8")
        contaminated = prod_content.replace("Deep Contemplation vs Digital Attention Economy", "Instant Operational Throughput vs Zero-Mistake Safety")
        prod_path.write_text(contaminated, encoding="utf-8")

        errors_contaminated = lint_mod.lint_spec_contracts(root, "editorial-reader")
        assert any(e.rule == "E002_TENSION_CONTAMINATED" for e in errors_contaminated)
