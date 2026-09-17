# Product understanding

Read before the first consequential product interpretation and again only when
relevant sources, scope or product semantics change. The output is a revisable,
source-grounded Product Thesis and model basis in `prototype/product.md`, not a
questionnaire or a replacement PRD.

## Deep sense-making and problem reframing

A mature principal designer does not accept PRDs as mere feature punchlists.
Reframe the problem before accepting solution shapes:

1. **Surface the Hidden Tension**:
   What is the unstated friction, cognitive dilemma, or emotional anxiety the user
   faces? (e.g. speed vs accuracy, delegation vs loss of control, exploration vs
   cognitive overload). The design exists to resolve this specific tension.
2. **Anchor the Domain-Native Mental Model Metaphor (When Value-Additive)**:
   Do not force products into generic canned tropes or ubiquitous dark-mode dashboards.
   Where an authentic physical analogy exists, extract a domain-native metaphor grounded in physical intuition, spatial habits,
   or cognitive routines of the target practitioner (e.g. an architect's tracing paper, an air traffic
   radar cone, a bespoke tailor's cutting table, an orchestral conductor's score, a watchmaker's bench).
   When applied, the metaphor guides physical interaction rhythms, spatial persistence, and feedback velocity. If no metaphor naturally serves the task, a clean, direct, and restrained functional UI is fully acceptable.

## Cognitive Load Analysis & Dual-Option Trade-off Rationale (Trade-off Thinking)

To demonstrate top-tier design maturity, do not present design decisions as infallible dogmas. Whenever designing core topologies or navigation flows:
1. **Visual Path & Cognitive Load**: Analyze the operator's eye scanpath (F-Pattern for text/filtering, Z-Pattern for landing summaries, Layered Triangles for complex workspaces) and progressive disclosure boundaries.
2. **Trade-off Formulation (Option A vs Option B)**: Formulate the primary operational trade-off:
   - **Option A (Efficiency / Density First)**: Minimize click-depth, maximize parallel viewport real estate, optimize for expert power users.
   - **Option B (Guidance / Cognitive Flow First)**: Staged progressive disclosure, larger negative space, contextual inline hints, optimize for reduced error rates.
   - **Clear Recommendation & Cost**: Explicitly declare which option is recommended, why, and what cost/consequence is accepted by doing so.

Read current sources directly. Establish, with pointers where consequential:

- who acts, what job they are trying to complete and what outcome matters;
- the first-class object or content they act on;
- the trigger, environment, frequency, stakes and recipient of the result;
- supported capabilities and their relationships;
- roles, permissions, lifecycle and constraints the source actually defines;
- explicit non-goals and the boundary of the current release.

Keep `explicit | observed | derived | hypothesis | unknown` distinct. A generated
summary, genre convention or inverse of a prohibition is not a product fact.
Illustrative content may make a design concrete but must not redefine the product.

## Form the Product Thesis

Write a compact thesis that answers:

1. Who needs the product in which consequential context?
2. What progress or change should it enable?
3. What makes this product's approach different or valuable?
4. What user and product outcome would show that it works?
5. What tension or risk should the design make easier to manage?

Separate an observed problem from an explanation of its cause. A source can
describe a process without proving its frequency or effectiveness. A product
aspiration can motivate a design opportunity without inventing a failure story.

## Model jobs, outcomes and constraints

For each in-scope actor, connect job → object/content → decision/action → outcome.
Name the information required at the decision and what happens after it. Distinguish
the user's outcome from a system output and a business metric. Record how success
could be observed without fabricating a metric or study result.

Follow a representative episode from trigger through result as far as sources
permit. Include a later return, handoff or recovery when it materially changes
the experience. Unsupported permissions, persistence, automation and causal
relationships remain open.

## Identify the design opportunity and business tension matrix

Locate the first consequential gap or tension in the account. Describe what could
improve attention, control, confidence, comprehension, expression or enjoyment,
and what competing priority constrains that improvement. Connect it to a concrete
design question and a future observation that could refute the current framing.

### Qualitative Business Tension Reasoning

To ensure design decisions are rooted in genuine business and operational reality rather
than mere layout styling, record consequential product tensions when they actually exist:

- Identify the competing priorities or roles in tension (e.g. Operator speed vs System auditability,
  Structured governance vs Expressive user freedom, Full technical transparency vs Cognitive shielding).
- State the priority chosen for the specific journey and the design mechanism that embodies it
  (e.g. optimistic execution with reversible quarantine, or modal double-confirmation).
- Declare the accepted trade-off or downside, and state an observable condition that would refute
  this priority choice.
- Never use synthetic percentages (e.g. `Speed 80% / Safety 20%`). Core invariants like security,
  authorization integrity, and data loss prevention can never be compromised for "speed".
- Record only tensions that genuinely shape the current problem; do not force a universal matrix.

When sources support more than one materially different interpretation, compare
their product consequences. When evidence determines the interpretation, do not
manufacture alternatives. A visual or interaction probe may help test an
interpretation, but its result returns here as evidence rather than becoming
product truth automatically.

## Decide whether to ask, research or proceed

- Research facts that can be obtained from supplied material, repository assets
  or permitted external sources.
- User Research (UR) Evidence Integrity and Heuristic Framing:
  - When empirical participant studies, customer interviews, or analytics telemetry are absent,
    all behavioral assumptions MUST be explicitly stamped as `Design Hypothesis` or `Expert Heuristic`.
  - Agents are strictly forbidden from fabricating synthetic user quotes, simulated participant
    test reports, or false claims of user validation.
  - In the absence of empirical research, frame behavioral uncertainty through structured heuristics:
    1. *Behavioral Analogy*: What established mental model or adjacent physical/digital workflow
       do users already master that informs their intuition here?
    2. *Critical Path Risk*: What is the user's primary cognitive dilemma or fear of error along this path?
    3. *Falsification Trigger*: What observable customer friction or telemetry signal (e.g. abort rate,
       rapid undo, repeated search refine) would prove this design hypothesis wrong in real usage?
- Ask the user when the unresolved answer changes product semantics, authority,
  a consequential value trade-off or the validity of the next dependent action.
- Proceed with an explicit hypothesis when the work is reversible and the result
  can test it without presenting it as approved truth.
- Continue independent branches while one dependent branch is blocked.

Do not require the user to complete persona, scene or operations fields already
supported by the brief. One useful synthesis plus a consequential question is
better than a generic discovery interview.

## Connect to the rest of the model

Before surface planning, hand off these relationships:

- Product Thesis and observable outcome;
- actors, jobs and first-class objects/content;
- lifecycle and authority boundaries;
- representative and contrasting contexts;
- constraints, non-goals and decision-changing unknowns;
- initial expression or interaction opportunities, clearly labeled as
  hypotheses;
- evidence needed for the highest-risk claim.

Use [experience validation](research.md) when user need,
comprehension or findability needs empirical investigation. Use
[interpretation rules](../04-governance/interpretation-rules.md) when compiling a formal contract
or resolving source authority. Use [discussion](../04-governance/discussion.md) to retain user
corrections, delegation and the next decision.
