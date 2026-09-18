# Product Experience Quality Bar

Read before recommending a direction, reviewing a connected experience or
accepting a prototype. Quality is the fitness and coherence of the whole product
experience, not visual polish, checklist completion or an aggregate score.

## Floor versus Quality separation

Evaluation strictly separates non-negotiable **Floor** from aspirational **Quality**:

### 1. The Floor (Absolute closure — zero tolerance)
An experience fails the Floor if any of the following occurs:
- Semantic drift or unsupported product capabilities attributed to source truth.
- Fabricated approval provenance or false claims of independent review.
- Silent no-ops, broken cancel/close/reopen/retry branches, or unhandled errors.
- Basic WCAG 2.2 AA accessibility failures (contrast, focus traps, pointer targets); tokens intended for long-form data/text must achieve WCAG AAA (7:1 contrast) under static analysis.
- Inline hex colors or hardcoded styling bypassing `shared/tokens.css` inheritance.
- False claims of verification without actual browser execution traces or without a verified `review-portal.html` multi-view walkthrough harness.
- Metaphor entity disguise: renaming or disguising core business objects into physics or sci-fi metaphors (e.g. calling tasks particles, calling risk controls detent rods).
- Ergonomic Reality Gate failures:
  - For B-Pro systems: An unbriefed operator cannot determine overall system health and the location of anomalies within 5 seconds.
  - For C-Consumer systems: Core user loops cannot be completed through intuitive lifeworld somatic habits without reading explanatory prose.
  - Missing Dual-Channel Affordance: Critical keyboard shortcuts or gestural interactions lack visible, accessible GUI buttons or controls.
- Technical shallowness & toy-demo collapse: Presenting a trivially linear, toy mockup that strips away essential domain mechanics (e.g. non-linear branching in DAG workflows, temporal baselines in telemetry) under the pretext of omission.
- Stale Template Plagiarism & Execution Evasion: Rote copy-pasting of prior design mockups, stale entity names, or hardcoded topologies without fresh Stage 1 divergence reasoning. Verification harness enforces anti-stagnation rules against placeholder content.

**Non-dilution rule**: a confirmed Floor violation is a failure on sight — never
averaged down because the overall craft is strong, the surface is minor, or the
prototype is otherwise impressive. A shortened report is acceptable; an
unreported blocker is not.

### 2. Quality Criteria (Craft, conviction, and resonance)
Above the Floor, design merit is judged by qualitative evidence across core dimensions:
- **Domain Verisimilitude & Professional Credibility (专业欺骗感与领域自洽性)**: The interface demonstrates genuine structural and behavioral depth. An experienced domain practitioner sitting in front of the screen immediately perceives it as an authentic, high-depth production instrument or lifeworld tool.
- **Sense & Kinetic Clarity**: Physical or somatic mechanics resolve operational tensions; dynamic signals (such as throughput pulses or status transitions) deliver immediate situational awareness rather than superficial decoration.
- **IA & Topology**: Information architecture reflects task priority and authentic entity relationships; non-linear topologies preserve context across branches and secondary workflows.
- **Contextual Craft & Density**: Metrics feature legible reference benchmarks (scales, gridlines, event markers, micro-sparklines); density calibrated to high signal-to-noise ratio without cramped text or vacuum voids.
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

## Verifiable assertion check

Before verified acceptance, Builder accounts for each Foundation assertion with
`pass | fail | unverified | n/a`. Record the expected value or relationship, actual
observation, precise evidence location and scope reason where applicable. Separate
clauses such as stored data, visible result, feedback and keyboard continuation;
a suite exit code or logged event cannot stand in for all of them.

Required failures or unverified checks block a `verified` implementation verdict.
Exploratory failure is learning, not permission to claim success. Contradictory
raw evidence overrides a summarized pass until resolved. Changing the requirement
to make a failed implementation pass requires an explicit successor design/spec
decision, not a silent repair.

The assertion account includes **reachable-control closure**. A happy-path pass
does not cover another enabled exit from the same state. Verify state cleanup and
focus/meaning continuity after cancel, close or reset, then re-enter before
claiming the subsequent submit/retry path works.

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

## Generated-output fingerprint check

Audit-side detector only — these fingerprints never enter generation prompts
(Foundation, Builder dispatch or tokens). Check combinations, not single values;
an individual color or word is not a violation by itself.

- **Color-combination fingerprints**: dark purple-black base (hue 260–300,
  saturation > 10%) paired with a violet accent and glow borders; pink-to-cyan
  or rainbow gradient buttons; multiple high-saturation neon accents with
  blur/glow stacking. Any single hue used intentionally with brand evidence is
  legitimate; the violation is the unconsidered default combination.
- **Fake-chrome fingerprints**: a hardcoded `HH:MM` status bar (e.g. `9:41`),
  signal/Wi-Fi/battery icon clusters, fake browser URL bar or traffic lights,
  fake Dynamic Island or device bezel drawn inside the prototype — unless the
  product itself is a browser, device preview or design canvas.
- **Placeholder-content fingerprints**: the literal strings `Lorem`,
  `John Doe`, `Acme`-style generic company names, `example.` email domains;
  the same metric value repeated across 3+ unrelated cards; uniformly round
  numbers where real observation produces irregular values; consecutive
  identical timestamps.
- **Register infidelity (two-way)**: the Foundation declared a loud/raw/dense
  register but delivery silently reverts to polished defaults (soft shadows,
  uniform radii, generous whitespace) — or declared quiet/polished but delivery
  forces grain, torn edges or brutalist borders. Both directions are Floor
  failures when the declared register cites evidence.

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
| A detector fingerprint reported without confirming the rendered output | Confirm against the running prototype, or drop it |
| Register judged only for under-expression | Check both directions: loud-reverted-to-polished and quiet-forced-to-gritty |
| A remediation that adds code where deletion or platform behavior suffices | Replace it with the cheapest rung that solves the defect |

---

# Integrated Design Floor Standards (Consolidated from design-floor)

## Geometric and Visual Anti-Toy Discipline
- Concentric Border Radii Rule: R_inner = max(0, R_outer - Padding). Any visual collision or concentric distortion is an instant Floor failure.
- Tabular Numerics: font-variant-numeric: tabular-nums on all high-frequency telemetry, timestamps, and currency values.
- Zero Naked Metrics: Every metric must display a baseline, threshold, or floor/ceiling benchmark.
- Atmospheric Undertone: Surfaces must derive from contextual dark/light undertones, eliminating flat dead neutral greys.
- Perceptible Action Feedback: Active states must provide immediate, perceptible feedback (e.g. tactile scale, elevation shift, or luminance pulse) with stable layout integrity.
- Action Verb Lifecycle: Interactive buttons must reflect full lifecycle state transitions (e.g. QUARANTINE STEP -> QUARANTINED).
- Non-Transfer Boundary: Every physical or conceptual metaphor must explicitly define and enforce its non-transfer boundary.
- Vague-Word Firewall: Reject any aesthetic justification relying on vague adjectives without concrete token, contrast, and spacing bounds.
