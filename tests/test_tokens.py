"""Guardrails for the spec-prototype DTCG token compiler."""
from __future__ import annotations

import json
from pathlib import Path
import importlib.util

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[1]
COMPILE_SCRIPT = ROOT / "skills/spec-prototype/scripts/compile_tokens.py"


def _load_compiler():
    spec = importlib.util.spec_from_file_location("compile_tokens", COMPILE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _luma(hex_code: str) -> tuple[int, int, int]:
    h = hex_code.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _is_gray(hex_code: str) -> bool:
    r, g, b = _luma(hex_code)
    return max(r, g, b) - min(r, g, b) == 0


def test_canonical_dtcg_uses_spec_2025_10_shapes():
    ct = _load_compiler()
    data = ct.generate_dtcg_json(ct.compute_tokens({}))

    assert "$schema" not in data  # DTCG 2025.10 defines no official JSON Schema URL.
    assert data["semantics"]["surface"]["base"]["$value"] == "{primitives.color.surface}"
    assert data["primitives"]["motion"]["duration-fast"]["$value"]["unit"] == "ms"
    assert "authority" not in data["primitives"]["color"]["surface"]
    assert data["primitives"]["color"]["surface"]["$extensions"]["design-prototype-kit"]["authority"]


def test_token_authority_requires_token_specific_confirmation():
    ct = _load_compiler()
    seed = "## Seed Palette\n- --accent-primary: #d6f56b\n"
    assert ct._has_confirmed_token_authority(seed) is False
    assert ct._has_confirmed_token_authority(
        "| palette | confirmed | user selected palette |") is True
    assert ct._has_confirmed_token_authority(
        "| rollout policy | confirmed | user selected rollout |") is False
    # A keyword confined to the reason/quote columns is a neighbouring decision,
    # not a palette confirmation (H5 column-restricted matching).
    assert ct._has_confirmed_token_authority(
        "| nav layout | confirmed | nav reuses the token pipeline |") is False
    assert ct._has_confirmed_token_authority(
        "| D1 | nav layout | confirmed | reuses the token pipeline | quote |"
        " confirmed | surfaces/nav |") is False
    # On the shipped 7-column table the trailing affected-scope column also
    # names the decision.
    assert ct._has_confirmed_token_authority(
        "| D2 | rollout | confirmed | user selected rollout | quote |"
        " confirmed | accent token |") is True
    # A Confirmed Decisions heading alone, with no palette decision in its body,
    # grants no authority; one that names the palette does.
    assert ct._has_confirmed_token_authority("## Confirmed Decisions\n\n| nav | confirmed | nav |\n") is False
    assert ct._has_confirmed_token_authority(
        "## Confirmed Decisions\n\n配色由用户确认。\n") is True


def test_compile_tokens_empty_dials_yield_neutral_scaffold():
    ct = _load_compiler()
    tokens = ct.compute_tokens({})
    colors = tokens["colors"]

    # Neutral scaffold carries no chosen brand hue or industrial near-black.
    assert _is_gray(colors["accent_primary"]), colors["accent_primary"]
    assert _is_gray(colors["bg_void"]), colors["bg_void"]
    assert _is_gray(colors["bg_surface"]), colors["bg_surface"]
    assert colors["accent_primary"] != "#d6f56b"
    assert colors["bg_void"] != "#080b0b"
    assert tokens["craft_stack"] == {}

    css = ct.generate_css(tokens)
    assert "machined-industrial" not in css
    assert "#d6f56b" not in css


def test_omitted_dials_palette_stays_neutral_in_formal_mode():
    ct = _load_compiler()
    palette = ct.extract_dynamic_palette("")
    assert _is_gray(palette["accent_primary"]), palette["accent_primary"]
    assert palette["bg_void"] != "#080b0b"

    # Probe mode is the only path that may infer a themed accent from domain prose.
    probed = ct.extract_dynamic_palette("SRE cluster telemetry incident ops", mode="probe")
    assert not _is_gray(probed["accent_primary"])


def _compile_tokens_from_discussion(tmp_path: Path, dials: str = "- Energy: steady\n") -> Path:
    """Author dials and palette in discussion.md, compile tokens.css, return the tmp root.

    `prototype/discussion.md` is the sole token authority: the retired
    `prototype/contracts/foundation/f1.md` sibling was a second authority that
    could silently outrank the discussion record.
    """
    ct = _load_compiler()
    discussion = tmp_path / "prototype/discussion.md"
    discussion.parent.mkdir(parents=True)
    discussion.write_text(f"""# Discussion

## Confirmed Decisions
{dials}- --accent-primary: #d6f56b
- --bg-surface: #080b0b
""", encoding="utf-8")

    out_css = tmp_path / "prototype/shared/tokens.css"
    ct.compile_tokens(str(discussion), str(out_css))
    return tmp_path


def test_compile_stamps_provenance_and_downstream_passes(tmp_path: Path):
    """Positive specimen: compile → tokens.css carries the source digest → downstream passes."""
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    css_path = root / "prototype/shared/tokens.css"

    css = css_path.read_text(encoding="utf-8")
    assert "Source digest: sha256:" in css
    assert "Authored dials: energy: steady" in css

    # CSS syntax validity: provenance block must be enclosed inside /* ... */ before :root
    comment_end = css.find("*/")
    root_start = css.find(":root {")
    assert comment_end != -1 and root_start != -1
    assert comment_end < root_start
    pre_root = css[:root_start].strip()
    assert pre_root.endswith("*/"), "Header comment must close immediately before :root with no bare text"
    assert "Source:" in pre_root[:comment_end]

    # Freshness fuse admits freshly compiled tokens for downstream consumption.
    sync = ct.check_tokens_sync(str(css_path), str(root / "prototype/discussion.md"))
    assert sync["state"] == "in_sync", sync
    ct.assert_tokens_in_sync(str(css_path), str(root / "prototype/discussion.md"))  # must not raise


def test_hand_edited_palette_marks_out_of_sync_and_rejects_downstream(tmp_path: Path):
    """Boundary specimen: flip one palette color after compile → fuse fails, downstream rejected."""
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    css_path = root / "prototype/shared/tokens.css"

    # Reviewer hand-edits a single palette color in the compiled stylesheet.
    edited = css_path.read_text(encoding="utf-8").replace("--accent-primary: #d6f56b;", "--accent-primary: #38bdf8;")
    css_path.write_text(edited, encoding="utf-8")

    # The freshness digest check fails (not just the dial annotations): the
    # source was untouched, so the drift is between the edited CSS and its seal.
    sync = ct.check_tokens_sync(str(css_path), str(root / "prototype/discussion.md"))
    assert sync["state"] == "out_of_sync"
    assert "digest" in sync["drift"]
    assert "tokens.css" in sync["drift"] or "hand edits" in sync["drift"]

    # Downstream consumption is hard-rejected naming tokens.css as out_of_sync.
    with pytest.raises(ct.TokensOutOfSyncError, match="out_of_sync"):
        ct.assert_tokens_in_sync(str(css_path), str(root / "prototype/discussion.md"))


def test_source_edit_marks_out_of_sync_even_with_matching_dials(tmp_path: Path):
    """Editing the source after compile is also drift: the digest no longer matches."""
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    css_path = root / "prototype/shared/tokens.css"
    (root / "prototype/discussion.md").write_text(
        "# Discussion\n\n## Confirmed Decisions\n- Energy: kinetic\n",
        encoding="utf-8")

    sync = ct.check_tokens_sync(str(css_path), str(root / "prototype/discussion.md"))
    assert sync["state"] == "out_of_sync"


def test_discussion_non_token_edits_do_not_stale_tokens(tmp_path: Path):
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    discussion = root / "prototype/discussion.md"
    discussion.write_text(
        discussion.read_text(encoding="utf-8") + "\n## Stage 4 review\n- visual_evidence: unverified\n",
        encoding="utf-8",
    )

    sync = ct.check_tokens_sync(str(root / "prototype/shared/tokens.css"), str(discussion))
    assert sync["state"] == "in_sync", sync


def test_token_input_edit_marks_tokens_out_of_sync(tmp_path: Path):
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    discussion = root / "prototype/discussion.md"
    discussion.write_text(
        discussion.read_text(encoding="utf-8").replace("#d6f56b", "#aa33cc"),
        encoding="utf-8",
    )

    sync = ct.check_tokens_sync(str(root / "prototype/shared/tokens.css"), str(discussion))
    assert sync["state"] == "out_of_sync", sync


def test_palette_only_edit_cannot_pass_dial_annotation_freshness(tmp_path: Path):
    """A hand edit to the stylesheet's dial annotation line fails freshness on its own."""
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    css_path = root / "prototype/shared/tokens.css"

    # Touch only the Authored dials line — palette bytes and source untouched.
    forged = css_path.read_text(encoding="utf-8").replace(
        "Authored dials: energy: steady", "Authored dials: energy: kinetic")
    css_path.write_text(forged, encoding="utf-8")

    sync = ct.check_tokens_sync(str(css_path), str(root / "prototype/discussion.md"))
    assert sync["state"] == "out_of_sync"
    assert "dial annotation" in sync["drift"]


def test_unsealed_tokens_css_is_out_of_sync(tmp_path: Path):
    """A stylesheet that never went through the compiler carries no seal: rejected."""
    ct = _load_compiler()
    root = _compile_tokens_from_discussion(tmp_path)
    css_path = root / "prototype/shared/tokens.css"
    css_path.write_text(":root { --accent-primary: #fff; }\n", encoding="utf-8")

    sync = ct.check_tokens_sync(str(css_path), str(root / "prototype/discussion.md"))
    assert sync["state"] == "out_of_sync"
    assert "no provenance" in sync["drift"]


def test_formal_empty_dials_yield_steady_motion_not_kinetic_hud():
    ct = _load_compiler()
    tokens = ct.compute_tokens({})
    motion = tokens["motion"]

    # Undeclared energy must not silently compile to a kinetic HUD detent.
    assert motion["ease_hud"] != "cubic-bezier(0.16, 1, 0.3, 1)"
    assert motion["duration_fast"] == "150ms"
    assert motion["duration_normal"] == "250ms"
    assert motion["duration_slow"] == "400ms"

    css = ct.generate_css(tokens)
    assert ".btn-tactile:active" not in css
    assert not motion["tactile_active"]


def test_explicit_kinetic_energy_restores_hud_motion_and_detent():
    ct = _load_compiler()
    tokens = ct.compute_tokens({"energy": "kinetic"})
    motion = tokens["motion"]

    assert motion["ease_hud"] == "cubic-bezier(0.16, 1, 0.3, 1)"
    assert motion["duration_fast"] == "80ms"
    assert motion["tactile_active"]

    css = ct.generate_css(tokens)
    assert ".btn-tactile:active" in css


def test_compile_tokens_reads_authored_dials_and_palette(tmp_path: Path):
    ct = _load_compiler()
    discussion = tmp_path / "prototype/discussion.md"
    discussion.parent.mkdir(parents=True)
    discussion.write_text("""# Discussion

## Confirmed Decisions
- Energy: kinetic
- Density: dense

## Reality Benchmark Anchors
- Operational Reference: Datadog

## Seed Palette / Color Register
- --accent-primary: #d6f56b
- --bg-surface: #080b0b
""", encoding="utf-8")

    out_css = tmp_path / "tokens.css"
    ct.compile_tokens(str(discussion), str(out_css))
    css = out_css.read_text(encoding="utf-8")

    # Dials and palette authored in the discussion record reach the compiler.
    assert "#d6f56b" in css
    assert "--bg-surface: #080b0b" in css
    assert "Energy: kinetic" in css


def test_retired_foundation_sibling_cannot_outrank_the_discussion_record(tmp_path: Path):
    ct = _load_compiler()
    # A leftover legacy sibling carries a different accent.
    foundation = tmp_path / "prototype/contracts/foundation/f1.md"
    foundation.parent.mkdir(parents=True)
    foundation.write_text("""# Project Experience Foundation: f1

## 5-Dial Style Register
- Energy: steady

## Seed Palette / Color Register
- --accent-primary: #d6f56b
""", encoding="utf-8")
    discussion = tmp_path / "prototype/discussion.md"
    discussion.write_text("""# Discussion

## Confirmed Decisions
- --accent-primary: #ff00ff
""", encoding="utf-8")

    out_css = tmp_path / "tokens.css"
    ct.compile_tokens(str(discussion), str(out_css))
    css = out_css.read_text(encoding="utf-8")

    # discussion.md is the sole token authority; the retired sibling is not a
    # second authority and contributes nothing to the compiled output.
    assert "#ff00ff" in css
    assert "#d6f56b" not in css


def test_compile_tokens_accepts_explicit_legacy_token_source_path(tmp_path: Path):
    ct = _load_compiler()
    legacy = tmp_path / "legacy-tokens.md"
    legacy.write_text("""# Legacy Token Record

## 5-Dial Style Register
- Energy: kinetic

## Seed Palette / Color Register
- --accent-primary: #d6f56b
""", encoding="utf-8")

    out_css = tmp_path / "tokens.css"
    ct.compile_tokens(str(legacy), str(out_css))
    # An explicit path stays readable as-authored; only generation of the
    # retired sibling is gone.
    assert "#d6f56b" in out_css.read_text(encoding="utf-8")


def test_layered_tree_tokens_are_checked_against_the_sealed_source(tmp_path: Path):
    """A layered tree has world.md and no discussion.md: the lint's freshness fuse must
    follow the seal to world.md instead of demanding the single-record path."""
    ct = _load_compiler()
    world = tmp_path / "prototype/world.md"
    world.parent.mkdir(parents=True)
    world.write_text("""# World

## Confirmed Decisions
- Energy: steady
- --accent-primary: #d6f56b
- --bg-surface: #080b0b
""", encoding="utf-8")
    css = tmp_path / "prototype/shared/tokens.css"
    ct.compile_tokens(str(world), str(css))
    assert not (tmp_path / "prototype/discussion.md").exists()

    import sys
    scripts = str(ROOT / "skills/spec-prototype/scripts")
    sys.path.insert(0, scripts)
    try:
        import lint_spec_contracts as lint
        source = lint._token_source_path(tmp_path, css)
    finally:
        sys.path.remove(scripts)
    assert source == world
    assert ct.check_tokens_sync(str(css), str(source))["state"] == "in_sync"


def test_layered_tree_confirmation_in_truth_md_grants_token_authority(tmp_path: Path):
    """The Decisions table lives in truth.md, the token values in world.md: a confirmed
    palette row in truth.md must make the compiled authority explicit_human, and the
    sealed stylesheet must stay in sync with that reading."""
    ct = _load_compiler()
    proto = tmp_path / "prototype"
    proto.mkdir()
    (proto / "truth.md").write_text(
        "# Truth\n\n| decision | status | note |\n| --- | --- | --- |\n"
        "| palette | confirmed | user selected palette |\n", encoding="utf-8")
    world = proto / "world.md"
    world.write_text("# World\n\n- Energy: steady\n- --accent-primary: #d6f56b\n- --bg-surface: #080b0b\n",
                     encoding="utf-8")
    css = proto / "shared/tokens.css"
    out_json = proto / "contracts/tokens/t1.json"
    ct.compile_tokens(str(world), str(css), str(out_json))

    assert "explicit_human" in out_json.read_text(encoding="utf-8")
    assert ct.check_tokens_sync(str(css), str(world))["state"] == "in_sync"

    # Without the sibling confirmation the same world.md stays derived.
    (proto / "truth.md").write_text("# Truth\n", encoding="utf-8")
    ct.compile_tokens(str(world), str(css), str(out_json))
    assert "explicit_human" not in out_json.read_text(encoding="utf-8")



def test_compile_tokens_refuses_missing_source(tmp_path: Path):
    """A missing token source must fail, not silently compile a neutral scaffold
    that the chain then admits as a pass."""
    ct = _load_compiler()
    out_css = tmp_path / "shared/tokens.css"
    with pytest.raises(FileNotFoundError, match="Token source not found"):
        ct.compile_tokens(str(tmp_path / "prototype" / "missing-world.md"), str(out_css))
    assert not out_css.exists(), "no artifact may be written for a refused source"
