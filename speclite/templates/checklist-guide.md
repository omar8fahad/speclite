# Checklist Guide (used within `/speclite.plan`)

*Condensed from Spec Kit's `checklist` command. This is what the Pre-Implementation Checklist
in `plan-template.md` is testing against - read this before ticking or leaving a box unchecked.*

## Core principle: test the requirements, not the implementation

Every checklist item evaluates the **spec/plan text itself**, not the eventual code, for:
**Completeness**, **Clarity**, **Consistency**, **Measurability**, **Coverage**.

❌ Wrong (tests implementation): "Verify the landing page shows 3 cards", "Confirm the logo
click navigates home."

✅ Right (tests the requirement): "Is 'prominent display' quantified with specific
sizing/positioning?", "Are keyboard-navigation requirements defined for all interactive UI?",
"Is the fallback behavior specified when an image fails to load?"

## Prohibited patterns

Never phrase an item as "Verify/Test/Confirm/Check <implementation behavior>", and never
reference code execution, clicks, rendering, or "works properly" / "displays correctly".

## Required patterns

- "Are [requirement type] defined/specified/documented for [scenario]?"
- "Is [vague term] quantified/clarified with specific criteria?"
- "Are requirements consistent between [section A] and [section B]?"
- "Can [requirement] be objectively measured/verified?"
- "Are [edge cases/scenarios] addressed in requirements?"

## What to check when filling in the Pre-Implementation Checklist

- **Completeness** - every necessary requirement present (error handling, a11y, edge cases)?
- **Clarity** - no vague adjectives ("fast", "robust", "intuitive") without a measurable target?
- **Consistency** - no contradictions between spec.md and plan.md, or within either file?
- **Measurability** - can each Success Criterion be objectively verified?
- **Coverage** - Primary / Alternate / Exception / Recovery / Non-Functional scenarios all
  addressed (or explicitly out of scope)?
- **Traceability** - can each plan decision be traced back to a spec requirement?

## When you find a problem

Don't just leave the box unchecked and move on - fix it now: tighten the wording in spec.md or
plan.md, add the missing requirement, or replace the vague term with a number. Only leave a box
unchecked (and tell the user why) when the fix genuinely needs their input.

**Exception**: the "does not conflict with `principles.md`" item is never "fixed" by editing
around it. If the plan conflicts with a MUST rule, leave that box unchecked, tell the user
exactly which rule and where, and let them decide: change the plan to comply, or amend the rule
itself via `/speclite.constitution`. This is the one box where "fix it now" does not apply.
