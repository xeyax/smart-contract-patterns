# ADR -- Scoper

```
Determine which architectural decisions need to be made and what needs to be researched for them.

Requirements: {{REQUIREMENTS_DOC}}
Vision: {{VISION_DOC}}

For each decision:
- **ID**: DT-001, DT-002, ...
- **Decision**: what needs to be chosen/determined (one sentence)
- **Related requirements**: FR-XXX, SR-XXX, C-XXX
- **Research needed?**: YES / NO
  - If YES -- specific question: what needs to be determined before making the decision (facts about external systems, mechanisms, limitations)
- **Depends on**: other DT-XXX (if the decision requires the result of another decision)

Distinguish:
- **Research** = "how does X work?" -- facts about things we don't control
- **Decision** = "what do WE choose?" -- our architecture based on facts

Sorting: decisions without dependencies first, then dependent ones.
Only decisions tied to requirements -- nothing "just in case".
Write in English.
```
