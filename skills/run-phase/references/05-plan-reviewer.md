# Development Plan -- Reviewer

```
Review the development plan. Work ONLY with the documents below. Build the traceability matrix yourself and compare with the plan.

Plan: {{PLAN_DOC}}
Requirements: {{REQUIREMENTS_DOC}}
ADR: {{ALL_ADRS}}

## Checklist

1. Is each task atomic? (can it be done and tested in isolation?)
2. Are dependencies correct? (no cycles, no missing ones)
3. Is deployment order accounted for?
4. Traceability matrix:
   - Read EACH FR-XXX and SR-XXX
   - Find the covering TASK-XXX
   - List ALL uncovered requirements
5. Do tasks match ADRs?
6. Are there tasks that are too large? (need to be split?)

## Test Scenarios

7. Does each task have a test scenario?
8. Does the happy path cover the main flow?
9. Are edge cases sufficient? (for each scenario -- what's present, what's missing)
10. Do revert cases cover all failure conditions from FR/SR?

## Additionally

- "Hidden tasks": deploy scripts, migrations, configuration?
- No duplication between tasks?

Find at least 3 problems.

Verdict: ACCEPTED / NEEDS REVISION.
```
