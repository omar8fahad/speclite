---
description: "Phase 5 - Implement: execute tasks.md end to end, then run a final gap-check - documenting test runs, screenshots, and other evidence in logs/ along the way."
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

2. Read `spec.md`, `plan.md`, `tasks.md`, and everything under `references/`. If
   `specs/ARCHITECTURE_MAP.md` and `specs/FILE_INDEX.md` exist (the optional Project Map has
   been built), check them too before writing new code - unlike the constitution (read once at
   the start), the map is useful continuously through this whole phase: before creating a new
   file or function, a quick look can confirm whether something similar already exists and
   where it should live, cutting down on redundant searching and inconsistent placement.

3. Execute `tasks.md` phase by phase:
   - Respect `[P]` parallel markers and file-level dependencies; run sequential tasks in order.
   - Mark each task `[X]` in `tasks.md` immediately after it completes - don't batch this at the
     end.
   - If a non-parallel task fails, halt, report the error with enough context to debug, and
     suggest a fix. For failed `[P]` tasks, continue the others and report the failure.
   - **If the task list is large**, it's completely fine for execution to span multiple turns
     or even multiple sessions - `status` picks up exactly where tasks were left unchecked.
     Don't rush or silently skip verification just to appear "done" in one turn; a checkpoint
     partway through (e.g. "Setup and Core are done, Polish is next") is a better outcome than
     a rushed, shallow pass through everything.

4. **Document as you go, organized by type, inside `<FEATURE_DIR>/logs/`.** This is a single
   flat folder - free-form evidence only, never used to decide whether the phase is done (that
   signal lives in `tasks.md` itself - see step 5). Create subfolders as the content calls for
   them, for example:
   - `logs/test-results/` - automated test/terminal output
   - `logs/screenshots/` - app/web UI captures proving a task works, including any screenshot
     the user already shared earlier in this conversation - save a copy here instead of letting
     it exist only in the chat history
   - `logs/notes/` - a brief summary of any notable decision or exchange from this session that
     isn't already captured in `spec.md`/`plan.md`/`tasks.md`

   Don't dump ungrouped files loose in `logs/` - organize by type. `logs/` is a good candidate
   for the user's own `.gitignore` (see `README.md`) since it tends to hold large or disposable
   evidence rather than source of truth.

5. **Final gap-check** (this is speclite's replacement for Spec Kit's standalone `converge`
   command): once every task is `[X]`, re-read `spec.md`'s Functional Requirements and Success
   Criteria against the code you just wrote.
   - If something is still missing or only partially done, append new checklist items under a
     `## Follow-up` heading at the bottom of `tasks.md` (never renumber or touch existing tasks)
     and **implement those too** before finishing - don't just report the gap and stop.
   - Once genuinely nothing remains, **tick the `Final Gap-Check` checkbox** in `tasks.md` -
     this is speclite's completion signal for this phase, read directly by `status`. Don't tick
     it as a formality or before follow-ups are actually done.

6. **After reporting completion**, this is a natural breakpoint to mention the optional Project
   Map (see `commands/speclite.map.md`) - especially if the feature was substantial. Offer it,
   don't run it automatically: e.g. "Want me to update the project map with this feature?" If
   the user already declined earlier in this session, don't ask again.

## Done When

- [ ] Every task in `tasks.md` is `[X]`, including any follow-ups appended during the final
      gap-check
- [ ] Implementation checked against `spec.md`'s Functional Requirements and Success Criteria
- [ ] `Final Gap-Check` checkbox ticked in `tasks.md`
- [ ] Supporting evidence (test output, screenshots, notes) filed under `logs/<type>/`, not
      loose
- [ ] Completion summary reported to the user, with the Project Map offered as an optional
      follow-up
