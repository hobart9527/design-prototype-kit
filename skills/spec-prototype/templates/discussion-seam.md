# Design discussion (resume seam)

Layered layout only. This file holds no design content: it is the checkpoint that lets a
truncated session resume, and it points at the three records that do. Decisions and
authority rows live in `prototype/truth.md`; tokens live in `prototype/world.md`.

## Resume

- Execution boundary: active
- Route basis (`visual-first | IA-first | IA-only | visual-only | spec-only | review-only | continuation | local-repair`), with source:
- Requested scope and stopping point:
- Active slice and its brief: `prototype/briefs/<slice_id>.md`
- Product truth / visual world status: `prototype/truth.md`, `prototype/world.md`
- Current prototype, captures and evidence links:
- Pending prerequisite (`none | needs_decision | needs_evidence | blocked`), impact and owner:
- Next action and its prerequisite:
- Stage checkpoint (`stage1-contract | stage2-probe | stage3-skeleton | stage4-audit | stage5-freeze`), completed in this turn:

A checkpoint is a recovery note, not a stop signal: keep working while authorized scope and
evidence remain, and write this block once per authoring pass. Stop only for an unresolved
user decision, a real stage boundary awaiting review, or an explicit session limit. The
Turn 1→2 seam of the 3-turn route is such a boundary: once the design record and this block
are written, end the turn instead of starting the anchor. Restate decision status verbatim
(`proposed`/`provisional`); never upgrade it to `confirmed` here.
