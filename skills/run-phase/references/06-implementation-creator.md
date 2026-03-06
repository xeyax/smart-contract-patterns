# Implementation -- Creator

Prompt for implementing a task from the plan. Placeholders: `{{VARIABLE}}` -- replace with project data.

---

```
You are implementing a task from the smart contract development plan.

Task:
{{TASK_DESCRIPTION}}

Context:
- Requirements (related): {{RELATED_REQUIREMENTS}}
- ADR (related): {{RELATED_ADRS}}
- Pattern library: {{RELEVANT_PATTERNS}}
- Already implemented contracts: {{EXISTING_CODE}}

Implement:

1. Contract / module code
2. Unit tests:
   - Happy path for each function
   - Edge cases (zero values, boundary conditions, overflow)
   - Revert cases (all require/revert conditions)
3. Comments for non-trivial logic

RULES:
- Follow decisions from ADRs
- Tests are written TOGETHER with the code, not after
- Events for all state changes
- Access control on all external/public functions
- No magic numbers (use constants)
- Checks for address(0) and empty values
- Don't optimize gas at the expense of readability
- If something is unclear in the requirements -- ASK, don't guess
```
