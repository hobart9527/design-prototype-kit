"""capture.mjs reads one slice's scope through the single design-record seam.

Before this, `capture.mjs` carried its own JS parser that knew only two shapes:
a `prototype/briefs/<slice>.md` file, else a `# Slice:` heading in a single
`discussion.md`. That parser could disagree with `compile_spec_ir` — the
authoritative reader — so the same slice could be captured at one viewport
ladder and compiled at another. These checks pin the two layouts to one
resolution: the same slice declaration yields the same viewports and states
whichever layout carries it.

Fixtures are built inline: `.gitignore` ignores `prototype/` everywhere, so a
checked-in fixture tree could never survive a clean checkout.

Hermetic: `node` + the repo's `python3` only; no browser, no network.
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[1]
CAPTURE = REPO_ROOT / "skills/spec-prototype/scripts/capture.mjs"
NODE_TIMEOUT = 30


def _resolve(expression: str, root: Path, slice_id: str):
    """Evaluate a `cap.<fn>(root, slice)` call inside capture.mjs and return JSON."""
    source = (
        "import * as cap from " + json.dumps(str(CAPTURE)) + ";\n"
        "const input = JSON.parse(process.env.LOOM_TEST_INPUT);\n"
        "const out = (" + expression + ");\n"
        "process.stdout.write(JSON.stringify(out));\n"
    )
    proc = subprocess.run(
        ["node", "--input-type=module", "-e", source],
        capture_output=True, text=True, timeout=NODE_TIMEOUT,
        cwd=str(REPO_ROOT),
        env={**os.environ, "LOOM_TEST_INPUT": json.dumps({"root": str(root), "slice": slice_id})},
    )
    assert proc.returncode == 0, f"node seam failed: {proc.stderr}"
    return json.loads(proc.stdout)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


_CONTRACT_BLOCK = "```contract:viewports\n- 390\n- 1280\n```\n"

_STATES_BLOCK = "```contract:required_states\n- default\n- degraded\n```\n"


def _layered_root(tmp_path: Path, slice_id: str) -> Path:
    _write(tmp_path / "prototype/truth.md", "# Product truth\n")
    _write(tmp_path / "prototype/world.md", "# World\n")
    _write(tmp_path / "prototype/briefs" / f"{slice_id}.md",
           f"---\nslice_id: {slice_id}\n---\n\n# Brief\n\n{_CONTRACT_BLOCK}\n{_STATES_BLOCK}")
    return tmp_path


def _single_record_root(tmp_path: Path, slice_id: str) -> Path:
    _write(tmp_path / "prototype/discussion.md",
           f"# Discussion\n\n## Slice: {slice_id}\n\n{_CONTRACT_BLOCK}\n{_STATES_BLOCK}")
    return tmp_path


def _scb():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "spec_contract_blocks", REPO_ROOT / "skills/spec-prototype/scripts/spec_contract_blocks.py")
    scb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scb)
    return scb


def test_viewports_match_across_both_layouts(tmp_path: Path):
    """The same slice declaration resolves to the same ladder in either layout."""
    layered = _resolve("cap.resolveSliceViewports(input.root, input.slice)",
                       _layered_root(tmp_path / "layered", "reader"), "reader")
    single = _resolve("cap.resolveSliceViewports(input.root, input.slice)",
                      _single_record_root(tmp_path / "single", "reader"), "reader")
    assert layered == [390, 1280]
    assert single == layered


def test_states_match_across_both_layouts(tmp_path: Path):
    """Required states resolve identically in either layout."""
    layered = _resolve("cap.resolveSliceStates(input.root, input.slice)",
                       _layered_root(tmp_path / "layered", "reader"), "reader")
    single = _resolve("cap.resolveSliceStates(input.root, input.slice)",
                      _single_record_root(tmp_path / "single", "reader"), "reader")
    assert layered == ["default", "degraded"]
    assert single == layered


def test_resolution_matches_the_compiler_seam(tmp_path: Path):
    """capture.mjs and the Python seam agree on the same declaration.

    The seam is the shared oracle: `spec_contract_blocks.slice_scope` is what
    `--dump` prints and what the compiler's record loader reads. If these ever
    diverge, the capture ladder and the compiled viewport contract disagree —
    the exact defect this seam exists to prevent.
    """
    scb = _scb()

    for layout in (_layered_root, _single_record_root):
        root = layout(tmp_path / layout.__name__, "reader")
        js = _resolve("cap.resolveSliceViewports(input.root, input.slice)", root, "reader")
        py = scb.slice_scope(root, "reader")
        assert py["viewports"] == js, f"{layout.__name__}: seam {py['viewports']} != capture {js}"


def test_seam_matches_the_compiled_ir(tmp_path: Path):
    """The seam resolves exactly what compile_spec_ir puts in the IR.

    `slice_scope` exists so capture and the compiler share one precedence: the
    contract block, then the Stage 3/4 verification fragment, then the merged
    frontmatter, then prose. A record that resolves differently in the two
    readers is the capture/compile divergence this seam was created to close.
    """
    import importlib.util
    import sys

    scripts = REPO_ROOT / "skills/spec-prototype/scripts"
    sys.path.insert(0, str(scripts))
    try:
        spec = importlib.util.spec_from_file_location(
            "compile_spec_ir", scripts / "compile_spec_ir.py")
        ir_compiler = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ir_compiler)

        # A record whose only required_states declaration is the labelled prose
        # form — the shape the old frontmatter-only reader silently dropped.
        root = _single_record_root(tmp_path, "reader")
        (root / "prototype/discussion.md").write_text(
            "# Discussion\n\n## Slice: reader\n\n- Required States: state-error, state-retry\n",
            encoding="utf-8")
        scope = _scb().slice_scope(root, "reader")
        assert scope["required_states"] == ["state-error", "state-retry"]
        ir = ir_compiler.compile_canonical_ir(root, slice_id="reader", allow_incomplete=True)
        assert ir["scope"]["verification_scope"]["required_states"] == ["state-error", "state-retry"]
    finally:
        sys.path.remove(str(scripts))


def test_a_slice_block_does_not_leak_from_a_neighbour(tmp_path: Path):
    """A partitioned record without this slice's block declares nothing here."""
    _write(tmp_path / "prototype/discussion.md",
           "# Discussion\n\n## Slice: other\n\n```contract:viewports\n- 1440\n```\n")
    out = _resolve("cap.resolveSliceViewports(input.root, input.slice)", tmp_path, "reader")
    assert out is None


def test_fragment_outranks_frontmatter_in_the_seam(tmp_path: Path):
    """A Stage 3/4 verification fragment outranks frontmatter, as in the compiler."""
    root = _layered_root(tmp_path, "reader")
    _write(root / "prototype/contracts/compiled/reader/state_model.slice.json",
           json.dumps({"viewports": [1024], "required_states": ["state-fragment"]}))
    scope = _scb().slice_scope(root, "reader")
    # The contract block still outranks everything; rewrite it out to expose the
    # fragment tier, which must outrank the brief's frontmatter carrier.
    _write(root / "prototype/briefs/reader.md",
           "---\nslice_id: reader\nviewports: [768]\nrequired_states: [default]\n---\n\n# Brief\n")
    scope = _scb().slice_scope(root, "reader")
    assert scope["viewports"] == [1024]
    assert scope["required_states"] == ["state-fragment"]


def test_malformed_contract_fails_closed_not_defaulted(tmp_path: Path):
    """A malformed contract block must abort the capture, not fall back to defaults.

    `resolveSliceViewports` previously swallowed every helper error into a
    `null`, so a broken `contract:viewports` block silently captured the default
    ladder while the record declared something else. The seam must surface the
    parse failure so the run stops before evidence is recorded against the
    wrong scope.
    """
    root = tmp_path
    _write(root / "prototype/discussion.md",
           "# Discussion\n\n## Slice: reader\n\n```contract:viewports\n- bad\n```\n")
    with pytest.raises(AssertionError, match="design-record scope could not be resolved"):
        _resolve("cap.resolveSliceViewports(input.root, input.slice)", root, "reader")


def test_dump_cli_prints_the_slice_scope(tmp_path: Path):
    """The seam's CLI mode emits the same JSON the module returns."""
    root = _layered_root(tmp_path, "reader")
    proc = subprocess.run(
        ["python3", str(REPO_ROOT / "skills/spec-prototype/scripts/spec_contract_blocks.py"),
         "--dump", str(root), "reader"],
        capture_output=True, text=True, timeout=NODE_TIMEOUT, cwd=str(REPO_ROOT),
    )
    assert proc.returncode == 0, proc.stderr
    scope = json.loads(proc.stdout)
    assert scope["viewports"] == [390, 1280]
    assert scope["required_states"] == ["default", "degraded"]


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
