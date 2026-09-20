# Baseline restore integrity

## Why

`ensure_baseline` still has two unguarded exits that `bench-skill-source-integrity`
did not close, both reachable with a baseline cache that is valid but whose
`MANIFEST.json` records an empty `hashes` map.

The guarded exit is `if not stale: require_complete_skill(...); return base`. When
`hashes` is empty, `divergences()` is unconditionally empty, so `stale` is empty
and a present-but-truncated cached tree is returned as a complete control arm
without any per-file hash being checked. The restore exit only calls
`require_complete_skill` in the branch that follows a divergent tree; an absent
tree restores from `git archive` and is returned with no integrity check at all.

Both exits exist to be complete, so an incomplete cached tree is accepted as the
`stable_skill` control. Measured against that control, a real regression can read
as an improvement.

A third defect sits on the same path: `divergences()` indexes `meta["sha256"]`
without validating the manifest entry, so a hash entry lacking `sha256` raises
`KeyError` instead of the documented `BenchBlocked` refusal.

## What changes

`divergences()` treats a manifest entry that is not a mapping carrying a string
`sha256` as a divergence naming that entry, so a malformed manifest is refused
with the existing `BenchBlocked` message instead of raising `KeyError`.

Both exits of `ensure_baseline` call `require_complete_skill` on the tree they
are about to return, so the cached tree and the freshly restored tree are held to
the same contract. The restore branch keeps the manifest divergences check as
well: the integrity contract proves the tree is shaped like a skill, the manifest
proves it is the frozen revision.

## Non-goals

- No new integrity contract and no change to `REQUIRED_SKILL_ENTRIES`.
- A tampered baseline is still rebuilt, never repaired in place.
- No change to the `candidate_skill` path, to `prepare_workspace` ordering, or to
  the `no_skill` exemption.
