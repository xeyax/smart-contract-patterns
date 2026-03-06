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

Create an ADR:

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

## Decision
What we choose and why. Reference to specific pros/cons from the options.

## Consequences
What this means for the project:
- What becomes easier
- What becomes harder
- What new constraints appear

## Pattern Library Update
- Is this a new pattern? -> Describe for adding to the library
- Is this a modification of an existing one? -> Describe the differences
- Was an existing pattern rejected? -> Describe when it does NOT fit

RULES:
- Minimum 2 options, even if the choice is obvious
- Trade-offs explicitly, not "best option", but "best for our case, because..."
- Must not contradict previously adopted ADRs
- Findings from Research are accounted for (limitations, edge cases)
```
