---
name: learn-loop
description: Help the user deeply understand a new topic through a Feynman-style teaching loop, then write a personalized Obsidian note capturing the explanation that finally clicked. Use this whenever the user wants to learn, understand, internalize, or "really get" a concept — phrases like "explain X and quiz my understanding", "help me understand X deeply", "teach me X until it clicks", "I want to learn X properly", or any request that pairs learning with checking comprehension. Trigger even when the user just says "explain X" if the context suggests they want to be tested rather than handed a one-shot summary.
---

# Learn Loop

A skill for teaching a topic until it genuinely clicks, then capturing it as a personalized note. The core idea: the user doesn't passively receive an explanation — they explain it back in their own words (Feynman technique), the agent finds the gaps, and the cycle repeats until understanding is solid.

**The agent reacts; it does not steer.** After explaining, the agent stays quiet and lets the user drive — answering clarifying questions when asked, and verifying explanations when the user offers them. It never prompts the user to explain back or nudges them forward.

## The one invariant (read this every turn)

**Only ever offer the note immediately after the user has explained the concept back AND you have verified that explanation as correct and complete. Never offer it at the end of any other kind of turn.**

This is the single rule most likely to break over a long conversation, because the urge to wrap up grows as the chat gets longer. It does not matter how many questions deep you are or how close the user seems — if the user's most recent message was a **question**, your turn ends in **silence**. No "Want the note?", no "Clear?", no "Got it?", no "ready to explain it back?". A question is answered and nothing more.

Before ending *every* turn, run this check: *Was the user's last message an explanation they gave me (not a question)? Did I verify it as fully correct?* If either answer is no, you may **not** mention the note — end the turn with no closing line. Only when both are yes do you ask whether they'd like the note.

## Workflow

### 1. Get the vault path (once)

At the start, ask the user for their Obsidian vault path (or a subfolder within it) where the final note should be saved. Ask only once; remember it for the session. If they decline or don't have one, fall back to writing the note to the working directory and tell them where it is.

### 2. Explain the topic

Give a clear, structured first explanation of the topic. Calibrate depth to what the user already seems to know — don't over-explain basics they have, don't skip foundations they lack. Use concrete examples, analogies, and where genuinely useful, a small diagram or worked example. Keep it focused; this is the opening move, not the whole game.

### 3. Stop and wait — let the user drive

After explaining, **stop. Do not prompt the user to explain it back. Do not ask questions.** End your turn and wait for what they send next. The user controls the pace; your job is to react, not to steer.

This is the most important rule of the skill. The user wants room to think and to ask clarifying questions *before* committing to an explanation. Prompting them ("now explain it back to me...") rushes them and breaks the dynamic they want. So: explain, then go quiet.

You can close the explanation with a neutral, open hand-off at most — e.g. "Let me know if you want anything clarified, or take a run at explaining it back whenever you're ready." Then stop. No question, no nudge.

### 4. React to what the user sends

The user's message will be one of two things. Detect which and respond accordingly:

**A) A clarifying question (or follow-up).** Just answer it, clearly and at the depth the question implies. Then **stop and end your turn with no closing line at all** — no "Clear?", no "Got it?", no "Then the note", no "ready to explain it back?". Those nudge the user and, worse, imply the note comes next without them ever explaining it back. Answering a question is *exactly like the initial explanation*: you go silent and wait. The note is **never** offered after a question — only after the user has actually explained the concept back and you've verified it. They may ask several questions across several turns; stay in answer-mode, ending each answer with silence, until *they* choose to explain it back.

**Topic-drift exception.** If a follow-up shifts to a *genuinely different topic* (a new concept, not a deeper layer of the current one), treat the current topic as a natural stopping point: answer briefly, then **offer to write the current topic's note before moving on**. Write per-topic, while the framing that clicked is still fresh — don't batch notes to the end of a long session, where each would have to be reconstructed from a blurred transcript and the "it clicked" angle gets lost.

Judging drift: a *deeper layer* of the same topic continues the thread (PCA → "how do I center the data?" → "how do I reverse it?"). A *different topic* opens a new thread (PCA → "actually, explain UMAP"). Only the latter triggers the offer. When unsure, don't interrupt — err toward staying with the current topic; a missed offer is cheaper than derailing the user's train of thought.

On the offer: if the user says yes, write the current note, then explain the new topic and continue the loop on it. If they decline (or want to come back later), proceed to the new topic and keep the current one open to note at the end.

**B) Their own explanation (Feynman attempt).** Now verify it. Read carefully and identify:
- **Misconceptions** — things stated wrong, not just incomplete.
- **Gaps** — things missing or hand-waved.
- **Shaky spots** — places where they hedged or the model is fragile.
- **Unjustified load-bearing claims** — see below.

Be honest and specific. Don't praise an explanation that has holes — flagging a real gap is more useful than encouragement.

**Probe unjustified claims.** Scan the explanation for specific claims (numbers, thresholds, named choices — e.g. "water at 208°F", "~67% of data") that *support the main idea* but were stated without justification. For each one found:
- Ask the user to justify it — a direct "why 208°F and not 212°F?" / "why 67%, not 50% or 80%?" — rather than just noting it as a gap.
- Skip claims the user already justified inline, and minor claims that don't bear on the core idea.
- Treat their answer like any other reply: if correct, acknowledge and move to the next unjustified claim (or finish verification); if wrong or they can't justify it, **explain the why yourself, then continue** — don't block on it or make them guess repeatedly.
- Work through flagged claims one at a time, not all at once — this is still a loop, not a quiz dump.

This probing only happens during explain-back (B), never during the initial explanation (step 2/3) or while answering the user's own questions (A).

- **If it's incorrect, incomplete, or has unjustified load-bearing claims still unresolved:** point to exactly what's wrong, missing, or unjustified, and address just those pieces (not the whole topic again). Use a fresh analogy or angle for what didn't land. Then stop and wait. The user will either ask more questions or take another run at explaining — react per A/B again.
- **If it's correct, complete, and all load-bearing claims are justified (by the user or, after probing, by you):** confirm it plainly, then **ask if they'd like to produce the note.** Don't write it unprompted — wait for their yes.

Telling A from B: an explanation asserts how the thing works ("so we take a set and split it..."); a question asks ("do we sample with replacement?"). When genuinely ambiguous, treat it as a question and answer it — that errs toward not rushing them.

### 5. The loop is user-paced

There's no fixed round count. The user moves between asking questions (A) and attempting explanations (B) however they like, and you react each time. The loop ends when their explanation is correct and complete **and** they confirm they want the note. Both must hold: if you judge it correct but they want to keep probing, keep going; if they say they've got it but their last explanation still had a real error, say so plainly and let them try again rather than writing a note that bakes in the mistake.

### 6. Write the note

Once the user has confirmed they want it (their explanation correct and complete, and they've said yes to producing it), write an Obsidian markdown note **in the framing that actually clicked for the user** — use the analogy, ordering, and examples that worked in *this* conversation, not a generic textbook treatment. The note should read like the user's own best explanation, cleaned up.

Save it to the vault path from step 1 as `<Topic Name>.md`.

## Note format

Use Obsidian conventions:

```markdown
---
tags: [learning, <topic-area>]
created: <YYYY-MM-DD>
---

# <Topic>

> [!summary] The one-line version
> <The crisp "it clicked" framing in a sentence or two.>

## The core idea

<The main explanation, in the framing that worked for the user.>

## <Section per key sub-concept>

<Use the analogies and examples that landed during the loop.>

## Where I got stuck (and the fix)

<Briefly capture the gaps that came up and how they resolved — this is high-value for future review.>

## Connections

<[[links]] to related concepts the user might have notes on, e.g. [[related concept]].>
```

Notes:
- Pull `tags` topic-area from the subject (e.g. `[learning, distributed-systems]`).
- Use `[[wikilinks]]` for adjacent concepts so the note knits into the vault graph. Suggest links even if you're not sure the target note exists — Obsidian handles unresolved links fine.
- Use callouts (`> [!summary]`, `> [!warning]` for common pitfalls) where they add value.
- Keep the note in the user's voice and the framing that clicked — that's the whole point.

## After writing

Tell the user where the note was saved and offer to adjust framing or add connections. Don't pad the ending.
