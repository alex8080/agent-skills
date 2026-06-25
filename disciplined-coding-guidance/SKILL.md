---
name: disciplined-coding-guidance
description: Engineering discipline for writing production code in any language. Use this skill whenever you are writing, generating, or substantially refactoring code — not just when asked for a "review." It enforces single-responsibility, no magic numbers, error handling, naming, immutability, functional-core/imperative-shell structure, and test-as-specification coverage. Trigger it for any non-trivial coding task (implementing a function, module, feature, or fix), even if the user doesn't name these principles. The key behavioral rule is that certain design tradeoffs (violating SRP, introducing internal dependency injection) are NOT the agent's to decide unilaterally — the agent must stop, present pros and cons with a recommendation and reasoning, and ask the user.
---

# Disciplined Coding

Guidance for writing production code that is correct, readable, and verifiable in any language. Follow the host language's idioms and community conventions first; these principles sit on top of, never against, idiomatic style.

The aim is code whose tests read as a specification, whose structure reveals intent, and whose tradeoffs were chosen deliberately — not by accident.

## The two decisions you may not make alone

Two design choices have no single right answer and materially shape readability. You must NOT resolve them silently. Stop, lay out the concrete pros and cons **for this specific case**, then state your recommendation and explain why you chose it — the reasoning that tips this case one way, not a generic platitude. The recommendation is advisory — the user decides — so keep the fork genuine: present both sides honestly rather than building a case for your pick, and do not proceed until the user confirms.

1. **Violating SRP.** If the cleanest path forward gives a unit more than one reason to change, do not just do it, and do not contort the code to avoid it. Surface it: what the merged responsibility buys (e.g. locality, fewer moving parts) vs. costs (harder to test, two change-axes coupled). Let the user decide.

2. **Internal dependency injection.** Injecting collaborators that have no reason to vary adds indirection and hurts readability. At true I/O boundaries (DB, clock, network, filesystem, randomness) inject by default — that is what makes the imperative shell testable and is rarely controversial. For *internal* collaborators, treat it like SRP: present pros and cons, ask.

When in doubt about whether something crosses these lines, ask rather than assume. A short question is cheaper than a silent wrong call.

## Structure: functional core, imperative shell

Prefer pushing decision and transformation logic into a pure core (deterministic, no I/O, no hidden state) and concentrating side-effects in a thin outer shell.

- A genuinely pure core needs **no** dependency injection — test it with plain values, no mocks. This is what keeps DI confined to a small, obvious perimeter.
- Inject I/O ports into the shell so the shell stays testable too.

This is a **default with an escape hatch, not a mandate.** It shines when logic and I/O separate cleanly. It strains when work is inherently I/O-interleaved (streaming, paginated fetch-process-fetch) — forcing purity there contorts control flow, and an imperative shell calling injected ports reads better. Prefer the functional core where logic and I/O separate cleanly; do not force it where they are genuinely braided.

## Single responsibility (and function length)

A unit should have one reason to change. The signal is *number of reasons to change*, not line count.

- A long, linear, single-purpose function is fine. **Do not** extract it into a method-bearing object or helper soup just to hit a length target — that indirection usually hurts readability more than the length did.
- Extract only when there is genuine reuse, or a second responsibility is hiding inside. The latter is an SRP fork — see above.
- Keep a single abstraction level within a function; mixing high-level orchestration with low-level fiddling is a stronger smell than length.

## No magic numbers

No unexplained literals in logic. Give every meaningful constant a name that states its meaning and, where useful, its unit (`MAX_RETRY_ATTEMPTS`, `TIMEOUT_MS`, `DEFAULT_PAGE_SIZE`). Exceptions: genuinely self-evident values in context (`0`, `1`, an index step) and well-known math. When unsure, name it.

## Error handling

Errors are never silently swallowed. Use the language's principled mechanism — errors as values (`Result`/`Either`/multi-return) or typed exceptions — and handle or propagate explicitly. An empty catch / discarded error is a defect. Validate inputs at boundaries (fail fast) and assert invariants the core relies on. Push error-prone I/O to the shell so the core can assume validated data.

## Immutability and shared state

Prefer immutable data and pure transformations. Avoid shared mutable state and hidden globals — they defeat local reasoning and make tests order-dependent. Confine necessary mutation to the smallest possible scope, ideally the shell.

## Naming

Names carry the design. Reveal intent: what a thing *is* or *does*, not how it is implemented. Avoid abbreviations that aren't domain-standard. A name that needs a comment to be understood is usually the wrong name — fix the name first.

## Comments

Sparse, and only where the code cannot speak for itself. Comments explain **why** — a non-obvious tradeoff, a workaround, a constraint, a reference. Never narrate **what** the code plainly does. If you feel the urge to comment *what*, prefer renaming or restructuring so the comment is unnecessary.

## Tests as specification

Tests are the executable specification of behavior for whoever reads the code next. Aim for high **functional** coverage — every function's behavior pinned — not a 100% line-coverage target.

Rules:
- **Every function gets at least one unit test** covering its behavior. The pure core is the easy, high-value target — test it with plain values.
- **Behavioral requirements beyond a simple input→output table get their own dedicated test.** If a function must, e.g., be idempotent, preserve ordering, be retry-safe, enforce a limit, or emit an event — write a test named for that requirement so the spec is visible. A reader should learn the contract from the test names.
- Name tests for the behavior they assert, not the function mechanics (`returns_empty_for_no_matches`, `is_idempotent_under_replay`), so the suite reads as documentation.
- **Consider whether an integration test is required.** Unit tests pin core logic; they do not prove the shell wires real I/O correctly. When the unit crosses a real boundary (DB schema, external API contract, serialization, transaction semantics, concurrency), call it out and propose an integration test. State explicitly when you judge one is *not* needed and why.

## Working rhythm

1. Sketch the shape; identify the core vs. shell split.
2. Spot SRP / internal-DI forks **before** writing — if present, stop, present pros/cons with a recommendation, and ask.
3. Write the core (pure), then the shell (injected ports).
4. Write tests as you go: behavior coverage first, then the named tests for extra behavioral requirements.
5. Name the integration-test decision out loud.
6. Re-read with fresh eyes for magic numbers, swallowed errors, and comments that should be names.
