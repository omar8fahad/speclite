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

3. **Analyze** - read `.speclite/templates/analyze-guide.md` for the full rules, then
   cross-check `spec.md`, `plan.md`, and `tasks.md` for duplication, ambiguity,
   underspecification, constitution conflicts, coverage gaps, and inconsistency. **Fix what you
   can fix directly** in any of the three files right now.

   **Exception**: a `principles.md` MUST violation is never fixed by editing around it - stop
   and tell the user exactly which rule and where the conflict is, and point them at
   `/speclite.constitution` if they want to amend the rule itself. A primary-story requirement
   with zero task coverage is also CRITICAL and stops the phase. Record the outcome in
   `tasks.md`'s **Analysis Pass** section - "Clean" if nothing remains, or a short list of open
   findings with severity.

4. Run:
   - Linux/macOS: `python .speclite/scripts/python/log_check.py --phase tasks --status PASS --summary "<N tasks, analyze result>"`
   - Windows: `.speclite/scripts/powershell/log-check.ps1 -Phase tasks -Status PASS -Summary "<N tasks, analyze result>"`

   Use `WARN` if analyze found non-critical findings that are still open.

## Done When

- [ ] `tasks.md` written, every requirement/success criterion traceable to at least one task
- [ ] Analyze pass complete, findings fixed inline or explicitly listed with severity
- [ ] Check recorded in the log
- [ ] User pointed at the next step: `/speclite.implement`
