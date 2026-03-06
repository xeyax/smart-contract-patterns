# Development Plan -- Creator

```
Create a development plan docs/plan.md for a smart contract project.
Break the project into atomic tasks with a dependency tree.

Context:
- Requirements: {{REQUIREMENTS_DOC}}
- ADR: {{ALL_ADRS}}

Sections:

## Tasks
For each task:
- ID: TASK-001, TASK-002, ...
- Title
- Description (1-3 sentences)
- Depends on: [list of TASK-IDs]
- Related requirements: FR-XXX, SR-XXX

## Test Scenarios
For each key flow from Requirements:
- Scenario name
- Related FR/SR
- Happy path (transaction steps)
- Edge cases (zero balance, price changed, gas spike, concurrent txs)
- Revert cases (what conditions should cause a revert)
- Related to which TASK-XXX

## Deployment Order
Which contract is deployed first, dependencies during deployment.

## Dependency Tree
Mermaid diagram or text.

## Traceability Matrix
Table: each FR-XXX and SR-XXX -> which TASK-XXX covers it.
Uncovered ones -- explicitly indicate.

RULES:
- Each task is atomic (one contract or one module)
- Dependencies are correct (no cycles)
- Each requirement is covered by at least one task
- Each task has at least one test scenario
- Use decisions from ADRs, don't reinvent
- Time estimates are NOT needed
- Write in English
```
