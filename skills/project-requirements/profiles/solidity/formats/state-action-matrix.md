# state-action-matrix.md formatting rules

## State categories (rows)

Default states:
- **Normal** — fully operational baseline.
- **Paused** — temporary halt of state-changing operations.
- **Emergency** — protective mode triggered by severe conditions.
- **Uninitialized** — pre-deployment / pre-setup state.

Profile may add system-specific states (e.g. `Migrating`, `Closed`, `Draining`).

## Structure

```markdown
# State × Action Matrix

| State \ Action | Deposit | Withdraw | Configure | Pause |
|----------------|---------|----------|-----------|-------|
| Normal         | works (FR-001) | works (FR-002) | works (FR-010) | works (FR-011) |
| Paused         | blocked (FR-001) | works (FR-002) | works (FR-010) | — |
| Emergency      | blocked (FR-001) | works via emergency (FR-014) | undefined | — |
| Uninitialized  | undefined | undefined | works (FR-010) | undefined |

## State entry / exit

- **Normal** → enter on init complete (FR-010); exit on Pause (FR-011) or Emergency (FR-013).
- **Paused** → enter via FR-011; exit via FR-012.
- **Emergency** → enter via FR-013; exit: [GAP] not defined.
- **Uninitialized** → exit on init (FR-010); never re-enter.

## Gaps

[GAP]: behavior of Configure in Emergency state not defined
[GAP]: behavior of Deposit/Withdraw/Pause in Uninitialized state not defined
[GAP]: Emergency state has no exit condition defined
```

## Rules

- One row per state, one column per distinct action.
- Cell values: `works (FR-NN)`, `blocked (FR-NN)`, `undefined`, or `—` (action not relevant in this state, e.g. you cannot `Pause` while already paused).
- Every `undefined` → `[GAP]` listed in the Gaps section.
- Every state without an entry/exit definition → `[GAP]`.
