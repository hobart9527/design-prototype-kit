# Stage 5: Silent Governance & Frozen Approved Delivery (冻 - 根)

Answer one question: *"How is the validated design frozen into an immutable,
downstream-consumable artifact set?"* Stage 5 is headless compilation of durable
specifications, design tokens, and verifiable asset digests for engineering
handoff.

## Pre-freeze Self-Check Checklist (前置自检清单 · 缺一不可)

在执行 Stage 5 freeze 之前，必须满足以下前置条件（任一失败将导致 freeze 拒绝并阻断下游）：
1. **状态模型完整**：`contract:states`, `contract:required_states`, `contract:actions`, `contract:invariants` 已完整声明（修复：补齐 slice brief 或 discussion 对应块）。
2. **决策授权有效**：Decisions 表包含当前 slice 的 `confirmed | delegated` 行。freeze 实际要求该行同时包含来源标记（如 `用户明确批准`、`explicit approval`、`delegated authority`；完整清单见 `handoff.py` 顶部 `APPROVAL_SOURCE_MARKERS` 常量）、定位标记（如 `turn` / `轮`、`date` / `日期`、`quote` / `原话`）、不含 `planned` / `will approve` 等禁用词，并在该行含精确 `slice_id`。缺项时按提示在 `truth.md` 或 `discussion.md` 补齐。
3. **Token 已编译**：执行下文 Pipeline 第 2 步后，`prototype/shared/tokens.css` 与 `prototype/contracts/tokens/t1.json` 同时存在（`compile_tokens.py` 是二者唯一写入者；手改 `tokens.css` 会触发 `out_of_sync`）。
4. **对比度与质量门由 freeze 自带执行**：非 spec-only 的 freeze 会先运行 `wcag-check.js` 与 `verify_prototype_quality.py`。任一失败（退出码非 0 且非降级）即拒绝 freeze；verify 退出码 2（渲染探针未运行）记为 `degraded` 写入 freeze-manifest 的 `preflight`，不等同通过。提前自跑同样命令可更早发现问题。

Stage 5 本身可选：仅在用户要求冻结或下游交付时执行；一旦要求下游交付，则它是唯一准入路径。

注意：命令必须在仓库根目录执行，`--root .` 即该根（边界 hook 不放行含 `$` 的命令，故不写 `$PWD`）；freeze 预检子进程以 `--root` 解析后的绝对路径运行，不受 cwd 影响。

## Headless Pipeline Execution

1. **Spec Compilation from Validated Design**:
   `python3 skills/spec-prototype/scripts/compile_spec_ir.py --slice <slice_id> --required-tier execution_spec`
   compiles the human decision record into the canonical machine IR (`r1.spec.json`)
   and RFC specification view (`r1.spec.md`). Freeze is the handoff, so a missing
   state model or verification scope fails hard here rather than being invented or
   left empty; the prototype stages before it never needed the Spec to exist.
   `--allow-incomplete` is a debugging bypass, never part of a delivery.
2. **DTCG Token Compilation**:
   `python3 skills/spec-prototype/scripts/compile_tokens.py` (default
   `--output-json prototype/contracts/tokens/t1.json`) compiles the authored token
   declarations in the design record into **both** the physical
   `shared/tokens.css` and a W3C DTCG `tokens.json` in one pass. It does not read
   `tokens.css` back: the flow is one-way (record → css + json), and the
   compiled output carries the flat `color` group that the contrast preflight
   consumes. On a single-record tree the source is `prototype/discussion.md`
   (the default `--discussion`); on a layered tree pass `--discussion
   prototype/world.md` so the token authority is the visual-world file.
   *Token flow discipline*: The design record (`world.md` or `discussion.md`) is the only token source at every stage. Record exploratory adjustments there and rerun `compile_tokens.py`; Stage 5 freezes the compiled outputs and makes no further source writebacks, preserving upstream SHA-256 seal integrity.
   **Do not substitute a Markdown-table token export for this step.** A re-export
   that groups tokens by CSS custom-property prefix omits the flat `color` group,
   so `wcag-check.js` reads no measurable set and exits non-zero with an explicit
   error (`skipped` names any token it could not resolve) — a refused preflight,
   not a false pass. `compile_tokens.py` is the only writer of the Stage 5
   preflight target. A missing token source is likewise refused: the compiler
   fails hard instead of emitting a neutral scaffold for a path that does not
   exist.
3. **WCAG static preflight**:
   `node skills/spec-prototype/scripts/wcag-check.js prototype/contracts/tokens/t1.json --level AA`
   checks critical text and figures against **WCAG 2.2 AA (4.5:1)**; long-reading
   and key data text should pursue **WCAG AAA (7:1)**. This is a static contrast
   preflight only — it does not replace full runtime accessibility review
   (keyboard focus management, screen-reader landmarks, reachable touch targets).
4. **SHA-256 asset identity binding / freeze**:

   `python3 skills/spec-prototype/scripts/handoff.py freeze --root . --spec prototype/specifications/<slice_id>/r1.spec.md`

   `--root` must point to the repository root (the directory containing `prototype/`), not to `prototype/` itself. The freeze command takes the Specification as its subject, computes SHA-256 fingerprints of every retained artifact, and writes the immutable freeze manifest to `prototype/evidence/<slice_id>/<candidate_id>/freeze-manifest.json`. `prototype/discussion.md` is the evolvable decision record and is never a freeze subject.

## Authority State

Delivery reaches `Frozen Approved` only here. This is the sole admission state for
downstream frontend engineering delivery (Loom Entry 2). See the full
authority-to-artifact lifecycle mapping and the artifact state
rules in [`../04-governance/artifact-lifecycle.md`](../04-governance/artifact-lifecycle.md).

## Manifest Discipline

- Every manifest entry binds a concrete artifact path to its digest; an artifact
  whose content changes after freeze invalidates its fingerprint and requires a
  new freeze rather than an in-place edit.
- The manifest is a durable delivery record, not a claim of completion; evidence
  lineage stays transparently recorded alongside it.

## Exit

Legal exit is the frozen manifest plus the DTCG token artifact set, ready for
`spec-prototype` handoff per [`../04-governance/handoff.md`](../04-governance/handoff.md).
