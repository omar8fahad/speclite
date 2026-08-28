---
name: "speclite"
description: "A condensed, 5-phase spec-driven feature-development workflow adapted from GitHub's Spec Kit, with a manager that auto-detects which phase to run next so the user never has to track progress themselves. Phases: constitution -> specify -> plan -> tasks -> implement. Constitution is a single project-wide file, matching Spec Kit's own model - never per-feature, and its non-negotiable MUST rules are never silently edited around. Includes a references/ folder per feature for user-supplied PRDs, images, fonts, sounds, videos, and data, and a logs/ folder per feature with one subfolder per feature-level phase for check history plus any test output, screenshots, or extra docs the agent wants to keep. Use this whenever the user wants to formalize a feature before coding, mentions "spec kit", "spec-driven development", asks to turn a PRD or a rough idea into a spec/plan/tasks, or the project already contains a `.speclite/` directory or a `specs/NNN-*` folder. Trigger it proactively for any non-trivial "build me a feature" request where jumping straight to code would skip requirements and planning. This skill IS the manager - it decides which phase to run, the user does not need to know or remember."
compatibility: "Requires speclite project structure with .speclite/ directory"
metadata:
  author: "speclite"
  source: "SKILL.md"
---

# speclite

A condensed, 5-phase clone of [GitHub's Spec Kit](https://github.com/github/spec-kit), with a
built-in manager so the person using it never has to know the phase order or where they left off.

## You are the manager - always check state first

**Before doing anything else in this skill, run the status script and act on its output.**
Never ask the user "which phase are we in?" or "what should I do next?" - figure it out yourself:

- Linux/macOS: `python .speclite/scripts/python/status.py --json`
- Windows: `.speclite/scripts/powershell/status.ps1 -Json`

The output tells you exactly what to do:

| `NEXT_PHASE` | Meaning | Your action |
|---|---|---|
| `install` | `.speclite/` doesn't exist in this repo yet | See "First use" below, then re-run status |
| `constitution` | Phase 1 needed | Read `.agents/commands/speclite.constitution.md`, execute it |
| `specify` | Phase 2 needed | Read `.agents/commands/speclite.specify.md`, execute it |
| `plan` | Phase 3 needed | Read `.agents/commands/speclite.plan.md`, execute it |
| `tasks` | Phase 4 needed | Read `.agents/commands/speclite.tasks.md`, execute it |
| `implement` | Phase 5 needed | Read `.agents/commands/speclite.implement.md`, execute it |
| `ambiguous` | Multiple features, none active | Ask the user which one (see below) - this is the only routine case where you ask before acting |
| `done` | Feature fully shipped | Tell the user; offer to start a new feature with `/speclite.specify` |

`REASON` is a human-readable one-liner explaining the verdict - relay it to the user briefly so
they know why you're doing what you're doing, instead of silently jumping around.

If `NEEDS_USER_INPUT` is `true` (open `[NEEDS CLARIFICATION]` markers, or an ambiguous
multi-feature repo), that question is part of the target phase itself - ask it as that phase's
first step, don't ask a separate meta-question first.

**Re-run `status` after every phase completes** (each command file ends by logging a check,
which is exactly what `status` reads) and immediately continue to whatever it reports next -
chain phases automatically in one session unless the user wants to stop. This is what lets
someone come back days later, having forgotten everything, and just say "continue" - `status`
picks up exactly where things left off.

## First use in a project: install

If `status` reports `NEXT_PHASE: install` (no `.speclite/` yet), tell the user to place this
whole `speclite/` folder inside their project root, next to their other project files, then run
the installer:

- Linux/macOS: `python speclite/install.py`
- Windows: `pwsh speclite/Install.ps1`

This deploys to three locations, each for a different purpose:

- `.speclite/` - internal machinery: scripts, templates, and project state (`feature.json`,
  `memory/principles.md`, `logs/`). Nothing here is meant to be read directly by another agent.
- `.agents/commands/` - the 5 phase command files, flat, for any agent that reads
  project-level custom slash-commands from an `.agents/` directory.
- `skills/` - the same 5 phases plus the manager itself, each as a self-contained
  `skills/<name>/SKILL.md` folder - matching Spec Kit's own `skills/speckit-<name>/SKILL.md`
  layout, for agents that use the Skill format.

The installer **only ever writes inside these three locations** - it never touches anything
else in the project, and it never overwrites a file that's already there (safe to re-run after
an update; conflicting files are skipped and reported, not clobbered). If you have shell access
and the user has already placed the `speclite/` folder in their project, you can run the
installer yourself instead of asking them to - it's read-only with respect to everything outside
those three locations, so there's nothing destructive to confirm first.

After installing, re-run `status` - it will report `NEXT_PHASE: constitution`.

## The 5 phases

| Phase | Command file | Replaces (Spec Kit) |
|---|---|---|
| 1. Constitution | `.agents/commands/speclite.constitution.md` | `constitution` |
| 2. Specify | `.agents/commands/speclite.specify.md` | `specify` + `clarify` |
| 3. Plan | `.agents/commands/speclite.plan.md` | `plan` + `checklist` |
| 4. Tasks | `.agents/commands/speclite.tasks.md` | `tasks` + `analyze` |
| 5. Implement | `.agents/commands/speclite.implement.md` | `implement` + `converge` |

Each command file is self-contained - read it fresh each time you execute that phase, don't rely
on memory of what it said last time. Supporting reference guides the phase commands point to
(`.speclite/templates/clarify-taxonomy.md`, `checklist-guide.md`, `analyze-guide.md`) preserve
Spec Kit's original rigor for clarification quality, requirements-quality checklisting, and
cross-artifact analysis - read those too when the phase tells you to, don't skip them for speed.

Dropped from Spec Kit's original 10 commands: `taskstoissues` (GitHub-specific - see "Optional
extras" below, do it ad hoc instead of as a scripted phase).

## `references/` - where the user's source material lives

Every feature gets `specs/NNN-name/references/` with these subfolders, created automatically:

`PRD/` `images/` `fonts/` `sounds/` `videos/` `data/` `docs/`

The user can add more subfolders later themselves. **This is where their ideas, requirements
docs, and other attachments for the feature live.** Always check it before drafting a spec or
plan. If you need something from the user mid-workflow - a document, a screenshot, a dataset,
anything - ask them to either paste/attach it directly in the conversation, or drop it into the
matching subfolder here, whichever is easier for them.

## `logs/` - one subfolder per phase, organized by content type

Every feature gets `specs/NNN-name/logs/` with four numbered subfolders, one per phase that
actually runs at the feature level (`2-specify/`, `3-plan/`, `4-tasks/`, `5-implement/`).
Constitution (Phase 1) has no per-feature folder here - it's always project-wide, logged once
at `.speclite/logs/1-constitution/index.md` instead. Inside each per-feature phase folder:

- `index.md` - append-only pass/fail check history for that phase, managed by `log_check`
  (`scripts/python/log_check.py` or `scripts/powershell/log-check.ps1`). Every phase ends by
  calling this - it's also what `status` reads to know a phase is done.
- **Anything else you want to keep** - automated test output, UI screenshots, extra
  documentation - goes here too, but **organize it into your own subfolders by type**
  (`test-results/`, `screenshots/`, `notes/`, etc.). You create these subfolders as needed; they
  aren't pre-scaffolded. Phase 5 (`implement`) is where this matters most - see its command file.

## Constitution (Phase 1) - matches Spec Kit's own model

There is **one `principles.md` for the entire project**, never per-feature - same as Spec Kit's
own `constitution.md`. `constitution_setup.py` / `constitution-setup.ps1` creates it once from
the template (never overwrites an existing one) at `.speclite/memory/principles.md`.

It's recommended as the first thing to do in a brand-new project - `status` will suggest it
before the first feature - but it's not a hard gate: once a feature exists, its absence never
blocks `specify`/`plan`/`tasks`/`implement`. Later phases just read it "if it exists," exactly
like Spec Kit does.

**A rule marked MUST is non-negotiable.** If `plan`, `tasks`, or `implement` finds a conflict
with one, they **stop and tell the user** - they never edit the spec, plan, or task to quietly
route around it. The only way to resolve that conflict is a conscious trip back to
`/speclite.constitution` to either amend the rule or decide the plan needs to change instead.
Never let any phase "fix" a MUST conflict inline - that's the one exception to "fix problems
immediately" that appears throughout this workflow.

## Scripts reference

All scripts live in two mirrored forms - use whichever matches the user's OS/shell:

| Script | Purpose |
|---|---|
| `common.py` / `common.ps1` | Shared path resolution, log helpers. Not invoked directly. |
| `status.py` / `status.ps1` | **The manager's detector** - run this first, always. |
| `install.py` / `Install.ps1` | One-time, non-destructive setup of `.speclite/` in a project. |
| `constitution_setup.py` / `constitution-setup.ps1` | Phase 1: stages the one project-wide `principles.md`, never overwrites it. |
| `new_feature.py` / `new-feature.ps1` | Phase 2: creates `specs/NNN-name/`, `references/`, `logs/`. |
| `setup_stage.py` / `setup-stage.ps1` | Phase 3: verifies spec is clarified, stages `plan.md`. |
| `setup_tasks_stage.py` / `setup-tasks-stage.ps1` | Phase 4: verifies plan's checklist is clean, stages `tasks.md`. |
| `check_prerequisites.py` / `check-prerequisites.ps1` | Phase 5: verifies plan+tasks are ready. |
| `log_check.py` / `log-check.ps1` | Every phase: appends one row to that phase's `index.md`. |

All scripts resolve the active feature via `.speclite/feature.json`, or the
`SPECLITE_FEATURE_DIRECTORY` environment variable to work on a specific feature without changing
what's "active" (useful if the user is juggling more than one at once).

## Optional extras (not part of the 5-phase core)

- **GitHub issues from tasks**: if the user wants each task turned into a GitHub issue, do it
  directly with whatever GitHub tool/MCP is available, mirroring Spec Kit's `taskstoissues`: for
  each unchecked task in `tasks.md`, strip the `- [ ] Txxx` prefix and file one issue titled
  `Txxx: <description>`, skipping any task ID that already has a matching open or closed issue.
- **Ad-hoc checklists**: if the user wants a focused quality checklist for one narrow domain
  (e.g. "check this spec for accessibility gaps") without a full `/speclite.plan` pass, just
  write one inline in the conversation.

See `README.md` in this package for the full rationale behind each merge and the directory
layout in detail.
