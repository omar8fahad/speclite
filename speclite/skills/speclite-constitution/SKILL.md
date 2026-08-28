---
name: "speclite-constitution"
description: "Phase 1 - Constitution: create or amend the ONE project-wide set of non-negotiable principles, matching Spec Kit's own constitution model."
compatibility: "Requires speclite project structure with .speclite/ directory"
metadata:
  author: "speclite"
  source: "commands/speclite.constitution.md"
---

## User Input

```text
$ARGUMENTS
```

Consider this input before proceeding, if not empty - it may already contain principles the
user wants recorded.

## Philosophy

This matches Spec Kit's own constitution model directly: **one file for the entire project**,
never per-feature. A rule marked **MUST** is non-negotiable - once written here, no later phase
(`plan`, `tasks`, `implement`) is allowed to silently edit a spec, plan, or task to route around
a conflict with it. When a conflict is found later, that phase stops and sends the user back
here. Changing a principle is always a conscious, explicit act done in this phase, never a side
effect of something else.

(speclite does simplify one thing versus Spec Kit's original: no semantic-version bump or
Sync Impact Report ceremony on every edit - `principles.md` is a plain file you edit directly.
The non-negotiable, stop-and-amend philosophy above is kept in full; only the versioning
bureaucracy around it is dropped.)

## When this phase runs

The manager (`SKILL.md`) routes here in two situations:

1. **Start of a brand-new project** - `status` reports `NEXT_PHASE: constitution` because no
   feature exists yet and `.speclite/memory/principles.md` doesn't either. This is recommended
   but not mandatory - if the user would rather skip straight to a feature, honor that and go to
   `/speclite.specify` instead; principles.md can always be created later.
2. **A later phase found a MUST-rule conflict** and sent the user back here on purpose to
   amend a principle. In this case, the user already knows why they're here - don't re-ask the
   scope question or anything else, just help them edit the specific rule in conflict.

## Outline

1. Run (from the repo root):
   - Linux/macOS: `python .speclite/scripts/python/constitution_setup.py --json`
   - Windows: `.speclite/scripts/powershell/constitution-setup.ps1 -Json`

   Parse `PRINCIPLES_FILE` and `ALREADY_EXISTED`. This script never overwrites an existing file
   - it only creates one from the template if none exists yet.

2. If `ALREADY_EXISTED` is `false`: open `PRINCIPLES_FILE` and help the user fill in real
   content - non-negotiable **MUST** rules, strong **SHOULD** defaults, and anything explicitly
   out of scope for the project. Keep it short - a handful of rules that actually matter, not a
   policy manual. Don't leave the template's bracketed placeholders unfilled.

3. If `ALREADY_EXISTED` is `true`: this is an amendment. Tell the user what's already there,
   ask what needs to change, and edit the specific rule(s) directly - don't recreate the file
   from scratch.

4. Run:
   - Linux/macOS: `python .speclite/scripts/python/log_check.py --phase constitution --status INFO --summary "<one line>"`
   - Windows: `.speclite/scripts/powershell/log-check.ps1 -Phase constitution -Status INFO -Summary "<one line>"`

## Done When

- [ ] `.speclite/memory/principles.md` exists with real content (or was intentionally skipped,
      in which case go straight to `/speclite.specify`)
- [ ] If this run was an amendment triggered by a conflict found in another phase, the specific
      rule in conflict was addressed
- [ ] Check recorded in the log
- [ ] User pointed at the next step: `/speclite.specify`
