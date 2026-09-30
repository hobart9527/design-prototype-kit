import importlib.util
from pathlib import Path
import tempfile

import pytest

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
    """The legacy six-piece lint (incl. E002 tension contamination) was retired with
    the six-piece set itself; the linter now only validates the canonical IR.
    Kept as a skipped marker so the scenario id stays greppable."""
    pytest.skip("lint_spec_contracts() legacy six-piece path retired; canonical IR lint covered by test_canonical_spec_ir.py")
