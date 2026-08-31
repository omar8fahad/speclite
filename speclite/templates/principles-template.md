# Project Principles

*speclite's lightweight stand-in for Spec Kit's `constitution.md` - plain notes instead of a
version-bumped document, but the same non-negotiable philosophy: this is ONE file for the
whole project (never per-feature), and a rule marked **MUST** cannot be silently worked around.*

*Every later phase (`plan`, `tasks`, `implement`) checks its work against this file. If any of
them finds a conflict with a MUST rule, they stop and tell you - they never edit the spec, plan,
or code to quietly route around it. The only way to resolve that conflict is to come back here
and consciously either (a) change the plan/code to comply, or (b) amend the rule itself by
re-running `/speclite.constitution` and editing this file directly.*

## Non-negotiable rules (MUST)

- [e.g. "All user input MUST be validated server-side before persistence."]

## Strong defaults (SHOULD)

- [e.g. "New endpoints SHOULD follow the existing REST conventions in `src/api/`."]

## Out of scope for this project

- [e.g. "No feature may introduce a new database engine without explicit sign-off."]
