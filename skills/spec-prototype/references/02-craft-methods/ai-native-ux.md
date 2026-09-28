# AI-Native UX — Design Methods for AI-Powered Interfaces

Read when the product's primary interaction involves a language model, generative
system, agentic workflow, or collaborative AI process. These patterns do not
replace general craft floors; they extend them for contexts where output is
probabilistic, latency is variable, and the human's model of the system's
capability is actively being formed.

## The Core Tension of AI Surfaces

AI surfaces carry a tension absent from deterministic products: the system's
actual capability is rarely fully legible to the user. Design's job is to make
the system's real behavior — including its limits, uncertainty, and failure modes
— honestly perceivable. Hiding uncertainty behind fluent output is a design
failure, not a polish decision.

## Streaming Output: Progress Without Deception

Long-form AI output streams token-by-token. The interface must communicate
genuine progress without implying false certainty about what is coming.

- **Incremental reveal**: render tokens as they arrive. Never buffer to a
  complete response before showing — buffering makes the system appear instant
  and the wait opaque.
- **Streaming cursor**: a visible, moving cursor on the live generation boundary
  signals active output. Static text blocks are indistinguishable from finished
  content; users scroll away prematurely.
- **No progress percentage for language model output**: token count is not
  useful time-to-completion data. Do not fabricate a progress bar that implies
  known completion time. Show elapsed time or a pulse indicator instead.
- **Interrupt affordance**: always provide a visible, reachable stop control
  during generation. Place it in the primary thumb zone on mobile, adjacent to
  the generation boundary on desktop. A stopped generation is an honest result;
  hide nothing about what was interrupted.

## Uncertainty Representation

A language model does not know what it does not know with the same reliability a
database does. Design must expose, not smooth over, uncertainty.

- **Confidence signals are contextual**: do not apply a universal low-confidence
  badge. Identify the specific claim types this product's model hedges on, and
  show uncertainty markers only for those types.
- **Citation and source attribution**: when output cites sources, the citation
  must be reachable from the claim it supports — not a footnote list at the
  bottom. Inline links or hover-anchored references preserve the relationship
  between claim and evidence.
- **Refusal and limit states are first-class**: a model refusal, capability
  limit, or out-of-context response is a product state, not an error. Design
  it: give it a visual form, an explanation appropriate to the user's context,
  and a clear recovery path. Do not leave a blank area or a raw error string.

## Human-in-the-Loop Confirmation Design

When an AI action is consequential — sending a message, modifying a file,
executing a command, making a purchase — the human confirmation step is the
trust anchor. Its design determines whether the human actually reviews the
action or rubber-stamps it.

- **Show the complete action, not a summary**: the confirmation surface renders
  the exact action that will be taken, in the format it will have when executed.
  A summary of the action is not enough; summaries get skimmed, full previews
  get read.
- **Diffs for modification actions**: when the AI proposes to modify existing
  content, show a before/after diff, not a description of the change. The diff
  is the confirmation surface.
- **Named irreversibility**: when an action cannot be undone, the confirmation
  button carries the consequence, not a generic label. "Delete 47 messages" not
  "Confirm". "Deploy to production" not "Proceed".
- **Delay friction for high-stakes actions**: a 2–3 second countdown before a
  destructive AI action executes — visible, interruptible — is not an obstacle.
  It is the design acknowledging the stakes.

## Progressive Context Establishment

AI systems improve as context accumulates. The interface should make this
visible and give the user agency over it.

- **Context state visibility**: show what context the system is currently
  working with — conversation history, attached documents, active constraints —
  as a scannable summary, not as a hidden system prompt. Users must be able to
  see what the AI knows about them right now.
- **Context editing affordance**: let users remove context items. A user who
  attached the wrong document should be able to detach it; a user who shared a
  persona constraint should be able to revoke it.
- **Session vs persistent context**: distinguish clearly between context that
  lives only in this session and context that the system will remember across
  sessions. This is a trust signal, not a technical detail.

## Multi-Turn Conversation Spatial Logic

A conversation surface is not a messaging thread with a different purpose. Its
spatial logic must reflect the work being done, not the chat paradigm.

- **Object persistence**: when the AI produces an artifact (a document, a plan,
  a code file), the artifact persists in a panel alongside the conversation, not
  as a transient message in the stream. The conversation drives the artifact;
  the artifact is the deliverable.
- **Turn navigation**: in long conversations, provide a way to jump to decision
  points (where the user gave a key instruction) not just to scroll position.
- **Branching when consequential**: when a user wants to explore two directions
  from the same starting point, the interface should support this explicitly
  rather than forcing linear continuation. A branch is a design affordance, not
  a technical hack.

## AI-Native States (Status Machine)

Every AI surface must have authored states for:

| State | Visual form |
|---|---|
| **Idle — awaiting input** | Clear input affordance, context summary visible |
| **Generating** | Streaming cursor, interrupt control, elapsed time |
| **Paused / interrupted** | Partial output preserved, resume and discard affordances |
| **Limit reached** | Named limit (context window, rate, capability), recovery path |
| **Error** | Error type distinguished from limit; retry or alternative path |
| **Confirmation required** | Full action preview, named consequence, escape route |
| **Completed** | Output settled, copy/share/act affordances, iteration entry |

Do not leave any of these states undesigned. An unstyled state is a blank page
or a raw error string — both are design failures.

## Agentic Flow: Multi-Step Visibility

When the AI takes a sequence of actions autonomously, the user must be able to
see what happened, in what order, and at what point to intervene.

- **Step log**: every completed action in a multi-step flow is recorded in a
  visible, scannable log. The log is not a transcript; it shows actions and
  their results, not reasoning tokens.
- **Decision points**: when the agent reaches a junction where it makes a
  consequential choice, show the choice and the selected path. Do not hide
  agent decision-making in a black box.
- **Intervention affordance at each step**: a user who sees the agent heading
  in a wrong direction should be able to intervene at the step level, not only
  by aborting the entire flow.
- **Recovery state**: if an agentic step fails, the interface shows what was
  completed before the failure, what failed, and the recovery options — retry
  this step, skip, or abort and restore to pre-flow state.
