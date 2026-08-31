# Analyze Guide (used within `/speclite.tasks`)

*Condensed from Spec Kit's `analyze` command. Run this pass after generating tasks.md and
before handing off to `/speclite.implement` - this is speclite's quality gate between planning
and writing code, so don't skip it even though it isn't a separate top-level command.*

## What to check

Cross-reference `spec.md`, `plan.md`, and `tasks.md`:

- **Duplication** - near-duplicate requirements or tasks that should be merged
- **Ambiguity** - vague adjectives (fast, scalable, secure, intuitive, robust) with no
  measurable criteria; unresolved placeholders (TODO, TKTK, `???`, `<placeholder>`)
- **Underspecification** - requirements with a verb but no object/outcome; tasks referencing
  files or components not defined anywhere in spec.md or plan.md
- **Constitution alignment** - anything conflicting with a MUST rule in
  `.speclite/memory/principles.md` (the one project-wide constitution, if it exists yet)
- **Coverage gaps** - a Functional Requirement or Success Criterion with zero tasks mapped to
  it; a task with no traceable requirement
- **Inconsistency** - terminology drift between files; task ordering that contradicts stated
  dependencies (e.g. an integration task before its prerequisite setup task)
- **Pre-existing implementation** - if `specs/FILE_INDEX.md` exists (the optional Project Map
  has been built), check whether any proposed task duplicates something already indexed there.
  Building the same thing twice is a duplication finding just like a duplicate requirement -
  flag it and consider scoping the task down to what's actually missing instead of a full
  rewrite.

## Severity

- **CRITICAL** - violates a `principles.md` MUST rule, or a requirement with zero coverage that
  blocks a primary user story. **Stop and tell the user before implementing.**
- **HIGH** - duplicate/conflicting requirement, ambiguous security/performance attribute,
  untestable acceptance criterion. Fix inline if possible; otherwise flag clearly.
- **MEDIUM/LOW** - terminology drift, missing non-functional coverage, minor redundancy. Note
  it, don't block on it.

## What to do with findings

Fix what you can fix directly in `spec.md`, `plan.md`, or `tasks.md` right now - that's the
point of pairing analyze with tasks generation instead of running it as a separate later step.

**Exception: a `principles.md` MUST-rule conflict is never fixed by editing spec.md, plan.md,
or tasks.md.** That would be silently routing around a non-negotiable rule. Stop, tell the
user exactly which rule and where it conflicts, and let them choose: change the plan/tasks to
comply, or consciously amend the rule itself via `/speclite.constitution`. Don't proceed to
`/speclite.implement` until that's resolved one way or the other.

Log the outcome (clean, or N findings of which M were fixed inline, or a CRITICAL constitution
conflict awaiting the user) directly in `tasks.md`'s Analysis Pass section, then tick its
`Analysis complete` checkbox once genuinely done.
