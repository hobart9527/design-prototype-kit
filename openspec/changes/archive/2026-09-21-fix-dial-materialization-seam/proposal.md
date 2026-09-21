# Proposal: Project Authored Five Dials Accurately into Foundation f1

## Why

When Stage 1 materializes `discussion.md` into `f1.md`, Five Dials expressed in markdown tables (e.g. `Density: sparse. Energy: quiet.`) failed to be extracted by `extract_section_by_patterns` because it looks for section headers or line-leading items. This resulted in `unspecified` being written into `f1.md`, breaking formal five_axes compilation from `f1.md`.

## What Changes

Update `materialize_contracts.py` to extract individual dial values via precise keyword pattern `\b{dial}\b\s*[:=]\s*([a-zA-Z0-9_-]+)` before falling back to section extraction and `UNSPECIFIED`.
