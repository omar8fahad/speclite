# speclite

A 5-phase clone of [GitHub Spec Kit](https://github.com/github/spec-kit)'s spec-driven
development workflow, with a built-in manager that auto-detects which phase to run next, a
`references/` folder per feature for user-supplied source material, and a `logs/` folder per
feature with one subfolder per phase for check history plus whatever else the agent wants to
keep (test output, screenshots, extra docs).

## Install

1. Copy this whole `speclite/` folder into your project root, next to your other project files.
2. Run the installer from the project root:
   - Linux/macOS: `python speclite/install.py`
   - Windows: `pwsh speclite/Install.ps1`

The installer **only ever writes inside `<project>/.speclite/`** - nothing else in your project
is touched. It never overwrites a file that already exists at the destination; if you re-run it
after updating this package, conflicting files are skipped and listed at the end instead of
being clobbered, so you can diff and merge them by hand if you want the newer version.

```
$ python speclite/install.py
Installing speclite into: /path/to/project/.speclite
Installed 27 file(s).
No conflicts.

Done. Next step: run /speclite.constitution (Phase 1) to get started.
```

## The manager

You don't need to remember the phase order, and you don't need to track where you left off -
that's what `status.py` / `status.ps1` is for. Run it any time (an AI agent using this skill
runs it automatically, always, before doing anything else):

```
$ python .speclite/scripts/python/status.py --json
{
  "INSTALLED": true,
  "REPO_ROOT": "/path/to/project",
  "ALL_FEATURES": ["001-oauth2-login"],
  "HAS_PROJECT_PRINCIPLES": true,
  "ACTIVE_FEATURE": "/path/to/project/specs/001-oauth2-login",
  "NEXT_PHASE": "plan",
  "REASON": "plan.md not created yet.",
  "NEEDS_USER_INPUT": false
}
```

`NEXT_PHASE` is always exactly what to do next - even if you (or the agent) walk away for a week
and come back having forgotten everything. If several features exist and none is marked active,
`status` reports `ambiguous` instead of guessing, so the agent asks which one to resume rather
than picking wrong silently.

## Why 5 phases instead of Spec Kit's 10 - and why not fewer?

| # | Spec Kit command(s) | speclite phase | Why merged this way (and not further) |
|---|---|---|---|
| 1 | `constitution` | **1. Constitution** | Kept as its own phase, and kept as ONE file for the *entire project* - exactly like Spec Kit's own model, never per-feature. A MUST rule is non-negotiable: any conflict found later stops the phase and requires a conscious trip back here, never a silent edit around it. Simplified from Spec Kit's own semantic-version/Sync-Impact-Report ceremony to a plain file. |
| 2, 3 | `specify` + `clarify` | **2. Specify** | Merged - clarification is cheapest immediately after drafting the spec, while context is loaded. Kept faithful to Spec Kit's own clarify rules (5-question cap, one at a time, recommended-option format, coverage taxonomy) via `clarify-taxonomy.md`, rather than a shortcut version. |
| 4, 6 | `plan` + `checklist` | **3. Plan** | Merged - the checklist is a quality gate *on the plan itself* ("unit tests for requirements"), so it belongs right where the plan is written, fixed inline instead of scheduled as a separate later command. Full rules preserved in `checklist-guide.md`. |
| 5, 7 | `tasks` + `analyze` | **4. Tasks** | Merged, and deliberately kept **separate from both plan and implement** (an earlier draft of this tool merged analyze into implement's pre-flight, which was too shallow) - analyze needs the finished task list to check coverage against, and needs to run *before* code is written, not after. Full detection-pass rules preserved in `analyze-guide.md`. |
| 8, 9 | `implement` + `converge` | **5. Implement** | Merged - rather than a separate audit command run after implement (which just appends tasks and stops), speclite closes the loop immediately: gaps found in the final check are implemented in the same pass, not left for a manual follow-up run. |
| 10 | `taskstoissues` | *(optional extra, not scripted)* | GitHub-specific and only relevant to a subset of users; documented as an ad-hoc pattern in `SKILL.md` instead of a dedicated phase. |

Net effect: **5 phases, 3 files per feature (`spec.md`, `plan.md`, `tasks.md`) plus
`references/` and `logs/`**, instead of Spec Kit's up to 8 files per feature (spec, plan, tasks,
research, data-model, quickstart, contracts/, checklists/) and 10 commands - while keeping every
phase's actual quality mechanics (clarification taxonomy, requirements-checklist philosophy,
analyze detection passes, severity grading) intact via the `*-guide.md` reference docs, not
watered down. Extension-hook machinery (`.specify/extensions.yml`) was dropped for the same
"fewer moving parts" reason.

## Directory layout

```
your-project/
├── speclite/                     # this package - keep it, install.py re-runs safely
├── .speclite/
│   ├── feature.json                # which specs/NNN-* is "active"
│   ├── memory/
│   │   └── principles.md           # the ONE project-wide constitution (Spec Kit's own model)
│   ├── logs/
│   │   └── 1-constitution/index.md # constitution check log - always here, never per-feature
│   ├── templates/
│   │   ├── spec-template.md
│   │   ├── plan-template.md
│   │   ├── tasks-template.md
│   │   ├── principles-template.md
│   │   ├── clarify-taxonomy.md     # Phase 2 reference guide
│   │   ├── checklist-guide.md      # Phase 3 reference guide
│   │   ├── analyze-guide.md        # Phase 4 reference guide
│   │   └── overrides/              # drop a same-named file here to override any template
│   ├── scripts/
│   │   ├── python/                 # status.py, constitution_setup.py, new_feature.py,
│   │   │                           # setup_stage.py, setup_tasks_stage.py,
│   │   │                           # check_prerequisites.py, log_check.py, common.py
│   │   └── powershell/             # same set, PascalCase/.ps1
│   └── commands/                   # the 5 phase command files, copied from speclite/commands/
└── specs/
    └── 001-your-feature/
        ├── spec.md
        ├── plan.md
        ├── tasks.md
        ├── references/
        │   ├── PRD/     ├── images/   ├── fonts/
        │   ├── sounds/  ├── videos/   ├── data/
        │   └── docs/
        └── logs/                      # no per-feature constitution folder - see above
            ├── 2-specify/index.md
            ├── 3-plan/index.md
            ├── 4-tasks/index.md
            └── 5-implement/
                ├── index.md
                ├── test-results/          # agent-created, as needed
                ├── screenshots/           # agent-created, as needed
                └── notes/                 # agent-created, as needed
```

## The check log (`logs/<phase>/index.md`)

Every phase appends one row via `log_check.py` / `log-check.ps1`:

```
# Implement - Check Log

Other files in this folder (test output, screenshots, extra docs) are organized by the
agent as needed - this table only tracks pass/fail checks.

| Time             | Status   | Summary                          |
|------------------|----------|-----------------------------------|
| 2026-08-27 09:12 | ✅ PASS  | 6/6 tasks done, gap-check clean   |
```

Longer notes attach as a collapsed `<details>` block via `--details` (Python) or `-Details`
(PowerShell). `index.md` is never rewritten, only appended to. Everything else in a phase's log
folder - a `test-results/` run, a `screenshots/` capture, a `notes/` write-up - is placed there
directly by the agent, grouped by type; `status.py` only reads `index.md`, so free-form content
never interferes with phase detection.

## Quick start

```bash
# 1. Install once per project (non-destructive, safe to re-run)
python speclite/install.py

# 2. Let the manager take it from here - it runs status, sees NEXT_PHASE: constitution,
#    helps draft the project's principles.md, then keeps chaining phases automatically:
#      constitution -> specify -> plan -> tasks -> implement
#
# 3. Drop any PRD/screenshots/fonts/etc. into the active feature's references/ subfolders
#    at any point - every phase checks there before assuming anything.
```

## Command files

- `commands/speclite.constitution.md`
- `commands/speclite.specify.md`
- `commands/speclite.plan.md`
- `commands/speclite.tasks.md`
- `commands/speclite.implement.md`

Each is a self-contained instruction file an AI agent reads before running that phase - same
convention as Spec Kit's own `.md` command files. `SKILL.md` is the manager that decides which
one to read, using `status.py` / `status.ps1`.
