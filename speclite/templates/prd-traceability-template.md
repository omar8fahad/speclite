# PRD Traceability

**Source documents**: every `specs/*/spec.md` plus every `specs/*/references/PRD/*` file
(auto-derived each run by `setup_map_stage.py` - don't hand-maintain this list).

*Status values: `implemented` / `partial` / `missing` / `unclear`. Never mark something
`implemented` without a specific file/symbol as evidence. See `map-guide.md` for the full
accuracy rules.*

## [Source Document Name]

### FR-001: [requirement name/description]

- **Status**: implemented | partial | missing | unclear
- **Files**: `path/to/file.ext`, ...
- **Symbols**: `functionName()`, `ClassName`, ...
- **Depends on**: [other requirement IDs, if any]
- **Notes**: [discrepancies between the doc and the actual implementation, if any]

<!-- Repeat per requirement. Group by source document. Reuse the FR-XXX IDs already used in
     spec.md directly - don't invent a parallel numbering scheme for speclite-generated specs. -->

## Implementation Without a Clear Requirement

[Code that appears to implement something, but no requirement in the source documents covers
it. List it here rather than silently ignoring it - the same "unrequested work" philosophy the
analyze pass in `/speclite.tasks` already uses.]

## Requirements Without Implementation

[Requirements from the source documents that have no code yet.]
