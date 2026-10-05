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

from spec_contract_blocks import parse_decision_table

# Authority levels that assert the user stated the mechanism. The rest
# (`derived`, `proposed`, `hypothesis`) are the designer's own work and need no
# provenance row.
ASSERTED_LEVELS = ("explicit",)

# `User source` column values that carry human authority. A synthetic fixture
# actor is a benchmark artefact, not a person, so it is deliberately absent.
AUTHORITATIVE_SOURCES = ("confirmed", "delegated")

# Status column values that record an actual decision rather than an open one.
SETTLED_STATUSES = ("confirmed", "delegated")


def parse_decision_rows(text: str) -> List[Dict[str, str]]:
    """Rows of the Decisions-and-authority table as dicts keyed by column name.

    Header cells are matched by keyword rather than position so a reordered or
    extended table still parses.
    """
    return [dict(row) for row in parse_decision_table(text)]


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
        def _matches(row: dict) -> bool:
            row_text = " ".join(row.values())
            for k in keys:
                # Use word-boundary regex if key is alphanumeric/ascii
                if re.search(r"(?i)(?<![a-zA-Z0-9_-])" + re.escape(k) + r"(?![a-zA-Z0-9_-])", row_text):
                    return True
            return False

        backing = [r for r in rows if _matches(r)]
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


def advisory_label_signals(discussion_text: str) -> List[str]:
    """Advisory-only signals for decision rows whose label outruns their evidence.

    These never fail a gate: a `confirmed`/`delegated` row with no recorded user
    quote or locator, or a settled row whose `User source` is not authoritative,
    is reported so the author can downgrade the label to `proposed` or
    `hypothesis` before the freeze check refuses it.
    """
    signals: List[str] = []
    for row in parse_decision_rows(discussion_text):
        status = _normalise(_column(row, "status", "状态"))
        if status not in SETTLED_STATUSES:
            continue
        rid = _column(row, "id") or "(row without id)"
        quote = _column(row, "quote", "locator", "引用").strip(" `-")
        source = _normalise(_column(row, "user source", "来源"))
        if not quote:
            signals.append(f"{rid}: status={status} but no user quote/locator recorded")
        if source not in AUTHORITATIVE_SOURCES:
            signals.append(f"{rid}: status={status} but User source={source or 'unrecorded'}")
    return signals


# r40 A2: the literal carry-forward phrase that promoted unchosen decisions to an
# approval. Any form of it is a hard failure, not a signal.
_APPROVALS_PRESERVED_RE = re.compile(r"approvals?\s+preserved", re.IGNORECASE)

# r40 A1: a user `confirmed`/`delegated` status requires in-session evidence of the
# user's own choice. A designer-authored rationale, a benchmark fixture actor, or a
# restatement of the brief is not a selection.
_USER_CHOICE_EVIDENCE_RE = re.compile(
    r"user\s*(?:message|selected|chose|confirmed|approved|locked)|"
    r"用户(?:确认|选择|批准|锁定)|in[- ]session|turn\s*\d+|choice_taken",
    re.IGNORECASE,
)


def check_decision_promotions(discussion_text: str) -> List[str]:
    """Hard failures for decision rows that promote themselves past their evidence.

    Two classes, both from r40:
    - A1: status `confirmed`/`delegated` with no in-session user-choice evidence in
      the row (quote, locator, or user-source). The mechanism parameters a designer
      derives stay `derived`/`provisional`; only the user's stated intent may settle.
    - A2: the literal `approvals preserved` carry-forward, which asserts unchosen
      decisions are approved. The honest form is `unaffected provisional decisions
      carried forward`.
    Returns a list of failure strings; empty means the table is honest.
    """
    failures: List[str] = []
    if _APPROVALS_PRESERVED_RE.search(discussion_text):
        failures.append(
            "authority assertion: `approvals preserved` promotes unchosen decisions to "
            "approval; record `unaffected provisional decisions carried forward` instead"
        )
    for row in parse_decision_rows(discussion_text):
        status = _normalise(_column(row, "status", "状态"))
        if status not in SETTLED_STATUSES:
            continue
        rid = _column(row, "id") or "(row without id)"
        quote = _column(row, "quote", "locator", "引用")
        source = _column(row, "user source", "来源")
        evidence_blob = f"{quote} {source}"
        if not _USER_CHOICE_EVIDENCE_RE.search(evidence_blob):
            failures.append(
                f"{rid}: status={status} but no in-session user-choice evidence "
                "(quote/locator/user-source naming a user selection); a designer-derived "
                "mechanism stays `derived`/`provisional`, never `confirmed`"
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
    for signal in advisory_label_signals(text):
        print(f"  [advisory] {signal}")
    print("AUTHORITY: " + ("pass" if not failures else "fail"))
    return 0 if not failures else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
