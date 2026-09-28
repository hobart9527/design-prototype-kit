"""Guardrails against the drift that broke real benchmark runs.

Each check here corresponds to a failure observed in a live run, not a style
preference: a template that no compiler accepts, a documented command the
boundary refuses, a shipped script no prose names, and an abort message
printed on a path that did not abort.
"""
import importlib.util
import json
import pathlib
import re
import sys

import jsonschema
import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/spec-prototype"
SCRIPTS = SKILL / "scripts"

sys.path.insert(0, str(SCRIPTS))
if "execution_boundary" not in sys.modules:
    spec = importlib.util.spec_from_file_location("execution_boundary", SCRIPTS / "execution_boundary.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["execution_boundary"] = module
    spec.loader.exec_module(module)
boundary = sys.modules["execution_boundary"]


def _prose() -> str:
    parts = [SKILL / "SKILL.md", SKILL / "CONTEXT.md"]
    parts += sorted((SKILL / "references").rglob("*.md"))
    return "\n".join(p.read_text(encoding="utf-8") for p in parts if p.is_file())


def test_templates_satisfy_their_own_schemas():
    """A shipped template that fails its schema teaches the wrong contract."""
    pairs = [("intent.json", "intent.v1.json")]
    for template_name, schema_name in pairs:
        template = SKILL / "templates" / template_name
        schema = json.loads((SKILL / "schemas" / schema_name).read_text(encoding="utf-8"))
        instance = json.loads(template.read_text(encoding="utf-8"))
        errors = list(jsonschema.Draft202012Validator(schema).iter_errors(instance))
        assert not errors, f"{template_name} violates {schema_name}: {[e.message for e in errors]}"


def test_documented_script_commands_are_admitted_by_the_boundary(tmp_path, monkeypatch):
    """A command the docs tell the author to run must not be refused by the hook."""
    prose = _prose()
    commands = sorted(set(re.findall(
        r"(?:python3(?:\.14)?|node)\s+skills/spec-prototype/scripts/[A-Za-z0-9_.-]+[^\n`]*", prose)))
    assert commands, "no documented script commands found; the extraction pattern went stale"
    # A hook runs with the session's own cwd, so `--root .` resolves there.
    monkeypatch.chdir(tmp_path)
    for command in commands:
        # Docs use `<placeholder>` for author-supplied values; substitute a
        # concrete value so the command shape is what gets exercised.
        concrete = re.sub(r"<[^>]+>", "sample-value", command).strip()
        boundary.shell_read(concrete, tmp_path)


# Shipped scripts the Skill prose does not name yet. Each is reachable only
# through another script or a test, so an author reading the Skill never learns
# it exists. The list is the retirement backlog: it may only shrink, and adding
# a new undocumented helper fails this test until it is either documented or
# removed. Documenting a name means the author can find it; silence does not.
UNDOCUMENTED_BACKLOG = {
    "check-assertions.py",
    "generate_review_portal.py",
    "lint_spec_contracts.py",
}


def test_skill_prose_never_names_a_script_that_does_not_ship():
    """A documented command pointing at a missing script is an author trap."""
    prose = _prose()
    named = set(re.findall(r"skills/spec-prototype/scripts/([A-Za-z0-9_.-]+\.(?:py|mjs|js))", prose))
    shipped = {p.name for p in SCRIPTS.iterdir() if p.is_file()}
    missing = sorted(named - shipped)
    assert not missing, f"prose names scripts that do not ship: {missing}"


def test_undocumented_script_backlog_only_shrinks():
    """Every shipped script is either documented or on the recorded backlog."""
    prose = _prose()
    shipped = {p.name for p in SCRIPTS.iterdir() if p.is_file()}
    undocumented = {name for name in shipped if name not in prose and name.removesuffix(".py") not in prose}
    newly_silent = sorted(undocumented - UNDOCUMENTED_BACKLOG)
    assert not newly_silent, (
        f"newly undocumented scripts: {newly_silent}. Document the helper in the "
        "Skill prose, or add it to UNDOCUMENTED_BACKLOG with its retirement plan."
    )
    retired = sorted(UNDOCUMENTED_BACKLOG - shipped)
    assert not retired, f"backlog lists scripts that no longer ship: {retired}; drop them from the backlog"


def test_abort_wording_is_limited_to_aborting_paths():
    """`编译中止` may only reach stderr from a path that actually aborts.

    The intent-tier NOTE compiles anyway. When it borrowed the abort header it
    told the author the run had stopped, which is how a Stage 1 pass was
    mistaken for a Stage 3/4 failure.
    """
    sys.path.insert(0, str(SCRIPTS))
    import compile_spec_ir

    note = compile_spec_ir.format_missing_sections(
        [{"key": "k", "label": "l", "section": "s", "form": "f", "example": "e"}],
        header=compile_spec_ir._MISSING_NOTE_HEADER)
    assert "编译中止" not in note

    abort = compile_spec_ir.format_missing_sections(
        [{"key": "k", "label": "l", "section": "s", "form": "f", "example": "e"}])
    assert "编译中止" in abort
