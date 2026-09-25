# Stage 0: Explore (探 - 轻量方向探针)

Load this module only when the request is a bounded exploration, an alternative
direction probe, or a low-fidelity L0/L1 scope adjustment. It is not the formal
delivery route.

## Purpose

Answer one question: *"Is there a defensible direction worth formalizing?"* An
exploration is a falsifiable probe, not a proto-delivery. It produces a direction
brief plus evidence, never a sealed contract and never an approved artifact.

## Entry Conditions

- Intent classified as **Explore** by the entry router in [SKILL.md](../../SKILL.md) (e.g. user seeks alternatives, aesthetic direction probes, or visual falsification).
- No sealed provisional Spec exists yet, and none is being claimed.
- Greenfield or high-uncertainty exploration prior to formal candidate delivery; distinct from the Change Scope Router's L0/L1 fast-tracks (which operate on an existing, post-spec codebase).

## Operating Rules

1. **Falsifiable brief first.** State the tension or uncertainty the probe tests,
   the observation that would falsify the proposed direction, and the evidence
   that would settle it. A probe without a falsification boundary is not a probe.
2. **Honest divergence.** Fork across as many genuinely distinct hypotheses as
   the open uncertainty actually holds; a candidate count follows the hypotheses,
   not a quota. Close cousins of one solution do not count as divergence. Use
   real-world Reference Benchmarks rather than invented anchors.
3. **No-build discipline.** A no-build request ("只讨论", "不制作页面") forbids
   runnable HTML/JS/CSS prototypes. It still **MANDATES** recording the design
   model and decisions in `prototype/discussion.md` as the central index. Never
   write proposals to arbitrary repository root files, and never leave them
   solely in chat dialogue.
4. **Evidence honesty.** Keep claims labelled `explicit | observed | derived |
   hypothesis | unknown`. A probe screenshot proves a rendered direction; it does
   not prove ergonomic viability or aesthetic fitness.
5. **Research conclusions are legal output without build authorization.** A
   no-build exploration may close with sourced research conclusions and the
   updated discussion record; building is never a precondition for a legal exit.

## Gated Output

- `prototype/discussion.md` updated with the probe record and Resume section.
- Optional single direction probe artifact under `prototype/experiments/`.
- A direction probe report stating the surviving direction, the falsification
  boundary, and what was consciously sacrificed. Screenshots are attached only
  when a probe artifact was actually built.

## Exit

Legal exit is the direction probe report — with screenshots only when a probe
was actually built — or an explicit promotion into [Stage 1](stage-1-frame.md)
when the direction becomes a formal candidate and therefore requires a sealed
provisional Spec.
