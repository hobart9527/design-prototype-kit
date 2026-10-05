# Product Experience Quality Bar

Read before recommending a direction, reviewing a connected experience or
accepting a prototype. Quality is the fitness and coherence of the whole product
experience, not visual polish, checklist completion or an aggregate score.

## Objective Floor vs Qualitative Craft Separation

Evaluation strictly separates non-negotiable **The Floor (Absolute closure — zero tolerance)** (verified by browser/runtime facts) from aspirational **Quality Criteria (Craft, conviction, and resonance)** (Qualitative Design Craft):

### 1. The Objective Floor (Zero Tolerance Runtime Facts)
An experience fails the Floor only if any of the following objective runtime defects occurs:
- Unhandled JS exceptions or fatal page crash during rendering.
- Stylesheet link broken or inline hex colors bypassing `shared/tokens.css` inheritance.
- Horizontal containment failure (scrollWidth > clientWidth) at standard viewports.
- Basic WCAG 2.2 AA accessibility failures: text contrast below 4.5:1 against surface, focus completely invisible, or missing basic keyboard navigation.
- Fabricated approval provenance or false claims of independent review.
- Silent dead buttons: clickable action buttons that trigger zero DOM or state change.
- **Craft invariants (hard defects strictly within their applicable scope)** — each carries its craft-floor rule id, the same anchor `../02-craft-methods/craft-floor.md` states and [`../../../scripts/detect.py`](../../scripts/detect.py) detects; this file never restates their definitions:
  - Commit controls require perceptible `:active` press feedback. Plain links and pure navigation are out of scope. `CRAFT-PRESS-DETENT`
  - A rounded child nested inside a rounded parent with padding `P` satisfies $R_{in} = \max(0, R_{out} - P)$ (1px measurement tolerance). `CRAFT-CONCENTRIC-RADII`
  - Numeric values that update in place or align in columns use `font-variant-numeric: tabular-nums`; prose numbers are out of scope. `CRAFT-TABULAR-NUMS`
  - A check that cannot run is recorded as `Not verified`, never an automated pass.

### 2. Quality Criteria (Craft, conviction, and resonance)
Above the Floor, design merit is judged by human aesthetic review and discussion:
- **Visual Expression & Typography**: Appropriate hierarchy, intentional scale contrast, and fit with the chosen modern design vocabulary ([`../02-craft-methods/modern-style-vocabulary.md`](../02-craft-methods/modern-style-vocabulary.md)).
- **Information Architecture & Density**: Clean scan paths, intentional grouping, and high signal-to-noise ratio.
- **Motion & Somatic Feel**: Meaningful state transitions and spring deceleration curves without gratuitous decoration.
- **No Mechanical Blockers**: Aesthetic suggestions, card layouts, and color choices are discussion points between designer and human reviewer, never blocking script errors.

## Contextual Craft Guidelines & Heuristics (optional)

Other geometry, surface and motion choices are candidate techniques, not global requirements. Tabular numerals can aid scanning where prose figures form a meaningful comparison; neutral surfaces remain valid. These contextual notes never soften a confirmed Floor defect.
- **Closure Rigor**: 100% state closure across core interactive branches with resilient error recovery.

## Constructive Critique & Trade-off Assessment (Anti-Bureaucratic Evaluation)

Avoid hollow letter-grades (e.g. "A+ 40/40") or rubber-stamp approvals. Constructive evaluation must:
1. **Identify Unexamined Edges**: Name the specific viewport edge-cases, extreme data conditions, or rapid-fire actions where the prototype's mental model strains.
2. **Weigh Intentional Sacrifices**: Acknowledge what the design deliberately sacrificed (e.g. sacrificed initial discoverability to achieve keyboard-first expert density) and validate whether that trade-off aligns with user priorities.
3. **Offer Actionable Refactoring Deltas**: Provide concrete CSS/DOM adjustments, spacing tokens, or micro-interaction tweaks that would materially elevate craft.

## Professional judgment model

Account for the applicable dimensions below. A dimension may be intentionally
quiet or out of scope with a reason; a serious weakness cannot be averaged away.

1. **Value and source fidelity** — sourced purpose, audience, scope, outcomes and
   limits survive the design. Unsupported capability blocks recommendation.
2. **Object and content integrity** — entities, terminology, relationships,
   lifecycle, provenance and representative content remain coherent.
3. **Journey and Surface Topology** — necessary surfaces, overlays, channels and
   service moments support complete work without page inflation or hidden gaps.
4. **Interaction utility** — controls, feedback, continuity, interruption and
   recovery improve the diagnosed task and preserve user agency.
5. **Accessibility, inclusion and trust** — applicable input, perception,
   language, authority, uncertainty and consequence boundaries are usable and
   understandable.
6. **Integrated expression** — content voice, hierarchy, type, color, imagery,
   iconography, component character, feedback and motion form coherent Signature
   Craft for this product. Consistency alone is not enough.
7. **Contextual signature** — the Signature Relationship expresses something
   specific to this product and transfers beyond a hero frame. Familiar and quiet
   work can be distinctive through precision and fitness.
8. **Feasibility and platform fit** — known data, APIs, permissions, runtime,
   conventions and implementation boundaries are respected.
9. **Evidence quality** — facts, expert judgments, preferences, hypotheses and
   observations are distinguished; each consequential claim has evidence capable
   of falsifying it.
10. **System coherence and adaptability** — shared rules remain stable where they
    should, while responsive, state and contextual variations preserve meaning.
11. **Usability and cognitive task flow (UE 可用性工程走查)** — primary task journeys
    demonstrate unambiguous discovery (scent), conceptual clarity, predictable action
    execution, and graceful recovery from interruptions or errors.
12. **User Research (UR) Evidence Integrity** — distinguishes genuine empirical findings from design hypotheses; strictly forbids fabricated participant quotes, synthetic usability studies, or vanity metric validation. All assumptions must cite observable falsification triggers.

Numeric scoring is used only when explicitly requested with a pinned rubric. It
never replaces a written judgment or human preference and approval.

## Review the work at the right fidelity

Match the evidence to the claim:

- **Product model or topology:** trace sourced jobs, objects and lifecycle through
  the surface relationships. A diagram cannot prove that an interaction works.
- **Design proposition:** compare the same task-and-content specimen. Inspect the
  actual composition before its rationale and test its stated benefit, cost,
  learning burden, falsification condition and transfer case.
- **Runnable experience:** attempt the task from visible cues, including a relevant
  interruption, recovery or return. Inspect actual-size rendered views at the
  contracted viewports and an applicable dense or consequential state. At every
  required state reached, enumerate its visible enabled consequential actions and
  exits. Exercise each branch—including cancel/close, re-entry, retry and reset—or
  retain a source-based out-of-scope disposition. An enabled silent no-op or stale
  state after re-entry is a required failure.
- **Accessibility or behavior:** use a real trace, measurement or assistive check.
  Screenshots establish appearance only; source, DOM and assertion output do not
  by themselves establish experienced behavior or visual craft.
- **Participant outcome:** requires participant evidence. A research plan,
  heuristic review or expert walkthrough is not usability-study evidence.

For mobile typography, inspect actual font/script fit, role emphasis, line
breaking, leading and task density in the same arrangement at narrow and enlarged
conditions. For a new language, account compactly for applicable content voice,
type, color, imagery, icons, components, motion, topology and interaction. Do not
add an image or animation just to populate a row.

When the proposition uses the three-part synopsis, check that Qualitative Design
DNA explains both combination and product basis; any Real-World Mapping separates
source status, observed mechanism, local translation and non-transfer boundary;
and Signature Craft concretely expresses the Signature Relationship while
adapting to context. A missing analogy is not a quality defect.

## Criticism that improves the owning decision

Before the first critique, read [the design-audit method](../02-craft-methods/resilience-trust.md#criticism-that-changes-the-design).
Identify:

- the strongest relationship to preserve;
- up to three consequential weaknesses, with location/state and user impact;
- whether each issue is a source fact, design judgment, user preference,
  implementation defect or missing evidence;
- the owning layer—product model, topology, interaction, expression, specification
  or implementation;
- the intervention and observation that would demonstrate improvement.

Repair the owning cause. A weak proposition returns to its Design Proposition; a
missing page relationship returns to Surface Topology; an execution defect goes
to Builder. Do not use additional CSS polish to conceal a semantic or journey
problem. Preserve product facts, current authority and unaffected strong work.

Compare consequential revisions on the same content, task and relevant transfer
case. Keep before/after evidence. One critique and one revision pass is normally
enough for an ordinary defect; continue only when evidence reveals a new cause or
the user changes scope. Do not invent a flaw to force iteration.

## Independent Critic checkpoint

Use the active host's independent Critic role for a consequential new direction,
topology/interaction recommendation or connected prototype before final
recommendation or handoff. The Critic is an independent professional product,
UX, interaction, UI and visual design reviewer—not an engineering-only gate and
not a proxy for human taste.

The Critic separately reports:

1. **Design merit** — product fit, usefulness, clarity, coherence, craft,
   character, benefit/cost, transfer, and authentic physical/natural expression
   (auditing that claimed optical, biomorphic, kinetic, or domain mappings
   genuinely manifest in observable behavior, not hollow cosmetic adjectives).
2. **Task and experience evidence** — what was actually seen or exercised and
   what remains unverified.
3. **Engineering conformance** — source fidelity, required behavior,
   accessibility and implementation defects.

It recommends an owning revision; it does not edit the target, select a direction
or create approval. The main designer reconciles its advice with source facts and
the user's authority.

Give the Critic the original source, requested task/scope, review question, target
identity/revision, applicable viewports/states, permitted evidence scope and
installed Skill root. Hold target bytes stable during review. Evidence reused
from an earlier run must be bound to the current revision, content, state,
viewport and capture provenance; otherwise recapture or mark it unverified.
A fresh context supports an independence claim; disclose shared context.
If an independent Critic review was not actually dispatched or completed,
the review MUST be labeled `review_independence: non-independent (unverified)`;
it must never claim independent verification or exceptional grade in self-review.

Stop when the scoped question is answered: consequential claims have potentially
falsifying observations, applicable required coverage has suitable evidence and
remaining uncertainty is explicit. Bounded review is question- and risk-directed,
not an arbitrary tool, screenshot or token quota.

## Candidate discipline

- Hold source constraints, representative specimen, task, viewport and review
  question constant across alternatives.
- Change one consequential experience relationship per proposition.
- Use one proposition when evidence determines the direction; use enough to expose
  a material choice when judgment is genuinely open. No default quota applies.
- Treat density, contrast, type or motion treatments inside one interaction model
  as focused expression studies, not automatically new product directions.
- Combining propositions creates a successor proposition and needs renewed
  rationale and evidence.

## Anti-generic and evidence discipline

“Anti-generic” means refusing context-free defaults, not enforcing a signature
recipe. Diagnose whether interchangeability comes from weak product understanding,
generic content, absent hierarchy, borrowed composition, incoherent craft or a
missing Signature Relationship. Light, dark, flat, layered, dense, spacious,
immediate, animated, familiar and unconventional designs are all legitimate when
they fit and are well executed.

External critiques and deterministic audits are supporting evidence. Record their
tool/reference version, target revision, inspected scope, method and limitations.
Keep detector findings separate from expert design judgment and user preference.
No score, linter or implementation receipt establishes creative excellence or
human approval.

An acceptance record links the run command/output, task traces, applicable state
coverage, actual-size rendered views, keyboard/focus and reduced-motion evidence,
relevant accessibility checks and per-assertion results. Mark the result
inconclusive when available evidence cannot answer the review question.

## Verification honesty

A check that was not actually run is `Not verified` — never a pass, and never a
reported finding on its own. Screenshot-only inspection establishes appearance,
not behavior. Detector hits are leads; confirm them against the rendered or
running prototype before counting them.

## Cheaper-fix accountability

When a defect admits more than one fix, prefer the earliest rung that solves it:
**Delete** the unnecessary element → **use the platform** (native element,
browser focus ring) → **reuse** an existing token or component → **correct the
value** → only then **add** new code. A Critic remediation that recommends Add
where Delete or platform behavior would have solved it is itself an invalid,
redundant finding — report the cheaper fix instead.

## Before you finish (mistake inversion)

| Mistake | Inversion |
|---|---|
| A Floor violation softened because the prototype is otherwise impressive | Report it on sight; craft never averages away a blocker |
| An unrun check recorded as pass | Mark it `Not verified` and say what would verify it |
| An aesthetic choice treated as an automated blocker | Discuss it with the human reviewer; do not block builds |
| A remediation that adds code where deletion or platform behavior suffices | Replace it with the cheapest rung that solves the defect |
