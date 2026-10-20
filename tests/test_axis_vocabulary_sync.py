"""The five-axis vocabulary table stays honest about what the compiler maps.

`world.tokens.example.md` Block 3 lists the words `compile_tokens.py` maps per
axis; the compiler silently falls back to the neutral branch on anything else.
The compiler is the authority, the table is its human-readable copy — so this
test reads the keyword sets out of the compiler source and fails when the table
no longer names them. A word added to the compiler without the table (or vice
versa) is a silent-fallback bug this pin catches.
"""
import ast
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
COMPILER = REPO / "skills/spec-prototype/scripts/compile_tokens.py"
DOC = REPO / "skills/spec-prototype/templates/world.tokens.example.md"


def _compiler_words() -> dict[str, set[str]]:
    """Pull the keyword tuple guarding each axis fallback append, via AST.

    Every axis check ends in `_axis_fallbacks.append(f"{axis}=...")`; the tuple
    of string literals in the enclosing `If` test is the mapped vocabulary.
    """
    src = COMPILER.read_text(encoding="utf-8")
    tree = ast.parse(src)
    words: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        # Walk the body instead: the append lives in the If's body.
        for stmt in node.body:
            for sub in ast.walk(stmt):
                if (
                    isinstance(sub, ast.Call)
                    and isinstance(sub.func, ast.Attribute)
                    and sub.func.attr == "append"
                    and isinstance(sub.func.value, ast.Name)
                    and sub.func.value.id == "_axis_fallbacks"
                    and sub.args
                    and isinstance(sub.args[0], ast.JoinedStr)
                ):
                    fstr_src = ast.get_source_segment(src, sub.args[0]) or ""
                    m = re.match(r"f?[\"'](\w+)=", fstr_src)
                    if not m or m.group(1) not in (
                        "density", "energy", "materiality", "rhythm", "character",
                    ):
                        continue
                    axis = m.group(1)
                    for t in ast.walk(node.test):
                        if isinstance(t, ast.Tuple) and all(
                            isinstance(e, ast.Constant) and isinstance(e.value, str)
                            for e in t.elts
                        ):
                            words.setdefault(axis, {e.value for e in t.elts})
                            break
    missing = [a for a in ("density", "energy", "materiality", "rhythm", "character") if a not in words]
    assert not missing, f"no keyword tuple found for axes {missing} in compiler"
    return words


def _doc_row(axis: str) -> str:
    text = DOC.read_text(encoding="utf-8")
    m = re.search(rf"^\| `{axis}` \| (.+?) \|", text, re.M)
    assert m, f"no vocabulary table row for axis {axis!r} in world.tokens.example.md"
    return m.group(1)


def test_every_compiler_keyword_appears_in_the_vocabulary_table():
    for axis, words in _compiler_words().items():
        row = _doc_row(axis)
        missing = sorted(w for w in words if f"`{w}`" not in row)
        assert not missing, (
            f"compiler maps {axis} words the table never names: {missing} "
            "(a user authoring them sees no fallback warning documented)"
        )


def test_every_documented_keyword_is_real():
    """A table word the compiler does not map teaches a silent fallback."""
    for axis, words in _compiler_words().items():
        row = _doc_row(axis)
        documented = set(re.findall(r"`([a-z-]+)`", row))
        phantom = sorted(documented - words)
        assert not phantom, (
            f"table names {axis} words the compiler does not map: {phantom} "
            "(authoring them falls back to neutral despite the table)"
        )
