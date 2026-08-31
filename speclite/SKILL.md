---
name: speclite
description: A condensed, 5-phase spec-driven feature-development workflow adapted from GitHub's Spec Kit, with a manager that auto-detects which phase to run next so the user never has to track progress themselves. Phases: constitution -> specify -> plan -> tasks -> implement. Constitution is a single project-wide file, matching Spec Kit's own model - never per-feature, and its non-negotiable MUST rules are never silently edited around. Phase completion is tracked entirely through the artifacts themselves (Spec Kit's own style, e.g. checkboxes in spec.md/plan.md/tasks.md) rather than a separate log. Includes a references/ folder per feature for user-supplied PRDs, images, fonts, sounds, videos, and data, a single flat logs/ folder per feature for free-form evidence (test output, screenshots, session notes) the agent organizes by type, and an optional, non-blocking Project Map (PROJECT_MAP.md, PRD_TRACEABILITY.md, ARCHITECTURE_MAP.md, FILE_INDEX.md in specs/) that grows with the project via cheap incremental updates and is suggested (never forced) after constitution or after implement. Use this whenever the user wants to formalize a feature before coding, mentions "spec kit", "spec-driven development", asks to turn a PRD or a rough idea into a spec/plan/tasks, or the project already contains a `.speclite/` directory or a `specs/NNN-*` folder. Trigger it proactively for any non-trivial "build me a feature" request where jumping straight to code would skip requirements and planning. This skill IS the manager - it decides which phase to run, the user does not need to know or remember.
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
| `constitution` | Phase 1 needed | Read `commands/speclite.constitution.md`, execute it |
| `specify` | Phase 2 needed | Read `commands/speclite.specify.md`, execute it |
| `plan` | Phase 3 needed | Read `commands/speclite.plan.md`, execute it |
| `tasks` | Phase 4 needed | Read `commands/speclite.tasks.md`, execute it |
| `implement` | Phase 5 needed | Read `commands/speclite.implement.md`, execute it |
| `ambiguous` | Multiple features, none active | Ask the user which one (see below) - this is the only routine case where you ask before acting |
| `done` | Feature fully shipped | Tell the user; offer to start a new feature with `/speclite.specify` |

`REASON` is a human-readable one-liner explaining the verdict - relay it to the user briefly so
they know why you're doing what you're doing, instead of silently jumping around.

If `NEEDS_USER_INPUT` is `true` (open `[NEEDS CLARIFICATION]` markers, or an ambiguous
multi-feature repo), that question is part of the target phase itself - ask it as that phase's
first step, don't ask a separate meta-question first.

**`status` also reports `MAP_SUGGESTION`** (`"build"`, `"update"`, or `null`) about the optional
Project Map - see the section below. This never changes `NEXT_PHASE` and never blocks anything;
only surface it at a natural breakpoint (right after `/speclite.implement` finishes, or before
starting the first feature in a project that already has code) - don't interrupt mid-phase with
it, and don't repeat it in the same session if the user already declined.

**Re-run `status` after every phase completes** (each phase's completion is written directly
into its own artifact - a checkbox in spec.md/plan.md/tasks.md - which is exactly what `status`
reads, Spec Kit's own style, no separate log involved) and immediately continue to whatever it
reports next - chain phases automatically in one session unless the user wants to stop. This is
what lets someone come back days later, having forgotten everything, and just say "continue" -
`status` picks up exactly where things left off.

## First use in a project: install

If `status` reports `NEXT_PHASE: install` (no `.speclite/` yet), tell the user to place this
whole `speclite/` folder inside their project root, next to their other project files, then run
the installer:

- Linux/macOS: `python speclite/install.py`
- Windows: `pwsh speclite/Install.ps1`

This deploys to three locations, each for a different purpose:

- `.speclite/` - internal machinery: scripts, templates, and project state (`feature.json`,
  `memory/principles.md`, `logs/`). Nothing here is meant to be read directly by another agent.
- `.agents/commands/` - the 5 phase command files plus the Project Map command, flat, for
  any agent that reads project-level custom slash-commands from an `.agents/` directory.
- `skills/` - the same 6 command files plus the manager itself, each as a self-contained
  `skills/<name>/SKILL.md` folder - matching Spec Kit's own `skills/speckit-<name>/SKILL.md`
  layout, for agents that use the Skill format.

The installer **only ever writes inside these three locations** - it never touches anything
else in the project, and it never overwrites a file that's already there (safe to re-run after
an update; conflicting files are skipped and reported, not clobbered). If you have shell access
and the user has already placed the `speclite/` folder in their project, you can run the
installer yourself instead of asking them to - it's read-only with respect to everything outside
those three locations, so there's nothing destructive to confirm first.

After installing, re-run `status` - it will report `NEXT_PHASE: constitution`.

## Project Map (optional, not one of the 5 phases)

A project-wide, growing reference map - `PROJECT_MAP.md`, `PRD_TRACEABILITY.md`,
`ARCHITECTURE_MAP.md`, `FILE_INDEX.md`, and `PROJECT_MAP.json` - that lets any agent or
developer coming later understand the project quickly and accurately, including how every
feature's requirements trace to actual code. Never blocking, never required.

**Unlike the constitution** (read once at the start of a phase and left alone), **the map is
meant to be consulted continuously** - during specify and plan for context, during analyze to
catch duplicate work, and especially during implement itself, before creating a new file or
following a pattern. This is what actually cuts down on distraction, mistakes, and repeated
searching through the codebase - the payoff compounds the more consistently it's used, not just
at the bookends of a feature.

- **Lives in `specs/` directly** (`specs/PROJECT_MAP.md`, etc.), as a sibling of the
  `specs/NNN-feature/` directories - project-wide like the constitution, not per-feature.
- **One command, two modes, auto-detected**: `commands/speclite.map.md` runs
  `setup_map_stage.py` / `setup-map-stage.ps1`, which reports `MODE: build` (first time) or
  `MODE: update`.
- **Updates are cheap by design**: for `update`, the script computes `CHANGED_FILES` - a git
  diff since the last sync (or a file-mtime fallback if there's no git) - so only what actually
  changed gets re-read, never the whole project again. Read `.speclite/templates/map-guide.md`
  before touching any of the map files; it has the full accuracy rules (verify, don't guess;
  `needs verification` over invented certainty) and the exact behavior for every field this
  script reports.
- **Suggest it, never run it silently**, in these situations only:
  1. Right after `/speclite.constitution`, if `MAP_SUGGESTION: build` (the repo already has
     real code - an existing project being onboarded).
  2. Right after a `/speclite.implement` gap-check passes, if `MAP_SUGGESTION: update`
     (especially for a substantial feature).
  3. On demand, whenever the user wants a periodic full audit.
- No `logs/` integration - the map's own sync state lives in an invisible
  `<!-- speclite-map-state -->` comment at the top of `PROJECT_MAP.md` itself, not a log file.

## The 5 phases (the required core)

| Phase | Command file | Replaces (Spec Kit) |
|---|---|---|
| 1. Constitution | `commands/speclite.constitution.md` | `constitution` |
| 2. Specify | `commands/speclite.specify.md` | `specify` + `clarify` |
| 3. Plan | `commands/speclite.plan.md` | `plan` + `checklist` |
| 4. Tasks | `commands/speclite.tasks.md` | `tasks` + `analyze` |
| 5. Implement | `commands/speclite.implement.md` | `implement` + `converge` |

Each command file is self-contained - read it fresh each time you execute that phase, don't rely
on memory of what it said last time. Supporting reference guides the phase commands point to
(`.speclite/templates/clarify-taxonomy.md`, `checklist-guide.md`, `analyze-guide.md`,
`map-guide.md`) preserve the original rigor for clarification quality, requirements-quality
checklisting, cross-artifact analysis, and project-map accuracy - read those too when a phase
tells you to, don't skip them for speed.

Dropped from Spec Kit's original 10 commands: `taskstoissues` (GitHub-specific - see "Optional
extras" below, do it ad hoc instead of as a scripted phase).

## Phase completion signals (artifact-based, Spec Kit's own style)

`status` never reads a separate log to decide whether a phase is done - it reads the artifact
that phase produces, the same way Spec Kit itself works:

| Phase | Done when |
|---|---|
| 1. Constitution | `.speclite/memory/principles.md` exists (checked, not gated - see below) |
| 2. Specify | `spec.md` has no `[NEEDS CLARIFICATION]` marker left |
| 3. Plan | `plan.md`'s Pre-Implementation Checklist is fully checked |
| 4. Tasks | `tasks.md`'s `Analysis complete` checkbox is ticked |
| 5. Implement | every task in `tasks.md` is `[X]` AND its `Final Gap-Check` checkbox is ticked |

Tick the Phase 4/5 checkboxes only when genuinely true - never as a formality to move on. See
`templates/tasks-template.md` for their exact wording.

## `references/` - where the user's source material lives

Every feature gets `specs/NNN-name/references/` with these subfolders, created automatically:

`PRD/` `images/` `fonts/` `sounds/` `videos/` `data/` `docs/`

The user can add more subfolders later themselves. **This is where their ideas, requirements
docs, and other attachments for the feature live.** Always check it before drafting a spec or
plan. If you need something from the user mid-workflow - a document, a screenshot, a dataset,
anything - ask them to either paste/attach it directly in the conversation, or drop it into the
matching subfolder here, whichever is easier for them.

## `logs/` - one flat folder per feature, free-form evidence only

Every feature gets a single `specs/NNN-name/logs/` folder - **not** split by phase. It never
decides whether a phase is done (see "Phase completion" above); it's purely a place to keep
free-form supporting evidence:

- Automated test/terminal output, UI screenshots proving something works (including a
  screenshot the user already shared earlier in the conversation - save a copy here instead of
  letting it live only in chat history), and brief session notes for a decision or exchange
  worth keeping that isn't already captured in `spec.md`/`plan.md`/`tasks.md`.
- **Organize it yourself, by type** (`test-results/`, `screenshots/`, `notes/`, etc.) - nothing
  is pre-scaffolded beyond the empty `logs/` folder itself. Don't dump files loose.
- **Recommended to exclude from git** (e.g. `specs/*/logs/` in `.gitignore`) since it tends to
  hold large or disposable evidence rather than source of truth - see `README.md` for the exact
  line. speclite never edits `.gitignore` itself; only suggest it, and let the user add it.
- **Useful input when building/updating the Project Map** - a note explaining *why* something
  was built a certain way often survives in `logs/` even when it's not obvious from the code
  alone. `map-guide.md` tells the map-building agent to check it.

## Large or complex work can span multiple turns or sessions - that's expected, not a failure

None of the 5 phases need to finish in a single turn. A big spec, a large plan, a long task
list, or implementing many tasks can legitimately take several turns - or the user closing the
chat and coming back later. Never compress or rush output just to make a phase appear "done" in
one turn: a shallow pass that has to be redone costs more, in time and tokens, than doing it
right the first time even if that takes longer. `status` and the artifact-based checkboxes exist
precisely so that pausing mid-phase costs nothing - picking back up is always exact, never a
guess. This applies especially to Phase 4's analyze pass and Phase 5's task execution and final
gap-check; `commands/speclite.tasks.md` and `commands/speclite.implement.md` call this out at
the specific checkboxes where it matters most, and `map-guide.md` has the equivalent guidance
for a large `/speclite.map` build (stage it, don't force one giant scan).

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
| `common.py` / `common.ps1` | Shared path resolution, git helpers. Not invoked directly. |
| `status.py` / `status.ps1` | **The manager's detector** - run this first, always. |
| `install.py` / `Install.ps1` | One-time, non-destructive setup of `.speclite/` in a project. |
| `constitution_setup.py` / `constitution-setup.ps1` | Phase 1: stages the one project-wide `principles.md`, never overwrites it. |
| `new_feature.py` / `new-feature.ps1` | Phase 2: creates `specs/NNN-name/`, `references/`, `logs/`. |
| `setup_stage.py` / `setup-stage.ps1` | Phase 3: verifies spec is clarified, stages `plan.md`. |
| `setup_tasks_stage.py` / `setup-tasks-stage.ps1` | Phase 4: verifies plan's checklist is clean, stages `tasks.md`. |
| `check_prerequisites.py` / `check-prerequisites.ps1` | Phase 5: verifies plan+tasks are ready. |
| `setup_map_stage.py` / `setup-map-stage.ps1` | Project Map (optional): detects build/update mode, computes the changed-files delta. |

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
