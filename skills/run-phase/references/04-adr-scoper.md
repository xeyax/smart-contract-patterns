# ADR -- Scoper

This prompt is used twice: first to produce the initial scope, then to refine it after developer feedback.

## Initial run

```
Determine which architectural decisions need to be made and what needs to be researched for them.

Requirements: {{REQUIREMENTS_DOC}}
Vision: {{VISION_DOC}}

## Step 1: Extract constraints

Before listing decisions, extract hard constraints from Requirements and Vision — things that are NOT decisions but given facts that narrow the solution space.

For each constraint:
- **ID**: CNST-001, CNST-002, ...
- **Constraint**: what is fixed (one sentence)
- **Source**: which requirement or vision statement implies this
- **Affects**: which decisions this constrains

## Step 2: List decisions

For each decision:
- **ID**: DT-001, DT-002, ...
- **Decision**: what needs to be chosen/determined (one sentence)
- **Related requirements**: FR-XXX, SR-XXX, C-XXX
- **Constrained by**: CNST-XXX (if any constraints narrow the options)
- **Research needed?**: YES / NO
  - If YES — specific question: what needs to be determined before making the decision (facts about external systems, mechanisms, limitations)
- **Depends on**: other DT-XXX (if the decision requires the result of another decision)

Distinguish:
- **Research** = "how does X work?" — facts about things we don't control
- **Decision** = "what do WE choose?" — our architecture based on facts

Only decisions tied to requirements — nothing "just in case".

## Step 3: Group and order

1. **Group** related decisions into clusters (e.g., "Upgradeability + Access Control + Deployment" or "Oracle + Data Feeds + Price Validation").
2. **Build a dependency graph** — which decisions block others.
3. **Propose execution order** — respecting dependencies, processing clusters together where possible.

## Output format

Write the result as a single document with three sections:
1. **Constraints** — extracted from Requirements/Vision
2. **Decision groups** — clustered DTs with dependencies, research needs, and constraints
3. **Proposed execution order** — numbered sequence of DTs/groups

Write in English.
```

## Refinement run (after developer feedback)

```
You are the scoper. You produced the initial scope document. The developer has reviewed it and provided feedback.

Current scope: {{SCOPING_DOC}}
Developer feedback: {{USER_FEEDBACK}}

Update the scope document. For each DT, set one of these statuses:

- **DECIDED** — the developer already made the decision. Record:
  - Decision: what was chosen
  - Rationale: why (from developer's input)
  - No research or ADR cycle needed.

- **NEEDS RESEARCH** — the decision requires facts. Record:
  - Research question: what specifically to investigate
  - Look at: where to search (specific protocols, docs, contracts)
  - Do NOT look at: what to skip (to save tokens)
  - Developer input: any leanings or context the developer shared

- **READY FOR ADR** — no research needed, but the decision is not yet made. Record:
  - Developer input: any preferences or constraints the developer mentioned

- **REMOVED** — not needed for MVP or dropped by developer.

Also update:
- Constraints — add any new constraints from developer feedback
- Execution order — adjust based on status changes

Write the updated scope document in full. This document is the single source of truth for all subsequent research and ADR steps.

Write in English.
```
