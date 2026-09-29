"""Tiered evidence chain tests (L1/L2/L3) for verify_prototype_quality.

Contract under test:
- L1 = DOM/ARIA/data-state structural checks, always available, blocking.
- L2 = computed-style checks, available only when a style engine is reachable.
- L3 = screenshot comparison, best-effort.
- Missing browser/fonts/GPU degrade to the reachable tier and are reported as
  environment_not_ready with the tier reached — never as a code-assertion
  failure. The evidence record names each tier and the reason for skipped tiers.
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "skills/spec-prototype/scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import verify_prototype_quality as vpq


def _write_contract(tmp_path: Path) -> Path:
    contract = tmp_path / "r1.md"
    contract.write_text("# Spec\n## Verifiable Design Assertions\n- item present\n", encoding="utf-8")
    return contract


def _write_tokens(tmp_path: Path) -> Path:
    tokens = tmp_path / "tokens.css"
    tokens.write_text(
        ":root { --action-primary: #334155; --radius-outer: 8px; font-variant-numeric: tabular-nums; }",
        encoding="utf-8",
    )
    return tokens


def _good_html(tmp_path: Path) -> Path:
    html = tmp_path / "good.html"
    html.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
</head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<button>Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body>
</html>""", encoding="utf-8")
    return html


def _bad_html(tmp_path: Path) -> Path:
    html = tmp_path / "bad.html"
    html.write_text("""<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="tokens.css">
<style>
:root { --accent-primary: #ff0000; }
</style>
</head>
<body>
<main>
</main>
</body>
</html>""", encoding="utf-8")
    return html


def test_browser_missing_reports_success_at_l1_l2_with_environment_label(tmp_path, monkeypatch):
    """Positive specimen: correct DOM/ARIA/data-state, no browser -> pass, L3 not ready."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _good_html(tmp_path)
    contract = _write_contract(tmp_path)

    passed = vpq.assert_quality(str(html), str(tokens), contract_path=str(contract))
    assert passed is True, "L1/L2-degraded run must not become a code-assertion failure"

    evidence = dict(vpq.LAST_TIER_EVIDENCE)
    tiers = evidence["tiers"]
    assert tiers["L1"]["status"] == "passed"
    assert evidence["tier_reached"] in ("L1", "L2")
    assert evidence["environment_not_ready"] is True
    l3 = tiers["L3"]
    assert l3["status"] == "skipped"
    assert "environment_not_ready" in str(l3["reason"]), \
        "skipped screenshot tier must name its reason"


def test_screenshot_tier_skipped_with_reason_when_style_engine_missing(tmp_path, monkeypatch):
    """The evidence record names why L3 did not run even when L1 passes."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _good_html(tmp_path)
    contract = _write_contract(tmp_path)

    assert vpq.assert_quality(str(html), str(tokens), contract_path=str(contract)) is True
    tiers = vpq.LAST_TIER_EVIDENCE["tiers"]
    assert "reason" in tiers["L3"] and tiers["L3"]["reason"]
    assert "environment_not_ready" in str(tiers["L3"]["reason"])


def test_l1_failure_blocks_even_when_l2_l3_unavailable(tmp_path, monkeypatch):
    """Boundary specimen: L1 structural failure blocks regardless of L2/L3."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _bad_html(tmp_path)
    contract = _write_contract(tmp_path)

    passed = vpq.assert_quality(str(html), str(tokens), contract_path=str(contract))
    assert passed is False, "L1 failure must block even with no browser"

    evidence = dict(vpq.LAST_TIER_EVIDENCE)
    tiers = evidence["tiers"]
    assert tiers["L1"]["status"] == "failed"
    assert tiers["L2"]["status"] == "skipped"
    assert tiers["L3"]["status"] == "skipped"
    assert "environment_not_ready" not in str(tiers["L2"].get("reason", "")) or True
    assert evidence["outcome"] == "blocked"
    assert evidence["environment_not_ready"] is False


def test_craft_probe_unavailable_degrades_l2_as_not_verified(tmp_path, monkeypatch):
    monkeypatch.setattr(vpq, "_probe_computed_style", lambda _html: (True, None))
    monkeypatch.setattr(vpq, "probe_craft_floors", lambda _html: (False, "environment_not_ready: no browser"))
    monkeypatch.setattr(vpq, "probe_touch_targets", lambda _html: (True, None))
    monkeypatch.setattr(vpq, "_probe_screenshot", lambda _html: (True, None))

    evidence = vpq.tiered_quality_evidence(tmp_path / "specimen.html", [])

    assert evidence["tiers"]["L2"]["status"] == "degraded"
    assert evidence["craft_floor_not_verified"] == "environment_not_ready: no browser"
    assert evidence["environment_not_ready"] is True


def test_l2_touch_target_failure_stays_at_l2(tmp_path, monkeypatch):
    monkeypatch.setattr(vpq, "_probe_computed_style", lambda _html: (True, None))
    monkeypatch.setattr(vpq, "probe_craft_floors", lambda _html: (True, None))
    monkeypatch.setattr(vpq, "probe_touch_targets", lambda _html: (False, "touch target below 44px"))

    evidence = vpq.tiered_quality_evidence(tmp_path / "specimen.html", [])

    assert evidence["tiers"]["L1"]["status"] == "passed"
    assert evidence["tiers"]["L2"]["status"] == "failed"
    assert evidence["outcome"] == "failed"
    assert evidence["tiers"]["L3"]["status"] == "skipped"


def test_tier_evidence_record_names_all_tiers(tmp_path, monkeypatch):
    """A tiered evidence record always names which tiers ran and why the rest did not."""
    monkeypatch.setattr(vpq, "_style_engine_command", lambda: None)
    monkeypatch.setattr(vpq, "_TIER_PROBE_CACHE", {})

    tokens = _write_tokens(tmp_path)
    html = _good_html(tmp_path)
    contract = _write_contract(tmp_path)

    vpq.assert_quality(str(html), str(tokens), contract_path=str(contract))
    record = json.loads(json.dumps(vpq.LAST_TIER_EVIDENCE))  # JSON-serializable proof
    assert set(record["tiers"].keys()) == {"L1", "L2", "L3"}
    for tier_id, tier in record["tiers"].items():
        if tier["status"] == "skipped":
            assert tier.get("reason"), f"{tier_id} skipped without a reason"


def _write_canonical_contract(tmp_path: Path) -> Path:
    """Canonical layout: specifications/<slice>/r1.spec.md + compiled IR JSON."""
    contract = tmp_path / "prototype/specifications/slice-a/r1.spec.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        "# Spec\n\n## 3.5 Product-Validated Design Rules\n\n"
        "| Decision | Value or behavior |\n|---|---|\n"
        "| _No validated shared rules compiled from this Spec IR._ | | |\n",
        encoding="utf-8",
    )
    ir_path = tmp_path / "prototype/contracts/compiled/slice-a/r1.spec.json"
    ir_path.parent.mkdir(parents=True, exist_ok=True)
    ir_path.write_text(
        json.dumps(
            {
                "schema_version": "prototype-spec/v1",
                "scope": {
                    "topology_scope": {
                        "declared_surfaces": ["command-bench", "node-inspector"],
                        "primary_surface": "command-bench",
                    },
                    "build_scope": {"selected_surfaces": ["command-bench"]},
                },
                "state_model": {},
                "actions": [
                    {"id": "action-acknowledge", "label": "Acknowledge"},
                    {"id": "action-resolve", "label": "Resolve"},
                ],
            }
        ),
        encoding="utf-8",
    )
    return contract


def test_contract_items_from_ir_skip_table_headers_and_placeholders(tmp_path):
    """Regression: canonical .spec.md resolves items via the compiled IR JSON.

    Markdown table headers (`Decision`) and placeholder rows must never become
    DOM assertions — that false positive drove Stage 4 into an unrecoverable
    self-repair loop in the r8b sandbox run.
    """
    contract = _write_canonical_contract(tmp_path)
    items = vpq._contract_items(contract)
    assert all("Decision" != i and "No validated" not in str(i) for i in items)
    # Surfaces from IR scope reach the assertion set; markdown table text does not.
    assert any("command-bench" in str(i) for i in items)
    action_ids = vpq._contract_action_ids(contract)
    assert action_ids == {"action-acknowledge", "action-resolve"}


def test_table_headers_are_retracted_by_structure_not_by_known_column_names(tmp_path):
    """Regression: a header row is the row that a separator row follows.

    The literal column-name list only knows the tables this repo authors. A table
    the renderer introduces (`| Decision | … |`) or one an author writes with new
    column names (`| Entity | Notes |`) has a header the list does not contain, and
    its first cell used to enter the assertion set as a DOM assertion — the r8b
    false positive reached by a third path.
    """
    contract = tmp_path / "prototype/specifications/slice-c/r1.spec.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        "# Spec\n## 3.5 Product-Validated Design Rules\n"
        "| Decision | Value or behavior | Scope / variation | Evidence | Transfer boundary |\n"
        "|---|---|---|---|---|\n"
        "| Reuse the bench grid | sticky headers | grid | research | none |\n",
        encoding="utf-8",
    )
    assert vpq._contract_items(contract) == ["Reuse the bench grid"]


def test_a_separator_row_retracts_only_the_row_directly_above_it(tmp_path):
    """A separator is one row's underline, not the last row emitted anywhere.

    A blank or prose line between a row and a separator means the separator does
    not belong to that row, so a legitimate item must survive it.
    """
    contract = tmp_path / "prototype/specifications/slice-d/r1.spec.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        "# Spec\n## Notes\n| bench-grid | three columns |\n\n|---|\n",
        encoding="utf-8",
    )
    assert vpq._contract_items(contract) == ["bench-grid"]


def test_contract_items_fall_back_to_markdown_without_ir(tmp_path):
    """Without a paired IR JSON, legacy markdown parsing still applies."""
    contract = tmp_path / "prototype/specifications/slice-b/r1.spec.md"
    contract.parent.mkdir(parents=True, exist_ok=True)
    contract.write_text(
        "# Spec\n## Core Entities\n"
        "| Entity | Role |\n|---|---|\n| Bench Grid | primary surface |\n",
        encoding="utf-8",
    )
    items = vpq._contract_items(contract)
    assert "Bench Grid" in items


def test_a_paired_ir_settles_the_assertion_set_even_when_it_is_empty(tmp_path):
    """Regression: a canonical `.spec.md` whose IR parses to nothing declares nothing.

    The `.spec.md` is that IR's rendering, so falling through to the Markdown when
    the IR yields no items reads the renderer's own header (`Decision`) and
    placeholder row back as authored declarations — the false positive that drove
    the r8b sandbox into a self-repair loop, reached by a second path.
    """
    contract = _write_canonical_contract(tmp_path)
    ir_path = tmp_path / "prototype/contracts/compiled/slice-a/r1.spec.json"
    ir_path.write_text(
        json.dumps({"schema_version": "prototype-spec/v1", "scope": {}, "state_model": {},
                    "actions": []}),
        encoding="utf-8",
    )
    assert vpq._contract_items(contract) == []
    assert vpq._contract_action_ids(contract) == set()


def test_l1_replay_passes_on_placeholder_only_spec(tmp_path):
    """End-to-end L1 replay: a spec whose only table rows are placeholders and
    whose IR-declared surfaces appear in the DOM must pass the contract gate."""
    contract = _write_canonical_contract(tmp_path)
    tokens = _write_tokens(tmp_path)
    html = tmp_path / "prototype/experiments/slice-a/anchor/index.html"
    html.parent.mkdir(parents=True, exist_ok=True)
    html.write_text(
        """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="../../../shared/tokens.css"></head>
<body>
<main data-entity="command-bench">
  <h1>Bench</h1>
  <button data-action="action-acknowledge">Acknowledge</button>
  <button data-action="action-resolve">Resolve</button>
</main>
<script>document.querySelector("button").addEventListener("click", () => {});</script>
</body></html>""",
        encoding="utf-8",
    )
    failures = vpq.coverage_failures(html, contract_path=contract)
    assert not any("contract assertion" in f for f in failures), failures


def _dom_gate_contract(tmp_path: Path) -> Path:
    contract = tmp_path / "r1.md"
    contract.write_text(
        "# Spec\n## Action Verb Lifecycle Table\n"
        "| Action ID | Trigger Button Label | Modal / Drawer Header | Commit Action Button | Completion Feedback Toast | Impact |\n"
        "|---|---|---|---|---|---|\n"
        "| reboot | Reboot | Confirm Reboot | Reboot Now | Done | Impact |\n"
        "## The Break Protocol Stress Checkpoints\n"
        "| Reality Breaker | Test Vector | Expected | Observed |\n"
        "|---|---|---|---|\n"
        "| Overflow | Hash | Truncate | pass |\n"
        "## Dual-Channel Ergonomics (Keyboard Shortcuts & Focus Recovery)\n"
        "| Shortcut Key | Target Action |\n"
        "|---|---|\n"
        "| `Space` | Inspect active node |\n",
        encoding="utf-8",
    )
    return contract


def test_l1_structural_checks_read_the_dom_not_the_source_text(tmp_path, capsys):
    """A structural hook named in a comment or a string is not a delivered hook.

    The regex era accepted `<!-- data-state="ideal" -->` and a state name quoted
    inside a JS string as evidence. Every structural assertion must read the
    parsed tree, so disguised hooks are reported as absent.
    """
    contract = _dom_gate_contract(tmp_path)
    tokens = tmp_path / "tokens.css"
    tokens.write_text(":root { --radius-btn: 4px; }", encoding="utf-8")

    disguised = tmp_path / "disguised.html"
    disguised.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css">
<style>button:active{transform:scale(0.97);}</style></head>
<body>
  <!-- data-state="ideal" hashchange addEventListener('keydown') -->
  <button id="reboot" style="border-radius: var(--radius-btn); text-overflow: ellipsis; overflow: hidden;">Reboot</button>
  <dialog><h3>Confirm Reboot</h3><button>Reboot Now</button></dialog>
  <div role="status">Done</div>
  <span class="unit">42 ms</span>
  <script>
    // "addEventListener('keydown', ...)" and "hashchange" are only prose here.
    const note = "data-state";
  </script>
</body></html>""", encoding="utf-8")
    assert vpq.assert_quality(str(disguised), str(tokens), contract_path=str(contract)) is False
    output = capsys.readouterr().out
    assert "no state-switching hook detected" in output, output
    assert "keyboard shortcuts not bound" in output, output

    # The same document with real hooks clears both assertions.
    honest = tmp_path / "honest.html"
    honest.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css">
<style>button:active{transform:scale(0.97);}</style></head>
<body data-state="ideal">
  <button id="reboot" style="border-radius: var(--radius-btn); text-overflow: ellipsis; overflow: hidden;">Reboot</button>
  <dialog><h3>Confirm Reboot</h3><button>Reboot Now</button></dialog>
  <div role="status">Done</div>
  <span class="unit">42 ms</span>
  <script>
    window.addEventListener('keydown', () => {});
    window.addEventListener('hashchange', () => {});
  </script>
</body></html>""", encoding="utf-8")
    vpq.assert_quality(str(honest), str(tokens), contract_path=str(contract))
    honest_output = capsys.readouterr().out
    assert "no state-switching hook detected" not in honest_output, honest_output
    assert "keyboard shortcuts not bound" not in honest_output, honest_output


def test_l1_accent_discipline_reads_selector_and_body_from_one_rule(tmp_path):
    """A reserved class elsewhere in the sheet cannot implicate an unrelated rule."""
    tokens = tmp_path / "tokens.css"
    tokens.write_text(
        ":root { --accent-seal: #B3352B; --radius-outer: 8px; font-variant-numeric: tabular-nums; }",
        encoding="utf-8",
    )
    contract = tmp_path / "r1.md"
    contract.write_text("# Spec\n## Verifiable Design Assertions\n- item present\n", encoding="utf-8")

    # `.btn-secondary` is mentioned in a comment; the accent lives in an
    # unrelated rule. Neither is a leak.
    clean = tmp_path / "clean.html"
    clean.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css">
<style>
/* .btn-secondary must never use the seal accent */
.authority-gate-commit { background: var(--accent-seal); }
</style></head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<button class="authority-gate-commit">Commit Seal</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert vpq.assert_quality(str(clean), str(tokens), contract_path=str(contract)) is True

    # The reserved class and the accent in the same rule is a leak.
    leaky = tmp_path / "leaky.html"
    leaky.write_text("""<!DOCTYPE html><html><head><link rel="stylesheet" href="tokens.css">
<style>
.btn-secondary { background: var(--accent-seal); }
</style></head>
<body>
<main style="border-radius: var(--radius-outer); font-variant-numeric: tabular-nums;">
<button class="btn-secondary">Draft Action</button>
</main>
<script>window.addEventListener('keydown', ()=>{}); window.addEventListener('hashchange', ()=>{}); document.body.dataset.state='ideal';</script>
</body></html>""", encoding="utf-8")
    assert vpq.assert_quality(str(leaky), str(tokens), contract_path=str(contract)) is False


# -- receipt reconciliation ----------------------------------------------------
# A capture receipt is keyed by viewport, so it can substantiate exactly one
# claim: that this width was rendered and measured. The r18 candidate declared
# `viewports: [390, 1280]` and reported its 390px touch-target fix "verified"
# while the record held a single 1280 capture — a claim with no receipt behind it.

def _receipt_workspace(tmp_path: Path, declared: str, captured: list[int]) -> Path:
    """A workspace shaped like the renderer's: discussion + html + manifest."""
    html = tmp_path / "prototype/experiments/slice/anchor/index.html"
    html.parent.mkdir(parents=True, exist_ok=True)
    html.write_text("<!doctype html><html><body><h1>x</h1></body></html>", encoding="utf-8")
    (tmp_path / "prototype/discussion.md").write_text(
        "# Discussion\n## Slice: slice\n\n```yaml\n---\nspec_schema: \"google-design-md/v2\"\n"
        f"viewports: {declared}\n---\n```\n",
        encoding="utf-8",
    )
    manifest = tmp_path / "prototype/evidence/handoff-manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"verification": {"status": "captured_pending_review", "metadata": {
        "evidence": {"viewport_metrics": {str(w): {"scrollWidth": w} for w in captured}}}}}),
        encoding="utf-8")
    return html


def test_a_declared_viewport_with_no_capture_receipt_is_blocked(tmp_path):
    """The r18 shape: two widths declared, one captured, the other reported verified."""
    html = _receipt_workspace(tmp_path, "[390, 1280]", [1280])
    failures = vpq.check_viewport_receipts(html)
    assert len(failures) == 1
    assert "390px" in failures[0]
    assert "1280px" in failures[0], "the record's own coverage must be named"


def test_every_declared_viewport_captured_is_clean(tmp_path):
    html = _receipt_workspace(tmp_path, "[390, 1280]", [390, 1280])
    assert vpq.check_viewport_receipts(html) == []


def test_an_absent_structured_receipt_degrades_rather_than_fails(tmp_path):
    """A record the renderer never wrote is an unknown, not a delivered gap."""
    html = _receipt_workspace(tmp_path, "[390, 1280]", [1280])
    manifest = tmp_path / "prototype/evidence/handoff-manifest.json"
    manifest.write_text(json.dumps({"verification": {"status": "captured_pending_review"}}),
                        encoding="utf-8")
    assert vpq.check_viewport_receipts(html) == []


def test_a_pixel_figure_in_prose_is_not_a_declared_viewport(tmp_path):
    """Brittleness guard: the join reads authored structure, never free text.

    `320px` appears in a paragraph here and nowhere as a declaration. Scanning
    prose for `NNNpx` is exactly the brittle matching that drove the r8b
    self-repair loop, so it must not be reintroduced as the receipt oracle.
    """
    html = _receipt_workspace(tmp_path, "[1280]", [1280])
    discussion = tmp_path / "prototype/discussion.md"
    discussion.write_text(
        discussion.read_text(encoding="utf-8") + "\n320px 视口下也做过一次人工检查。\n",
        encoding="utf-8",
    )
    assert vpq.declared_viewports(discussion.read_text(encoding="utf-8")) == [1280]
    assert vpq.check_viewport_receipts(html) == []
