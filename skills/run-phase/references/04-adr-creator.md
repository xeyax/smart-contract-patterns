# ADR -- Creator

Prompt for creating an Architecture Decision Record. Placeholders: `{{VARIABLE}}` -- replace with project data.

---

```
You are creating an Architecture Decision Record (ADR) for a smart contract project.

Project context:
- Vision: {{VISION_DOC}}
- Requirements: {{REQUIREMENTS_DOC}}
- Research (if available): {{RESEARCH_DOCS}}

Pattern library (available patterns):
{{PATTERNS_LIST}}

Decision to be made:
{{DECISION_TOPIC}}

You will produce TWO files:

### File 1: Decision — {{ADR_PATH}} (e.g., docs/adr/ADR-001.md)

This is the compact, authoritative record. Other agents (plan, implementation) will read ONLY this file. Keep it concise.

## Summary
- **Question**: one sentence — what needs to be decided
- **Decision**: one sentence — what was chosen
- **Status**: PROPOSED / ACCEPTED / SUPERSEDED

## Decision
What we choose (2-3 paragraphs max). Reference key trade-offs, not all of them.

## Consequences
- What becomes easier
- What becomes harder
- New constraints

## Pattern Library Update
- New pattern? -> one paragraph description
- Modification of existing? -> differences
- Rejected pattern? -> when it does NOT fit

### File 2: Analysis — {{ADR_ANALYSIS_PATH}} (e.g., docs/adr/ADR-001-analysis.md)

This is the full reasoning. The reviewer reads both files. Developers read this when they need to understand WHY.

## Context
What problem we are solving. Reference to specific requirements (FR-XXX).

## Existing Patterns
Which patterns from the library are relevant. For each:
- Name and brief description
- Suitable / not suitable for our case and why

## Options
Minimum 2 options. For each:
- Description of the approach
- Pros
- Cons
- Risks

## Rationale
Why the chosen option was selected. Detailed comparison with rejected options. Reference to specific pros/cons.

RULES:
- Minimum 2 options, even if the choice is obvious
- Trade-offs explicitly, not "best option", but "best for our case, because..."
- Must not contradict previously adopted ADRs
- Findings from Research are accounted for (limitations, edge cases)
- Decision file must be self-contained — a reader should understand the decision without opening the analysis
```
