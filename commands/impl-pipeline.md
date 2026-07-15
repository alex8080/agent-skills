---
description: Run the three-agent spec-implementation pipeline (implement → acceptance tests → review) over an approved spec, with the orchestrator verifying green between stages.
argument-hint: <path/to/spec.md>
---

# Spec Implementation Pipeline

Drive an approved spec to reviewed, green, uncommitted code using three sequential sub-agents plus your own verification between and after each stage.

**Target spec:** `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask which spec in `docs/spec/` to run against and stop until answered. Read the spec fully before spawning anything — it is the contract every agent works from.

## Language-agnostic — the project's CLAUDE.md defines the tooling

This command works with any language. Do NOT assume a toolchain. **Before anything else, read the project's root `CLAUDE.md` (plus any nested `CLAUDE.md` the spec touches)** and extract:

- **The verification suite / definition of done** — the ordered set of commands (build/compile, lint, format-check, test) that must all run clean/green. Use exactly these commands; do not substitute your own.
- **The public surface** acceptance tests drive (e.g. a CLI entrypoint, an HTTP client, a library API, an ingest path).
- **The test-layer convention** — where acceptance tests vs. unit tests live and how they're named.
- **Which docs** to update when a change alters an endpoint, contract, or subsystem.

If the project's CLAUDE.md does not specify the verification commands or test-layer convention, STOP and ask the user to add them rather than guessing — the whole pipeline hinges on this.

Throughout this document, "**the verification suite**" means exactly those commands as defined in the project's CLAUDE.md.

## Roles are separated on purpose — do not let them blur

1. **Implement** — production code + co-located unit tests ONLY (per the project's test-layer convention). This agent MUST NOT write acceptance tests (nothing new in the acceptance-test location, though it may extend shared test fakes/fixtures if a new interface method forces it). Keeping tests out of the implementer's hands prevents tests that merely re-assert whatever the code happens to do.
2. **Acceptance tests** — end-to-end tests through the public surface the project's CLAUDE.md names, one per spec `### Scenario:` that is *observable*. This agent may extend the acceptance-test location and shared fixtures, but MUST NOT change production source. If a test can only pass by editing production source, it stops and reports a defect rather than "fixing" the code.
3. **Review** — reads the full working-tree diff against the spec + project `CLAUDE.md`/design docs, hunts bugs, checks disciplined-coding adherence, and runs the verification suite itself. Review only — no code changes.

## Non-negotiable rules to pass into every agent

- **Coding agents (1 and 2) MUST invoke `/disciplined-coding-guidance` first** and follow it (SRP, no magic numbers → named constants, functional-core/imperative-shell split, error handling, immutability, test-as-specification).
- A sub-agent cannot ask the user. So instruct each: when you hit a design tradeoff the skill says isn't yours to decide unilaterally (SRP violation, internal DI, a new interface method, changed error/atomicity semantics), pick the option most consistent with existing codebase conventions, implement it, and **document the decision + reasoning in your final report** for human review.
- **Definition of done for every coding stage:** every command in the project's verification suite runs clean/green. **Do NOT commit** — leave changes in the working tree.
- Update the project docs named in its CLAUDE.md where the change alters an endpoint, interface, or subsystem status.

## Your job as orchestrator — this is where the value is, not the fan-out

### Step 0 — test-layer triage (before spawning agent 1)

After reading the spec and BEFORE launching the implementer, map **every** spec `### Scenario:` to a test layer and target file, per the project's test-split convention (root `CLAUDE.md`, plus any nested `CLAUDE.md` the spec touches):

- **(a) new observable input→output behavior** → acceptance test (through the public surface the project's CLAUDE.md names) — owned by agent 2;
- **(b) pure-logic edge case** (parsing, counting, boundaries, normalization) → unit test — owned by agent 1;
- **(c) already covered by the existing suite** → map to the existing test, keep green, no new test — duplication is a defect, not thoroughness.

Rule of thumb: if a scenario's expected outcome is only observable by inspecting *how many calls happened* or *how a string was parsed*, it's a unit test, not acceptance. Contract/wiring/auth/UX flows are acceptance.

Feed the mapping into **both** agents' prompts: agent 1 gets its unit-test rows (and must not write the acceptance rows); agent 2 gets the full mapping and must return a scenario→`file::test_name` traceability table against it, covering ALL scenarios (including the mapped-to-existing ones).

### Between and after each stage

Run the three agents **sequentially** (each depends on the prior). Between and after each stage:

- **Re-verify green yourself.** Do not trust an agent's "all tests pass" claim — run the project's verification suite and read the real output before proceeding. IDE/language-server diagnostics injected mid-run are often stale mid-refactor state; the authoritative signal is a clean verification run you launched. If a background agent stalls on an API error mid-task, resume it via SendMessage (its context is intact) rather than restarting.
- **Relay flagged interpretation risks forward.** The implementer will flag spec ambiguities it had to resolve (invented schemas, changed skip/atomicity semantics, occurrence-vs-distinct counting, etc.). Pass those explicitly to the acceptance-test agent and tell it to read the implementation and assert the *implemented* behavior on those points — never independently invent a conflicting shape, and flag (not silently fix) any genuine spec divergence.
- **Re-check the Step 0 triage before launching agent 2.** The implementer's report may reveal a scenario landed at a different layer than triaged (e.g. logic that ended up in a handler, or a new policy worth pinning); update the mapping and hand agent 2 the revised version, noting what changed and why.

## Closing the loop

After the reviewer returns:

- Do a final verification-suite run yourself.
- Separate the reviewer's findings into **must-fix-before-mergeable** vs **optional**. For a must-fix that is a genuine code bug, spawn a focused fix agent (with `/disciplined-coding-guidance`) and re-verify. For a must-fix that is actually a **spec/design decision** (a spec-internal contradiction, a changed contract), do NOT have an agent guess — surface it to the user with a concrete recommendation and let them decide before implementing.
- Report to the user: what landed, the reviewer's verdict, any decisions made, remaining optional items, and confirm the final verification state. Do not commit unless the user asks.
