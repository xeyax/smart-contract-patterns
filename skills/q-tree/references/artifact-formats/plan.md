# Plan Formatting Rules

Rules for `plan.md` artifact.

## Structure

```markdown
# Development Plan

## Tasks

| # | Task | Contract | Depends on | Traceable to |
|---|------|----------|------------|-------------|
| 1 | Deploy setup (Foundry, fork, test infra) | — | — | — |
| 2 | Vault base (ERC-4626, deposit/withdraw) | Vault | 1 | d:capital-flow |
| 3 | Strategy base (deploy/withdraw capital) | Strategy | 2 | d:strategy-sep |
| 4 | Integration tests on fork | All | 2, 3 | — |

## Order

Build bottom-up: adapters → core contracts → integrations → tests.

(mermaid graph LR showing task dependencies)
```

## Rules

- One task = one bounded unit of work (implementable + testable in isolation).
- **Depends on** = what must be done first. No circular dependencies.
- **Traceable to** = q-tree `[d:tag]` that defines this task's scope.
- Include setup as task 1 and integration tests as final task.
- Mermaid `graph LR` for dependency visualization.
