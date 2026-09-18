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


from typing import Any, Dict, Tuple
import math


def _srgb_to_linear(v: float) -> float:
    return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(v: float) -> float:
    v = max(0.0, min(1.0, v))
    return 12.92 * v if v <= 0.0031308 else 1.055 * (v ** (1.0 / 2.4)) - 0.055


def _rgb_to_oklab(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convert sRGB float (0..1) to OKLab (L, a, b)."""
    lr = _srgb_to_linear(r)
    lg = _srgb_to_linear(g)
    lb = _srgb_to_linear(b)

    l = 0.4122214708 * lr + 0.5363325363 * lg + 0.0514459929 * lb
    m = 0.2119034982 * lr + 0.6806995451 * lg + 0.1073969566 * lb
    s = 0.0883024619 * lr + 0.2817188376 * lg + 0.6299787005 * lb

    l_ = l ** (1.0 / 3.0) if l > 0 else 0.0
    m_ = m ** (1.0 / 3.0) if m > 0 else 0.0
    s_ = s ** (1.0 / 3.0) if s > 0 else 0.0

    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, a, b


def _oklab_to_rgb(L: float, a: float, b: float) -> Tuple[float, float, float]:
    """Convert OKLab (L, a, b) to sRGB float (0..1)."""
    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b

    l = l_ ** 3.0 if l_ > 0 else 0.0
    m = m_ ** 3.0 if m_ > 0 else 0.0
    s = s_ ** 3.0 if s_ > 0 else 0.0

    lr = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    lg = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    lb = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

    return _linear_to_srgb(lr), _linear_to_srgb(lg), _linear_to_srgb(lb)


def _hex_to_oklab(hex_code: str) -> Tuple[float, float, float]:
    r, g, b = _hex_to_rgb(hex_code)
    return _rgb_to_oklab(r / 255.0, g / 255.0, b / 255.0)


def _oklab_to_hex(L: float, a: float, b: float) -> str:
    r, g, b = _oklab_to_rgb(L, a, b)
    return _rgb_to_hex(int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))


def derive_perceptual_surface_scale(base_hex: str, is_light: bool) -> Dict[str, str]:
    """Derive perceptually uniform surface elevations and borders via OKLab lightness steps."""
    L, a, b = _hex_to_oklab(base_hex)
    scale: Dict[str, str] = {}

    if is_light:
        # Light surface step-downs: void is slight warm wash, base/surface pure or near white, borders step down in L
        scale["bg_void"] = base_hex
        scale["bg_base"] = _oklab_to_hex(min(0.99, L + 0.02), a * 0.7, b * 0.7)
        scale["bg_surface"] = _oklab_to_hex(min(1.0, L + 0.04), a * 0.5, b * 0.5)
        scale["bg_surface_raised"] = _oklab_to_hex(1.0, 0.0, 0.0)
        scale["bg_overlay"] = _oklab_to_hex(1.0, 0.0, 0.0)

        # Border steps (decreasing lightness)
        scale["border_dim"] = _oklab_to_hex(max(0.0, L - 0.06), a, b)
        scale["border_subtle"] = _oklab_to_hex(max(0.0, L - 0.12), a, b)
        scale["border_bright"] = _oklab_to_hex(max(0.0, L - 0.24), a, b)

        # Text steps (high contrast dark)
        scale["text_primary"] = _oklab_to_hex(0.18, a * 0.2, b * 0.2)
        scale["text_secondary"] = _oklab_to_hex(0.42, a * 0.3, b * 0.3)
        scale["text_tertiary"] = _oklab_to_hex(0.58, a * 0.3, b * 0.3)
    else:
        # Dark surface step-ups (increasing lightness)
        scale["bg_void"] = base_hex
        scale["bg_base"] = _oklab_to_hex(min(0.9, L + 0.035), a, b)
        scale["bg_surface"] = _oklab_to_hex(min(0.9, L + 0.07), a, b)
        scale["bg_surface_raised"] = _oklab_to_hex(min(0.9, L + 0.11), a, b)
        scale["bg_overlay"] = _oklab_to_hex(min(0.9, L + 0.16), a, b)

        # Border steps (increasing lightness in dark mode)
        scale["border_dim"] = _oklab_to_hex(min(0.9, L + 0.10), a, b)
        scale["border_subtle"] = _oklab_to_hex(min(0.9, L + 0.16), a, b)
        scale["border_bright"] = _oklab_to_hex(min(0.9, L + 0.26), a, b)

        # Text steps (high contrast light)
        scale["text_primary"] = _oklab_to_hex(0.96, a * 0.2, b * 0.2)
        scale["text_secondary"] = _oklab_to_hex(0.70, a * 0.3, b * 0.3)
        scale["text_tertiary"] = _oklab_to_hex(0.48, a * 0.3, b * 0.3)

    return scale


def check_wcag_contrast(fg_hex: str, bg_hex: str) -> float:
    """Calculate WCAG 2.1 relative luminance contrast ratio."""
    def _rel_lum(h: str) -> float:
        r, g, b = _hex_to_rgb(h)
        rgb_lin = [_srgb_to_linear(c / 255.0) for c in (r, g, b)]
        return 0.2126 * rgb_lin[0] + 0.7152 * rgb_lin[1] + 0.0722 * rgb_lin[2]

    l1 = _rel_lum(fg_hex)
    l2 = _rel_lum(bg_hex)
    return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)


# Legacy named palettes remain available only for callers that explicitly opt in.
DARK_ATMOSPHERES = {
    # Modern Industrial Craft Palettes (P9+ Reality Anchors)
    "warm-graphite-lime": {  # Teenage Engineering / Industrial Hardware Anchor
        "bg_void": "#080b0b",
        "bg_base": "#101414",
        "bg_surface": "#181d1d",
        "bg_surface_raised": "#222929",
        "bg_overlay": "#2c3535",
        "border_dim": "#222a2a",
        "border_subtle": "#2f3a3a",
        "border_bright": "#425252",
        "text_primary": "#f4f5f1",
        "text_secondary": "#9aa49e",
        "text_tertiary": "#55615a",
        "accent_primary": "#d6f56b",  # Functional acid lime / silkscreen signal
        "accent_subtle": "rgba(214, 245, 107, 0.12)",
        "accent_hover": "#e2f98f",
        "status_running": "#d6f56b",
        "status_warning": "#f59e0b",
        "status_danger": "#ff4d4d",
        "border_danger": "rgba(255, 77, 77, 0.4)",
        "border_warning": "rgba(245, 158, 11, 0.4)",
    },
    "zinc-cobalt": {  # Linear / Precision SaaS Pro Anchor
        "bg_void": "#08090c",
        "bg_base": "#0e1017",
        "bg_surface": "#151824",
        "bg_surface_raised": "#1d2233",
        "bg_overlay": "#262c42",
        "border_dim": "rgba(255, 255, 255, 0.07)",
        "border_subtle": "rgba(255, 255, 255, 0.12)",
        "border_bright": "rgba(255, 255, 255, 0.22)",
        "text_primary": "#f2f4f8",
        "text_secondary": "#8c96a8",
        "text_tertiary": "#515a6b",
        "accent_primary": "#5e6ad2",  # Restrained cobalt indigo
        "accent_subtle": "rgba(94, 106, 210, 0.15)",
        "accent_hover": "#7480e6",
        "status_running": "#22c55e",
        "status_warning": "#eab308",
        "status_danger": "#ef4444",
        "border_danger": "rgba(239, 68, 68, 0.4)",
        "border_warning": "rgba(234, 179, 8, 0.4)",
    },
    "titanium-amber": {  # Datadog / Aviation Instrument Anchor
        "bg_void": "#0d0e10",
        "bg_base": "#14161a",
        "bg_surface": "#1c1f24",
        "bg_surface_raised": "#252930",
        "bg_overlay": "#2f343d",
        "border_dim": "#252930",
        "border_subtle": "#333842",
        "border_bright": "#474e5c",
        "text_primary": "#eceff4",
        "text_secondary": "#8f98a7",
        "text_tertiary": "#565d6a",
        "accent_primary": "#ff9800",  # Calibrated safety amber
        "accent_subtle": "rgba(255, 152, 0, 0.14)",
        "accent_hover": "#ffac33",
        "status_running": "#10b981",
        "status_warning": "#ff9800",
        "status_danger": "#f43f5e",
        "border_danger": "rgba(244, 63, 94, 0.4)",
        "border_warning": "rgba(255, 152, 0, 0.4)",
    },
    # Legacy / Complementary Palettes
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
        "accent_primary": "#00f0ff",
        "accent_subtle": "rgba(0, 240, 255, 0.12)",
        "accent_hover": "#38bdf8",
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

PALETTE_ALIASES = {
    "teenage-engineering": "warm-graphite-lime",
    "teenage_engineering": "warm-graphite-lime",
    "acid-lime": "warm-graphite-lime",
    "warm-graphite": "warm-graphite-lime",
    "linear": "zinc-cobalt",
    "linear-dark": "zinc-cobalt",
    "cobalt": "zinc-cobalt",
    "datadog": "titanium-amber",
    "amber": "titanium-amber",
    "aviation": "titanium-amber",
    "emerald": "obsidian-emerald",
    "cyan": "plasma-cyan",
}


# Canonical v10 Five Axes (Optional & Composable)
CANONICAL_FIVE_AXES = ("density", "energy", "materiality", "rhythm", "character")
# Legacy dial aliases for backwards compatibility
LEGACY_DIAL_MAP = {
    "finish": "materiality",
    "weight": "materiality",
    "seriousness": "character",
}


def parse_five_axes(discussion_text: str) -> Dict[str, str]:
    """Extract optional Five Axes decisions from discussion; returns empty/partial dict if undeclared.

    Never fails if axes are omitted. Maps legacy 5-dial terms into canonical axes where appropriate.
    """
    axes: Dict[str, str] = {}
    # 1. Search canonical axes
    for key in CANONICAL_FIVE_AXES:
        match = re.search(rf"[`*]*{key}[`*]*\s*:\s*[`*]*([a-zA-Z0-9_-]+)[`*]*", discussion_text, re.IGNORECASE)
        if match:
            axes[key] = match.group(1).lower()

    # 2. Check legacy dial keys if canonical axes were not declared
    for legacy_key, target_axis in LEGACY_DIAL_MAP.items():
        if target_axis not in axes:
            match = re.search(rf"[`*]*{legacy_key}[`*]*\s*:\s*[`*]*([a-zA-Z0-9_-]+)[`*]*", discussion_text, re.IGNORECASE)
            if match:
                axes[target_axis] = match.group(1).lower()

    return axes


def parse_5dials(discussion_text: str) -> Dict[str, str]:
    """Backwards-compatible alias for parse_five_axes."""
    return parse_five_axes(discussion_text)


def _hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    h = hex_code.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def _is_light_color(hex_code: str) -> bool:
    try:
        r, g, b = _hex_to_rgb(hex_code)
        # Perceived brightness according to ITU-R BT.601
        return (r * 299 + g * 587 + b * 114) / 1000 > 160
    except Exception:
        return False


def _extract_confirmed_section(text: str) -> str:
    """Extract confirmed decisions or active selected option block if present."""
    # 1. Explicit confirmed decisions heading
    m_conf = re.search(r"^##+[^\n]*?(?:Confirmed|Selected|Decision|Final|已确认|已选定|决策)[^\n]*\n(.*?)(?=\n##+|\Z)", text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
    if m_conf and m_conf.group(1).strip():
        return m_conf.group(1).strip()

    # 2. Option marked as selected, e.g. Option B (Selected) or [x] Option B
    m_opt = re.search(r"^###+[^\n]*?(?:Option|方案|方向)[^\n]*?(?:Selected|Confirmed|Chosen|已选|✓|\[x\])[^\n]*\n(.*?)(?=\n###+|\n##+|\Z)", text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
    if m_opt and m_opt.group(1).strip():
        return m_opt.group(1).strip()

    return ""


def extract_dynamic_palette(discussion_text: str, fallback_palette: str = "warm-graphite-lime") -> Dict[str, str]:
    """Dynamically extract authored chromatic tokens from Stage 1 discussion or synthesize mathematically.

    Prioritizes confirmed/selected decision sections over rejected candidate options.
    """
    token_keys = {
        "accent_primary": ["accent-primary", "accent_primary", "primary-accent", "accent"],
        "accent_hover": ["accent-hover", "accent_hover"],
        "bg_void": ["bg-void", "bg_void", "background-void", "void-bg"],
        "bg_base": ["bg-base", "bg_base", "background-base"],
        "bg_surface": ["bg-surface", "bg_surface", "surface-bg"],
        "bg_surface_raised": ["bg-surface-raised", "bg_surface_raised", "surface-raised"],
        "bg_overlay": ["bg-overlay", "bg_overlay"],
        "border_dim": ["border-dim", "border_dim"],
        "border_subtle": ["border-subtle", "border_subtle", "border"],
        "border_bright": ["border-bright", "border_bright", "border-focus"],
        "text_primary": ["text-primary", "text_primary", "primary-text"],
        "text_secondary": ["text-secondary", "text_secondary"],
        "text_tertiary": ["text-tertiary", "text_tertiary"],
        "status_running": ["status-running", "status_running"],
        "status_warning": ["status-warning", "status_warning"],
        "status_danger": ["status-danger", "status_danger"],
    }

    confirmed_block = _extract_confirmed_section(discussion_text)
    extracted: Dict[str, str] = {}

    for canon_key, aliases in token_keys.items():
        # First priority: check confirmed / selected block
        if confirmed_block:
            found_in_confirmed = False
            for alias in aliases:
                pattern = rf"(?:--)?(?:color-)?{alias}\s*[:|=]\s*[`*]*([#0-9a-fA-F]{{3,8}}|rgba?\([^)]+\))[`*]*"
                matches = list(re.finditer(pattern, confirmed_block, re.IGNORECASE))
                if matches:
                    extracted[canon_key] = matches[-1].group(1).strip()
                    found_in_confirmed = True
                    break
            if found_in_confirmed:
                continue

        # Second priority: search full text, taking the LAST authored match (so latest choice overrides earlier drafts)
        for alias in aliases:
            pattern = rf"(?:--)?(?:color-)?{alias}\s*[:|=]\s*[`*]*([#0-9a-fA-F]{{3,8}}|rgba?\([^)]+\))[`*]*"
            matches = list(re.finditer(pattern, discussion_text, re.IGNORECASE))
            if matches:
                extracted[canon_key] = matches[-1].group(1).strip()
                break

    pal_match = re.search(
        r"[`*]*(?:palette|color\s+palette|atmosphere)[`*]*\s*[:|=]\s*[`*]*([a-zA-Z0-9_-]+)[`*]*",
        discussion_text,
        re.IGNORECASE,
    )
    base_name = pal_match.group(1).lower() if pal_match else fallback_palette
    resolved_base = PALETTE_ALIASES.get(base_name, base_name)
    if resolved_base not in DARK_ATMOSPHERES:
        resolved_base = "warm-graphite-lime"

    base_colors = dict(DARK_ATMOSPHERES[resolved_base])

    # If custom background was authored, synthesize physical elevation hierarchy via OKLab perceptual scale
    if "bg_void" in extracted and extracted["bg_void"].startswith("#"):
        try:
            is_light = _is_light_color(extracted["bg_void"])
            oklab_scale = derive_perceptual_surface_scale(extracted["bg_void"], is_light)
            for k, v in oklab_scale.items():
                base_colors[k] = extracted.get(k, v)
        except Exception:
            pass

    # If custom accent was authored, derive interactive and hover variants
    if "accent_primary" in extracted and extracted["accent_primary"].startswith("#"):
        try:
            ar, ag, ab = _hex_to_rgb(extracted["accent_primary"])
            base_colors["accent_primary"] = extracted["accent_primary"]
            base_colors["accent_subtle"] = extracted.get("accent_subtle", f"rgba({ar}, {ag}, {ab}, 0.14)")
            base_colors["accent_hover"] = extracted.get("accent_hover", _rgb_to_hex(min(255, int(ar * 1.15)), min(255, int(ag * 1.15)), min(255, int(ab * 1.15))))
        except Exception:
            pass

    for k, v in extracted.items():
        base_colors[k] = v

    return base_colors


def compute_tokens(dials: Dict[str, str] | None = None, palette_or_colors: str | Dict[str, str] = "warm-graphite-lime") -> Dict[str, Any]:
    """Derive full design token tree from optional Five Axes / dials and an explicit palette or dynamic color dict.

    All axes are optional. Undeclared axes fall back gracefully to balanced defaults.
    """
    if dials is None:
        dials = {}

    if isinstance(palette_or_colors, dict):
        colors = palette_or_colors
    else:
        palette_name = str(palette_or_colors)
        resolved_palette = PALETTE_ALIASES.get(palette_name.lower(), palette_name.lower())
        if resolved_palette not in DARK_ATMOSPHERES:
            resolved_palette = "warm-graphite-lime"
        colors = DARK_ATMOSPHERES[resolved_palette]

    # Density calibration (Density Axis)
    density = dials.get("density", "balanced").lower()
    if density in ("dense", "compact", "high"):
        space = {1: "4px", 2: "8px", 3: "12px", 4: "16px", 5: "20px", 6: "24px", 8: "32px"}
        r_outer_val = 8
        padding_val = 4
    elif density in ("sparse", "relaxed", "low", "airy"):
        space = {1: "8px", 2: "16px", 3: "24px", 4: "32px", 5: "40px", 6: "48px", 8: "64px"}
        r_outer_val = 16
        padding_val = 8
    else:
        # Balanced default
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

    # Materiality / Finish Axis calibration
    materiality = dials.get("materiality", dials.get("finish", "machined-industrial")).lower()
    if any(k in materiality for k in ("editorial", "paper", "reading")):
        fonts = {
            "sans": 'Charter, "Bitstream Charter", "Sitka Text", Cambria, Georgia, serif',
            "mono": '"SF Mono", "Fira Code", Menlo, monospace',
        }
    elif any(k in materiality for k in ("somatic", "touch", "mobile", "glass", "organic")):
        fonts = {
            "sans": '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif',
            "mono": '"SF Mono", "Fira Code", monospace',
        }
        # Touch profiles favor slightly larger card radii and ergonomic buttons
        radii["card"] = f"{r_card_val + 2}px"
        radii["btn"] = "9999px"
    else:
        fonts = {
            "sans": '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
            "mono": '"JetBrains Mono", "SF Mono", "Fira Code", Menlo, monospace',
        }

    # Weight / Tactile Physics Axis calibration
    weight = dials.get("weight", dials.get("materiality", "regular")).lower()
    if any(k in weight for k in ("dense-tactile", "heavy", "dense")):
        tactile_scale = "0.96"
    elif any(k in weight for k in ("light", "subtle", "airy")):
        tactile_scale = "0.99"
    else:
        tactile_scale = "0.98"

    # Energy & Rhythm Axis calibration (temporal physics & rhythm)
    # v10.1: Rhythm and Energy are distinct; rhythm affects pacing scale, energy affects duration speed
    rhythm = dials.get("rhythm", "steady").lower()
    energy = dials.get("energy", "kinetic").lower()

    if any(k in energy for k in ("calm", "serene", "quiet")):
        base_fast, base_norm, base_slow = 120, 240, 400
        ease_hud = "cubic-bezier(0.2, 0.8, 0.2, 1)"
    else:
        base_fast, base_norm, base_slow = 80, 180, 320
        ease_hud = "cubic-bezier(0.16, 1, 0.3, 1)"

    # Rhythm modifier: measured/stately lengthens transitions slightly; rapid/brisk tightens
    if any(k in rhythm for k in ("measured", "stately", "deliberate", "relaxed")):
        base_fast = int(base_fast * 1.25)
        base_norm = int(base_norm * 1.25)
        base_slow = int(base_slow * 1.25)
    elif any(k in rhythm for k in ("rapid", "brisk", "instant", "snappy")):
        base_fast = max(50, int(base_fast * 0.75))
        base_norm = max(100, int(base_norm * 0.75))
        base_slow = max(200, int(base_slow * 0.75))

    motion = {
        "duration_fast": f"{base_fast}ms",
        "duration_normal": f"{base_norm}ms",
        "duration_slow": f"{base_slow}ms",
        "ease_hud": ease_hud,
        "ease_out": "cubic-bezier(0, 0, 0.2, 1)",
        "active_scale": tactile_scale,
    }

    # Character Axis calibration (affects typography tone, density feel, and feedback prominence)
    character = dials.get("character", dials.get("seriousness", "utilitarian")).lower()
    if any(k in character for k in ("scholarly", "editorial", "academic")):
        line_height_body = "1.6"
        line_height_heading = "1.25"
    elif any(k in character for k in ("playful", "expressive", "friendly")):
        line_height_body = "1.55"
        line_height_heading = "1.2"
        radii["card"] = f"{int(r_outer_val * 1.2)}px"
    else:
        line_height_body = "1.5"
        line_height_heading = "1.2"

    # 3-Tier Semantic & Component Hierarchy (Rich Contract, Lean Engine)
    is_light = _is_light_color(colors.get("bg_void", "#080b0b"))
    text_inverse = "#121518" if is_light else "#f8fafc"

    semantics = {
        "surface_base": colors["bg_surface"],
        "surface_elevated": colors["bg_surface_raised"],
        "surface_sunken": colors["bg_base"],
        "surface_overlay": colors["bg_overlay"],
        "text_primary": colors["text_primary"],
        "text_secondary": colors["text_secondary"],
        "text_tertiary": colors["text_tertiary"],
        "text_muted": colors["text_tertiary"],
        "text_inverse": text_inverse,
        "action_primary": colors["accent_primary"],
        "action_primary_hover": colors["accent_hover"],
        "action_primary_active": colors["accent_hover"],
        "action_ghost_hover": colors["accent_subtle"],
        "status_nominal": colors["status_running"],
        "status_warning": colors["status_warning"],
        "status_danger": colors["status_danger"],
    }

    components = {
        "input_bg": colors["bg_base"],
        "input_border": colors["border_subtle"],
        "input_border_focus": colors["accent_primary"],
        "input_focus_ring": f"0 0 0 2px {colors['accent_subtle']}",
        "card_bg": colors["bg_surface"],
        "card_bg_hover": colors["bg_surface_raised"],
        "card_border": colors["border_subtle"],
        "card_border_active": colors["border_bright"],
        "table_row_hover": colors["bg_surface_raised"],
        "table_border": colors["border_dim"],
        "badge_bg": colors["accent_subtle"],
        "badge_text": colors["accent_primary"],
        "modal_backdrop": "rgba(0, 0, 0, 0.70)" if not is_light else "rgba(15, 23, 42, 0.40)",
        "modal_surface": colors["bg_surface_raised"],
        "modal_border": colors["border_bright"],
    }

    return {
        "dials": dials,
        "colors": colors,
        "space": space,
        "radii": radii,
        "fonts": fonts,
        "motion": motion,
        "semantics": semantics,
        "components": components,
    }


def generate_css(tokens: Dict[str, Any]) -> str:
    """Render CSS variables and physical craft classes."""
    c = tokens["colors"]
    s = tokens["space"]
    r = tokens["radii"]
    f = tokens["fonts"]
    m = tokens["motion"]

    d = tokens.get("dials", {})
    energy_desc = d.get("energy", "balanced")
    materiality_desc = d.get("materiality", d.get("finish", "machined-industrial"))
    density_desc = d.get("density", "balanced")

    lines = [
        "/* ==========================================================================",
        "   DTCG Design Tokens - Derived from v10 Five Axes / Experience Foundation",
        f"   Energy: {energy_desc} | Materiality: {materiality_desc} | Density: {density_desc}",
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
        "  /* Domain-Specific Semantic Extension Variables */",
        f"  --status-p0: {c.get('status_p0', c['status_danger'])};",
        f"  --status-p1: {c.get('status_p1', c['status_warning'])};",
        f"  --status-ok: {c.get('status_ok', c['status_running'])};",
        f"  --paper-bg: {c.get('paper_bg', c['bg_surface'])};",
        f"  --ink-primary: {c.get('ink_primary', c['text_primary'])};",
        f"  --ink-secondary: {c.get('ink_secondary', c['text_secondary'])};",
        f"  --reading-measure-max: 68ch;",
        "  --line-height-body: 1.5;",
        "  --line-height-heading: 1.2;",
        "  --min-touch-target: 44px;",
        "  --safe-area-inset-bottom: env(safe-area-inset-bottom, 16px);",
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
        "",
        "  /* ==========================================================================",
        "     Layer 2: Semantic Tokens (Functional Roles & Expressive Intent)",
        "     ========================================================================== */",
        "  --surface-base: var(--bg-surface);",
        "  --surface-elevated: var(--bg-surface-raised);",
        "  --surface-sunken: var(--bg-base);",
        "  --surface-overlay: var(--bg-overlay);",
        "",
        "  --text-muted: var(--text-tertiary);",
        f"  --text-inverse: {tokens['semantics']['text_inverse']};",
        "",
        "  --action-primary: var(--accent-primary);",
        "  --action-primary-hover: var(--accent-hover);",
        f"  --action-primary-active: {tokens['semantics']['action_primary_active']};",
        "  --action-ghost-hover: var(--accent-subtle);",
        "",
        "  --status-nominal: var(--status-running);",
        "",
        "  /* ==========================================================================",
        "     Layer 3: Component & Container Slots (Zero-Boilerplate Front-End Slots)",
        "     ========================================================================== */",
        "  --input-bg: var(--bg-base);",
        "  --input-border: var(--border-subtle);",
        "  --input-border-focus: var(--accent-primary);",
        f"  --input-focus-ring: {tokens['components']['input_focus_ring']};",
        "",
        "  --card-bg: var(--bg-surface);",
        "  --card-bg-hover: var(--bg-surface-raised);",
        "  --card-border: var(--border-subtle);",
        "  --card-border-active: var(--border-bright);",
        "",
        "  --table-row-hover: var(--bg-surface-raised);",
        "  --table-border: var(--border-dim);",
        "",
        "  --badge-bg: var(--accent-subtle);",
        "  --badge-text: var(--accent-primary);",
        "",
        f"  --modal-backdrop: {tokens['components']['modal_backdrop']};",
        "  --modal-surface: var(--bg-surface-raised);",
        "  --modal-border: var(--border-bright);",
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
        "",
        "/* Reduced Motion A11y Resilience */",
        "@media (prefers-reduced-motion: reduce) {",
        "  *, ::before, ::after {",
        "    animation-duration: 0.01ms !important;",
        "    animation-iteration-count: 1 !important;",
        "    transition-duration: 0.01ms !important;",
        "    scroll-behavior: auto !important;",
        "  }",
        "}",
    ])
    return "\n".join(lines) + "\n"


def generate_dtcg_json(tokens: Dict[str, Any]) -> Dict[str, Any]:
    """Render W3C DTCG-compliant 3-Tier JSON token specification.

    Produces structured 3-tier architecture (Primitives -> Semantics -> Components)
    with explicit authority provenance and metadata, while preserving backward-compatible
    top-level groups for export-tokens.py and downstream CLI consumption.
    """
    c = tokens["colors"]
    s = tokens["space"]
    r = tokens["radii"]
    f = tokens["fonts"]
    m = tokens.get("motion", {})
    sem = tokens.get("semantics", {})
    comp = tokens.get("components", {})

    # Determine authority provenance
    # Explicit Human Decision > Frozen Product Rule > Derived Token > Default
    default_auth = tokens.get("authority", "derived")

    color_tokens: Dict[str, Any] = {
        "primary": {"$value": c["accent_primary"], "$type": "color", "$description": "Primary action and key interactive state", "authority": default_auth},
        "primary-hover": {"$value": c["accent_hover"], "$type": "color", "$description": "Hover state of primary", "authority": default_auth},
        "surface": {"$value": c["bg_surface"], "$type": "color", "$description": "Card, panel, and workbench base surface", "authority": default_auth},
        "surface-raised": {"$value": c["bg_surface_raised"], "$type": "color", "$description": "Elevated modal, sheet, or popover", "authority": default_auth},
        "surface-overlay": {"$value": c["bg_overlay"], "$type": "color", "$description": "Top-tier fly-by-wire controls and overlay", "authority": default_auth},
        "border": {"$value": c["border_subtle"], "$type": "color", "$description": "Default component boundary", "authority": default_auth},
        "border-strong": {"$value": c["border_bright"], "$type": "color", "$description": "Active or emphasized component boundary", "authority": default_auth},
        "border-dim": {"$value": c["border_dim"], "$type": "color", "$description": "Subtle hairline divider", "authority": default_auth},
        "text-primary": {"$value": c["text_primary"], "$type": "color", "$description": "Primary high-contrast typography", "authority": default_auth},
        "text-secondary": {"$value": c["text_secondary"], "$type": "color", "$description": "Supplementary metadata and labels", "authority": default_auth},
        "text-tertiary": {"$value": c["text_tertiary"], "$type": "color", "$description": "De-emphasized or disabled controls and copy", "authority": default_auth},
        "status-running": {"$value": c["status_running"], "$type": "color", "$description": "Nominal operational state", "authority": default_auth},
        "status-warning": {"$value": c["status_warning"], "$type": "color", "$description": "Warning state or capacity threshold", "authority": default_auth},
        "status-danger": {"$value": c["status_danger"], "$type": "color", "$description": "Critical failure or thermal alert", "authority": default_auth},
        "bg-void": {"$value": c["bg_void"], "$type": "color", "$description": "Deepest atmospheric background", "authority": default_auth},
        "bg-base": {"$value": c["bg_base"], "$type": "color", "$description": "App foundation background chassis", "authority": default_auth},
    }

    spacing_tokens: Dict[str, Any] = {
        str(k): {"$value": v, "$type": "dimension", "$description": f"Spacing unit {k}", "authority": default_auth}
        for k, v in sorted(s.items())
    }

    radius_tokens: Dict[str, Any] = {
        "outer": {"$value": r["outer"], "$type": "dimension", "$description": "Outer container boundary", "authority": default_auth},
        "inner": {"$value": r["inner"], "$type": "dimension", "$description": "Concentric inner child boundary", "authority": default_auth},
        "card": {"$value": r["card"], "$type": "dimension", "$description": "Card entity radius", "authority": default_auth},
        "btn": {"$value": r["btn"], "$type": "dimension", "$description": "Interactive control radius", "authority": default_auth},
        "pill": {"$value": r["pill"], "$type": "dimension", "$description": "Status badge pill radius", "authority": default_auth},
    }

    typography_tokens: Dict[str, Any] = {
        "font-sans": {"$value": f["sans"], "$type": "fontFamily", "$description": "Primary UI font family", "authority": default_auth},
        "font-mono": {"$value": f["mono"], "$type": "fontFamily", "$description": "Telemetry and code font family", "authority": default_auth},
    }

    motion_tokens: Dict[str, Any] = {
        "duration-fast": {"$value": m.get("duration_fast", "80ms"), "$type": "duration", "$description": "Fast tactile duration", "authority": default_auth},
        "duration-normal": {"$value": m.get("duration_normal", "180ms"), "$type": "duration", "$description": "Normal transition duration", "authority": default_auth},
        "ease-hud": {"$value": m.get("ease_hud", "cubic-bezier(0.16, 1, 0.3, 1)"), "$type": "cubicBezier", "$description": "HUD snappy curve", "authority": default_auth},
    }

    # Structured 3-Tier Organization
    primitives = {
        "color": color_tokens,
        "spacing": spacing_tokens,
        "radius": radius_tokens,
        "typography": typography_tokens,
        "motion": motion_tokens,
    }

    semantics = {
        "surface": {
            "base": {"$value": "{primitives.color.surface.$value}", "$type": "color", "$description": "Base canvas and container surface", "authority": default_auth},
            "elevated": {"$value": "{primitives.color.surface-raised.$value}", "$type": "color", "$description": "Elevated modal, sheet, or popover", "authority": default_auth},
            "sunken": {"$value": "{primitives.color.bg-base.$value}", "$type": "color", "$description": "Sunken instrument well or canvas backdrop", "authority": default_auth},
        },
        "text": {
            "primary": {"$value": "{primitives.color.text-primary.$value}", "$type": "color", "$description": "Primary high-contrast typography", "authority": default_auth},
            "secondary": {"$value": "{primitives.color.text-secondary.$value}", "$type": "color", "$description": "Supplementary metadata and labels", "authority": default_auth},
            "muted": {"$value": "{primitives.color.text-tertiary.$value}", "$type": "color", "$description": "De-emphasized or disabled controls", "authority": default_auth},
        },
        "action": {
            "primary": {"$value": "{primitives.color.primary.$value}", "$type": "color", "$description": "Primary action trigger", "authority": default_auth},
            "primary-hover": {"$value": "{primitives.color.primary-hover.$value}", "$type": "color", "$description": "Primary hover state", "authority": default_auth},
        },
        "status": {
            "nominal": {"$value": "{primitives.color.status-running.$value}", "$type": "color", "$description": "Nominal operational state", "authority": default_auth},
            "warning": {"$value": "{primitives.color.status-warning.$value}", "$type": "color", "$description": "Warning state or capacity threshold", "authority": default_auth},
            "danger": {"$value": "{primitives.color.status-danger.$value}", "$type": "color", "$description": "Critical failure or alert", "authority": default_auth},
        }
    }

    components = {
        "input": {
            "bg": {"$value": "{primitives.color.bg-base.$value}", "$type": "color", "$description": "Input field background", "authority": default_auth},
            "border": {"$value": "{primitives.color.border.$value}", "$type": "color", "$description": "Input field boundary", "authority": default_auth},
            "focus": {"$value": "{primitives.color.primary.$value}", "$type": "color", "$description": "Input focus ring color", "authority": default_auth},
        },
        "card": {
            "bg": {"$value": "{primitives.color.surface.$value}", "$type": "color", "$description": "Card surface background", "authority": default_auth},
            "border": {"$value": "{primitives.color.border.$value}", "$type": "color", "$description": "Card boundary", "authority": default_auth},
        },
        "table": {
            "row-hover": {"$value": "{primitives.color.surface-raised.$value}", "$type": "color", "$description": "Table row hover highlight", "authority": default_auth},
            "border": {"$value": "{primitives.color.border-dim.$value}", "$type": "color", "$description": "Table divider hairline", "authority": default_auth},
        }
    }

    return {
        "$schema": "https://design-tokens.github.io/community-group/format/v1.0.0/schema.json",
        "$description": "Machine-compiled 3-Tier DTCG token specification with authority provenance.",
        "primitives": primitives,
        "semantics": semantics,
        "components": components,
        # Backward-compatible flat groups for legacy export tools
        "color": color_tokens,
        "spacing": spacing_tokens,
        "radius": radius_tokens,
        "typography": typography_tokens,
        "motion": motion_tokens,
    }


def generate_markdown(tokens: Dict[str, Any], foundation_rev: str = "f1", tokens_rev: str = "t1") -> str:
    """Render canonical Markdown token contract matching handoff.py and export-tokens.py specifications."""
    c = tokens["colors"]
    s = tokens["space"]
    r = tokens["radii"]
    f = tokens["fonts"]

    lines = [
        "# Design Tokens",
        "",
        "## Identity",
        f"- Foundation revision: {foundation_rev}",
        f"- Tokens revision: {tokens_rev}",
        "- Status: frozen",
        "- Generated at: machine-compiled from 5-dials",
        "",
        "## Breakpoints",
        "| Token | Value | Usage |",
        "|---|---|---|",
        "| `--bp-mobile` | 390px | Mobile viewport breakpoint |",
        "| `--bp-tablet` | 768px | Tablet viewport breakpoint |",
        "| `--bp-desktop` | 1280px | Desktop workbench default |",
        "",
        "## Color",
        "| Token | Value | Usage |",
        "|---|---|---|",
        f"| `--color-bg-void` | {c['bg_void']} | Deepest atmospheric void |",
        f"| `--color-bg-base` | {c['bg_base']} | App foundation background |",
        f"| `--color-bg-surface` | {c['bg_surface']} | Card and workbench panel surface |",
        f"| `--color-bg-surface-raised` | {c['bg_surface_raised']} | Elevated dropdown / popover |",
        f"| `--color-border-dim` | {c['border_dim']} | Subtle dividing border |",
        f"| `--color-border-subtle` | {c['border_subtle']} | Standard component boundary |",
        f"| `--color-border-bright` | {c['border_bright']} | Focused or active boundary |",
        f"| `--color-text-primary` | {c['text_primary']} | Primary high-contrast typography |",
        f"| `--color-text-secondary` | {c['text_secondary']} | Secondary context / telemetry label |",
        f"| `--color-accent-primary` | {c['accent_primary']} | Signature interactive accent |",
        f"| `--color-status-running` | {c['status_running']} | Active operational state |",
        f"| `--color-status-warning` | {c['status_warning']} | Warning / capacity threshold |",
        f"| `--color-status-danger` | {c['status_danger']} | Critical failure / thermal error |",
        "",
        "## Spacing",
        "| Token | Value | Usage |",
        "|---|---|---|",
    ]
    for k, v in sorted(s.items()):
        lines.append(f"| `--space-{k}` | {v} | Spacing unit {k} |")

    lines.extend([
        "",
        "## Radius",
        "| Token | Value | Usage |",
        "|---|---|---|",
        f"| `--radius-outer` | {r['outer']} | Outer container boundary |",
        f"| `--radius-inner` | {r['inner']} | Concentric inner child boundary |",
        f"| `--radius-card` | {r['card']} | Card entity radius |",
        f"| `--radius-btn` | {r['btn']} | Interactive control radius |",
        f"| `--radius-pill` | {r['pill']} | Status badge pill radius |",
        "",
        "## Typography",
        "| Token | Value | Usage |",
        "|---|---|---|",
        f"| `--font-sans` | {f['sans']} | Primary UI font family |",
        f"| `--font-mono` | {f['mono']} | Telemetry and code font family |",
        "",
    ])
    return "\n".join(lines)


def compile_tokens(
    discussion_path: str,
    output_css_path: str,
    output_json_path: str | None = None,
    output_md_path: str | None = None,
) -> None:
    disc_p = Path(discussion_path)
    disc_text = disc_p.read_text(encoding="utf-8") if disc_p.is_file() else ""
    dials = parse_5dials(disc_text)

    # Dynamic LLM chromatic derivation: extracts authored tokens, palette alias, or derives mathematically
    dynamic_colors = extract_dynamic_palette(disc_text)
    computed = compute_tokens(dials, dynamic_colors)

    has_confirmed = "## Confirmed Decisions" in disc_text or any(
        k in disc_text for k in ("--color-primary", "--accent-primary", "--bg-surface")
    )
    computed["authority"] = "explicit_human" if has_confirmed else "derived"

    # Perform WCAG AAA/AA relative luminance pre-flight diagnostics
    c = computed["colors"]
    c_ratio = check_wcag_contrast(c["text_primary"], c["bg_surface"])
    c_ratio_void = check_wcag_contrast(c["text_primary"], c["bg_void"])
    if c_ratio < 7.0:
        print(f"[TOKEN COMPILER WARNING] text_primary/bg_surface contrast ratio {c_ratio:.2f}:1 is below WCAG AAA (7.0:1)")
    if c_ratio_void < 7.0:
        print(f"[TOKEN COMPILER WARNING] text_primary/bg_void contrast ratio {c_ratio_void:.2f}:1 is below WCAG AAA (7.0:1)")

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

    if output_md_path:
        out_md = Path(output_md_path)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        md_content = generate_markdown(computed)
        out_md.write_text(md_content, encoding="utf-8")
        print(f"[TOKEN COMPILER] Successfully compiled Token Markdown contract to {out_md}")


def reconcile_tokens_from_css(
    css_path: str,
    discussion_path: str,
    json_path: str | None = None,
    md_path: str | None = None,
) -> None:
    """Read review modifications from tokens.css and reconcile back into discussion.md and t1 contracts."""
    css_p = Path(css_path)
    disc_p = Path(discussion_path)
    if not css_p.is_file():
        print(f"[RECONCILE] Error: CSS file not found: {css_path}")
        return
    if not disc_p.is_file():
        print(f"[RECONCILE] Error: Discussion file not found: {discussion_path}")
        return

    css_text = css_p.read_text(encoding="utf-8")
    var_matches = re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", css_text)
    if not var_matches:
        print("[RECONCILE] No CSS variables found to reconcile.")
        return

    reconciled_vars = {k.strip(): v.strip() for k, v in var_matches}
    disc_text = disc_p.read_text(encoding="utf-8")

    reconcile_lines = [
        "\n\n## Confirmed Decisions (Reconciled from Review tokens.css)",
        f"- Reconciled from: `{css_path}`",
    ]
    for k, v in sorted(reconciled_vars.items()):
        if any(c in k for c in ("color", "accent", "bg-", "border-", "text-", "status-", "radius-", "font-", "motion-", "space-")):
            reconcile_lines.append(f"- {k}: {v}")

    reconcile_block = "\n".join(reconcile_lines) + "\n"
    if "## Confirmed Decisions (Reconciled from Review tokens.css)" in disc_text:
        disc_text = re.sub(
            r"## Confirmed Decisions \(Reconciled from Review tokens\.css\).*?(?=\n## |\Z)",
            reconcile_block.strip() + "\n",
            disc_text,
            flags=re.DOTALL,
        )
    else:
        disc_text = disc_text.rstrip() + reconcile_block

    disc_p.write_text(disc_text, encoding="utf-8")
    print(f"[RECONCILE] Successfully synced review tokens back into {disc_p}")

    compile_tokens(str(disc_p), str(css_p), json_path, md_path)


def main():
    parser = argparse.ArgumentParser(description="Compile DTCG tokens from Stage 1 5-dial state machine.")
    parser.add_argument("--discussion", default="prototype/discussion.md", help="Path to discussion.md")
    parser.add_argument("--output-css", default="prototype/shared/tokens.css", help="Target CSS file")
    parser.add_argument("--output-json", default="prototype/contracts/tokens/t1.json", help="Target DTCG JSON file")
    parser.add_argument("--output-md", default="prototype/contracts/tokens/t1.md", help="Target Markdown contract file")
    parser.add_argument("--reconcile-from-css", help="Reconcile human review edits from tokens.css back into discussion.md and contracts")
    args = parser.parse_args()

    if args.reconcile_from_css:
        reconcile_tokens_from_css(args.reconcile_from_css, args.discussion, args.output_json, args.output_md)
        return

    compile_tokens(args.discussion, args.output_css, args.output_json, args.output_md)


if __name__ == "__main__":
    main()
