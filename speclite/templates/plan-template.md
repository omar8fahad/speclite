# Implementation Plan: [FEATURE NAME]

**Spec**: `spec.md` · **Feature Directory**: `[FEATURE_DIR]`

## Technical Context

- **Stack**: [language / framework / runtime]
- **Dependencies**: [libraries, external services]
- **Constraints**: [performance, security, compatibility, compliance]
- **Open Questions**: [any `[NEEDS CLARIFICATION]` markers still open - resolve before Phase 4]

## Architecture Overview

[Short narrative of the approach, plus the key components/modules touched.]

## Data Model *(include only if the feature involves data)*

- **[Entity]**: fields, relationships, validation rules, state transitions

## Interfaces / Contracts *(include only if the feature exposes an API, CLI, or schema)*

[Document the contract format appropriate for the project: REST endpoints, CLI commands,
function signatures, event schemas, etc.]

## Pre-Implementation Checklist

*"Unit tests for requirements" - see `checklist-guide.md` in `.speclite/templates/` for how to
write and evaluate these. Fix anything unticked right here before moving to `/speclite.tasks`;
don't defer it.*

- [ ] Every functional requirement in spec.md is testable and unambiguous
- [ ] No unresolved `[NEEDS CLARIFICATION]` markers remain in spec.md or this plan
- [ ] Success criteria are measurable and technology-agnostic
- [ ] Data model / contracts above (if any) match what spec.md implies
- [ ] Terminology is consistent between spec.md and this plan
- [ ] Primary, Alternate, Exception, Recovery, and Non-Functional scenarios are all addressed
      (or explicitly marked out of scope)
- [ ] Plan does not conflict with any MUST rule in `.speclite/memory/principles.md` (if it
      exists yet - if it doesn't, that's fine, this box can be checked)

## Validation Guide

[How to prove the feature works end-to-end once implemented: prerequisites, setup commands,
run/test commands, expected outcome. Keep this a guide, not a full test suite.]
