"""CRR-002 / CRR-SCN-003 contract: builder must mandate an in-memory state store.

The Spec Prototype Builder agent instructions must require interactive
prototypes to route form drafts, tab/filter state and drawer/sub-modal open
flags through one centralized in-memory state object, must forbid heavy
external state-management libraries, and must cite Method 5 (Decisive
3-Frame / Context Preservation) as the owning craft rule.
"""

from pathlib import Path

BUILDER = Path(__file__).resolve().parents[1] / "agents" / "spec-prototype-builder.md"
METHODS = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "spec-prototype"
    / "references"
    / "01-foundations"
    / "design-methods.md"
)


def builder_text() -> str:
    assert BUILDER.is_file(), f"builder instructions absent: {BUILDER}"
    return BUILDER.read_text(encoding="utf-8")


def test_builder_requires_centralized_in_memory_state_store():
    text = builder_text()
    assert "window.__prototypeState" in text, (
        "builder must name the centralized in-memory state object window.__prototypeState"
    )
    lowered = text.lower()
    assert "in-memory state" in lowered or "in-memory store" in lowered, (
        "builder must declare an in-memory state store requirement"
    )


def test_builder_routes_form_drafts_tabs_filters_and_drawer_flags_through_store():
    lowered = builder_text().lower()
    for fragment in ("form draft", "table filter", "drawer"):
        assert fragment in lowered, (
            f"builder must route {fragment!r} state through the store"
        )
    assert "tab" in lowered and "filter" in lowered, (
        "builder must keep active tab/filter state in the store"
    )


def test_builder_forbids_heavy_external_state_libraries():
    lowered = builder_text().lower()
    assert "external state management" in lowered or "state management librar" in lowered, (
        "builder must forbid heavy external state-management libraries"
    )
    for banned in ("redux", "zustand", "mobx", "vuex"):
        assert banned not in lowered, (
            f"builder must not sanction external library {banned!r}"
        )


def test_builder_forbids_unpreserved_modal_or_drawer_resets():
    lowered = builder_text().lower()
    assert "context preservation" in lowered, (
        "builder must name the Context Preservation invariant"
    )
    assert "method 5" in lowered, "builder must cite Method 5 as the owning rule"
    assert "3-frame" in lowered or "three-frame" in lowered, (
        "builder must cite the Decisive 3-Frame mapping"
    )


def test_method5_reference_still_owns_context_preservation():
    assert METHODS.is_file(), f"design methods reference absent: {METHODS}"
    text = METHODS.read_text(encoding="utf-8")
    assert "Context Preservation" in text
    assert "Decisive 3-Frame" in text
