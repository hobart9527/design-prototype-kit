#!/usr/bin/env python3
"""Authority fidelity: an action may only claim the authority its record supports.

The compiler reads an authored `authority:` marker on each `contract:actions`
entry and refuses an unknown level. That stops an *unmarked* mechanism from
being promoted to `explicit`, but it cannot tell whether a *marked* `explicit`
is true: a discussion that writes `authority: explicit` on a mechanism the user
never chose is still an authority promotion, and it is the exact defect that
made a derived lifecycle mechanism read as a user-confirmed fact.

This module closes that half. `explicit` is a claim about provenance, so it is
checked against the provenance record the discussion is required to keep — the
`## Decisions and authority` table. An action claiming `explicit` must be backed
by a row that both names the action and carries a user source of `confirmed` or
`delegated` with a settled status. A row whose `User source` is
`synthetic-fixture` carries zero human authority, so it cannot back an
`explicit` claim.

No join is invented where none exists: an action id that appears in no decision
row is a failure with the action named, never a silent pass.
"""
from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Sequence

# Authority levels that assert the user stated the mechanism. The rest
# (`derived`, `proposed`, `hypothesis`) are the designer's own work and need no
# provenance row.
ASSERTED_LEVELS = ("explicit",)

# `User source` column values that carry human authority. A synthetic fixture
# actor is a benchmark artefact, not a person, so it is deliberately absent.
AUTHORITATIVE_SOURCES = ("confirmed", "delegated")

# Status column values that record an actual decision rather than an open one.
SETTLED_STATUSES = ("confirmed", "delegated")

_DECISIONS_HEADING = re.compile(
    r"^#{1,6}\s+.*(?:Decisions\s+and\s+authority|决策与授权|Decisions?\b)",
    re.IGNORECASE | re.MULTILINE,
)
_HEADING = re.compile(r"^#{1,6}\s+", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\s*\|(.+)\|\s*$")
# A cell boundary is an unescaped pipe: the template's `User source` header
# spells its enum as `confirmed \| delegated \| synthetic-fixture`, and a naive
# split on every pipe makes that header one cell longer than every data row,
# which would silently skip the whole table.
_CELL_SPLIT = re.compile(r"(?<!\\)\|")
_SEPARATOR_CELL = re.compile(r"^:?-{2,}:?$")


def _decisions_section(text: str) -> str:
    """The Decisions-and-authority section body, or the whole text when absent.

    Returning the whole text on a missing heading is deliberate: a discussion
    that keeps no provenance table has no rows, so every asserted authority
    fails. Slicing to nothing would make an absent table look like an absent
    claim instead.
    """
    start = _DECISIONS_HEADING.search(text)
    if not start:
        return text
    rest = text[start.end():]
    nxt = _HEADING.search(rest)
    return rest[: nxt.start()] if nxt else rest


def parse_decision_rows(text: str) -> List[Dict[str, str]]:
    """Rows of the Decisions-and-authority table as dicts keyed by column name.

    Header cells are matched by keyword rather than position so a reordered or
    extended table still parses. A row whose cell count does not match the
    header is skipped: a malformed row is not evidence of anything.
    """
    section = _decisions_section(text)
    rows: List[Dict[str, str]] = []
    header: List[str] | None = None
    for line in section.splitlines():
        m = _TABLE_ROW.match(line)
        if not m:
            continue
        cells = [c.strip() for c in _CELL_SPLIT.split(m.group(1))]
        if all(_SEPARATOR_CELL.match(c) or not c for c in cells):
            continue
        if header is None:
            header = [c.strip().strip("`").lower() for c in cells]
            continue
        if len(cells) != len(header):
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def _column(row: Dict[str, str], *keywords: str) -> str:
    """The first cell whose column name contains any keyword, else ''."""
    for name, value in row.items():
        if any(k in name for k in keywords):
            return value
    return ""


def _normalise(value: str) -> str:
    """A table cell reduced to its bare token: backticks, emphasis and the
    escaped pipe of the template header all stripped."""
    return value.strip().strip("`*_ ").replace("\\|", "|").split("|")[0].strip().lower()


def _action_keys(action: Dict[str, Any]) -> List[str]:
    """Strings that identify an action in a decision row.

    The id is the canonical key, but the discussion is authored prose: an author
    who records the decision writes the verb or the commit far more often than
    the machine id. All three are accepted so a recorded decision is not read as
    a missing one.
    """
    keys = []
    for field in ("id", "verb", "commit_action"):
        value = str(action.get(field) or "").strip()
        if len(value) >= 2:
            keys.append(value)
    return keys


def check_action_authority(
    actions: Iterable[Dict[str, Any]], discussion_text: str
) -> List[str]:
    """Failures for actions asserting an authority the discussion cannot back.

    One failure per unsupported action, naming the action and the reason, so the
    repair is unambiguous: either drop the action's `authority` back to the
    level its evidence supports, or record the user decision that raised it.
    """
    rows = parse_decision_rows(discussion_text)
    failures: List[str] = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        level = str(action.get("authority") or "").strip().lower()
        if level not in ASSERTED_LEVELS:
            continue
        keys = _action_keys(action)
        aid = str(action.get("id") or "").strip()
        if not aid:
            failures.append(
                "authority-fidelity assertion: an action claims "
                f"authority={level} but carries no id, so the claim cannot be "
                "checked against the discussion record"
            )
            continue
        backing = [r for r in rows if any(k in " ".join(r.values()) for k in keys)]
        if not backing:
            failures.append(
                f"authority-fidelity assertion: {aid} claims authority={level} "
                "(the user stated it) but no row in the Decisions and authority "
                "table names it; record the user decision or set the action's "
                "authored authority to the level its evidence supports"
            )
            continue
        supported = [
            r for r in backing
            if _normalise(_column(r, "user source", "来源")) in AUTHORITATIVE_SOURCES
            and _normalise(_column(r, "status", "状态")) in SETTLED_STATUSES
        ]
        if supported:
            continue
        sources = sorted({
            _normalise(_column(r, "user source", "来源")) or "unrecorded"
            for r in backing
        })
        failures.append(
            f"authority-fidelity assertion: {aid} claims authority={level} but "
            f"its decision row(s) record User source={sources}, which is not one "
            f"of {list(AUTHORITATIVE_SOURCES)}; a mechanism the user never chose "
            "carries derived/proposed authority, and a synthetic-fixture actor "
            "carries none"
        )
    return failures


def main(argv: Sequence[str] | None = None) -> int:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(
        description="Check that action authority claims are backed by the discussion record"
    )
    parser.add_argument("--ir", required=True, help="Compiled Spec IR JSON (r1.spec.json)")
    parser.add_argument("--discussion", required=True, help="discussion.md to read the decisions from")
    args = parser.parse_args(argv)

    ir = json.loads(Path(args.ir).read_text(encoding="utf-8"))
    text = Path(args.discussion).read_text(encoding="utf-8")
    failures = check_action_authority(ir.get("actions") or [], text)
    for i, failure in enumerate(failures, 1):
        print(f"  [{i}] {failure}")
    print("AUTHORITY: " + ("pass" if not failures else "fail"))
    return 0 if not failures else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
