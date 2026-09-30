# Product truth — <product name>

Layered layout: this file owns product facts, the core tension, the success
metrics and the **Decisions and authority** table that `handoff.py freeze` reads.
It is one of three files that replace `prototype/discussion.md`:

- `prototype/truth.md` — this file: product truth and decision provenance.
- `prototype/world.md` — the shared visual world; sole token authority.
- `prototype/briefs/<slice_id>.md` — one per slice; surface strategy and evidence.

`prototype/discussion.md` may coexist as a thin Resume seam that points at
these three; it carries no decisions of its own.

## Problem Framing & Drivers

- **Core Tension**: `<A>` vs `<B>` — the authentic trade-off that drives the
  design. A default fallback tension is a defect; cite what makes it true here.
- **Design Driver**: `tension` | `failure_mode`
- **Reference Benchmarks**:
  - `Adopt`: real products whose mechanism transfers, with the mechanism named
  - `Refuse`: patterns this product must not copy, with the reason
- **Material Non-transfer Boundaries**: what the analog cannot carry over.
- **Ruthless Omissions**: what the sources explicitly do not ask for; never
  invent capability to fill the matrix.
- **Content Language (Locked)**: `<BCP-47 tag, e.g. zh-Hans | en-US>`

## Success metrics

State how this work will be judged — by the user, not by the agent. Metrics are
product outcomes and observable behaviors, never "the prototype exists".

| ID | Metric | Baseline | Target | How it is observed | Status (`[explicit] | [derived] | [hypothesis]`) |
|---|---|---|---|---|---|---|
| | | | | | |

Rules:

- Every metric names its observation method: a task a person performs, a number
  a real system reports, or a specific capture. "Feels better" is not a metric.
- A metric the sources never stated carries `[derived]` or `[hypothesis]` and
  is labelled as the agent's proposal awaiting the user's confirmation.
- Do not invent telemetry, analytics, or research that does not exist. If a
  metric cannot currently be observed, say so in the observation column rather
  than promising instrumentation.

## Decisions and authority

This is the table `handoff.py freeze` binds against. One row per consequential
decision; the freeze refuses to run without a `confirmed` or `delegated` row
that names this slice and cites its approval source.

| ID | Decision or authoritative section link | Status | Reason / evidence | Actual user quote + turn/date or source locator + delegated scope | User source (`confirmed \| delegated \| synthetic-fixture`) | Affected artifacts / minimal owning scope |
|---|---|---|---|---|---|---|
| | | | | | | |

Status: `proposed | confirmed | delegated | needs-evidence | superseded`.
Only an actual user decision or an explicit prior delegation can populate
`confirmed`/`delegated`; AI recommendations, Builder receipts, Critic reports
and test passes are not approval. A bare "continue" instruction without a
chosen direction never resolves an open direction choice into a confirmed
decision.

A decision that binds one slice names its `slice_id` in the scope column;
`handoff.py` binds a freeze only to rows that name its slice.

## Open frontier

| ID | Question | Depends on | Impact | Recommendation | Owner |
|---|---|---|---|---|---|
