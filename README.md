# agent-skills

A collection of Claude Code skills and commands for development workflows and learning. Skills live in `skills/`, slash commands in `commands/`.

## Skills

### `learn-loop`

A Feynman-technique teaching loop that iterates until a concept genuinely clicks, then captures the explanation as a personalized Obsidian note.

The flow: the agent explains a topic, waits for the user to ask questions or attempt an explanation, finds the gaps, and repeats — reacting rather than steering. The note is only written once the user's own explanation is verified as correct and complete. The note uses the framing, analogies, and examples that actually worked in that conversation, not a generic textbook treatment.

**Works well with [StudyBuddy](../StudyBuddy/).** StudyBuddy is a self-hosted server that ingests an Obsidian vault, uses an LLM to generate flashcards from the notes, and schedules reviews via spaced repetition (SM-2). The notes that `learn-loop` writes land directly in the vault — so the understanding loop feeds the retention loop: learn a concept until it clicks → Obsidian note → StudyBuddy flashcards → spaced review.

### `disciplined-coding-guidance`

Engineering discipline for writing production code in any language. Enforces single responsibility, no magic numbers, functional core / imperative shell structure, principled error handling, immutability, and tests-as-specification coverage.

Two design decisions — SRP violations and internal dependency injection — are never resolved silently. The agent stops, presents concrete pros and cons with a recommendation, and asks the user. All other principles are applied directly.

### `acceptance-spec`

Drives a feature to a complete, gap-free acceptance criteria specification *before* any implementation begins. Turns a PRD, ticket, prose description, or rough criteria into a rigorous spec — the deliverable is requirements, not tests or code.

The core discipline is *never assume, always ask*: any gap or ambiguity becomes a question to the user, never a plausible default. The agent drafts spec-level Given/When/Then, then runs a two-layer coverage gate — a breadth checklist (did we forget a category: actors, error paths, auth, concurrency, failure states?) and load-bearing probing (is each criterion actually complete, or does it rest on an unjustified claim?). Nothing proceeds downstream until the user explicitly approves the spec, which is saved to `docs/spec/` structured so a later agent can derive tests from it.

## Commands

### `/impl-pipeline <path/to/spec.md>`

Drives an approved `acceptance-spec` deliverable to reviewed, green, uncommitted code through three sequential sub-agents whose roles stay deliberately separated: **implement** (production code + in-module unit tests only), **acceptance tests** (end-to-end tests through the public surface, no `src/` changes), and **review** (reads the full diff against the spec and `CLAUDE.md`/`DESIGN.md`, no code changes).

The value is in the orchestrator, not the fan-out. Before spawning anything it triages every spec `### Scenario:` to a test layer (acceptance / unit / already-covered) and hands each agent only its rows. Between stages it re-verifies green itself (`cargo build`/`clippy`/`fmt`/`test`) rather than trusting an agent's claim, relays flagged spec-ambiguity resolutions forward so downstream agents assert the *implemented* behavior, and routes reviewer findings — code bugs to a focused fix agent, spec/design decisions back to the user. Nothing is committed; changes are left in the working tree.

Pairs directly with `acceptance-spec`: spec the feature until approved → run `/impl-pipeline` against it.
