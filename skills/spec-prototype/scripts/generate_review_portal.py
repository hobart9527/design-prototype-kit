#!/usr/bin/env python3
"""Review Portal Dynamic Compiler.

Compiles prototype/review-portal.html based on prototype/contracts/surface-maps/m1.md
and actual disk-resident surfaces, eliminating dead links and path disparity.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
from typing import Dict, List, Tuple
import json

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

    # Check surface map
    smap = root / "prototype/contracts/surface-maps/m1.md"
    smap_text = smap.read_text(encoding="utf-8") if smap.is_file() else ""

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
    sources = {
        "surface_map": root / "prototype/contracts/surface-maps/m1.md",
        "product": root / "prototype/product.md",
        "foundation": root / "prototype/contracts/foundation/f1.md",
        "specification": None,
    }
    specs = sorted((root / "prototype/specifications").glob("*/r1.md"))
    sources["specification"] = specs[0] if specs else None
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
        '<section id="coverage-reconciliation">'
        f'<h2>Coverage: {reconciliation.get("coverage")} (rev {reconciliation.get("revision")})</h2>'
        f'<p>In round: {", ".join(reconciliation.get("in_round") or []) or "none"}</p>'
        f'<p>Outside this round: {", ".join(reconciliation.get("outside_round") or []) or "none"}</p>'
        f'<p>Declared but absent: {", ".join(reconciliation.get("missing_delivery") or []) or "none"}</p>'
        f'<p>Missing evidence: {", ".join(reconciliation.get("missing_evidence") or []) or "none"}</p>'
        + (f'<p data-scope-error="{governing.get("code", "")}">Scope error: {governing["code"]}</p>'
           if governing else "")
        + f'<p data-completion="{str(completion).lower()}">'
        f'Completion: {"met" if completion else "withheld"}</p>'
        "<table><tr><th>Surface</th><th>Scope</th><th>Delivery</th><th>Evidence</th><th>Blocker</th></tr>"
        + "".join(rows) + "</table></section>")


def build_portal_html(surfaces: List[Dict[str, str]], title: str = "Prototype Review Portal", verification: Dict[str, str] | None = None) -> str:
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

    btn_html_list = []
    for i, s in enumerate(surfaces):
        active_cls = " active" if i == 0 else ""
        btn_html_list.append(
            f'<button class="view-btn{active_cls}" onclick="loadView(\'{s["url"]}\', this)">{s["name"]}</button>'
        )
    btn_group_html = "\n      ".join(btn_html_list)

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
      width: 100%;
      height: calc(100vh - 48px - 36px);
      background: var(--bg-void, #05070a);
      display: flex;
      justify-content: center;
      align-items: stretch;
      overflow: hidden;
      padding: 10px 0;
    }}
    iframe {{
      width: 100%;
      height: 100%;
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
  </style>
</head>
<body>
  <div class="portal-nav">
    <div class="portal-title">
      <span>{title.upper()} // REVIEW PORTAL</span>
      <span class="portal-subtitle">[CANONICAL SPEC HARNESS]</span>
    </div>
    <div class="view-switcher">
      {btn_group_html}
    </div>
    <div class="viewport-tools">
      <span class="vp-label">VIEWPORT:</span>
      <button class="vp-btn active" onclick="setViewport('100%')">FULL</button>
      <button class="vp-btn" onclick="setViewport('1440px')">1440px (Wide)</button>
      <button class="vp-btn" onclick="setViewport('1024px')">1024px (Compact)</button>
      <button class="vp-btn" onclick="setViewport('768px')">768px</button>
      <button class="vp-btn" onclick="setViewport('390px')">390px (Mobile)</button>
    </div>
  </div>

  <div class="portal-frame-box">
    <iframe id="preview-frame" src="{default_url}"></iframe>
  </div>

  <div class="portal-status-bar">
    <div class="status-item">
      <div class="indicator-green"></div>
      <span>QUALITY HARNESS: {status_label} · {evidence_label}</span>
    </div>
    <div class="status-item">
      <span>SHORTCUTS: [SPACE/P: DRAIN] [ESC: CLOSE] [J/K: SELECT]</span>
    </div>
    <div class="status-item">
      <span>DTCG TOKENS: FROZEN</span>
    </div>
  </div>

  <script>
    function loadView(url, btn) {{
      document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('preview-frame').src = url;
    }}

    function setViewport(w) {{
      document.querySelectorAll('.vp-btn').forEach(b => b.classList.remove('active'));
      event.target.classList.add('active');
      document.getElementById('preview-frame').style.width = w;
    }}
  </script>
</body>
</html>
"""


def main():
    parser = argparse.ArgumentParser(description="Generate unified review portal.")
    parser.add_argument("--root", type=str, default=".", help="Repository root")
    parser.add_argument("--output", type=str, default="prototype/review-portal.html", help="Output path")
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
    html = build_portal_html(surfaces, verification=verification)
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
