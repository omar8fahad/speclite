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
`.speclite/templates/`. If everything is clean, say so in one line; only list findings that are
still open (fixed findings don't need to be listed here - they're already reflected above).*

- [Clean / list of open findings with severity]

<!--
  Anything appended below a "## Follow-up" heading was added by /speclite.implement's
  final gap-check (speclite's merged replacement for Spec Kit's /speckit.converge).
  Never renumber or delete tasks above this point once implementation has started.
-->
