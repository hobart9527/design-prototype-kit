#!/usr/bin/env python3
"""Review Portal Dynamic Compiler.

Compiles prototype/review-portal.html from the authored coverage record (the compiled
slice specification, or the legacy surface map when a tree predates it) and the actual
disk-resident surfaces, eliminating dead links and path disparity.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Dict, List
import json
import hashlib
import re

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prototype_context  # noqa: E402


def _read_verification(root: Path) -> Dict[str, str]:
    manifest = root / "prototype/evidence/handoff-manifest.json"
    if not manifest.is_file():
        return {}
    try:
        return json.loads(manifest.read_text(encoding="utf-8")).get("verification", {})
    except (OSError, json.JSONDecodeError):
        return {}


def discover_surfaces(root: Path) -> List[Dict[str, str]]:
    surfaces: List[Dict[str, str]] = []

    # Primary Core Anchor(s) (supporting neutral anchor/ and legacy hero-anchor/)
    exp_dir = root / "prototype/experiments"
    if exp_dir.is_dir():
        anchor_candidates = sorted(list(exp_dir.glob("*/anchor/index.html")) + list(exp_dir.glob("*/hero-anchor/index.html")))
        for hero in anchor_candidates:
            rel_path = hero.relative_to(root / "prototype").as_posix()
            slice_name = hero.parent.parent.name
            if not any(s["id"] == f"primary-{slice_name}" for s in surfaces):
                surfaces.append({
                    "id": f"primary-{slice_name}",
                    "name": f"Core Anchor [{slice_name}]",
                    "tier": "Tier 0 - Primary",
                    "url": rel_path,
                    "exists": True
                })

    # Contextual and Supporting surfaces in prototype/surfaces/
    surf_dir = root / "prototype/surfaces"
    if surf_dir.is_dir():
        for surf_html in sorted(surf_dir.glob("*/index.html")):
            rel_path = surf_html.relative_to(root / "prototype").as_posix()
            surf_name = surf_html.parent.name
            surfaces.append({
                "id": f"surface-{surf_name}",
                "name": f"Surface: {surf_name.replace('-', ' ').title()}",
                "tier": "Tier 1/2 - Expanded Surface",
                "url": rel_path,
                "exists": True
            })

    # If surfaces were rolled out under experiments/ (fallback)
    if exp_dir.is_dir():
        for exp_html in sorted(exp_dir.glob("*/index.html")):
            rel_path = exp_html.relative_to(root / "prototype").as_posix()
            if "hero-anchor" not in rel_path:
                name = exp_html.parent.name
                surfaces.append({
                    "id": f"exp-{name}",
                    "name": f"Surface: {name.replace('-', ' ').title()}",
                    "tier": "Expanded Surface",
                    "url": rel_path,
                    "exists": True
                })

    return surfaces


def read_coverage(root: Path) -> Dict[str, object] | None:
    """Reconcile authored scope with on-disk delivery for the review view.

    Declared-but-absent surfaces stay visible; review management statuses stay
    out of the prototype's own navigation.
    """
    # The canonical tree carries topology and product meaning inside the compiled
    # slice specification; the retired pillar files are read only when a legacy
    # tree has no r1.spec.md to stand in for them.
    canonical_specs = sorted((root / "prototype/specifications").glob("*/r1.spec.md"))
    legacy_specs = sorted((root / "prototype/specifications").glob("*/r1.md"))
    spec = canonical_specs[0] if canonical_specs else (legacy_specs[0] if legacy_specs else None)
    sources = {
        "surface_map": (root / "prototype/contracts/surface-maps/m1.md"
                        if not canonical_specs else spec),
        "product": (root / "prototype/discussion.md" if (root / "prototype/discussion.md").is_file()
                    else root / "prototype/product.md"),
        "foundation": (root / "prototype/contracts/foundation/f1.md"
                       if not canonical_specs else spec),
        "specification": spec,
    }
    texts = {}
    for key, path in sources.items():
        texts[key] = path.read_text(encoding="utf-8") if path and path.is_file() else ""
    if not texts["surface_map"]:
        return None
    context = prototype_context.read_context(**texts)

    delivered: Dict[str, str] = {}
    for html in sorted((root / "prototype/surfaces").glob("*/index.html")) + sorted(
            (root / "prototype/experiments").glob("*/**/index.html")):
        name = html.parent.parent.name if html.parent.name in ("anchor", "hero-anchor") else html.parent.name
        delivered[name] = html.relative_to(root).as_posix()

    return prototype_context.reconcile_obligations(context, delivered=delivered)


def build_coverage_html(reconciliation: Dict[str, object] | None) -> str:
    if not reconciliation:
        return ""
    # An unusable scope never renders met: completion stays withheld and the
    # governing scope error is named in the view.
    completion = bool(reconciliation.get("completion")) and not reconciliation.get("governing_error")
    governing = reconciliation.get("governing_error") or {}
    rows = []
    for obligation in reconciliation.get("obligations", []):
        rows.append(
            "<tr><td>{surface}</td><td>{scope}</td><td>{delivery}</td>"
            "<td>{evidence}</td><td>{blocker}</td></tr>".format(
                surface=obligation["surface"], scope=obligation["scope"],
                delivery=obligation["delivery"], evidence=obligation["evidence"],
                blocker=obligation["blocker"] or "-"))
    return (
        '<section id="coverage-reconciliation" class="portal-collapsible">'
        '<details>'
        f'<summary>📋 Coverage: {reconciliation.get("coverage")} (rev {reconciliation.get("revision")}) · '
        f'Completion: {"met" if completion else "withheld"}</summary>'
        '<div class="collapsible-content">'
        f'<p>In round: {", ".join(reconciliation.get("in_round") or []) or "none"}</p>'
        f'<p>Outside this round: {", ".join(reconciliation.get("outside_round") or []) or "none"}</p>'
        f'<p>Declared but absent: {", ".join(reconciliation.get("missing_delivery") or []) or "none"}</p>'
        f'<p>Missing evidence: {", ".join(reconciliation.get("missing_evidence") or []) or "none"}</p>'
        + (f'<p data-scope-error="{governing.get("code", "")}">Scope error: {governing["code"]}</p>'
           if governing else "")
        + f'<p data-completion="{str(completion).lower()}">'
        f'Completion: {"met" if completion else "withheld"}</p>'
        "<table><tr><th>Surface</th><th>Scope</th><th>Delivery</th><th>Evidence</th><th>Blocker</th></tr>"
        + "".join(rows) + "</table></div></details></section>")


def discover_directions(root: Path) -> List[Dict[str, str]]:
    """The exploration slots a session authored, as decision candidates.

    A slot is a *candidate direction* only when it is one: `dirs/<letter>/index.html`
    under an experiment. The anchor is the converged result, not a candidate, so it is
    excluded — a picker offering the winner beside its own inputs asks a question that
    has already been answered.
    """
    directions: List[Dict[str, str]] = []
    exp_dir = root / "prototype/experiments"
    if not exp_dir.is_dir():
        return directions
    for slot in sorted(exp_dir.glob("*/dirs/*/index.html")):
        slot_id = slot.parent.name
        slice_name = slot.parent.parent.parent.name
        directions.append({
            "id": f"{slice_name}-{slot_id}",
            "name": f"Direction {slot_id.upper()} [{slice_name}]",
            "url": slot.relative_to(root / "prototype").as_posix(),
            # A URL is mutable: a comment pinned to the same path after an in-place
            # edit would silently describe different pixels. The content digest
            # names the exact revision under review, so a comment stays bound to
            # what the reviewer actually saw.
            "revision": _artifact_revision(slot),
        })
    return directions


def _artifact_revision(html_path: Path) -> str:
    """Short content digest of every file in the direction slot, path-qualified.

    The digest is over bytes on disk, not a label, so an in-place edit to the HTML
    or its stylesheets changes it and an unchanged slot keeps it. Unreadable slots
    degrade to `unhashed` rather than fabricating a revision that looks authoritative.
    """
    parts: list[bytes] = []
    try:
        for path in sorted(p for p in html_path.parent.glob("**/*") if p.is_file()):
            parts.extend((path.relative_to(html_path.parent).as_posix().encode(), path.read_bytes()))
    except OSError:
        return "unhashed"
    if not parts:
        return "unhashed"
    digest = hashlib.sha256(b"\0".join(parts)).hexdigest()
    return f"sha256:{digest[:12]}"


def build_decision_html(directions: List[Dict[str, str]]) -> str:
    """The co-creation decision bar: pick a direction, then approve, steer or re-roll.

    Rendered only when there is more than one candidate: with a single direction there
    is no choice to put to a human, and a control that cannot change the outcome is
    worse than no control. The verdict is written to `location.hash` so a reviewer can
    hand the session a URL carrying their decision instead of prose.
    """
    if len(directions) < 2:
        return ""
    picks = "".join(
        f'<button class="pick-btn" data-variant="{d["id"]}" '
        f'onclick="pickVariant(\'{d["id"]}\', this)">{d["name"]}</button>'
        for d in directions)
    return (
        '<section id="co-creation" data-decision-bar class="portal-collapsible">'
        '<details>'
        '<summary>🎯 Direction Decision — Co-creation Review Bar (Click to toggle)</summary>'
        '<div class="collapsible-content">'
        '<h2>Direction Decision</h2>'
        '<p>Two-axis verdict recorded. Pick the direction that carries the product, '
        'or steer / re-roll with a reason.</p>'
        f'<div class="pick-row">{picks}</div>'
        '<div class="verdict-row">'
        '<button class="verdict-btn" data-verdict="approve" onclick="recordVerdict(\'approve\', this)">APPROVE</button>'
        '<button class="verdict-btn" data-verdict="steer" onclick="recordVerdict(\'steer\', this)">STEER</button>'
        '<button class="verdict-btn" data-verdict="re-roll" onclick="recordVerdict(\'re-roll\', this)">RE-ROLL</button>'
        '<button class="verdict-btn" data-verdict="canon" onclick="recordVerdict(\'canon\', this)">EXIT TO CANON</button>'
        '</div>'
        '<label class="reason-label" for="decision-reason">Reason (required for steer / re-roll)</label>'
        '<input id="decision-reason" class="reason-input" type="text" '
        'placeholder="what this direction must change, or why both miss">'
        '<p class="decision-out" data-decision-out>No decision recorded yet.</p>'
        '</div></details></section>')


def build_comment_overlay_html(directions: List[Dict[str, str]]) -> str:
    """Point-click review: click a spot on a direction, leave an attributed comment.

    A reviewer's objection is about a *place on a specific candidate*, so the
    comment carries the variant it was made on. Without that attribution the
    feedback is prose about "the prototype" and cannot steer one direction.
    Rendered only when there is a candidate set to comment on.
    """
    if not directions:
        return ""
    return (
        '<section id="comment-overlay" class="portal-collapsible">'
        '<details>'
        '<summary>💬 Point-click comments (attributed to the picked direction)</summary>'
        '<div class="collapsible-content">'
        '<div class="comment-tools">'
        '<button class="pick-btn" id="comment-mode" data-comment-mode="off" '
        'onclick="toggleCommentMode(this)">COMMENT: OFF</button>'
        '<button class="pick-btn" onclick="copyComments()">COPY AS JSON</button>'
        '<button class="pick-btn" data-comment-download onclick="downloadComments()">DOWNLOAD JSON</button>'
        '<span class="comment-hint">Pick a direction, turn comment mode on, then click the preview. '
        'Comments are a draft you export and record as evidence — they never approve a direction on their own.</span>'
        '</div>'
        '<ol class="comment-list" data-comment-list></ol>'
        '<pre class="comment-out" data-comment-out>No comments recorded yet.</pre>'
        '</div></details></section>')


def _comment_style() -> str:
    return """
    .comment-catcher {
      position: absolute; inset: 0; display: none; cursor: crosshair;
      background: rgba(0, 240, 255, 0.04);
    }
    .comment-catcher.on { display: block; }
    .comment-catcher:focus-visible { outline: 3px solid var(--accent-primary, #00f0ff); outline-offset: -3px; }
    .comment-catcher[aria-pressed="true"] { background: rgba(0, 240, 255, 0.1); }
    .comment-pin {
      position: absolute; width: 14px; height: 14px; margin: -7px 0 0 -7px;
      border-radius: 50%; background: var(--accent-primary, #00f0ff);
      color: #000; font: 9px/14px var(--font-mono, monospace); text-align: center;
    }
    .comment-tools { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; margin-bottom: 8px; }
    .comment-hint { color: var(--text-secondary, #94a3b8); }
    .comment-list { margin: 0 0 8px 16px; }
    .comment-list li { margin-bottom: 4px; }
    .comment-list .comment-variant { color: var(--accent-primary, #00f0ff); }
    .comment-out { color: var(--text-secondary, #94a3b8); white-space: pre-wrap; }
"""


def _comment_script() -> str:
    return """
    var comments = [];
    var commentMode = false;

    function setCommentMode(on, btn) {
      commentMode = on;
      var button = btn || document.getElementById('comment-mode');
      if (button) {
        button.textContent = 'COMMENT: ' + (commentMode ? 'ON' : 'OFF');
        button.classList.toggle('active', commentMode);
        button.setAttribute('aria-pressed', String(commentMode));
      }
      var catcher = document.querySelector('.comment-catcher');
      if (catcher) {
        catcher.classList.toggle('on', commentMode);
        // Off keeps the preview interactive: the catcher is display:none, so the
        // iframe underneath receives the pointer and its own keyboard focus.
        catcher.tabIndex = commentMode ? 0 : -1;
        catcher.setAttribute('aria-pressed', String(commentMode));
      }
    }

    function toggleCommentMode(btn) { setCommentMode(!commentMode, btn); }

    function renderComments() {
      var list = document.querySelector('[data-comment-list]');
      var out = document.querySelector('[data-comment-out]');
      if (list) {
        list.innerHTML = '';
        comments.forEach(function (c) {
          var li = document.createElement('li');
          var who = document.createElement('span');
          who.className = 'comment-variant';
          who.textContent = c.variant;
          li.appendChild(who);
          // The visible list carries the same attribution as the export, so a
          // reviewer reading the pins does not have to open the JSON to know
          // which page and frame width the note belongs to.
          var where = [c.viewport, c.page].filter(Boolean).join(' · ');
          li.appendChild(document.createTextNode(
            (where ? ' [' + where + ']' : '') + ' @' + c.x + '%/' + c.y + '% — ' + c.text));
          list.appendChild(li);
        });
      }
      if (out) { out.textContent = comments.length ? JSON.stringify(comments, null, 2) : 'No comments recorded yet.'; }
    }

    // The click lands on the catcher rather than the frame, so the iframe keeps its
    // own interactivity when comment mode is off and the coordinates stay relative
    // to the preview the reviewer is looking at.
    function addComment(event) {
      if (!commentMode) return;
      if (!currentVariant) { alert('Pick a direction first — a comment must attach to one.'); return; }
      var rect = event.currentTarget.getBoundingClientRect();
      var clientX = event.type === 'keydown' ? rect.left + rect.width / 2 : event.clientX;
      var clientY = event.type === 'keydown' ? rect.top + rect.height / 2 : event.clientY;
      var x = Math.round(((clientX - rect.left) / rect.width) * 100);
      var y = Math.round(((clientY - rect.top) / rect.height) * 100);
      var text = window.prompt('Comment on ' + currentVariant + ' at ' + x + '%/' + y + '%:');
      if (!text || !text.trim()) return;
      // Keep direction, page, viewport and the exact reviewed revision together:
      // coordinates alone are ambiguous when the reviewer switches candidates,
      // frame widths, or the artifact is edited in place under the same URL.
      var vpFrame = document.querySelector('.viewport-frame');
      var viewport = vpFrame ? (vpFrame.getAttribute('data-viewport-frame') || null) : null;
      var dir = DIRECTIONS.filter(function (d) { return d.id === currentVariant; })[0];
      comments.push({
        variant: currentVariant,
        version: dir ? (dir.revision || null) : null,
        url: document.getElementById('preview-frame').src,
        page: currentView,
        viewport: viewport,
        x: x,
        y: y,
        text: text.trim()
      });

      var pin = document.createElement('span');
      pin.className = 'comment-pin';
      pin.style.left = x + '%';
      pin.style.top = y + '%';
      pin.textContent = String(comments.length);
      event.currentTarget.appendChild(pin);
      renderComments();
    }

    function copyComments() {
      var text = JSON.stringify(comments, null, 2);
      if (navigator.clipboard) { navigator.clipboard.writeText(text); }
    }

    // Comments live only in this page's memory until exported; a reviewer who
    // closes the tab loses them. The download writes the same attributed JSON to
    // a file the session records as evidence — no feedback database, and the
    // export never asserts a decision the user did not make.
    function downloadComments() {
      var blob = new Blob([JSON.stringify(comments, null, 2)], { type: 'application/json' });
      var link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'review-comments.json';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(link.href);
    }

    document.addEventListener('DOMContentLoaded', function () {
      var catcher = document.querySelector('.comment-catcher');
      if (catcher) {
        catcher.addEventListener('click', addComment);
        // Keyboard parity: a reviewer who cannot point can still place a comment
        // at the preview's centre. Without this the overlay is pointer-only and
        // the attributed feedback it exists to collect is unreachable.
        catcher.addEventListener('keydown', function (event) {
          if (event.key === 'Enter' || event.key === ' ') {
            event.preventDefault();
            addComment(event);
          }
        });
        setCommentMode(false, document.getElementById('comment-mode'));
      }
      renderComments();
    });
"""


def _decision_style() -> str:
    return """
    .portal-collapsible {
      background: var(--bg-base, #0b0f17);
      border-bottom: 1px solid var(--border-dim, #1e293b);
      font-size: 11px;
    }
    .portal-collapsible details {
      width: 100%;
    }
    .portal-collapsible summary {
      padding: 6px 16px;
      cursor: pointer;
      user-select: none;
      color: var(--text-secondary, #94a3b8);
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      outline: none;
      transition: color 0.15s;
    }
    .portal-collapsible summary:hover {
      color: var(--text-primary, #e2e8f0);
    }
    .portal-collapsible .collapsible-content {
      padding: 10px 16px 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      background: var(--bg-surface, #0f172a);
    }
    #co-creation h2 { font-size: 12px; font-weight: 600; margin-bottom: 4px; }
    #co-creation p { color: var(--text-secondary, #94a3b8); margin-bottom: 8px; }
    .pick-row, .verdict-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 8px; }
    .pick-btn, .verdict-btn {
      background: var(--bg-void, #05070a);
      border: 1px solid var(--border-dim, #1e293b);
      color: var(--text-secondary, #94a3b8);
      padding: 5px 12px;
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      cursor: pointer;
      border-radius: 3px;
    }
    .pick-btn.active, .verdict-btn.active {
      border-color: var(--accent-primary, #00f0ff);
      color: var(--accent-primary, #00f0ff);
    }
    .pick-btn:active, .verdict-btn:active { transform: translateY(1px); }
    .reason-label { display: block; color: var(--text-secondary, #94a3b8); margin-bottom: 4px; }
    .reason-input {
      width: 100%;
      background: var(--bg-void, #05070a);
      border: 1px solid var(--border-dim, #1e293b);
      color: var(--text-primary, #e2e8f0);
      padding: 6px 8px;
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      border-radius: 3px;
    }
    .decision-out { margin-top: 8px; font-family: var(--font-mono, monospace); }
    #coverage-reconciliation table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      font-family: var(--font-mono, monospace);
      font-size: 11px;
    }
    #coverage-reconciliation th, #coverage-reconciliation td {
      border: 1px solid var(--border-dim, #1e293b);
      padding: 4px 8px;
      text-align: left;
    }
    #coverage-reconciliation th {
      background: var(--bg-surface-raised, #1e293b);
    }
"""


def _decision_script() -> str:
    return """
    var currentVariant = null;
    var currentVerdict = null;

    function variantFromHash() {
      var m = /(?:^|[#&])variant=([^&]+)/.exec(location.hash || '');
      return m ? decodeURIComponent(m[1]) : null;
    }

    // A URL carrying ?variant= opens on that candidate, so a reviewer can hand the
    // session a link instead of describing which direction they mean.
    function pickVariant(id, btn) {
      currentVariant = id;
      document.querySelectorAll('.pick-btn').forEach(function (b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
      var dir = DIRECTIONS.filter(function (d) { return d.id === id; })[0];
      if (dir) { loadView(dir.url, null); }
      location.hash = 'variant=' + encodeURIComponent(id);
      renderDecision();
    }

    function recordVerdict(verdict, btn) {
      currentVerdict = verdict;
      document.querySelectorAll('.verdict-btn').forEach(function (b) { b.classList.remove('active'); });
      if (btn) btn.classList.add('active');
      renderDecision();
    }

    function renderDecision() {
      var out = document.querySelector('[data-decision-out]');
      if (!out) return;
      var reason = (document.getElementById('decision-reason') || {}).value || '';
      var needsReason = currentVerdict === 'steer' || currentVerdict === 're-roll';
      if (!currentVariant) { out.textContent = 'Pick a direction first.'; return; }
      if (!currentVerdict) { out.textContent = 'Picked ' + currentVariant + '. Choose a verdict to record a decision.'; return; }
      if (needsReason && !reason.trim()) {
        out.textContent = currentVerdict.toUpperCase() + ' needs a reason before it can be recorded.';
        return;
      }
      out.textContent = 'DECISION: ' + currentVerdict.toUpperCase() + ' on ' + currentVariant
        + (reason.trim() ? ' — ' + reason.trim() : '');
    }

    document.addEventListener('DOMContentLoaded', function () {
      var reason = document.getElementById('decision-reason');
      if (reason) { reason.addEventListener('input', renderDecision); }
      var initial = variantFromHash();
      if (initial) {
        var btn = document.querySelector('.pick-btn[data-variant="' + initial + '"]');
        if (btn) { pickVariant(initial, btn); }
      }
    });
"""


def _viewport_label(width: int) -> str:
    if width >= 1200:
        return f"{width}px (Desktop)"
    elif width >= 700:
        return f"{width}px (Tablet)"
    return f"{width}px (Mobile)"


def discover_viewports(root: Path, surfaces: List[Dict[str, str]] | None = None) -> List[int]:
    """The viewports the record actually declares, newest declaration first.

    The declaration parse is delegated to the verifier's `declared_viewports`,
    which reads authored structure only (`viewports:` frontmatter or a
    `contract:viewports` block) and owns the layered shared-zone + per-slice
    ownership. Each discovered surface is asked through its own document path,
    so a slice's brief speaks for that slice's surfaces rather than for the
    whole tree; the rail is the union across surfaces. A button for a width
    nobody declared is a capture claim the record never made. A tree with no
    record keeps the caller's default rail.
    """
    scripts_dir = Path(__file__).resolve().parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    try:
        import verify_prototype_quality as vpq
    except ImportError:
        return []
    documents = [root / "prototype" / s["url"] for s in (surfaces or []) if s.get("url")]
    if not documents:
        documents = [root / "prototype/anchor.html"]
    widths: set[int] = set()
    for document in documents:
        try:
            parts = vpq._design_record_parts(document)
        except (OSError, ValueError, TypeError):
            continue
        widths.update(width for part in (parts or [])
                      for width in vpq.declared_viewports(part))
    return sorted(widths, reverse=True)


def build_portal_html(surfaces: List[Dict[str, str]], title: str = "Prototype Review Portal", verification: Dict[str, str] | None = None, directions: List[Dict[str, str]] | None = None, viewports: List[int | str] | None = None) -> str:
    default_url = surfaces[0]["url"] if surfaces else "about:blank"
    verification = verification or {}
    verified = (
        verification.get("status", "unverified").lower() == "verified"
        or (verification.get("browser", "").lower() == "verified" and verification.get("visual", "").lower() == "verified")
    )
    status_label = "VERIFIED" if verified else "UNVERIFIED"
    evidence_label = verification.get("evidence") or (
        f"Browser: {verification.get('browser', 'unverified')}, Visual: {verification.get('visual', 'unverified')}, Human: {verification.get('human', 'unverified')}"
    )
    # Direction Contract six questions, read from the latest capture receipt; the
    # review starts from these six, never from defect scanning alone.
    metadata = verification.get("metadata") or {}
    evidence_block = metadata.get("evidence") if isinstance(metadata, dict) else None
    checklist = (evidence_block or {}).get("direction_contract_checklist") or []
    checklist_items = "\n".join(
        f"      <li>{item}</li>" for item in checklist
    )
    checklist_html = (
        '<details class="direction-contract"><summary>Direction Contract six questions</summary>'
        '<ol class="direction-contract-list">' + checklist_items + "</ol></details>"
        if checklist else ""
    )

    btn_html_list = []
    for i, s in enumerate(surfaces):
        active_cls = " active" if i == 0 else ""
        btn_html_list.append(
            f'<button class="view-btn{active_cls}" onclick="loadView(\'{s["url"]}\', this)">{s["name"]}</button>'
        )
    if directions:
        for d in directions:
            btn_html_list.append(
                f'<button class="view-btn" onclick="loadView(\'{d["url"]}\', this)">{d["name"]}</button>'
            )
    btn_group_html = "\n      ".join(btn_html_list)
    default_url_json = json.dumps(default_url)
    directions = directions or []
    directions_json = json.dumps(directions)
    decision_html = build_decision_html(directions)
    comment_html = build_comment_overlay_html(directions)

    vp_list = viewports or [1440, 768, 390]
    vp_buttons = []
    for vp in vp_list:
        if isinstance(vp, int) or (isinstance(vp, str) and vp.replace("px", "").isdigit()):
            w_int = int(str(vp).replace("px", ""))
            lbl = _viewport_label(w_int)
            w_str = f"{w_int}px"
        else:
            w_str = str(vp)
            lbl = str(vp)
        vp_buttons.append(
            f'<button class="vp-btn" data-viewport="{w_str}" onclick="setViewport(\'{w_str}\', this)">{lbl}</button>'
        )
    vp_buttons_html = "\n      ".join(vp_buttons)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Review Portal - {title}</title>
  <link rel="stylesheet" href="shared/tokens.css">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg-void, #05070a);
      color: var(--text-primary, #e2e8f0);
      font-family: var(--font-sans, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif);
      font-size: 13px;
      height: 100vh;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .portal-nav {{
      background: var(--bg-base, #0b0f17);
      border-bottom: 1px solid var(--border-dim, #1e293b);
      padding: var(--space-2, 8px) var(--space-4, 16px);
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: 48px;
    }}
    .portal-title {{
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .portal-subtitle {{
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      color: var(--text-secondary);
    }}
    .vp-label {{
      font-size: 11px;
      color: var(--text-secondary);
    }}
    .view-switcher {{
      display: flex;
      background: var(--bg-surface, #0f172a);
      border: 1px solid var(--border-dim, #1e293b);
      border-radius: var(--radius-btn, 4px);
      padding: 2px;
      gap: 2px;
    }}
    .view-btn {{
      background: transparent;
      border: none;
      color: var(--text-secondary, #94a3b8);
      padding: 6px 14px;
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      cursor: pointer;
      border-radius: 4px;
      transition: all 0.15s;
    }}
    .view-btn:hover {{ color: var(--text-primary, #e2e8f0); }}
    .view-btn.active {{
      background: var(--accent-primary, #00f0ff);
      color: #000;
      font-weight: 600;
    }}
    .viewport-tools {{
      display: flex;
      gap: 6px;
      align-items: center;
    }}
    .vp-btn {{
      background: var(--bg-surface, #0f172a);
      border: 1px solid var(--border-dim, #1e293b);
      color: var(--text-secondary, #94a3b8);
      padding: 4px 8px;
      font-size: 11px;
      font-family: var(--font-mono, monospace);
      cursor: pointer;
      border-radius: 2px;
      transition: all 0.15s ease;
    }}
    .vp-btn.active {{
      border-color: var(--accent-primary, #00f0ff);
      color: var(--accent-primary, #00f0ff);
      background: var(--bg-surface-raised, #1e293b);
    }}
    .portal-frame-box {{
      flex: 1;
      min-height: 0;
      width: 100%;
      background: var(--bg-void, #05070a);
      display: flex;
      overflow: auto;
      padding: 10px;
      box-sizing: border-box;
    }}
    .viewport-frame {{
      position: relative;
      width: 100%;
      max-width: 100%;
      height: 100%;
      min-height: 100%;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      transition: width 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    }}
    iframe {{
      width: 100%;
      height: 100%;
      min-height: 0;
      border: 1px solid var(--border-dim, #1e293b);
      border-radius: var(--radius-outer, 6px);
      background: var(--bg-void, #05070a);
      transition: width 0.25s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.25s ease;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.36);
    }}
    .portal-status-bar {{
      background: var(--bg-base, #0b0f17);
      border-top: 1px solid var(--border-dim, #1e293b);
      padding: 0 var(--space-4, 16px);
      height: 36px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-family: var(--font-mono, monospace);
      font-size: 11px;
      color: var(--text-secondary, #94a3b8);
    }}
    .status-item {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .indicator-green {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: var(--status-running, #10b981);
      box-shadow: 0 0 6px var(--status-running, #10b981);
    }}
{_decision_style()}
{_comment_style()}
  </style></head>
<body>
  <div class="portal-nav">
    <div class="portal-title">
      <span>{title.upper()} // REVIEW PORTAL</span>
      <span class="portal-subtitle">[CANONICAL SPEC HARNESS]</span>
    </div>
    <div class="view-switcher">
      {btn_group_html}
    </div>
    <div class="viewport-tools" data-viewport-rail>
      <span class="vp-label">VIEWPORT:</span>
      <button class="vp-btn active" data-viewport="100%" onclick="setViewport('100%', this)">FULL</button>
      {vp_buttons_html}
      <button class="vp-btn" data-break-protocol="off" onclick="setBreakProtocol(null, this)">BREAK: OFF</button>
      <button class="vp-btn" data-break-protocol="overflow" data-stress="overflow" onclick="setBreakProtocol('overflow', this)">BREAK: OVERFLOW</button>
      <button class="vp-btn" data-break-protocol="empty" data-stress="empty" onclick="setBreakProtocol('empty', this)">BREAK: EMPTY</button>
    </div>
  </div>

  {decision_html}
  {comment_html}

  <div class="portal-frame-box">
    <div class="viewport-frame" data-viewport-frame="100%">
      <iframe id="preview-frame" src="{default_url}"></iframe>
      <div class="comment-catcher" role="button" aria-pressed="false" tabindex="-1"
           aria-label="Add a point-click comment at the preview centre"></div>
    </div>
  </div>

  <div class="portal-status-bar">
    <div class="status-item">
      <div class="indicator-green"></div>
      {checklist_html}
      <span>QUALITY HARNESS: {status_label} · {evidence_label}</span>
    </div>
    <div class="status-item">
      <span>SHORTCUTS: [ESC: CLOSE] [J/K: SELECT]</span>
    </div>
    <div class="status-item">
      <span>DTCG TOKENS: SEALED_PROVISIONAL</span>
    </div>
  </div>

  <script>
    var DIRECTIONS = {directions_json};
    var currentView = {default_url_json};
    var currentStress = null;
    var STRESS_QUERY = {{
      overflow: '?stress=overflow',
      empty: '?stress=empty'
    }};

    function frameUrl(url, stress) {{
      var query = STRESS_QUERY[stress];
      if (!query) return url;
      return url + (url.indexOf('?') >= 0 ? '&' + query.slice(1) : query);
    }}

    function loadView(url, btn) {{
      currentView = url;
      document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      applyFrame();
    }}

    function setViewport(w, btn) {{
      document.querySelectorAll('[data-viewport]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      var frameBox = document.querySelector('.viewport-frame');
      var frame = document.getElementById('preview-frame');
      if (frameBox) {{
        frameBox.style.width = w;
        frameBox.style.maxWidth = w === '100%' ? '100%' : 'none';
        frameBox.setAttribute('data-viewport-frame', w);
      }}
      if (frame) {{
        frame.style.width = w === '100%' ? '100%' : w;
      }}
    }}

    function setBreakProtocol(stress, btn) {{
      currentStress = stress;
      document.querySelectorAll('[data-break-protocol]').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      applyFrame();
    }}

    function applyFrame() {{
      document.getElementById('preview-frame').src = frameUrl(currentView, currentStress);
    }}

    function setViewportWidth(w) {{
      setViewport(w, document.querySelector('[data-viewport="' + w + '"]'));
    }}
{_decision_script()}
{_comment_script()}
  </script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate unified review portal.")
    parser.add_argument("--root", type=str, default=".", help="Repository root")
    parser.add_argument("--output", type=str, default="prototype/review-portal.html", help="Output path")
    parser.add_argument("--viewports", nargs="*", type=int, help="Override target review viewports")
    parser.add_argument("--open", action="store_true", help="Open generated review portal in default browser")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    surfaces = discover_surfaces(root)
    if not surfaces:
        print("Warning: No surfaces discovered under prototype/experiments or prototype/surfaces")

    verification = {}
    manifest = root / "prototype/evidence/handoff-manifest.json"
    if manifest.is_file():
        try:
            verification = json.loads(manifest.read_text(encoding="utf-8")).get("verification", {})
        except (json.JSONDecodeError, OSError):
            verification = {}
    directions = discover_directions(root)
    declared_viewports = args.viewports or discover_viewports(root, surfaces) or None
    html = build_portal_html(surfaces, verification=verification, directions=directions, viewports=declared_viewports)
    coverage_html = ""
    reconciliation = read_coverage(root)
    if reconciliation:
        coverage_html = build_coverage_html(reconciliation)
        marker = "  <div class=\"portal-frame-box\">"
        if marker in html:
            html = html.replace(marker, coverage_html + "\n" + marker, 1)
    out_path = root / args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"Generated review portal with {len(surfaces)} surfaces -> {out_path}")
    if directions:
        print(f"Decision bar carries {len(directions)} candidate direction(s)")

    if args.open:
        import subprocess
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(out_path)], check=False)
            elif sys.platform.startswith("linux"):
                subprocess.run(["xdg-open", str(out_path)], check=False)
            elif sys.platform == "win32":
                subprocess.run(["cmd", "/c", "start", str(out_path)], check=False)
        except Exception as e:
            print(f"Could not open browser: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
