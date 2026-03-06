# Functional Requirements -- Creator

```
Create a functional requirements document docs/requirements.md.
Describe WHAT the system does, without HOW.

Project Vision:
{{VISION_DOC}}

Sections:

## Functional Requirements
By features/modules. "The system must...". Numbering: FR-001, FR-002...

## Constraints
Networks, protocols, limits, compatibility. Numbering: C-001, C-002...

## Security Requirements
Access control, upgradeability, pause, rate limits. Numbering: SR-001, SR-002...

RULES:
- ONLY the 3 sections above. No "Design Principles", "Architecture", "Non-functional Requirements", etc.
- "What", not "how" -- no Solidity, data structures, patterns
- Each requirement is testable (clear pass/fail)
- All users and metrics from Vision are covered
- Do NOT include use cases / scenarios -- they will be in the development plan as test scenarios
- Write in English
```
