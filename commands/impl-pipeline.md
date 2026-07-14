---
description: Run the three-agent spec-implementation pipeline (implement → acceptance tests → review) over an approved spec, with the orchestrator verifying green between stages.
argument-hint: <path/to/spec.md>
---

# Spec Implementation Pipeline

Drive an approved spec to reviewed, green, uncommitted code using three sequential sub-agents plus your own verification between and after each stage.

**Target spec:** `$ARGUMENTS`

If `$ARGUMENTS` is empty, ask which spec in `docs/spec/` to run against and stop until answered. Read the spec fully before spawning anything — it is the contract every agent works from.

## Roles are separated on purpose — do not let them blur

1. **Implement** — production code + in-module unit tests ONLY. This agent MUST NOT write acceptance tests (nothing new in `tests/`, though it may extend `tests/common/` fakes if a new trait method forces it). Keeping tests out of the implementer's hands prevents tests that merely re-assert whatever the code happens to do.
2. **Acceptance tests** — end-to-end tests through the public surface (HTTP `Client` / `cli::run_*` / ingest path), one per spec `### Scenario:` that is *observable*. This agent may extend `tests/` and `tests/common/`, but MUST NOT change production `src/`. If a test can only pass by editing `src/`, it stops and reports a defect rather than "fixing" the code.
3. **Review** — reads the full working-tree diff against the spec + `CLAUDE.md`/`DESIGN.md`, hunts bugs, checks disciplined-coding adherence, and runs the build itself. Review only — no code changes.

## Non-negotiable rules to pass into every agent

- **Coding agents (1 and 2) MUST invoke `/disciplined-coding-guidance` first** and follow it (SRP, no magic numbers → named constants, functional-core/imperative-shell split, error handling, immutability, test-as-specification).
- A sub-agent cannot ask the user. So instruct each: when you hit a design tradeoff the skill says isn't yours to decide unilaterally (SRP violation, internal DI, a new trait method, changed error/atomicity semantics), pick the option most consistent with existing codebase conventions, implement it, and **document the decision + reasoning in your final report** for human review.
- **Definition of done for every coding stage:** `cargo build --all-targets`, `cargo clippy --all-targets`, `cargo fmt --check`, `cargo test` all clean/green. **Do NOT commit** — leave changes in the working tree.
- Update `docs/api.md` / `docs/architecture.md` where the change alters an endpoint, trait, or subsystem status.

## Your job as orchestrator — this is where the value is, not the fan-out

### Step 0 — test-layer triage (before spawning agent 1)

After reading the spec and BEFORE launching the implementer, map **every** spec `### Scenario:` to a test layer and target file, per the project's test-split convention (root `CLAUDE.md`, plus `web/CLAUDE.md` when the spec touches the frontend):

- **(a) new observable input→output behavior** → acceptance test (`tests/*.rs` through `Client`/`cli::run_*`, or web page/fetch-contract tests) — owned by agent 2;
- **(b) pure-logic edge case** (parsing, counting, boundaries, normalization) → in-module unit test — owned by agent 1;
- **(c) already covered by the existing suite** → map to the existing test, keep green, no new test — duplication is a defect, not thoroughness.

Rule of thumb: if a scenario's expected outcome is only observable by inspecting *how many calls happened* or *how a string was parsed*, it's a unit test, not acceptance. Contract/wiring/auth/UX flows are acceptance.

Feed the mapping into **both** agents' prompts: agent 1 gets its unit-test rows (and must not write the acceptance rows); agent 2 gets the full mapping and must return a scenario→`file::test_name` traceability table against it, covering ALL scenarios (including the mapped-to-existing ones).

### Between and after each stage

Run the three agents **sequentially** (each depends on the prior). Between and after each stage:

- **Re-verify green yourself.** Do not trust an agent's "all tests pass" claim — run `cargo build --all-targets`, `cargo clippy --all-targets`, `cargo fmt --check`, `cargo test` and read the real output before proceeding. IDE/rust-analyzer diagnostics injected mid-run are often stale mid-refactor state; the authoritative signal is a clean `cargo` run you launched. If a background agent stalls on an API error mid-task, resume it via SendMessage (its context is intact) rather than restarting.
- **Relay flagged interpretation risks forward.** The implementer will flag spec ambiguities it had to resolve (invented schemas, changed skip/atomicity semantics, occurrence-vs-distinct counting, etc.). Pass those explicitly to the acceptance-test agent and tell it to read the implementation and assert the *implemented* behavior on those points — never independently invent a conflicting shape, and flag (not silently fix) any genuine spec divergence.
- **Re-check the Step 0 triage before launching agent 2.** The implementer's report may reveal a scenario landed at a different layer than triaged (e.g. logic that ended up in a handler, or a new client-side policy worth pinning); update the mapping and hand agent 2 the revised version, noting what changed and why.

## Closing the loop

After the reviewer returns:

- Do a final `cargo` verification yourself.
- Separate the reviewer's findings into **must-fix-before-mergeable** vs **optional**. For a must-fix that is a genuine code bug, spawn a focused fix agent (with `/disciplined-coding-guidance`) and re-verify. For a must-fix that is actually a **spec/design decision** (a spec-internal contradiction, a changed contract), do NOT have an agent guess — surface it to the user with a concrete recommendation and let them decide before implementing.
- Report to the user: what landed, the reviewer's verdict, any decisions made, remaining optional items, and confirm the final `cargo` state. Do not commit unless the user asks.
