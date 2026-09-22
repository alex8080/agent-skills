---
name: code-review
description: Rigorous review of existing code — a diff, PR, file, or module someone hands you to critique. Use whenever the task is to review, audit, or assess code that already exists, rather than to write it. The review's spine is a test-coverage audit: for every function, verify that unit tests exercise the edge cases of each input parameter (empty, null, zero, boundary, max, malformed, wrong type) — a missing edge is a finding, not a nitpick. It also checks SRP, error handling, magic numbers, naming, immutability, and comments. Trigger on "review this PR", "review this code", "audit this diff", "what's wrong with this function", or any request to assess code already written. For authoring new code, use disciplined-coding-guidance instead.
---

# Code Review

Assess code that already exists and report findings. This is the review counterpart to `disciplined-coding-guidance`: that skill governs writing code, this one governs judging it after the fact. The design principles are shared; what differs is posture — here you are auditing someone else's decisions, not making your own.

Follow the host language's idioms first. A finding must be a real defect or a real risk, not a deviation from your personal style. Separate the two explicitly (see Severity).

## The spine: test-coverage audit per parameter

The central job of a review is to answer one question for every function: **if this breaks in production, would a test have caught it?** Line coverage does not answer that. Edge coverage does.

For each function under review, take each input parameter in turn and check that a unit test exercises its failure-prone values:

- **Empty** — empty string, empty collection, empty map.
- **Null / absent** — null, `None`, `nil`, missing optional, unset.
- **Zero and boundary** — `0`, `-1`, `1`, the min and max of the valid range, and the values just outside it (off-by-one).
- **Malformed / wrong shape** — unparseable input, wrong type where the language allows it, mixed encoding, oversized.
- **Domain-specific poison** — the value that is legal to the type system but illegal to the domain (a negative amount, a future timestamp where only past is valid, a self-referential ID).

A parameter whose edges are untested is a **finding**, named as such: *"`transfer(amount, currency)` — no test for `amount = 0` or negative; boundary behavior unspecified."* Do not soften it into a suggestion. The absence of the test is the defect.

Combinations matter where parameters interact. If two parameters have a relationship (a start/end range, a value and its unit, a key and the map it indexes), the edge is the *combination* — flag when the interaction is untested even if each parameter is individually covered.

Trivial functions (pure pass-throughs, branchless getters) don't need exhaustive edge tables — say so and move on rather than padding the report. Reserve the depth for functions that branch, transform, or carry a behavioral contract.

## Beyond input parameters

The per-parameter pass finds the common gaps. Also check:

- **Behavioral contracts.** If a function must be idempotent, preserve ordering, be retry-safe, enforce a limit, or emit an event, is there a test *named for that contract*? A reader should learn the contract from the test names. Missing → finding.
- **Error paths.** Every error branch and every `catch` should have a test proving it fires and does the right thing. An untested error path is where production dies quietly.
- **Integration seams.** Unit tests don't prove the shell wires real I/O correctly. Where the code crosses a real boundary (DB schema, external API contract, serialization, transaction, concurrency), call out whether an integration test exists, and flag its absence.
- **State after failure.** When a function fails partway, what is left behind? If nothing tests the post-failure state, note it.

## What else to review

The rest of the review applies the `disciplined-coding-guidance` principles as a checklist against existing code. For each, a violation is a finding:

- **Single responsibility.** Does a unit have more than one reason to change? Name the two axes. (In review you *report* an SRP violation; you don't need to ask permission — the author already decided. Flag it and let them respond.)
- **Error handling.** Any swallowed error, empty catch, discarded `Result`, or unvalidated boundary input.
- **Magic numbers.** Unexplained literals in logic that should be named constants.
- **Naming.** Names that mislead, abbreviate non-standardly, or need a comment to be understood.
- **Immutability / shared state.** Hidden globals, shared mutable state, mutation reaching beyond the smallest necessary scope.
- **Comments.** Comments that narrate *what* (should be a name/restructure) vs. explain *why* (fine). Flag stale or absent *why* on a non-obvious workaround.
- **Functional core / imperative shell.** Is decision logic tangled with I/O where it could cleanly separate? Note it — but respect that braided I/O (streaming, paginated fetch-process) is sometimes genuinely better as an imperative shell; don't flag that as a defect.
- **Dead code.** Unreachable branches, functions/variables/parameters never used, conditions that can't be false, imports and feature-flag paths with no live caller, commented-out blocks left in. Flag it — dead code hides intent and rots. Distinguish genuinely dead from reachable-only-via-reflection/DI/dynamic-dispatch, which the tooling may not see; note the uncertainty rather than asserting.
- **Simplification.** Redundant conditionals, reinvented stdlib functions, needless intermediate state, over-nested logic that flattens, checks that can't fail. A real simplification improves readability or correctness — Should-fix. Don't manufacture them; only flag where the simpler form is clearly better, not merely different.
- **Language idioms.** Where non-idiomatic code could be written the idiomatic way (Rust `?` over manual match-and-return, iterator over index loop, `match` over nested `if`): flag as **Blocking/Should-fix only when the idiom improves correctness, safety, or genuinely reduces cognitive load.** Otherwise report it as a **Nit** at most — a working non-idiomatic construct is not a defect. Never rewrite to taste; idiom preference is where reviews turn into bikeshedding.

## Concurrency

If the code can run on more than one thread — or handle concurrent requests, callbacks, or async tasks sharing state — audit for concurrency defects. Missing safety here is **Blocking** by default: these bugs are rare-to-reproduce and expensive in production.

Check:
- **Shared mutable state** reached from multiple threads without synchronization — the core race. Name the state and the unguarded access.
- **Check-then-act** races (test a condition, then act on it, with a window between) — needs atomicity, not two steps.
- **Non-atomic compound operations** on data assumed safe (read-modify-write on a "thread-safe" collection is still a race).
- **Lock discipline** — inconsistent lock ordering (deadlock risk), locks held across I/O or callbacks, lock released too early, forgotten lock on one access path.
- **Visibility / memory model** — state published without the language's happens-before guarantee (missing `volatile`/atomic/memory fence where the idiom requires it).
- **Non-thread-safe types used as if safe** — a shared instance of something documented single-threaded. Before asserting a type is unsafe, verify against its current docs rather than memory.
- **Async-specific** — blocking calls on an async runtime, shared state across `.await` points, unhandled task cancellation leaving partial state.

For tests: is the concurrent behavior actually exercised, or only the single-threaded happy path? A race with no test is a finding on top of the race itself. Note that concurrency tests are probabilistic — flag when correctness rests on timing rather than a proven invariant.

If you can't tell whether the code runs concurrently, ask rather than assume — the answer changes the severity of everything above.

## Severity — separate defects from taste

Every finding carries a severity so the author can triage. Do not present a style preference at the same weight as a correctness bug.

- **Blocking** — correctness, security, data-loss, or a missing test for a real failure mode. Must be fixed.
- **Should-fix** — a real weakness (untested edge on a trivial-ish path, SRP violation, swallowed error with low blast radius) that isn't strictly breaking.
- **Nit** — style, naming preference, optional structural improvement. Explicitly labeled so it can be ignored guilt-free.

If you're unsure whether something is a defect or your taste, say so and mark it Nit. Honesty about the line keeps the review trustworthy.

## Output

Lead with a one- or two-line summary: overall assessment and the single most important thing to address. Then findings grouped by severity, most severe first. For each finding: the location, what's wrong, and — for a missing test — the specific edge case(s) to add.

End with what the code does *well*, briefly and only if true. Don't manufacture praise; a review is trusted for its findings, not its bedside manner. Don't pad the ending.
