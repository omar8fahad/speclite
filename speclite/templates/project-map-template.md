<!-- speclite-map-state
last_sync_commit: none
last_sync_timestamp:
scan_mode: build
-->

# Project Map: [PROJECT NAME]

**Last updated**: [DATE] · **Codebase state**: [commit hash, or "no git - timestamp-based"]

*Entry point for understanding this project - for any agent or developer coming later. See
`map-guide.md` in `.speclite/templates/` for the accuracy rules this file (and its siblings)
must follow: no guessing, no unverified claims.*

## Summary

[1-3 sentences: what this project does.]

## Tech Stack

[Languages, frameworks, key libraries - discovered from the actual codebase, not assumed.]

## Top-Level Structure

[High-level folder layout with a one-line purpose per top-level folder.]

## Key Components / Domains

[Main modules or domains, one line each.]

## Where to Look

*Only include rows for categories that actually exist in this project - don't list
"Authentication" if there is none.*

| Looking for... | Go to |
|---|---|
| ... | ... |

## Reference Files

- [`PRD_TRACEABILITY.md`](./PRD_TRACEABILITY.md) - which requirements map to which implementation
- [`ARCHITECTURE_MAP.md`](./ARCHITECTURE_MAP.md) - how the pieces connect (data flow, dependencies)
- [`FILE_INDEX.md`](./FILE_INDEX.md) - purpose and relationships of individually important files
- [`PROJECT_MAP.json`](./PROJECT_MAP.json) - the same relationships, machine-readable

## Maintenance Rules

Re-run `/speclite.map` whenever: a feature is added, removed, or materially changed; an
API/endpoint is added or removed; an important file is added, deleted, moved, or renamed; the
database schema changes; the architecture changes; a new external integration is added;
authentication/authorization changes; a requirement's implementation status changes; or
something documented here turns out to be stale. It's optional and non-blocking, not a required
step in the 5-phase workflow - but keeping it current is what makes it useful. Which map file to
touch for each case is detailed in `map-guide.md`.

## Coverage & Gaps

- **PRDs/specs reviewed**: [list]
- **PRDs/specs not accessible**: [list, if any]
- **Requirements implemented / partial / missing / unclear**: [counts - details in `PRD_TRACEABILITY.md`]
- **Code with no clear requirement link**: [list, if any]
- **Architecture areas needing review**: [list, if any]
- **Needs human verification**: [list, if any]

## Map Change Log

*Most recent first. Once this grows past ~10 rounds, older entries move to `MAP_CHANGELOG.md`.*

- **[DATE]** (build): initial map created.
