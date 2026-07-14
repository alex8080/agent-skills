---
name: acceptance-spec
description: Drive a feature to a complete, gap-free acceptance criteria specification BEFORE any implementation begins. Use whenever the user wants to start feature development, work through requirements, or turn a PRD, ticket, feature description, or rough acceptance criteria into a rigorous spec. The agent drafts, audits for coverage, probes every load-bearing assumption, and never assumes — it asks. Output is a spec (not tests) saved to docs/spec/, structured so a downstream agent can later derive tests. Trigger on "build a feature", "write acceptance criteria", "spec out X", "here's a PRD/ticket, let's start", or any feature work that should begin with agreed criteria.
---

# Acceptance Spec

Produce a complete, unambiguous **acceptance criteria specification** for a feature before a line of implementation is written. The spec is executable requirements in prose: it says *what correct behavior is and when*, not *how it's built* and not *how it's tested*. A separate implementation agent derives tests and code from it later.

## The core discipline: never assume, always ask

The single job of this skill is to eliminate gaps and hidden assumptions from a feature's requirements. The agent's default posture is **interrogation, not authorship-by-guess**.

- When the input is silent or ambiguous on something, the agent **asks** — it does not fill the gap with a plausible default.
- The agent **may recommend** ("I'd suggest rejecting these silently — here's why"), but a recommendation is a proposal awaiting the user's yes, never a decision.
- A criterion built on an unstated assumption is a defect, even if the assumption is reasonable. Surface it.

If the agent ever finds itself writing a criterion it can't trace to something the user stated or approved, stop and ask instead.

## The gate (read before every handoff)

**No implementation, no test-writing, no code — nothing downstream — until the user has explicitly approved the spec.** This is a hard stop. "Looks good, start building" is approval; silence, a thumbs-up on one section, or the agent's own judgment that it's ready is not. The spec is the deliverable of this skill; producing code is out of scope.

## Workflow

### 1. Ingest the input

The user provides one of: a PRD, a ticket, a prose feature description, or an initial set of acceptance criteria. Whatever the form, treat it as **raw material, not a finished spec** — even user-supplied acceptance criteria get audited for gaps.

Read it fully. If a `prd-review` skill or similar produced structured output, consume that. Then restate the feature in your own words back to the user in 2–3 sentences and confirm you've understood the intent before going further. Correct understanding up front is cheaper than a spec built on a misread.

### 2. Draft the spec

Write structured acceptance criteria as **spec-level Given/When/Then** — behavioral, implementation-free. Group by scenario. For each: the actor, precondition, trigger, and observable expected outcome.

Include from the start:
- **Happy paths** — the feature working as intended, per distinct actor.
- **Error and edge cases** — invalid input, boundaries, empty/null, unauthorized, conflicting state, external failure.
- **Non-functional criteria** — only where testable and stated/agreed (latency, throughput, auditability, security). Don't invent NFRs; ask if the input implies one without stating it.
- **Explicitly out of scope** — what this feature does *not* do. Prevents scope creep and tells the downstream agent where the edges are.
- **Open questions** — anything you couldn't resolve without the user.

Mark anything you inferred rather than were told, so it's visible for approval.

### 3. The layered coverage gate

Before showing the spec as "complete," run all three layers. This is what enforces "no gaps."

**Layer 1 — breadth checklist (did we forget a category?).** Run this fixed list against the spec:
- Every actor / role covered?
- Every error path for each happy path?
- Boundary and degenerate inputs (empty, null, zero, max, malformed)?
- Authorization / permission cases — who can't do this, and what happens when they try?
- Concurrency / conflicting-state cases, if the feature has shared state?
- External dependency failure modes (timeout, error, partial response)?
- Idempotency / retry behavior, if applicable?
- Observability — is anything required to be logged, audited, or emitted?
- State after failure — what's the system left in when something goes wrong?
- Each stated NFR expressed as a *testable* criterion?

The checklist catches missing **categories**. It only finds what's on the list.

**Layer 2 — load-bearing probing (is each criterion actually complete?).** For each criterion, find claims the spec **depends on but doesn't justify**, and interrogate them. This is the `learn-loop` move applied to requirements: attack the spec's own reasoning, not a generic template.

Example: criterion says *"reject invalid transfers."* Probe:
- What defines invalid? (amount? currency? account state? sanctions hit?)
- Who or what decides?
- What happens to a rejected transfer — dropped, queued, returned to sender?
- Is the rejection surfaced to the actor? Logged? Audited?
- Is "reject" synchronous or deferred?

Every probe whose answer isn't already in the spec becomes a **question to the user** (per the never-assume rule), or a recommendation for them to confirm. The checklist finds forgotten breadth; probing finds shallow depth.

**Layer 3 — cross-scenario consistency (do the scenarios contradict or leave holes between them?).** Layers 1–2 audit scenarios one at a time; contradictions live *between* them. Two checks:

- **Pairwise conflict:** for each pair of scenarios that share a state, signal, or observable (the same list, flag, message, response), check their Givens can't both hold while their Thens conflict — and that neither scenario's Then quietly forecloses the other's Given.
- **State-space sweep:** for each trigger, enumerate the small state combinations behind it (e.g. due? × tagged? × cached?) and confirm every combination reaches exactly one defined outcome. A combination no scenario claims is a hole; one that two scenarios claim differently is a contradiction.

Real example of what this layer exists to catch: a backend scenario allowed "empty tag list" to mean *either* nothing due *or* due-but-untagged, while a UI scenario treated "empty tag list" as *proof* nothing was due — individually fine, jointly making due-but-untagged cards unreviewable. Layers 1–2 passed it; only the combination check would have caught it.

All three layers run; none substitutes for another.

### 4. Surface gaps and resolve with the user

Present what the three layers found: uncovered categories, unjustified claims, cross-scenario conflicts or unclaimed state combinations, open questions, and any inferences you flagged. For each, either ask the user directly or make a recommendation for them to accept or reject. Loop with the user until nothing is unresolved.

The user may, after your initial draft, ask you to **co-write** — work through criteria together interactively rather than review-and-return. Support both modes; the authoring model is "agent drafts, user approves, and may pull you into co-writing at any point."

### 5. Approval gate

When you believe the spec is complete and no open questions remain, present it and **ask for explicit approval**. Do not proceed past this point, and do not offer to implement or write tests, until the user clearly approves. If they raise anything, return to step 4.

### 6. Write the spec artifact

On approval, save the spec to `docs/spec/` as `<feature-name>.md` (kebab-case). Confirm the path to the user. Structure it so a downstream implementation agent can derive tests directly — clear scenario boundaries, unambiguous outcomes, explicit scope edges.

## Spec format

```markdown
---
feature: <Feature Name>
status: approved
source: <PRD | ticket | description | initial-criteria>
created: <YYYY-MM-DD>
---

# <Feature Name> — Acceptance Specification

## Intent

<2–3 sentences: what this feature is and why, in the agreed framing.>

## Actors

<Each role/system that interacts with the feature.>

## Acceptance criteria

### Scenario: <name>
- **Given** <precondition>
- **When** <trigger by actor>
- **Then** <observable expected outcome>

<Repeat per scenario. Cover happy paths, then error/edge/boundary/auth/failure cases.>

## Non-functional criteria

<Testable NFRs only, each phrased so it can be checked. Omit the section if none.>

## Out of scope

<What this feature explicitly does not do.>

## Open questions

<Empty at approval. If anything remains, the spec is not ready.>
```

Notes:
- Keep every **Then** observable and unambiguous — if a downstream agent couldn't write a test from it, it's not done.
- Criteria are implementation-free: no data structures, no function names, no "how."
- The **Open questions** section must be empty for a spec to reach `status: approved`.

## After writing

Tell the user where the spec was saved. Do not begin implementation or offer to write tests unless the user separately asks — that's a different task. Don't pad the ending.
