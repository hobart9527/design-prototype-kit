# Lean Delivery Rules (轻量化高质交付)

Negative rules accumulated from benchmark regressions. They are always in force;
they are loaded here once at the start of Turn 3 (Look & Deliver), which is when
verification claims, authority tags, and lifecycle boundaries get written into
the record and the receipt. Loading them earlier spends Turn 1/2 context on
rules that only bite at receipt time.

## Surgical Prototype Scope & Physical Triad

Keep interactive prototypes focused and lightweight; size follows the declared scope, not a line quota. For complex multi-surface or operational consoles, use the physical triad (`index.html` structure + `anchor.css` + `anchor.js`), and ALWAYS generate `prototype/shared/tokens.css` with DTCG root tokens and link it in `index.html` (`<link rel="stylesheet" href="../../../shared/tokens.css">`) so token inheritance passes.
Crucially, `index.html` must follow progressive enhancement: the primary view and initial fold must author authentic domain entities (e.g. target machines/nodes, regions, affected services) directly in static markup. Never render an empty body that depends on client-side JavaScript hydration to populate the initial screen.

## Anti-Slop Discipline: No Thick Container Accent Stripes (SLOP-002)

Containers, cards, and panel wrappers must never use thick side accent stripes (e.g. `border-left: 3px solid var(--accent)` or heavy left indicator lines on static layout cards). High-severity AI slop flags this pattern. Differentiate containers using grid rhythm, subtle surface brightness contrast, or refined 1px perimeter borders. An accent border is legitimate only on transient status toasts or on the single currently selected/active row.

## Interactive Ergonomics & Task Trace Feedback (交互人体工学与状态反馈闭环)

For destructive operations (e.g. drain, offline, delete) and safety confirmation gates:

- Use clickable controls (e.g. a review confirmation checkbox `<input type="checkbox" id="reviewed"> <label for="reviewed">已复核影响面</label>` or standard modal dialog with a "确认" button). NEVER require typing arbitrary strings in a text input box to unlock buttons (automation runners and assistive tech drive interfaces via clicks/focus, not required string typing).
- Clicking the commit button must immediately transition the task into an active/terminal state with visible feedback keywords (`处理中`, `已排空`, `已完成`), and display visible, clickable recovery/abort controls (`撤销`, `紧急终止`, `回滚`).

## Domain Entity Grounding & Neutral Seeding (领域实体锚定与中性命名)

Mock datasets, service topologies, and entity lists must strictly stay grounded in the core problem domain stated by the brief. When the brief supplies numeric quantities without specific names (e.g. "7 downstream services", "3 regions"), use neutral systematic identifiers (e.g. `service-01 ~ service-07`, `region-1 ~ region-3`) instead of inventing domain-specific entities (e.g. billing, payment gateways, ticketing, external channels). Never invent unprompted lateral business domains. Never invent unprompted telemetry data sources, system capacities, or monitoring metrics (e.g. "剩余容量", "CPU水位", "网络吞吐") unless explicitly stated in the brief. Design concepts (THESIS, OWN-WORLD, STORY, briefs) describe spatial layout, visual metaphor, and interaction ergonomics — never assert unrequested technical capabilities (e.g. "不可篡改", "区块链存证", "自动根因分析", "零数据丢失保证") as factual promises. Never invent unprompted lifecycle phases, status models, or process pipelines (e.g. inventing a three-phase model like "止血 / 收敛 / 收尾" as surface banner elements when unstated in brief); interactions must reflect only the authentic task actions requested.

**The symmetric duty: present what the brief gives.** Anti-fabrication is not a licence to leave declared facts blank. Quantities and entities the brief or session events state (e.g. "7 downstream services affected", "P0 for 12 minutes") must be fully rendered as usable information — a list of 7 services with a stated-elsewhere aggregate is expected, not a "placeholder, not inferred" panel. Withholding a declared fact is a task failure, not caution. What must NOT be asserted is the *mapping between* declared facts that the brief does not give (e.g. which service depends on which machine): render the declared sets, leave the undeclared relation unstated — per-machine "all 7 affected" labels are exactly the fabricated mapping to avoid.

**Required destructive-action feedback is not fabrication.** When the brief names a destructive task and its pain ("不能操作错", "没法回滚"), consequence preview, confirmation language (确认/复核) and a recovery entry (撤销/回滚) are required task feedback, not invented capability. What stays prohibited is asserting a *mechanism* the brief does not state (e.g. a concrete rollback window, backend semantics): present the control and its scope honestly ("台内可撤销", "后端机制未提供"), do not promise backend reversibility.

**Consistency between record and render.** A fact recorded in truth.md as `[derived]` / `[unknown]` must not appear in the UI as unqualified asserted text, and a fact the record says is snapshot-only must be labelled as a snapshot in the render. The record and the render must agree on evidence status.

## Precondition & Historical Invariant Fidelity (物理事实与不可逆约束守恒)

When the user brief establishes constraints or historical facts (e.g. past events that were catastrophic or irreversible, physical limits, or non-negotiable boundaries), the design must respect them as invariants. Never hallucinate mechanisms that retroactively negate or reverse declared historical outcomes; protective gates and undo mechanisms apply strictly to prospective, in-flight operations within the tool's immediate scope.

## Ground Truth & Attribution Fidelity (真值守恒与零臆测归因)

Assert as fact only what is explicitly supported by the user brief or session inputs. Never fabricate unprompted user-research findings, psychological profiles, operator experience tiers, usage cadence, or drill frequencies (e.g. inventing "daily use", "高频使用", "日常演练", "expert operator", "新值班员需一次讲解", "适合新值班员", "资深值班员抵触向导" to argue a design direction or innovation budget). Never fabricate unverified root-cause attributions or re-label historical failures with unstated failure mechanisms (e.g. claiming "无复核" or "触控误触" was the root cause, or re-labeling an incident as "选错机器/误下线/误选节点/点击执行前未经影响预览" in metrics tables or decisions when the user only stated that someone accidentally drained a production node with one click and could not roll it back). Cite historical events strictly by what was explicitly stated (e.g. "上月一键排空且不可回滚"), without attributing unverified causes, targets, or failure mechanisms to past events. Never invent unrequested organizational or operational objects (e.g. inventing "批次/batch" when unstated). Unverified rationale and trade-offs must remain `[hypothesis]`.

## Strict Authority Boundaries & Atomic Tagging (严格权威封顶与原子化标签标注)

User inputs supply intent, but derived implementation parameters (e.g. exact timeout windows, wizard steps, two-man confirmation rules, or derived UI constraints like "零长列表") remain `derived` / `provisional` and must never be promoted to user `confirmed`. The `[explicit]` tag applies SOLELY to pure, verbatim facts directly stated by the user. NEVER combine user facts with derived interpretations, synthetic identifiers (`region-1 ~ region-3`, `service-01 ~ service-07`), or design solutions in a single bullet or clause under an `[explicit]` tag; place derived additions in separate bullets tagged `[derived]`. In journey/flow descriptions, unconfirmed design mechanisms (e.g. "双人确认", "必经影响预览") must be explicitly qualified as `[derived, provisional]`, never presented as settled facts. When stating user confirmations (`confirmed` or "用户已确认/用户已显性确认"), bound the assertion strictly to what the user explicitly stated; NEVER bundle derived design parameters into the same confirmed clause or decision row. Initial interpretations of brief scope, historical constraints, and architecture directions MUST remain `proposed(provisional)` or `derived` — NEVER mark initial decisions as `confirmed` without an in-session explicit user reply confirming that specific choice. Decisions without explicit in-session user choice carry forward as `unaffected provisional decisions carried forward`, NEVER as `approvals preserved` or `confirmed`.

## Receipt & Verification Honesty (物理收据与度量真值对齐)

Reconcile verification claims against `handoff-manifest.json` field by field. Quote exact recorded counts (touch target counts, overflow, stylesheet status) faithfully — NEVER deny, misrepresent, or claim runner defects to contradict recorded manifest metrics (e.g. never claim touch target count is 0 when manifest records 3; explain desktop pointer density vs touch target floor honestly instead). If `diagnostics_summary.runtime_errors` contains any JavaScript runtime error (ReferenceError, TypeError, SyntaxError), the prototype is broken: do NOT report `runtime_errors: []` or claim visual/interactive passes while errors are present; fix the code immediately. If screenshot capture reports runtime failures, `stylesheets_applied: false`, or pending review, state `visual_evidence: unverified` / `PARTIAL` honestly; never assert visual passes or fabricate rendered observations from unrendered artifacts. Never claim automated, interactive, or Playwright test passes (e.g. "Playwright 实测", "端到端实测", "脚本在 /tmp 不入库") unless test scripts and execution logs are physically persisted in `prototype/evidence/` with passing receipts recorded in `handoff-manifest.json`. Asserting test verification without durable on-disk receipts is forbidden evidence fabrication.

## Bounded Lifecycle Closure (生命周期终态封闭)

Interaction workflows and task completions close cleanly at the precise boundary requested by the user. Once an operation completes its terminal state, acknowledge it as terminal within this interface; do not invent speculative post-task organizational workflows (e.g. cutover procedures, external re-registration, or external recovery pipelines) unless explicitly stated in the brief.

## Graceful Degradation & Progressive Disclosure

Hard gates block only on semantic fabrication, authority escape, or critical task breaks. Craft and performance optimizations are advisory. The escalation rule is owned by [`../02-craft-methods/craft-floor.md`](../02-craft-methods/craft-floor.md) § Progressive Escalation.
