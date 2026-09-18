#!/usr/bin/env python3
"""Export a frozen spec-prototype tokens.md into W3C Design Tokens format (DTCG).

Zero-dependency stdlib script.
Usage: python3 export-tokens.py <path/to/tokens.md> [--output tokens.json]
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile
from typing import Any


SECTION_TYPE_MAP = {
    "color": "color",
    "spacing": "dimension",
    "radius": "dimension",
    "shadow / elevation": "shadow",
    "shadow": "shadow",
    "elevation": "shadow",
    "breakpoints": "dimension",
}


def parse_tokens_markdown(content: str) -> dict[str, Any]:
    tokens: dict[str, Any] = {
        "$schema": "https://design-tokens.github.io/community-group/format/v1.0.0/schema.json",
    }

    # Extract metadata from identity section if present
    identity_match = re.search(r"##\s+Identity\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if identity_match:
        meta: dict[str, str] = {}
        for line in identity_match.group(1).splitlines():
            m = re.match(r"^-\s*([^:]+):\s*(.*)$", line.strip())
            if m:
                meta[m.group(1).strip()] = m.group(2).strip()
        if meta:
            tokens["$description"] = (
                f"Generated from Foundation {meta.get('Foundation revision', 'draft')} "
                f"at {meta.get('Generated at', 'unspecified')}"
            )

    sections = re.split(r"^##\s+(.+)$", content, flags=re.MULTILINE)
    for i in range(1, len(sections), 2):
        title = sections[i].strip()
        title_lower = title.lower()
        if title_lower in ("identity", "export", "verifiable assertion anchors"):
            continue

        body = sections[i + 1]
        # Group name in DTCG
        group_name = title_lower.split("/")[0].strip()
        if group_name == "shadow":
            group_name = "elevation"

        group_tokens: dict[str, Any] = {}
        default_type = SECTION_TYPE_MAP.get(title_lower, "other")

        # Match table rows line by line: | Token | Value | Usage | or | Token | Value |
        rows = []
        for line in body.splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            cells = [c.strip() for c in line.split("|")]
            if cells and cells[0] == "":
                cells = cells[1:]
            if cells and cells[-1] == "":
                cells = cells[:-1]
            if len(cells) < 2:
                continue
            token_cell = cells[0].strip("` ")
            if not token_cell.startswith("--") or set(token_cell) <= {"-", " "}:
                continue
            val_cell = cells[1].strip()
            usage_cell = cells[2].strip() if len(cells) > 2 else ""
            rows.append((token_cell, val_cell, usage_cell))

        for raw_token, raw_value, raw_usage in rows:
            name = raw_token.strip().lstrip("-")
            # Strip group prefix if redundant: e.g. color-primary -> primary
            prefix = f"{group_name}-"
            if name.startswith(prefix):
                name = name[len(prefix):]
            elif group_name == "breakpoints" and name.startswith("bp-"):
                name = name[3:]
            elif group_name == "spacing" and name.startswith("space-"):
                name = name[6:]

            val = raw_value.strip().strip("`")
            usage = raw_usage.strip()

            # Skip header or empty placeholder values
            if not val or val.lower() in ("value", "---", "--"):
                continue

            # Infer specific type for typography and motion
            token_type = default_type
            if group_name == "typography":
                if name.startswith("font-") or "font" in name:
                    token_type = "fontFamily"
                elif name.startswith("tracking-"):
                    token_type = "dimension"
                else:
                    token_type = "typography"
            elif group_name == "motion":
                if name.startswith("duration-") or "duration" in name:
                    token_type = "duration"
                elif name.startswith("ease-"):
                    token_type = "cubicBezier"
                elif name.startswith("spring-"):
                    token_type = "transition"

            token_obj: dict[str, Any] = {
                "$value": val,
                "$type": token_type,
                "authority": "frozen_spec",
            }
            if usage:
                token_obj["$description"] = usage

            group_tokens[name] = token_obj

        if group_tokens:
            tokens[group_name] = group_tokens

    return tokens


def parse_tokens_css(content: str) -> dict[str, Any]:
    tokens: dict[str, Any] = {
        "$schema": "https://design-tokens.github.io/community-group/format/v1.0.0/schema.json",
    }
    # Match --name: value;
    matches = re.findall(r"(--[a-zA-Z0-9_-]+)\s*:\s*([^;]+);", content)
    for raw_name, raw_val in matches:
        var_name = raw_name.strip().lstrip("-")
        val = raw_val.strip()
        # Classify group by prefix
        parts = var_name.split("-", 1)
        group_name = parts[0]
        sub_name = parts[1] if len(parts) > 1 else var_name
        token_type = SECTION_TYPE_MAP.get(group_name, "other")
        if group_name == "color":
            token_type = "color"
        elif group_name in ("space", "spacing", "bp", "radius"):
            token_type = "dimension"
        elif group_name == "motion" or group_name in ("duration", "ease"):
            if "ease" in var_name:
                token_type = "cubicBezier"
            elif "duration" in var_name:
                token_type = "duration"
            else:
                token_type = "transition"

        if group_name not in tokens:
            tokens[group_name] = {}
        tokens[group_name][sub_name] = {
            "$value": val,
            "$type": token_type,
        }
    return tokens


def main() -> int:
    parser = argparse.ArgumentParser(description="Export tokens.md or tokens.css to W3C DTCG format.")
    parser.add_argument("tokens_file", type=Path, help="Path to tokens.md or tokens.css")
    parser.add_argument("--output", "-o", type=Path, help="Destination JSON file (default: stdout)")
    args = parser.parse_args()

    if not args.tokens_file.is_file():
        sys.stderr.write(f"Error: tokens file not found: {args.tokens_file}\n")
        return 1

    try:
        content = args.tokens_file.read_text(encoding="utf-8")
        if args.tokens_file.suffix.lower() == ".css":
            tokens = parse_tokens_css(content)
        else:
            tokens = parse_tokens_markdown(content)
        formatted = json.dumps(tokens, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            if args.output.suffix != '.json' or args.output.is_symlink():
                raise ValueError('Export requires a regular .json destination.')
            args.output.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(dir=args.output.parent, delete=False) as temporary:
                temporary_path = Path(temporary.name)
            try:
                temporary_path.write_text(formatted, encoding='utf-8')
                try:
                    os.link(temporary_path, args.output)
                except FileExistsError:
                    if args.output.is_symlink() or args.output.read_bytes() != formatted.encode('utf-8'):
                        raise ValueError('Existing export differs; use a successor revision.')
            finally:
                temporary_path.unlink()
        else:
            sys.stdout.write(formatted)
    except (OSError, ValueError) as error:
        sys.stderr.write(f'Error: {error}\n')
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
