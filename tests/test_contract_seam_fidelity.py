import importlib.util
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills/spec-prototype/scripts"


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_lint_spec_contracts_catches_contamination_and_passes_clean():
    """Verify that lint_spec_contracts catches SRE contamination and validates complete contracts."""
    lint_mod = _load("lint_spec_contracts", "lint_spec_contracts.py")

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # 1. Clean legacy contract set: every required artifact authored by hand,
        #    so the linter's floors are exercised without a contract generator.
        _write(root / "prototype/product.md",
               "# Product\n- Core Tension: Deep Contemplation vs Digital Attention Economy\n"
               "- Reality Anchors: iA Writer, The New Yorker\n- Content Language: zh-CN\n")
        _write(root / "prototype/contracts/surface-maps/m1.md", "# Surface Map\n")
        _write(root / "prototype/contracts/foundation/f1.md", "# Foundation\n")
        _write(root / "prototype/shared/tokens.css", ":root { --bg: #fff; }\n")
        _write(root / "prototype/contracts/tokens/t1.md", "# Tokens\n")
        _write(root / "prototype/contracts/slices/editorial-reader/c1.md",
               "# Slice contract\n## Action Verb Lifecycle\n"
               "| Action ID | Trigger | Commit | Feedback |\n|---|---|---|---|\n"
               "| `save-to-library` | Save Article | Confirm Save | Article Saved |\n")
        _write(root / "prototype/specifications/editorial-reader/r1.md",
               "# Spec\n## Verifiable Design Assertions\n| Space | pass |\n"
               "## The Break Protocol\n- 320px fold, 1000-item overflow\n")

        errors = lint_mod.lint_spec_contracts(root, "editorial-reader")
        assert len(errors) == 0, f"Expected 0 errors on clean contract, got: {[str(e) for e in errors]}"

        # 2. Contaminated tension test
        prod_path = root / "prototype/product.md"
        contaminated = prod_path.read_text(encoding="utf-8").replace(
            "Deep Contemplation vs Digital Attention Economy",
            "Instant Operational Throughput vs Zero-Mistake Safety")
        prod_path.write_text(contaminated, encoding="utf-8")

        errors_contaminated = lint_mod.lint_spec_contracts(root, "editorial-reader")
        assert any(e.rule == "E002_TENSION_CONTAMINATED" for e in errors_contaminated)
