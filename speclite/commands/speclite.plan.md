---
description: "Phase 3 - Plan: write the implementation plan, then run the Pre-Implementation Checklist quality gate inline."
---

## User Input

```text
$ARGUMENTS
```

Consider this input (tech stack preferences, constraints, etc.) before proceeding, if not empty.

## Outline

1. Run (from the repo root):
   - Linux/macOS: `python .speclite/scripts/python/setup_stage.py --json`
   - Windows: `.speclite/scripts/powershell/setup-stage.ps1 -Json`

   Parse `SPEC_FILE`, `PLAN_FILE`, `PRINCIPLES_FILE`, `REFERENCES`. The script fails with a
   clear error if `spec.md` doesn't exist yet, or still has open `[NEEDS CLARIFICATION]`
   markers - if so, send the user back to `/speclite.specify`.

2. Read `SPEC_FILE` and everything listed in `REFERENCES` (grouped by subfolder - `PRD/`,
   `images/`, etc.). Read `PRINCIPLES_FILE` if it's set - that's the project's one constitution
   at `.speclite/memory/principles.md`, if it exists.

3. Fill `PLAN_FILE` using `plan-template.md`'s structure: technical context, architecture, data
   model / interfaces if applicable.

4. **Checklist** - read `.speclite/templates/checklist-guide.md` for the full rules ("unit tests
   for requirements", not implementation tests), then work through the Pre-Implementation
   Checklist section already in `plan-template.md`. **Fix problems immediately instead of
   deferring them**: if a box can't be honestly ticked because of a `[NEEDS CLARIFICATION]`
   marker or an ambiguous requirement, resolve it right now by editing `spec.md` or `plan.md`
   directly.

   **Exception - never do this for a MUST-rule conflict.** If the plan conflicts with a
   non-negotiable rule in `principles.md`, that box stays unticked. Do not edit the plan or
   spec to quietly route around it. Stop, tell the user exactly which rule and where the
   conflict is, and let them choose: change the plan to comply, or consciously amend the rule
   by running `/speclite.constitution`. Don't continue to `/speclite.tasks` until that's
   resolved one way or the other - this is the one thing in this phase that always needs the
   user's explicit call, never a guess.

5. Run:
   - Linux/macOS: `python .speclite/scripts/python/log_check.py --phase plan --status PASS --summary "<checklist result>"`
   - Windows: `.speclite/scripts/powershell/log-check.ps1 -Phase plan -Status PASS -Summary "<checklist result>"`

   Use `WARN` if any checklist item was intentionally left unticked pending user input.

## Done When

- [ ] `plan.md` written
- [ ] Pre-Implementation Checklist fully checked, or unchecked items explicitly called out to
      the user with a reason
- [ ] Check recorded in the log
- [ ] User pointed at the next step: `/speclite.tasks`
