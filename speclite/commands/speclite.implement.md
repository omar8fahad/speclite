---
description: "Phase 5 - Implement: execute tasks.md end to end, then run a final gap-check - documenting test runs, screenshots, and other artifacts in logs/5-implement/ along the way."
---

## User Input

```text
$ARGUMENTS
```

Consider this input before proceeding, if not empty.

## Outline

1. Run (from the repo root):
   - Linux/macOS: `python .speclite/scripts/python/check_prerequisites.py --json --require-plan --require-tasks`
   - Windows: `.speclite/scripts/powershell/check-prerequisites.ps1 -Json -RequirePlan -RequireTasks`

   Parse `FEATURE_DIR`. If the script errors, send the user back to whichever phase it names.

2. Read `spec.md`, `plan.md`, `tasks.md`, and everything under `references/`.

3. Execute `tasks.md` phase by phase:
   - Respect `[P]` parallel markers and file-level dependencies; run sequential tasks in order.
   - Mark each task `[X]` in `tasks.md` immediately after it completes - don't batch this at the
     end.
   - If a non-parallel task fails, halt, report the error with enough context to debug, and
     suggest a fix. For failed `[P]` tasks, continue the others and report the failure.

4. **Document as you go, organized by type, inside `<FEATURE_DIR>/logs/5-implement/`.** This
   folder is yours to structure - create subfolders as the content calls for them, for example:
   - `logs/5-implement/test-results/` - automated test run output
   - `logs/5-implement/screenshots/` - app/web UI captures proving a task works
   - `logs/5-implement/notes/` - any extra write-up worth keeping (a tricky decision, a
     workaround, something the user should know)

   Only `index.md` inside each phase folder is managed by `log_check` - everything else in
   `logs/5-implement/` is content you place there directly, grouped sensibly. Don't dump
   ungrouped files loose in the folder.

5. **Final gap-check** (this is speclite's replacement for Spec Kit's standalone `converge`
   command): once every task is `[X]`, re-read `spec.md`'s Functional Requirements and Success
   Criteria against the code you just wrote.
   - If something is still missing or only partially done, append new checklist items under a
     `## Follow-up` heading at the bottom of `tasks.md` (never renumber or touch existing tasks)
     and **implement those too** before finishing - don't just report the gap and stop.
   - If nothing remains, say so explicitly; don't add an empty `## Follow-up` heading.

6. Run:
   - Linux/macOS: `python .speclite/scripts/python/log_check.py --phase implement --status PASS --summary "<N/N tasks done, gap-check result>"`
   - Windows: `.speclite/scripts/powershell/log-check.ps1 -Phase implement -Status PASS -Summary "<N/N tasks done, gap-check result>"`

   Use `WARN` if follow-up tasks were needed and completed, `FAIL` if the feature could not be
   completed and work is left undone.

## Done When

- [ ] Every task in `tasks.md` is `[X]`, including any follow-ups appended during the final
      gap-check
- [ ] Implementation checked against `spec.md`'s Functional Requirements and Success Criteria
- [ ] Supporting artifacts (test output, screenshots, notes) filed under
      `logs/5-implement/<type>/`, not loose
- [ ] Check recorded in the log
- [ ] Completion summary reported to the user
