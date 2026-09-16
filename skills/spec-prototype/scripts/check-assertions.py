#!/usr/bin/env python3
"""Bind Foundation `required` assertions to falsifiable Prototype Evidence checks.

Deterministic post-build gate. It does not judge whether a check is wise; it rejects
the case seen in practice: a required assertion recorded `pass` by a check that could
not have failed for the asserted risk.

Usage:
    check-assertions.py --foundation <path> --evidence <path>

Exit 0 when every required assertion is present, resolved `pass`, and carries a check
anchor (backticked command/path, path with `/`, or a measured value with a unit).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED = "required"
RESULTS = ("pass", "fail", "unverified", "n/a")
ANCHOR = re.compile(
    r"(`[^`\s]+(?:\s+[^`\s]+)*`"       # backticked command, path or expression (non-trivial)
    r"|[\w.~-]*/[\w./-]+"             # path with a directory component
    r"|\d+(?:[.,]\d+)?\s*(?:px|%|s|ms|ch|em|rem|vw|vh|cqw|dvh|:1|CR|dE|ratio))",  # measured value with a unit
)


class CheckError(ValueError):
    pass


def cells(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_delimiter(row: list[str]) -> bool:
    return bool(row) and all(re.fullmatch(r":?-{2,}:?", cell.strip()) for cell in row)


def table_rows(text: str, header_contains: str) -> list[list[str]]:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if not line.strip().startswith("|"):
            continue
        header = [cell.lower() for cell in cells(line)]
        if not any(header_contains in cell for cell in header):
            continue
        rows: list[list[str]] = []
        for candidate in lines[index + 2:]:
            if not candidate.strip().startswith("|"):
                break
            row = cells(candidate)
            if is_delimiter(row):
                continue
            rows.append(row)
        return rows
    return []


def normalize(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def words(text: str) -> list[str]:
    return re.sub(r"\s+", " ", text.strip()).split()


def matches(assertion: str, candidate: str) -> bool:
    left, right = normalize(assertion), normalize(candidate)
    if not left or not right:
        return False
    return left == right or left in right or right in left


def required_assertions(foundation: str) -> list[str]:
    rows = table_rows(foundation, "required or exploratory")
    if not rows:
        raise CheckError("Foundation has no assertion table with a Required or exploratory column")
    result = []
    for row in rows:
        if len(row) < 5:
            continue
        if row[4].strip().strip("`").lower() == REQUIRED:
            result.append(row[0])
    return result


def evidence_rows(evidence: str) -> list[list[str]]:
    rows = table_rows(evidence, "exact trace/measurement")
    if not rows:
        raise CheckError("Evidence has no assertion table with an Exact trace/measurement column")
    return rows


def closure_rows(evidence: str) -> list[list[str]]:
    return table_rows(evidence, "source disposition")


def evaluate(foundation: str, evidence: str) -> list[str]:
    required = required_assertions(foundation)
    rows = evidence_rows(evidence)
    violations: list[str] = []
    for assertion in required:
        label = assertion if len(assertion) <= 72 else assertion[:69] + "..."
        found = [row for row in rows if row and matches(assertion, row[0])]
        if not found:
            violations.append(f"required assertion absent from evidence: {label}")
            continue
        row = found[0]
        if len(row) < 5:
            violations.append(f"required assertion has an incomplete row: {label}")
            continue
        observation, check, result = row[2], row[3], row[4].strip().strip("`").lower()
        if result not in RESULTS:
            violations.append(f"required assertion has an unsupported result: {label}")
            continue
        if result == "n/a":
            if len(words(observation)) < 3:
                violations.append(f"required assertion is n/a without a scope reason: {label}")
            continue
        if result in ("fail", "unverified"):
            violations.append(f"required assertion is not resolved ({result}): {label}")
            continue
        if not ANCHOR.search(check):
            violations.append(
                f"required assertion claims pass without a falsifiable check: {label}")

    # Evaluate reachable-control closure
    c_rows = closure_rows(evidence)
    for row in c_rows:
        if len(row) < 7:
            continue
        state, action, disp, result = row[0], row[1], row[2].strip().strip("`").lower(), row[6].strip().strip("`").lower()
        if disp == REQUIRED:
            branch_label = f"{state} -> {action}"
            if result not in RESULTS:
                violations.append(f"required reachable-control closure has an unsupported result: {branch_label}")
            elif result in ("fail", "unverified"):
                violations.append(f"required reachable-control closure is not resolved ({result}): {branch_label}")
            elif result == "n/a":
                obs = row[4] if len(row) > 4 else ""
                if len(words(obs)) < 3:
                    violations.append(f"required reachable-control closure is n/a without a scope reason: {branch_label}")

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--foundation", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    try:
        violations = evaluate(args.foundation.read_text(), args.evidence.read_text())
    except (CheckError, OSError, UnicodeError) as error:
        print(f"assertions_blocked: {error}", file=sys.stderr)
        return 1
    if violations:
        print("assertions_blocked:", file=sys.stderr)
        for violation in violations:
            print(f"  - {violation}", file=sys.stderr)
        return 1
    print("✓ Every required assertion is bound to a falsifiable check and resolved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
