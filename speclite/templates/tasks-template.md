# Tasks: [FEATURE NAME]

**Input**: `plan.md`, `spec.md` · **Feature Directory**: `[FEATURE_DIR]`

Each line below is a checkbox, a zero-padded task ID (T001, T002, ...), an optional `[P]`
parallel marker, and a description with an exact file path.
`[P]` = safe to run in parallel (touches different files, no unmet dependency).

## Phase 1: Setup

- [ ] T001 [project init / config task with file path]

## Phase 2: Core Implementation

- [ ] T002 [P] [model/service/endpoint task with file path]
- [ ] T003 [model/service/endpoint task with file path]

## Phase 3: Polish

- [ ] T004 [tests, docs, cleanup task with file path]

## Dependencies

[Note which tasks block which, e.g. "T003 depends on T002".]

## Analysis Pass

*Filled in by the analyze step of `/speclite.tasks` - see `analyze-guide.md` in
`.speclite/templates/`. This checkbox is speclite's completion signal for this phase - `status`
reads it directly, there is no separate log for it. Don't rush a large or complex plan just to
tick this box quickly; a thorough pass now is cheaper than a bug found later. It's fine for
this analysis to take multiple turns on a large plan - tick the box only when it's genuinely
done.*

- [ ] Analysis complete: no CRITICAL findings remain

[List any HIGH/MEDIUM/LOW findings still open below, or write "None" - fixed findings don't
need to be listed here, they're already reflected above.]

## Final Gap-Check

*Filled in by the final step of `/speclite.implement`, only after every task above (including
any Follow-up tasks appended below) is `[X]`. This is speclite's completion signal for
Phase 5 - `status` reads it directly, there is no separate log. For a large feature, it's fine
for implementation itself to span multiple sessions - `status` picks up exactly where tasks
were left unchecked. Only tick this once the whole feature has genuinely been verified against
spec.md, not as a formality.*

- [ ] Verified against spec.md's Functional Requirements and Success Criteria - no gaps remain

<!--
  Anything appended below a "## Follow-up" heading was added by /speclite.implement's
  final gap-check (speclite's merged replacement for Spec Kit's /speckit.converge).
  Never renumber or delete tasks above this point once implementation has started.
-->
