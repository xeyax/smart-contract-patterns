# Plan Formatting Rules (Python library)

Rules for `plan.md` artifact.

## Structure

```markdown
# Development Plan

## Tasks

| # | Task | Component | Depends on | Traceable to |
|---|------|-----------|------------|-------------|
| 1 | Project scaffolding (`src/` layout, pyproject.toml, CI) | — | — | — |
| 2 | Exception hierarchy module | `mypkg.errors` | 1 | AD-012, error-taxonomy |
| 3 | Config loader + validation | `mypkg.config` | 2 | AD-004 |
| 4 | Core parser | `mypkg.parser` | 2 | AD-007, interfaces |
| 5 | Session orchestrator | `mypkg.session` | 3, 4 | AD-001, call-diagrams |
| 6 | Public API surface + `__init__.py` exports | `mypkg` | 5 | AD-015, public-api |
| 7 | Contract test suite (abstract base classes) | `tests/` | 4, 5 | specs |
| 8 | Integration tests against reference data | `tests/integration` | 7 | — |

## Order

Build inside-out:
1. Foundations (scaffolding, errors, config) — no library deps on each other.
2. Pure modules (parser, transformers) — depend only on foundations.
3. Orchestrators (Session) — tie pure modules together.
4. Public surface (`__init__.py` exports) — last, so internal structure can still move.
5. Tests alongside each layer, then cross-layer integration.

(mermaid graph LR showing task dependencies)
```

## Rules

- **One task = one bounded unit of work** (implementable + testable in isolation).
- **Component** column is the Python module/package the task delivers. Use `—` for cross-cutting tasks (setup, integration tests).
- **Depends on** = task numbers that must be done first. No circular dependencies.
- **Traceable to** = `AD-NNN` decisions or artifact name (e.g. `specs`, `interfaces`) that define this task's scope.
- Include scaffolding as task 1. Include a separate task for the public API surface — it must come after all internals are in place so exports do not churn.
- Mermaid `graph LR` for dependency visualization.
- If any component from `components.md` or any function from `interfaces/*.py` does not map to a task → `[GAP]`.
