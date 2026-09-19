#!/usr/bin/env python3
"""Check the minimal shape of a spec-prototype discussion record."""

from pathlib import Path
import re
import sys


REQUIRED_RESUME = (
    "Execution boundary:",
    "Active track / current decision:",
    "Route basis",
    "Requested scope and stopping point:",
    "Pending prerequisite",
    "Next action and its prerequisite:",
)
ROUTES = {
    "visual-first", "IA-first", "IA-only", "visual-only", "spec-only",
    "review-only", "continuation", "local-repair",
}
STATUSES = {"explicit", "derived", "unknown"}


def fail(message: str) -> int:
    print(f"discussion incomplete: {message}", file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) != 2:
        return fail("usage: check-discussion.py <repository-root>")
    record = Path(sys.argv[1]).resolve() / "prototype/discussion.md"
    if not record.is_file() or record.is_symlink():
        return fail("prototype/discussion.md must be a regular file")
    text = record.read_text(encoding="utf-8")
    if "## Resume" not in text:
        return fail("missing `## Resume`")
    resume = text.split("## Resume", 1)[1].split("\n## ", 1)[0]
    for field in REQUIRED_RESUME:
        if field not in resume:
            return fail(f"missing Resume field `{field}`")
    route_line = next((line for line in resume.splitlines() if "Route basis" in line), "")
    routes = set(re.findall(
        r"(?<![A-Za-z])(?:visual-first|IA-first|IA-only|visual-only|spec-only|"
        r"review-only|continuation|local-repair)(?![A-Za-z])",
        route_line,
    ))
    if not routes:
        return fail("Route basis has no recognized route")

    if "## Cold-start inference & seed status" in text:
        cold = text.split("## Cold-start inference & seed status", 1)[1].split("\n## ", 1)[0]
        has_unknown = False
        for dimension in ("Actor", "Use scene", "Information priority", "Main journey", "Style tone"):
            match = re.search(
                rf"- {re.escape(dimension)}:\s*`?\[?(explicit|derived|unknown)\]?`?",
                cold,
            )
            if not match or match.group(1) not in STATUSES:
                return fail(f"{dimension} needs explicit evidence status")
            has_unknown |= match.group(1) == "unknown"
        if "- Scene sentence:" not in cold:
            return fail("cold start needs a scene sentence")
        if "Anti-slop match-and-refuse bans:" not in cold:
            return fail("cold start needs anti-slop boundary status")
        if "Seed confirmation Gate:" not in cold:
            return fail("cold start needs seed gate status")
        if has_unknown and not re.search(
            r"- Unknowns that could change the current decision, impact and owner:\s*\S",
            cold,
        ):
            return fail("unknown cold-start dimensions need impact and owner")

    if "## Candidate propositions" in text:
        candidates_block = text.split("## Candidate propositions", 1)[1].split("\n## ", 1)[0]
        table_lines = [line.strip() for line in candidates_block.splitlines() if line.strip().startswith("|")]
        if len(table_lines) >= 2:
            header_cells = [c.strip().lower() for c in table_lines[0].split("|")[1:-1]]
            required_cols = {
                "focal": ("focal", "dominance"),
                "specimen": ("specimen", "content"),
                "tradeoff": ("trade-off", "tradeoff", "sacrificed"),
                "evidence": ("evidence", "probe"),
                "status": ("status",),
            }
            col_indices = {}
            for key, patterns in required_cols.items():
                for idx, cell in enumerate(header_cells):
                    if any(p in cell for p in patterns):
                        col_indices[key] = idx
                        break
            placeholder_re = re.compile(r"^(todo|tbd|n/a|-|\.+|\?+)$", re.IGNORECASE)
            for row_line in table_lines[2:]:
                cells = [c.strip() for c in row_line.split("|")[1:-1]]
                if not cells or not any(cells):
                    continue
                status_idx = col_indices.get("status")
                row_status = cells[status_idx].lower() if status_idx is not None and status_idx < len(cells) else ""
                if "proposed" in row_status or "confirmed" in row_status:
                    for req_key, idx in col_indices.items():
                        val = cells[idx] if idx < len(cells) else ""
                        if len(val) < 3 or placeholder_re.match(val):
                            return fail(f"candidate proposition missing valid {req_key}: `{val}`")
    print(f"discussion shape ok: {record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
