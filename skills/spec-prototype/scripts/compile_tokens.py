#!/usr/bin/env python3
"""Automated Design Token Derivation and Compiler for spec-prototype.

Translates Stage 1 5-Dial registers and domain grounding into mathematical,
DTCG-compliant CSS custom properties and JSON tokens.

Eliminates manual CSS guesswork and enforces:
1. Atmospheric Undertone: Chromatic darks/lights, zero flat sterile grays (#808080).
2. Concentric Radii Mathematics: R_inner = max(0, R_outer - Padding).
3. Density-calibrated Spacing Scales: Dense (4px), Normal (8px), Sparse (12px).
4. Machined Industrial Finish: 1px layered edge hierarchy & tabular-nums.
5. Mechanical Tactile Physics: :active scale(0.97) micro-motion & cubic-bezier.

Usage:
  python3 compile_tokens.py [--discussion prototype/discussion.md]
                            [--output-css prototype/shared/tokens.css]
                            [--output-json prototype/contracts/tokens/t1.json]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Dict


# Atmospheric color undertone palettes (Hue-infused, zero dead grays)
DARK_ATMOSPHERES = {
    "plasma-cyan": {
        "bg_void": "#05070a",
        "bg_base": "#0a0d14",
        "bg_surface": "#111622",
        "bg_surface_raised": "#182030",
        "bg_overlay": "#1f293d",
        "border_dim": "#1e2638",
        "border_subtle": "#28334a",
        "border_bright": "#3b4b6e",
        "text_primary": "#e6edf3",
        "text_secondary": "#8b949e",
        "text_tertiary": "#484f58",
        "accent_primary": "#38bdf8",
        "accent_subtle": "rgba(56, 189, 248, 0.12)",
        "accent_hover": "#7dd3fc",
        "status_running": "#22c55e",
        "status_warning": "#eab308",
        "status_danger": "#ef4444",
        "border_danger": "rgba(239, 68, 68, 0.4)",
        "border_warning": "rgba(234, 179, 8, 0.4)",
    },
    "obsidian-emerald": {
        "bg_void": "#060907",
        "bg_base": "#0c130f",
        "bg_surface": "#131f18",
        "bg_surface_raised": "#1b2c22",
        "bg_overlay": "#243b2e",
        "border_dim": "#1a2e23",
        "border_subtle": "#254232",
        "border_bright": "#335b45",
        "text_primary": "#e6f3ec",
        "text_secondary": "#8ba194",
        "text_tertiary": "#485b51",
        "accent_primary": "#10b981",
        "accent_subtle": "rgba(16, 185, 129, 0.12)",
        "accent_hover": "#34d399",
        "status_running": "#10b981",
        "status_warning": "#f59e0b",
        "status_danger": "#f43f5e",
        "border_danger": "rgba(244, 63, 94, 0.4)",
        "border_warning": "rgba(245, 158, 11, 0.4)",
    }
}


def parse_5dials(discussion_text: str) -> Dict[str, str]:
    """Extract 5-dial configuration from discussion.md or fallback to defaults."""
    dials = {
        "energy": "quiet",
        "finish": "machined-industrial",
        "density": "dense",
        "weight": "dense-tactile",
        "seriousness": "solemn",
    }
    for key in dials.keys():
        match = re.search(rf"[`*]*{key}[`*]*\s*:\s*[`*]*([a-zA-Z0-9_-]+)[`*]*", discussion_text, re.IGNORECASE)
        if match:
            dials[key] = match.group(1).lower()
    return dials


def compute_tokens(dials: Dict[str, str], palette_name: str = "plasma-cyan") -> Dict[str, Any]:
    """Derive full design token tree based on 5 dials and concentric geometry."""
    colors = DARK_ATMOSPHERES.get(palette_name, DARK_ATMOSPHERES["plasma-cyan"])

    # Density calibration
    density = dials.get("density", "dense")
    if density == "dense":
        space = {1: "4px", 2: "8px", 3: "12px", 4: "16px", 5: "20px", 6: "24px", 8: "32px"}
        r_outer_val = 8
        padding_val = 4
    elif density == "sparse":
        space = {1: "8px", 2: "16px", 3: "24px", 4: "32px", 5: "40px", 6: "48px", 8: "64px"}
        r_outer_val = 16
        padding_val = 8
    else:
        space = {1: "6px", 2: "12px", 3: "18px", 4: "24px", 5: "30px", 6: "36px", 8: "48px"}
        r_outer_val = 12
        padding_val = 6

    # Concentric Radii Rule: R_inner = max(0, R_outer - Padding)
    r_inner_val = max(0, r_outer_val - padding_val)
    r_card_val = max(0, r_outer_val - 2)
    r_btn_val = max(0, r_card_val - 2)

    radii = {
        "outer": f"{r_outer_val}px",
        "inner": f"{r_inner_val}px",
        "card": f"{r_card_val}px",
        "btn": f"{r_btn_val}px",
        "sm": "2px",
        "pill": "9999px",
        "padding_panel": f"{padding_val}px",
    }

    # Typography & Finish
    finish = dials.get("finish", "machined-industrial")
    fonts = {
        "sans": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
        "mono": '"SF Mono", "Fira Code", "Roboto Mono", Menlo, monospace',
    }

    # Motion & Tactile Physics
    tactile_scale = "0.97" if dials.get("weight") in ("dense-tactile", "heavy") else "0.98"
    motion = {
        "duration_fast": "80ms",
        "duration_normal": "180ms",
        "duration_slow": "320ms",
        "ease_hud": "cubic-bezier(0.16, 1, 0.3, 1)",
        "ease_out": "cubic-bezier(0, 0, 0.2, 1)",
        "active_scale": tactile_scale,
    }

    return {
        "dials": dials,
        "colors": colors,
        "space": space,
        "radii": radii,
        "fonts": fonts,
        "motion": motion,
    }


def generate_css(tokens: Dict[str, Any]) -> str:
    """Render CSS variables and physical craft classes."""
    c = tokens["colors"]
    s = tokens["space"]
    r = tokens["radii"]
    f = tokens["fonts"]
    m = tokens["motion"]

    lines = [
        "/* ==========================================================================",
        "   DTCG Design Tokens - Machine-Derived from Stage 1 5-Dial State Machine",
        f"   Energy: {tokens['dials']['energy']} | Finish: {tokens['dials']['finish']} | Density: {tokens['dials']['density']}",
        "   ========================================================================== */",
        ":root {",
        "  /* Atmospheric Undertone Palette (Non-sterile chromatic surfaces) */",
        f"  --bg-void: {c['bg_void']};",
        f"  --bg-base: {c['bg_base']};",
        f"  --bg-surface: {c['bg_surface']};",
        f"  --bg-surface-raised: {c['bg_surface_raised']};",
        f"  --bg-overlay: {c['bg_overlay']};",
        "",
        "  /* Machined Layered Borders */",
        f"  --border-dim: {c['border_dim']};",
        f"  --border-subtle: {c['border_subtle']};",
        f"  --border-bright: {c['border_bright']};",
        f"  --border-danger: {c['border_danger']};",
        f"  --border-warning: {c['border_warning']};",
        "",
        "  /* Typography System */",
        f"  --font-sans: {f['sans']};",
        f"  --font-mono: {f['mono']};",
        f"  --font-variant-numeric: tabular-nums;",
        f"  --text-primary: {c['text_primary']};",
        f"  --text-secondary: {c['text_secondary']};",
        f"  --text-tertiary: {c['text_tertiary']};",
        "",
        "  /* Accent & Telemetry */",
        f"  --accent-primary: {c['accent_primary']};",
        f"  --accent-subtle: {c['accent_subtle']};",
        f"  --accent-hover: {c['accent_hover']};",
        f"  --status-running: {c['status_running']};",
        f"  --status-warning: {c['status_warning']};",
        f"  --status-danger: {c['status_danger']};",
        "",
        "  /* Spacing Hierarchy */",
    ]
    for k, v in sorted(s.items()):
        lines.append(f"  --space-{k}: {v};")

    lines.extend([
        "",
        "  /* Concentric Radii Hierarchy (R_inner = max(0, R_outer - Padding)) */",
        f"  --radius-outer: {r['outer']};",
        f"  --padding-panel: {r['padding_panel']};",
        f"  --radius-inner: {r['inner']};",
        f"  --radius-card: {r['card']};",
        f"  --radius-btn: {r['btn']};",
        f"  --radius-sm: {r['sm']};",
        f"  --radius-pill: {r['pill']};",
        "",
        "  /* Motion & Kinematic Physics */",
        f"  --duration-fast: {m['duration_fast']};",
        f"  --duration-normal: {m['duration_normal']};",
        f"  --duration-slow: {m['duration_slow']};",
        f"  --ease-hud: {m['ease_hud']};",
        f"  --ease-out: {m['ease_out']};",
        "}",
        "",
        "/* ==========================================================================",
        "   Global Craft, Dual-Channel Affordances & Tactile Physics",
        "   ========================================================================== */",
        ".tabular-nums {",
        "  font-variant-numeric: tabular-nums;",
        "}",
        "",
        "/* Mechanical Tactile Feedback (:active detent) */",
        f".btn-tactile:active, button:active, [role=\"button\"]:active {{",
        f"  transform: scale({m['active_scale']});",
        f"  transition: transform {m['duration_fast']} {m['ease_hud']};",
        "}",
        "",
        "/* High-Density Scrollbars */",
        "::-webkit-scrollbar {",
        "  width: 6px;",
        "  height: 6px;",
        "}",
        "::-webkit-scrollbar-track {",
        "  background: var(--bg-void);",
        "}",
        "::-webkit-scrollbar-thumb {",
        "  background: var(--border-subtle);",
        "  border-radius: var(--radius-sm);",
        "}",
        "::-webkit-scrollbar-thumb:hover {",
        "  background: var(--border-bright);",
        "}",
    ])
    return "\n".join(lines) + "\n"


def generate_dtcg_json(tokens: Dict[str, Any]) -> Dict[str, Any]:
    """Render W3C DTCG-compliant JSON token specification."""
    c = tokens["colors"]
    s = tokens["space"]
    r = tokens["radii"]
    return {
        "$schema": "https://design-tokens.github.io/community-group/format/v1.0.0/schema.json",
        "$description": "Machine-compiled from spec-prototype 5-dial state machine.",
        "color": {
            "background": {
                "void": {"$value": c["bg_void"], "$type": "color"},
                "base": {"$value": c["bg_base"], "$type": "color"},
                "surface": {"$value": c["bg_surface"], "$type": "color"},
                "surfaceRaised": {"$value": c["bg_surface_raised"], "$type": "color"},
            },
            "border": {
                "dim": {"$value": c["border_dim"], "$type": "color"},
                "subtle": {"$value": c["border_subtle"], "$type": "color"},
                "bright": {"$value": c["border_bright"], "$type": "color"},
            },
            "accent": {
                "primary": {"$value": c["accent_primary"], "$type": "color"},
                "subtle": {"$value": c["accent_subtle"], "$type": "color"},
            },
            "status": {
                "running": {"$value": c["status_running"], "$type": "color"},
                "warning": {"$value": c["status_warning"], "$type": "color"},
                "danger": {"$value": c["status_danger"], "$type": "color"},
            }
        },
        "dimension": {
            "spacing": {str(k): {"$value": v, "$type": "dimension"} for k, v in s.items()},
            "radius": {
                "outer": {"$value": r["outer"], "$type": "dimension"},
                "inner": {"$value": r["inner"], "$type": "dimension"},
                "card": {"$value": r["card"], "$type": "dimension"},
                "btn": {"$value": r["btn"], "$type": "dimension"},
            }
        }
    }


def compile_tokens(discussion_path: str, output_css_path: str, output_json_path: str | None = None) -> None:
    disc_p = Path(discussion_path)
    disc_text = disc_p.read_text(encoding="utf-8") if disc_p.is_file() else ""
    dials = parse_5dials(disc_text)

    # Determine palette based on energy line & explicit color keywords
    energy_match = re.search(r"Energy[^\n]+", disc_text, re.IGNORECASE)
    energy_line = energy_match.group(0).lower() if energy_match else ""

    palette = "plasma-cyan"
    if any(k in energy_line for k in ["emerald", "green"]):
        palette = "obsidian-emerald"
    elif any(k in energy_line for k in ["cyan", "plasma", "blue"]):
        palette = "plasma-cyan"

    computed = compute_tokens(dials, palette)
    css_content = generate_css(computed)

    out_css = Path(output_css_path)
    out_css.parent.mkdir(parents=True, exist_ok=True)
    out_css.write_text(css_content, encoding="utf-8")
    print(f"[TOKEN COMPILER] Successfully compiled tokens to {out_css}")

    if output_json_path:
        out_json = Path(output_json_path)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        dtcg_data = generate_dtcg_json(computed)
        out_json.write_text(json.dumps(dtcg_data, indent=2), encoding="utf-8")
        print(f"[TOKEN COMPILER] Successfully compiled DTCG JSON to {out_json}")


def main():
    parser = argparse.ArgumentParser(description="Compile DTCG tokens from Stage 1 5-dial state machine.")
    parser.add_argument("--discussion", default="prototype/discussion.md", help="Path to discussion.md")
    parser.add_argument("--output-css", default="prototype/shared/tokens.css", help="Target CSS file")
    parser.add_argument("--output-json", default=None, help="Target DTCG JSON file")
    args = parser.parse_args()

    compile_tokens(args.discussion, args.output_css, args.output_json)


if __name__ == "__main__":
    main()
