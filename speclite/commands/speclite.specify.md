---
description: "Phase 2 - Specify: draft the feature spec from a description and any reference materials, then clarify open questions inline."
---

## User Input

```text
$ARGUMENTS
```

The text the user typed after `/speclite.specify` **is** the feature description. Don't ask
them to repeat it unless the command was invoked with nothing at all.

## Outline

1. Run (from the repo root):
   - Linux/macOS: `python .speclite/scripts/python/new_feature.py --json "<description>"`
   - Windows: `.speclite/scripts/powershell/new-feature.ps1 -Json "<description>"`

   Parse `FEATURE_DIR`, `SPEC_FILE`, `REFERENCES_DIR`, `PROJECT_PRINCIPLES_FILE`.

2. **`REFERENCES_DIR` is where the user's ideas, PRDs, and other source material for this
   feature live** - it has `PRD/`, `images/`, `fonts/`, `sounds/`, `videos/`, `data/`, and
   `docs/` subfolders (the user can add more later). Read everything already there before
   writing anything. If you need something from the user during this phase or any later one -
   a document, a screenshot, a data sample - ask them to either paste/attach it in the chat, or
   drop it into the matching subfolder of `references/`.

3. If `PROJECT_PRINCIPLES_FILE` is set, read it now - it's the project's one constitution. If
   it's not set, that's fine; constitution is optional and speclite proceeds without it (Spec
   Kit's own model treats it the same way - read "if it exists").

4. Draft the spec into `SPEC_FILE` following `spec-template.md`'s structure:
   - Extract actors, actions, data, and constraints from the description and references.
   - Use informed defaults for unspecified details; record them under **Assumptions**.
   - Only add a `[NEEDS CLARIFICATION: ...]` marker when the answer materially changes scope,
     security, or UX, and no reasonable default exists.
   - Write testable Functional Requirements (`FR-001`, ...) and measurable, technology-agnostic
     Success Criteria (`SC-001`, ...).
   - Focus on WHAT and WHY, not HOW - no tech stack, APIs, or code structure here (that's
     `/speclite.plan`).

5. **Clarify** - read `.speclite/templates/clarify-taxonomy.md` for the full rules, then run the
   sequential clarification loop: scan the taxonomy categories, queue up to 5 high-impact
   questions, ask **one at a time** in the `**Question:** ... ? / **Recommended:**` format the
   guide describes, and integrate each accepted answer into the spec immediately (under
   `## Clarifications`, and into the relevant section) before asking the next.

6. Run:
   - Linux/macOS: `python .speclite/scripts/python/log_check.py --phase specify --status PASS --summary "<N questions asked, spec sections touched>"`
   - Windows: `.speclite/scripts/powershell/log-check.ps1 -Phase specify -Status PASS -Summary "<N questions asked, spec sections touched>"`

   Use `WARN` instead of `PASS` if the user chose to proceed with an open question.

## Done When

- [ ] `spec.md` written with no unresolved `[NEEDS CLARIFICATION]` markers (or the user
      explicitly accepted the risk of proceeding with one)
- [ ] Every accepted clarification is reflected both in `## Clarifications` and in the section it
      actually affects
- [ ] Check recorded in the log
- [ ] User told about `references/` and pointed at the next step: `/speclite.plan`
