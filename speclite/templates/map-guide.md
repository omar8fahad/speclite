# Project Map Guide (used by `/speclite.map`)

*Condensed from the original build/update project-map prompts. Read this before writing or
updating `PROJECT_MAP.md` or any of its sibling files in `specs/`.*

## Core principle: verify, don't guess

- Never treat a file or symbol name as evidence of implementation just because it *sounds*
  related. Check the actual content/behavior before recording something as `implemented`.
- If you can't verify something, write `unclear` or `needs verification` - never guess, and
  never silently drop it instead of flagging it.
- Distinguish explicitly between: a stated requirement, the current implementation, and an
  *inferred* relationship. If a relationship is inferred rather than confirmed, say so in the
  text (e.g. "likely calls X, based on the import - not confirmed by tracing execution").
- If a source document conflicts with the code, don't assume either is "right" - document the
  conflict plainly and let a human resolve intent if it matters.

## Which mode is running

`setup_map_stage.py` reports `MODE: build` or `MODE: update` - don't ask the user which one,
just follow what it reports:

- **build** (`PROJECT_MAP.md` doesn't exist yet in `specs/`): full scan. Read every
  `SOURCE_PRD`, scan the project structure, identify the tech stack from actual files (not
  assumptions), find entry points, trace requirements to implementation, then write all four
  files from their templates.
- **update**: the script already computed `CHANGED_FILES` - a git diff since the last sync, or
  a file-mtime fallback if there's no usable git history - so read *those* files plus anything
  in the existing map that references them, not the whole repository again. This is what keeps
  updates cheap; don't defeat it by re-reading everything anyway.
  - If `CHANGED_FILES_TRUNCATED` is true, the delta was too large for a precise file-by-file
    pass (`> 200` files) - do a broader targeted sweep of the affected directories instead.
  - If `TRIGGERING_FEATURE_DIR` is set (this run followed that feature's `/speclite.implement`):
    also read that feature's `spec.md`/`plan.md`/`tasks.md` directly regardless of what the diff
    shows - guaranteed relevant even if not everything was committed yet.
  - If `KNOWN_CHANGES_HINT` is set (the user described specific known changes): treat it as a
    starting point, but still check for secondary effects the user might not know about (a
    shared file that changed, a dependency that moved).
  - If neither of the above applies and the diff came back empty or unreliable: treat this as a
    full-sync - compare the existing map against the current codebase broadly, still preferring
    the changed-files signal where available to bound the work.

## Updating without losing information

1. Never silently delete something - if an item must be removed or corrected, record it in
   `PROJECT_MAP.md`'s **Map Change Log** section.
2. On conflict between the old map and current code: the code wins for current *state*, but log
   the correction rather than discarding the old entry silently.
3. If two map files disagree with each other, resolve it, and note which one was trusted and
   why.
4. Re-check any earlier `needs verification` item you can now verify - don't just leave it.
5. Requirement status changes only with evidence: `missing -> implemented` needs a real
   file/symbol; `implemented -> partial` needs a specific reason for the downgrade.
6. Fix every stale path or broken link you notice along the way, not just ones tied to the
   current change.
7. Preserve existing structure and conventions in the files - don't restructure sections
   without a real reason, and if you do, note why in the Change Log.

## Style rules

- Use paths relative to the repo root, exactly as they appear in the code.
- Prefer `path/to/file.ext -> functionName()` over a line number - line numbers drift, symbol
  references don't. A line number can be added as a minor aid only if genuinely useful.
- Don't paste large code blocks - this is a map, not a copy of the codebase.
- Cross-references between the map files should be relative Markdown links where practical.
- Don't reference a file that doesn't actually exist.

## Before finishing: Validation Pass

- Every path mentioned resolves to a real file.
- Every symbol mentioned actually exists in that file.
- No dangling references introduced by this update.
- Status is consistent across `PRD_TRACEABILITY.md`, `PROJECT_MAP.md`'s Coverage & Gaps section,
  and `FILE_INDEX.md`.
- Every requirement from every `SOURCE_PRD` has a status, even if that status is
  `needs verification`.
- If `PROJECT_MAP.json` is enabled, its content matches the Markdown - resolve any conflict in
  Markdown's favor, then fix the JSON, and note it in the Change Log if it was actually wrong
  (not just stale).
- The Map Change Log documents this run: date, mode, what was added/modified/removed/corrected,
  what's still `needs verification`.

## Finishing the sync

Embed the updated state block at the very top of `PROJECT_MAP.md` (replace the old one):

```
<!-- speclite-map-state
last_sync_commit: <CURRENT_COMMIT from setup_map_stage.py, or "none" if no git>
last_sync_timestamp: <current ISO 8601 timestamp>
scan_mode: <build | targeted | full-sync | feature-integration>
-->
```

This is what makes the *next* run cheap - skip it, and every future update falls back to a full
scan of the whole project.

## `PROJECT_MAP.json` - the compact machine-readable index

Enabled by default because it's genuinely cheap: keep it **structural only** - IDs, paths,
statuses, dependency lists - and never duplicate the prose descriptions from the Markdown files.
That's what keeps generating and updating it low-cost. Shape:

```json
{
  "project": "...",
  "last_sync_commit": "...",
  "last_updated": "...",
  "requirements": {
    "FR-001": {
      "source": "specs/001-x/spec.md",
      "status": "implemented",
      "files": ["src/a.py"],
      "symbols": ["funcA"]
    }
  },
  "files": {
    "src/a.py": {
      "purpose": "...",
      "exports": ["funcA"],
      "depends_on": ["src/b.py"],
      "depended_by": ["src/c.py"],
      "related_requirements": ["FR-001"]
    }
  },
  "modules": {
    "auth": {"related_modules": ["users"], "entry_points": ["src/auth/index.py"]}
  }
}
```

On an update, patch only the entries touched by `CHANGED_FILES` - there's no need to regenerate
the whole file from scratch. If the user has no use for it and asks to turn it off, that's fine
- it's a convenience export, not required by anything else in speclite.
