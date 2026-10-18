# Lean Delivery Rules (轻量化高质交付)

These are **boundary** rules: truth, authority, scope and receipt honesty. They are
always in force, but load only the sections needed at each stage: the author-side
sections **Interactive Ergonomics**, **Domain Entity Grounding**, and **Precondition**
before the first runnable write in Turn 2; receipt and authority sections at the
start of Turn 3, when verification claims and lifecycle boundaries enter the record.

This file owns its boundary rules. Other files link to those rules; they do not restate
them. Generating-side craft floors, including `SLOP-002`, are owned by
[`../02-craft-methods/craft-floor.md`](../02-craft-methods/craft-floor.md).

## This is a boundary list, not a design checklist

A rule belongs here only when it guards **truth, authority, scope or receipt
integrity** — the classes where a violation is a factual defect (a fabricated
capability, a promoted authority, a dishonest receipt), not a weaker aesthetic.
Composition, typography, motion, color and density quality are owned by
[`../02-craft-methods/craft-floor.md`](../02-craft-methods/craft-floor.md) and the
craft references, and are improved through the
[`refine operators`](../operators.md), not through new prohibitions here.

When one benchmark exposes a gap, the default fix is **not** a new hard rule here:

- A defect that is one product's vocabulary (a specific verb, a specific surface) is
  fixed by faithful generation against the brief, or by one already-owned rule — not
  by a new global rule.
- A quality gap (hierarchy, rhythm, colour, motion, density) is raised by the positive
  scaffold in [Stage 2](../stages/stage-2-probe.md) and [Stage 3](../stages/stage-3-skeleton.md),
  then improved via an operator pass with a named target and falsifier.
- Add a rule here only when the failure is a truth/authority/scope defect that no
  owned rule already covers, and state which of those classes it guards.

Growing this list per benchmark error produces defensive over-restriction: the model
satisfies the literal letter of each rule while delivering less design. Keep the list
small and general, and push the ceiling up instead of the floor higher.


## Surgical Prototype Scope & Physical Triad

Keep interactive prototypes focused and lightweight; size follows the declared scope, not a line quota. For complex multi-surface or operational consoles, use the physical triad (`index.html` structure + `anchor.css` + `anchor.js`), and ALWAYS generate `prototype/shared/tokens.css` with DTCG root tokens and link it in `index.html` (`<link rel="stylesheet" href="../../../shared/tokens.css">`) so token inheritance passes.
Crucially, `index.html` must follow progressive enhancement: the primary view and initial fold must author the entities the brief gives directly in static markup. Never render an empty body that depends on client-side JavaScript hydration to populate the initial screen.

## Interactive Ergonomics & Risk-Tiered Confirmation Contract (交互人体工学与风险分级确认契约)

For destructive operations (delete, offline, drain, overwrite) and safety confirmation gates, friction scales with irreversibility. Reversible actions need no gate; irreversible ones may carry stronger friction (consequence preview, explicit review checkbox, two-step confirm). Whatever the tier, the mechanism must be drivable by discrete clicks, and the commit must close into honest feedback:

- `CRAFT-CONFIRM-DRIVABLE`: the gate offers a reachable confirm control and a cancel control that stay enabled and keyboard-operable. A native `<dialog>` opened via `showModal()` is the recommended mechanism; an inline confirmation panel is acceptable when its text and controls are visible in the snapshot (see `L22`). Typing a phrase, long-press/hold, or slide-to-unlock may only appear as an additional tier for a genuinely irreversible operation the brief names; they never replace the discrete-click path, because automation and assistive tech drive discrete clicks and gestures freeze task execution.
- `CRAFT-NATIVE-CONTROL`: every actionable control, selectable row, list item, or tab is keyboard-operable, focus-visible, and carries a stable trigger. Prefer native elements (`<button>`, `<a>`, `<input>`); a table row or list item may remain a `<tr>`/`<li>` when the actionable affordance inside it is a native control with clear focus and text/ARIA label. A chosen option or row shows its state both to assistive technology and to the next snapshot: `aria-checked` for radios, `aria-selected` for tabs/options, `aria-pressed` for toggle buttons, and visible text or marker where users need it. Never leave a control unlabeled, unfocusable, or dead.
- `CRAFT-MINIMAL-PATH`: the central task completes from its real entry to a meaningful result with the least unnecessary navigation. A step split or screen change serves a task dependency, reduces cognitive load, or separates irreversible risk; it is not a step-count quota. Single-screen, multi-step, and wizard flows are all valid when the dependency justifies them. Preserve user input and context across steps; never drop progress on return or retry.
- `CRAFT-STATE-ENTRY`: when the brief names a recoverable or exceptional state (conflict, failure, empty, already-processed), expose a deterministic entry for review (e.g. `?state=<name>`, a demo switch, or an explicit interaction path). Record it so reviewers can reproduce the state without replaying the whole flow. A mid-flow state entry seeds the necessary upstream decisions and lands on the step where the state is observable. Specific aliases and scenario seeding belong to [benchmark-only rules](../../../../benchmarks/legacy-rules.md) and apply only at benchmark runtime.
- `CRAFT-TASK-COPY`: task-critical UI copy uses the brief's own verbs and nouns verbatim. A recoverable-alternative prompt names the alternative in the brief's terms. The rule is verbatim-match against the brief, not a fixed keyword list: derive required substrings from the brief at author time. See [benchmark-only rules](../../../../benchmarks/legacy-rules.md) for scenario-specific examples, active only at benchmark runtime.
- `CRAFT-ACTION-FEEDBACK`:
  - *(state clause)* committing must immediately move the task into a visible in-progress or terminal state in plain words.
  - *(terminal-freeze clause)* once a business action commits on an item, that same action cannot be submitted again on it: disable that control or replace it with a terminal status in plain words (e.g. `已通过`). This does not freeze legitimate viewing, undo, or follow-up actions.
  - *(terminal-attribution clause)* when the brief names an auditable decision (approve / reject / publish / pay / confirm), the terminal state must show the decision record itself — at minimum the resulting status plus the brief's own actor/timestamp vocabulary when supplied. A transient toast alone is not a terminal state; users returning to the list must still see that the item was decided. If the brief supplies no actor/timestamp, render the status alone — do not invent names.
  - *(audit-record clause)* when the brief frames the system as auditable, render a dedicated audit-record surface independent of the queue. Queue rows retain terminal status, or a separate audit view lists every decision. Scenario-specific text examples are in [benchmark-only rules](../../../../benchmarks/legacy-rules.md), active only at benchmark runtime.
  - *(destructive-exit clause)* the render must expose a clickable recovery/abort control (撤销/回滚/终止 or the brief's own term) that stays operable and halts or reverts that state. Never render it dead or permanently `disabled`.
  - *(live-control clause)* every exposed tab, filter chip, and navigation button must be wired to active DOM state updates (no dead controls/dead tabs that do nothing on click).
- `L22` — verification framing stays honest about mechanism: a confirmation surface without a native `<dialog>` is verified through the snapshot-text fallback in the task judge, not recorded as a dialog failure. Never describe that fallback path as a missing-dialog break.
- `L23` — the risk tier is judged against the operation's reversibility: banning typing/long-press outright is as wrong as making them the only path. The contract itself is owned by `CRAFT-CONFIRM-DRIVABLE` above.

## Domain Entity Grounding & Neutral Seeding (领域实体锚定与中性命名)

Mock data, topologies, and UI copy stay inside what the brief and session events state. Each rule below has one ID.

Content falls into three classes, and the treatment differs:

- **Known facts** — names, amounts, statuses, roles, and constraints the user or brief supplied. Preserve them verbatim; never replace them with samples.
- **Display samples** — realistic placeholder content used only to test layout, density, and readability. Mark them clearly as demonstration in the render (e.g. `演示数据` in the header, `样例` badge, or a visible note). Samples must not be presented as user facts, business rules, or real observations.
- **Capabilities & guarantees** — payment, locking, notification, permission, audit, and state-transition promises. These must be implemented or explicitly disclaimed in the copy. A sample amount cannot become a fee, and a demo badge does not authorize a capability the brief never requested. **A brief that says "publish" or "release" without defining the downstream platform authorizes only the in-prototype decision state; the UI must not claim "可发布 / approved for publication" when the platform is undefined — use "核对通过，待下游流程" or the brief's own terminal wording.**
- **Benchmark-specific constraints.** Concrete scenario clauses are in [benchmark-only rules](../../../../benchmarks/legacy-rules.md) and apply only when that benchmark runs. The general rule remains: show only amounts and task actions supported by the active brief.

- `CRAFT-DATA-DISCIPLINE`:
  - Entities stay in the brief's domain. When the brief gives a quantity without names, use neutral systematic identifiers (`<kind>-01 ~ <kind>-NN`); never invent lateral business domains.
  - Status labels, audit states, and verification indicators must use the verbatim vocabulary provided in the brief and requirements (e.g. `已核对|未核实|缺失`; do not invent lateral synonyms like `未完成`).
  - Personal names, specific addresses, and exact dates may be used as display samples when the brief does not supply them, provided they are marked as demonstration and do not assert a capability or business rule.
  - Never invent telemetry, capacities, metrics, live counts, or percentages the brief does not state. Use neutral placeholders (`--`, `<kind>-NN`) when the brief supplies nothing.
  - Never invent lifecycle phases, status models, or process pipelines; the UI reflects only the task actions requested.
  - Display samples are labeled as demonstration in the render, never presented as live truth. Mocked interactions and demo data are marked as demonstration in the render and never worded as backend guarantees; the record keeps the existing `[explicit]` / `[derived, provisional]` / `[hypothesis]` labels.
  - `L12` — symmetric to the bans above: render the entities the brief already supplied. Withholding provided domain facts (names, counts, severities, timestamps) behind generic placeholders is a presentation failure, not caution.
- `CRAFT-NO-FABRICATED-MAPPING`:
  - Never invent hierarchy, bipartite, or dependency mappings between independent sets the brief gives; render them as parallel lists or global tallies.
  - A global fact renders in the global header or summary area, never attached to one sub-scope (drawer, node, row).
- `CRAFT-NO-INVENTED-CAPABILITY`: concept text (THESIS, OWN-WORLD, STORY, briefs) and UI copy (dialogs, helpers, banners) describe layout, metaphor, and interaction ergonomics. They never assert capabilities or backend mechanisms the brief does not state (immutability, audit trail, automatic analysis, delivery guarantees, automatic migration, recorded actor). If a capability is not in the brief or ground truth, do not present it as active.
- `CRAFT-NO-INVENTED-LIFECYCLE`: never invent lifecycle transitions, post-task escalation roles, or irreversibility claims the brief does not state. A rejection action does not imply a "resubmit after edit" path unless the brief says so; a payment or commit action does not become "不可撤回 / 不可撤销" unless the brief says so; a terminal status does not invent contact roles ("如需更正请联系管理员 / 请联系客服") unless the brief explicitly names them. Render the action the brief names with its immediate consequence in plain words; leave downstream re-entry, administrative cutover, and external helpdesk roles unstated (e.g. "已通过" or "已打回" alone, not "已打回，如需更正请联系管理员").
- `CRAFT-DERIVED-NOT-UI-RULE`: a fact tagged `[derived]` / `[hypothesis]` in truth.md or briefs must never be rendered as a hard UI rule, required-field error, or blocking constraint. If "打回必须填写理由" or "大额二次确认" is derived, the brief/contract invariants table must mark it as `advisory` (or `provisional`), never `severity: blocking`. Derived rules stay designer-internal; only explicit brief rules become enforcement.
- `CRAFT-AUDIT-RECORD-SEEDING`: where the brief requires a record surface, provide enough truthful initial and in-session state to inspect retention without inventing processed history. Benchmark fixture counts and vocabulary are in [benchmark-only rules](../../../../benchmarks/legacy-rules.md), active only at benchmark runtime.
- `CRAFT-SPEC-TIER-HONESTY`: a compiled specification must never claim `execution_spec` / `frozen` / `approved` when the design record says the direction is `proposed`, `provisional`, or awaiting user selection. Spec tier matches recorded decision state: proposed direction → `draft_spec` or `review_spec`; explicit user selection → `execution_spec`. Compiling an execution_spec off a provisional decision is authority promotion, not thoroughness.
- `CRAFT-TRIGGER-FIDELITY`: when the brief names a verb ("高亮", "批注", "打回") without naming the trigger or commit mechanic, the trigger stays `[derived]` in the spec — never compile `trigger: "选中文字后点击色块"` as `explicit` when only the verb is user-stated. The verb is explicit; the interaction mechanics (trigger, commit, undo, focus order) are derived unless the brief spells them out.
- `CRAFT-AFFORDANCE-DISCOVERABLE`: task-critical affordances named in the brief must be discoverable and reachable without hidden prerequisites or uncommunicated interactions. Where transient controls (e.g. selection menus, flyouts) house primary verbs, provide context-aware access or standard keyboard shortcuts so actions remain discoverable and accessible without arbitrary obstacle. Every action must provide immediate affirmative visual feedback when triggered.
- `CRAFT-DYNAMIC-BEHAVIOR-TRUTH`: code comments, documentation prose, and design records must only assert dynamic behaviors that are physically implemented in the accompanying JavaScript or CSS. Never write comments claiming dynamic node relocation (e.g. "JS moves it under the row") unless the script physically executes `insertBefore`/`appendChild`/`replaceChild`. If an element is statically placed in HTML and revealed via `hidden = false` or class toggle, the comment and design record must state that physical reality accurately.
- `CRAFT-SCREENSHOT-STATUS-HONESTY`: a state or screen that is `capture_failed`, has 0 screenshots, is unconfirmed, or is `pending_review` is never reported under `## Verified this turn`; it goes under `## 未验证（不得读作已验证）` / `Limitations` tagged `[hypothesis]` / `[unverified]`. Promoting it is an authority-promotion defect. Full rule and reconcile line: [`../stages/stage-4-audit.md`](../stages/stage-4-audit.md) "Manifest cross-check".
- `CRAFT-EVIDENCE-SCOPE-HONESTY`: never claim a viewport, screen size, or render state is "verified" / "已验证" unless `handoff-manifest.json` records a snapshot for that exact viewport. If the manifest only covers `390` and `1280`, the record must say `1440: hypothesis` or `1440: unverified`, not `1440: verified`. Viewport claims beyond the manifest are evidence-coverage gaps, not verified facts.
- `CRAFT-REVISION-COMPARE`: when the brief asks to identify changed passages, render a compare/diff surface that makes passage-level changes visible. A revision history that labels versions without showing what changed does not satisfy the task. Use navigable passage anchors; benchmark-specific vocabulary and anchor examples are in [benchmark-only rules](../../../../benchmarks/legacy-rules.md), active only at benchmark runtime.

**The symmetric duty: present what the brief gives.** Anti-fabrication is not a licence to leave declared facts blank. Quantities and entities the brief or session events state must be fully rendered as usable information; withholding a declared fact is a task failure, not caution. What must NOT be asserted is a *mapping between* declared facts that the brief does not give: render the declared sets, leave the undeclared relation unstated.

**Required destructive-action feedback is not fabrication.** When the brief names a destructive task and its pain, consequence preview, confirmation language, and a recovery entry are required task feedback, not invented capability. What stays prohibited is asserting a *mechanism* the brief does not state (a concrete rollback window, backend semantics): present the control and its scope honestly (e.g. "台内可撤销", "后端机制未提供"), and do not promise backend reversibility.

**Consistency between record and render.** A fact recorded in truth.md as `[derived]` / `[unknown]` must not appear in the UI as unqualified asserted text, and a fact the record says is snapshot-only must be labelled as a snapshot in the render. The record and the render must agree on evidence status.

## Precondition & Historical Invariant Fidelity (物理事实与不可逆约束守恒)

When the user brief establishes constraints or historical facts (past events that were irreversible, physical limits, non-negotiable boundaries), the design must respect them as invariants. Never hallucinate mechanisms that retroactively negate or reverse declared historical outcomes; protective gates and undo mechanisms apply strictly to prospective, in-flight operations within the tool's immediate scope.

## Ground Truth & Attribution Fidelity (真值守恒与零臆测归因)

Assert as fact only what the user brief or session inputs explicitly support. Never fabricate user-research findings, operator profiles or experience tiers, usage cadence, or frequency to argue a design direction or innovation budget. Never fabricate root-cause attributions, or re-label a past event with a failure mechanism, target, or cause the user did not state. Cite historical events strictly by what was stated. **Never invent domain-object attributes the brief does not name**: an entity has no rating, seniority, payment constraint, or specialized attribute unless the brief says so; a user demographic has no unstated numeric threshold. Unverified rationale and trade-offs remain `[hypothesis]`. **Interactive UI feedback and toast strings must remain strictly grounded**: never promise ungrounded capabilities in UI feedback copy (such as undo mechanics, author notifications, or external system synchronizations when downstream systems or recovery channels are explicitly undefined in the brief). **Stage 4 audits must record discrepancies as objective factual observations**: never assert speculative root-cause attributions (e.g. claiming a test harness probe artifact caused a contract divergence) without verified physical evidence. **When a session event injects a domain statement ("keep this citation unverified", "this slot is taken"), record it as `confirmed` only for the exact claim the event makes; do not promote adjacent derived rules to `confirmed` on the event's authority.** This binds design-rationale prose in `truth.md` / `discussion.md` / `briefs/` as much as UI copy: arguing a direction with how users feel ("制造焦虑", "所有年龄段都懂"), what they would accept, or unstated legacy implementation history ("上一版实现方式") is asserted fact unless tagged `[hypothesis]`. State the user's reported symptom verbatim and the design consequence; leave the cause and the user's psychology unasserted. Separate display samples from facts: a name or amount shown for layout testing is not a user fact.

## Strict Authority Boundaries & Atomic Tagging (严格权威封顶与原子化标签标注)

User inputs supply intent; derived implementation parameters (timeouts, step counts, confirmation rules, derived UI constraints) remain `derived` / `provisional` and must never be promoted to user `confirmed`.

- The `[explicit]` tag applies SOLELY to pure, verbatim facts the user stated. Never combine user facts with derived interpretations, synthetic identifiers, or design solutions in one bullet or clause under `[explicit]`; put derived additions in separate `[derived]` bullets.
- **Tag fidelity across documents.** When a downstream record (briefs/<slice>.md, c1.md, contract) cites a fact from truth.md or discussion.md, preserve the original evidence tag verbatim. A fact tagged `[derived]` or `[hypothesis]` upstream must never be re-tagged `[explicit]` or `confirmed` downstream. Aggregating several facts into one bullet upgrades each to its strongest source — never to a stronger one.
- In journey/flow descriptions, unconfirmed design mechanisms are qualified `[derived, provisional]`, never presented as settled.
- Bound any `confirmed` / "用户已确认" assertion strictly to what the user explicitly stated; never bundle derived parameters into the same clause or decision row.
- **Atomic authority in code comments.** When documenting decisions in CSS/JS comments (e.g. `/* D9 derived; D8 confirmed */`), never attribute a derived parameter (e.g. `64px`, `56px`, `12 分钟`) to a confirmed constraint. State the physical parameter and the user constraint as distinct items: `/* 64px: D9 derived; constraint: D8 confirmed (45+ users, touch precision) */`. Attributing a derived number to a confirmed decision is authority promotion in code comments.
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
