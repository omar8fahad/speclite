---
name: "speclite-map"
description: "Project Map (optional): build or incrementally update a project-wide reference map (PROJECT_MAP.md, PRD_TRACEABILITY.md, ARCHITECTURE_MAP.md, FILE_INDEX.md) so any agent or developer coming later can understand the project quickly and accurately."
compatibility: "Requires speclite project structure with .speclite/ directory"
metadata:
  author: "speclite"
  source: "commands/speclite.map.md"
---

## User Input

```text
$ARGUMENTS
```

Consider this input before proceeding, if not empty - it may describe known changes (targeted
mode) or a reason for running this now.

## What this is

Not one of the 5 core phases, and never blocking - a project-wide, optional reference map that
grows alongside the project. Lives in `specs/` directly, as siblings of the `specs/NNN-feature/`
directories (never inside one of them), because it's project-wide like the constitution, not
per-feature like spec/plan/tasks.

## When this runs

The manager suggests this (never forces it) in three situations - see `SKILL.md`:

1. **Right after `/speclite.constitution`**, if the repo already has real code in it (onboarding
   an existing project) - build mode, full scan, one-time.
2. **Right after a `/speclite.implement` gap-check passes**, especially for a substantial
   feature - update mode, feature-integration.
3. **On demand**, any time the user wants a periodic full audit - update mode, full-sync.

If the user declines a suggestion, don't repeat it later in the same session.

## Outline

1. Run (from the repo root):
   - Linux/macOS: `python .speclite/scripts/python/setup_map_stage.py --json [--feature-dir <path>] [--known-changes "<text>"]`
   - Windows: `.speclite/scripts/powershell/setup-map-stage.ps1 -Json [-FeatureDir <path>] [-KnownChanges "<text>"]`

   Pass `--feature-dir`/`-FeatureDir` when this follows a specific feature's implement phase.
   Pass `--known-changes`/`-KnownChanges` when the user described specific changes themselves
   (targeted mode).

2. Read `.speclite/templates/map-guide.md` in full before writing anything - it has the accuracy
   rules (verify, don't guess, `needs verification` over invented certainty), the exact
   behavior for each mode (`MODE`, `CHANGED_FILES`, `CHANGED_FILES_TRUNCATED`,
   `TRIGGERING_FEATURE_DIR`, `KNOWN_CHANGES_HINT`), the Validation Pass, and the
   `PROJECT_MAP.json` schema.

3. Follow `MODE` from step 1's output:
   - **build**: read every path in `SOURCE_PRDS`, scan the project structure, and fill in all
     four files (`project-map-template.md`, `prd-traceability-template.md`,
     `architecture-map-template.md`, `file-index-template.md` were already staged into
     `MAP_FILES` by the script).
   - **update**: read only `CHANGED_FILES` (plus the triggering feature's own docs, plus
     anything the existing map already links to those files) - not the whole project again.

4. Update `PROJECT_MAP.json` (structural fields only, per the guide's schema) unless the user
   has explicitly said they don't want it.

5. Run the Validation Pass from `map-guide.md`, then embed the refreshed
   `<!-- speclite-map-state -->` block at the top of `PROJECT_MAP.md` with the current commit
   (or "none") and timestamp - this is what keeps the *next* run cheap.

## Done When

- [ ] `PROJECT_MAP.md`, `PRD_TRACEABILITY.md`, `ARCHITECTURE_MAP.md`, `FILE_INDEX.md` all
      reflect the current codebase, with no information silently dropped
- [ ] Every requirement from every `SOURCE_PRD` has a status (or `needs verification`)
- [ ] Map Change Log entry added for this run
- [ ] `speclite-map-state` block refreshed with the current commit/timestamp
- [ ] `PROJECT_MAP.json` updated (unless disabled)
- [ ] User told what changed and what, if anything, still needs human verification
