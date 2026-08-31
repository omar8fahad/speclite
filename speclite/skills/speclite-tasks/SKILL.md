---
name: "speclite-tasks"
description: "Phase 4 - Tasks: generate the dependency-ordered task list, then run the analyze consistency pass inline before implementation begins."
compatibility: "Requires speclite project structure with .speclite/ directory"
metadata:
  author: "speclite"
  source: "commands/speclite.tasks.md"
---

## User Input

```text
$ARGUMENTS
```

Consider this input before proceeding, if not empty.

## Outline

1. Run (from the repo root):
   - Linux/macOS: `python .speclite/scripts/python/setup_tasks_stage.py --json`
   - Windows: `.speclite/scripts/powershell/setup-tasks-stage.ps1 -Json`

   Parse `SPEC_FILE`, `PLAN_FILE`, `TASKS_FILE`. The script fails if `plan.md`'s
   Pre-Implementation Checklist still has unchecked items - if so, send the user back to
   `/speclite.plan`.

2. Generate `TASKS_FILE` from `tasks-template.md`: dependency-ordered, strict checkbox format
   `- [ ] T001 [P?] Description with exact file path`, grouped into phases (Setup -> Core ->
   Polish). Mark tasks `[P]` only when they touch different files and have no unmet dependency.
   Map every Functional Requirement and Success Criterion in `spec.md` to at least one task.

   **If the plan is large** (many components, a big surface area), it's fine for this
   breakdown to take multiple turns to get right - don't compress a genuinely large task list
   into something shallow just to move faster. A thorough breakdown now is cheaper than
   discovering missing tasks mid-implementation.

3. **Analyze** - read `.speclite/templates/analyze-guide.md` for the full rules, then
   cross-check `spec.md`, `plan.md`, and `tasks.md` for duplication, ambiguity,
   underspecification, constitution conflicts, coverage gaps, and inconsistency. **Fix what you
   can fix directly** in any of the three files right now.

   **Exception**: a `principles.md` MUST violation is never fixed by editing around it - stop
   and tell the user exactly which rule and where the conflict is, and point them at
   `/speclite.constitution` if they want to amend the rule itself. A primary-story requirement
   with zero task coverage is also CRITICAL and stops the phase.

4. Record the outcome directly in `tasks.md`'s **Analysis Pass** section: list any HIGH/MEDIUM/
   LOW findings still open (or write "None"), then **tick the `Analysis complete` checkbox** -
   this is speclite's completion signal for this phase, read directly by `status`. Don't tick it
   as a formality; only once you're genuinely confident no CRITICAL issue remains. It's fine for
   analysis on a large plan to take the time (and turns) it needs before this box is ticked.

## Done When

- [ ] `tasks.md` written, every requirement/success criterion traceable to at least one task
- [ ] Analyze pass complete, findings fixed inline or explicitly listed with severity
- [ ] `Analysis complete` checkbox ticked in `tasks.md`
- [ ] User pointed at the next step: `/speclite.implement`
