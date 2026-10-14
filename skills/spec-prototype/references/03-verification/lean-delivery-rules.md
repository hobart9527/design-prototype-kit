# Lean Delivery Rules (轻量化高质交付)

Negative rules accumulated from benchmark regressions. They are always in force;
they are loaded here once at the start of Turn 3 (Look & Deliver), which is when
verification claims, authority tags, and lifecycle boundaries get written into
the record and the receipt. Loading them earlier spends Turn 1/2 context on
rules that only bite at receipt time.

This file is the sole owner of every rule ID below. Other files link to the ID; they do not restate the rule.

## Surgical Prototype Scope & Physical Triad

Keep interactive prototypes focused and lightweight; size follows the declared scope, not a line quota. For complex multi-surface or operational consoles, use the physical triad (`index.html` structure + `anchor.css` + `anchor.js`), and ALWAYS generate `prototype/shared/tokens.css` with DTCG root tokens and link it in `index.html` (`<link rel="stylesheet" href="../../../shared/tokens.css">`) so token inheritance passes.
Crucially, `index.html` must follow progressive enhancement: the primary view and initial fold must author the entities the brief gives directly in static markup. Never render an empty body that depends on client-side JavaScript hydration to populate the initial screen.

## Anti-Slop Discipline: No Thick Container Accent Stripes (SLOP-002)

Containers, cards, and panel wrappers must never use thick side accent stripes (e.g. `border-left: 3px solid var(--accent)` or heavy left indicator lines on static layout cards). High-severity AI slop flags this pattern. Differentiate containers using grid rhythm, subtle surface brightness contrast, or refined 1px perimeter borders. An accent border is legitimate only on transient status toasts or on the single currently selected/active row.

## Interactive Ergonomics & Risk-Tiered Confirmation Contract (交互人体工学与风险分级确认契约)

For destructive operations (delete, offline, drain, overwrite) and safety confirmation gates, friction scales with irreversibility. Reversible actions need no gate; irreversible ones may carry stronger friction (consequence preview, explicit review checkbox, two-step confirm). Whatever the tier, the mechanism must be drivable by discrete clicks, and the commit must close into honest feedback:

- `CRAFT-CONFIRM-DRIVABLE`: the gate offers a reachable confirm control and a cancel control that stay enabled and keyboard-operable. A native `<dialog>` opened via `showModal()` is the recommended mechanism; an inline confirmation panel is acceptable when its text and controls are visible in the snapshot (see `L22`). Typing a phrase, long-press/hold, or slide-to-unlock may only appear as an additional tier for a genuinely irreversible operation the brief names; they never replace the discrete-click path, because automation and assistive tech drive discrete clicks and gestures freeze task execution.
- `CRAFT-NATIVE-CONTROL`: actionable controls, selectable queue rows, list items, and tabs must be authored using native clickable elements (`<button>`, `<a>`, `<input>`) or carry an explicit `data-action="..."` attribute and proper ARIA semantics (`role="button"`, `role="tab"`). Never render selectable items as plain `<li role="option">` without actionable container wrappers or event handlers; automation and screen readers require drivable control surfaces. Correct event delegation is acceptable, and ARIA state follows each control's own semantics (`aria-selected`, `aria-pressed`, `aria-current` as fits).
- `CRAFT-ACTION-FEEDBACK`:
  - *(state clause)* committing must immediately move the task into a visible in-progress or terminal state in plain words.
  - *(terminal-freeze clause)* once a business action commits on an item, that same action cannot be submitted again on it: disable that control or replace it with a terminal status in plain words (e.g. `已通过`). This does not freeze legitimate viewing, undo, or follow-up actions.
  - *(destructive-exit clause)* the render must expose a clickable recovery/abort control (撤销/回滚/终止 or the brief's own term) that stays operable and halts or reverts that state. Never render it dead or permanently `disabled`.
  - *(live-control clause)* every exposed tab, filter chip, and navigation button must be wired to active DOM state updates (no dead controls/dead tabs that do nothing on click).
- `L22` — verification framing stays honest about mechanism: a confirmation surface without a native `<dialog>` is verified through the snapshot-text fallback in the task judge, not recorded as a dialog failure. Never describe that fallback path as a missing-dialog break.
- `L23` — the risk tier is judged against the operation's reversibility: banning typing/long-press outright is as wrong as making them the only path. The contract itself is owned by `CRAFT-CONFIRM-DRIVABLE` above.

## Domain Entity Grounding & Neutral Seeding (领域实体锚定与中性命名)

Mock data, topologies, and UI copy stay inside what the brief and session events state. Each rule below has one ID.

- `CRAFT-DATA-DISCIPLINE`:
  - Entities stay in the brief's domain. When the brief gives a quantity without names, use neutral systematic identifiers (`<kind>-01 ~ <kind>-NN`); never invent lateral business domains.
  - Status labels, audit states, and verification indicators must use the verbatim vocabulary provided in the brief and requirements (e.g. `已核对|未核实|缺失`; do not invent lateral synonyms like `未完成`).
  - Never invent telemetry, capacities, metrics, live counts, or percentages the brief does not state. Use neutral placeholders (`--`, `<kind>-NN`).
  - Never invent lifecycle phases, status models, or process pipelines; the UI reflects only the task actions requested.
  - Fixture data used only to illustrate layout is labelled as placeholder in the render, never presented as live truth. Likewise, mocked interactions and demo data are marked as demonstration in the render and never worded as backend guarantees; the record keeps the existing `[explicit]` / `[derived, provisional]` / `[hypothesis]` labels.
  - `L12` — symmetric to the bans above: render the entities the brief already supplied. Withholding provided domain facts (names, counts, severities, timestamps) behind generic placeholders is a presentation failure, not caution.
- `CRAFT-NO-FABRICATED-MAPPING`:
  - Never invent hierarchy, bipartite, or dependency mappings between independent sets the brief gives; render them as parallel lists or global tallies.
  - A global fact renders in the global header or summary area, never attached to one sub-scope (drawer, node, row).
- `CRAFT-NO-INVENTED-CAPABILITY`: concept text (THESIS, OWN-WORLD, STORY, briefs) and UI copy (dialogs, helpers, banners) describe layout, metaphor, and interaction ergonomics. They never assert capabilities or backend mechanisms the brief does not state (immutability, audit trail, automatic analysis, delivery guarantees, automatic migration, recorded actor). If a capability is not in the brief or ground truth, do not present it as active.

**The symmetric duty: present what the brief gives.** Anti-fabrication is not a licence to leave declared facts blank. Quantities and entities the brief or session events state must be fully rendered as usable information; withholding a declared fact is a task failure, not caution. What must NOT be asserted is a *mapping between* declared facts that the brief does not give: render the declared sets, leave the undeclared relation unstated.

**Required destructive-action feedback is not fabrication.** When the brief names a destructive task and its pain, consequence preview, confirmation language, and a recovery entry are required task feedback, not invented capability. What stays prohibited is asserting a *mechanism* the brief does not state (a concrete rollback window, backend semantics): present the control and its scope honestly (e.g. "台内可撤销", "后端机制未提供"), and do not promise backend reversibility.

**Consistency between record and render.** A fact recorded in truth.md as `[derived]` / `[unknown]` must not appear in the UI as unqualified asserted text, and a fact the record says is snapshot-only must be labelled as a snapshot in the render. The record and the render must agree on evidence status.

## Precondition & Historical Invariant Fidelity (物理事实与不可逆约束守恒)

When the user brief establishes constraints or historical facts (past events that were irreversible, physical limits, non-negotiable boundaries), the design must respect them as invariants. Never hallucinate mechanisms that retroactively negate or reverse declared historical outcomes; protective gates and undo mechanisms apply strictly to prospective, in-flight operations within the tool's immediate scope.

## Ground Truth & Attribution Fidelity (真值守恒与零臆测归因)

Assert as fact only what the user brief or session inputs explicitly support. Never fabricate user-research findings, operator profiles or experience tiers, usage cadence, or frequency to argue a design direction or innovation budget. Never fabricate root-cause attributions, or re-label a past event with a failure mechanism, target, or cause the user did not state. Cite historical events strictly by what was stated. Never invent organizational or operational objects the brief does not name. Unverified rationale and trade-offs remain `[hypothesis]`.

## Strict Authority Boundaries & Atomic Tagging (严格权威封顶与原子化标签标注)

User inputs supply intent; derived implementation parameters (timeouts, step counts, confirmation rules, derived UI constraints) remain `derived` / `provisional` and must never be promoted to user `confirmed`.

- The `[explicit]` tag applies SOLELY to pure, verbatim facts the user stated. Never combine user facts with derived interpretations, synthetic identifiers, or design solutions in one bullet or clause under `[explicit]`; put derived additions in separate `[derived]` bullets.
- In journey/flow descriptions, unconfirmed design mechanisms are qualified `[derived, provisional]`, never presented as settled.
- Bound any `confirmed` / "用户已确认" assertion strictly to what the user explicitly stated; never bundle derived parameters into the same clause or decision row.
- Initial interpretations of brief scope, historical constraints, and architecture direction stay `proposed(provisional)` or `derived` until an in-session explicit user reply confirms that specific choice. Decisions without one carry forward as `unaffected provisional decisions carried forward`, never as `approvals preserved` or `confirmed`.
- Brief inputs and supplements are not confirmed decisions. Without an explicit in-session user selection, the honest authority statement is "Zero confirmed decisions (all decisions stay proposed/provisional awaiting explicit user choice)".
- In design records and artifacts, never use "Confirmed" in Markdown section headings (e.g. `## Confirmed — visual tokens`) unless the enclosed facts were explicitly approved by the user in-session; use `Proposed Tokens` or `Provisional Tokens` instead.

## Receipt & Verification Honesty (物理收据与度量真值对齐)

The reconcile rules are owned by
[`../stages/stage-4-audit.md`](../stages/stage-4-audit.md) "Manifest cross-check" —
read it there and apply it here. In one line: quote recorded manifest counts as
recorded, downgrade to `visual_evidence: unverified` / `PARTIAL` when capture failed
or `stylesheets_applied: false`, and never claim an automated or interactive test pass
without scripts and logs physically persisted under `prototype/evidence/`.

## Bounded Lifecycle Closure (生命周期终态封闭)

Interaction workflows and task completions close cleanly at the precise boundary requested by the user. Once an operation completes its terminal state, acknowledge it as terminal within this interface; do not invent speculative post-task organizational workflows (e.g. cutover procedures, external re-registration, or external recovery pipelines) unless explicitly stated in the brief.

## Graceful Degradation & Progressive Disclosure

Hard gates block only on semantic fabrication, authority escape, or critical task breaks. Craft and performance optimizations are advisory. The escalation rule is owned by [`../02-craft-methods/craft-floor.md`](../02-craft-methods/craft-floor.md) § Progressive Escalation.
