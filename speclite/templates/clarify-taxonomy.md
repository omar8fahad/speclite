# Clarification Guide (used within `/speclite.specify`)

*Condensed from Spec Kit's `clarify` command. Read this before asking the user anything.*

## Coverage taxonomy

Scan the draft spec against these categories; a category is Clear / Partial / Missing:

- **Functional Scope & Behavior** - core actions, actors, triggers, expected outcomes
- **Domain & Data Model** - entities, relationships, cardinalities, validation, lifecycle
- **Interaction & UX Flow** - navigation, states, transitions, error/loading states
- **Non-Functional Quality** - performance targets, scale/load, reliability, observability,
  security & privacy, compliance
- **Integration & External Dependencies** - external services, failure modes, data formats
- **Edge Cases & Failure Handling** - negative scenarios, throttling, conflict resolution
- **Constraints & Tradeoffs** - technical constraints, explicit tradeoffs / rejected alternatives
- **Terminology & Consistency** - canonical glossary terms, avoided synonyms
- **Completion Signals** - acceptance criteria testability, measurable definition of done

For each Partial/Missing category, a question is a *candidate* only if the answer would
materially change architecture, data modeling, task decomposition, test design, UX behavior,
operational readiness, or compliance - skip anything that's a stylistic preference or belongs
in the planning phase instead.

## Hard limits

- **Maximum 5 questions total** per spec (retries on the same question don't count as new ones).
- Ask **exactly one question at a time**, in priority order (impact × uncertainty).
- Never reveal future queued questions in advance.

## Question format

Every question:

- Leads with `**Question:**` followed by a full, self-contained interrogative ending in `?`.
  Never use a heading/label/requirement-id as the question itself.
- Immediately followed by one plain-language "why it matters" sentence.

For **multiple-choice** (2-5 mutually exclusive options): pick and state your recommended
option first (`**Recommended:** Option X - <1-2 sentence reasoning>`), then a table:

| Option | Description |
|--------|-------------|
| A | ... |
| B | ... |
| Short | Free-form alternative (<=5 words), if appropriate |

For **short-answer** (no discrete options): state a suggestion first
(`**Suggested:** <answer> - <brief reasoning>`), then note the <=5 word constraint.

The user can accept your recommendation/suggestion by saying "yes", pick a letter, or give
their own short answer.

## Integrating each accepted answer

After each answer, immediately (don't batch):

1. Append one bullet under `## Clarifications > ### Session <today>`: `- Q: <question> → A: <answer>`
2. Apply the answer to the most relevant section (Functional Requirements, Key Entities, Success
   Criteria, Edge Cases, etc.) - replace vague text rather than duplicating it.
3. Save the file.

Stop early if the user says "done"/"good"/"no more", or once critical ambiguities are resolved
- don't force all 5 questions if fewer are needed.

## If nothing needs asking

If the draft has no meaningful ambiguity (or every remaining gap is low-impact), say so plainly
- "No critical ambiguities detected worth formal clarification" - and move straight to
`/speclite.plan`.
